"""---
_genealogy:
  injected_at: '2026-04-16T00:23:59.041572'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SVC-FR-015-task-broker
related_ssot:
  - NC-TOOL-FR-035-task
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-SVC-FR-015-task-broker.py
FR-015  TaskBroker: Persistent task tracking with retry and polling.

Provides centralized task registration, persistence, status tracking,
and result retrieval for orchestrated tasks sent to sub-servers.
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskBroker:
    """
    Persistent task broker for orchestration.

    Features:
    - Register tasks with UUID
    - Persist state to JSON file
    - Polling with exponential backoff (2s  4s  8s)
    - Status tracking: queued, running, done, failed, timeout, cancelled
    - Automatic retry (3 attempts)
    """

    _instance = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(TaskBroker, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._lock = threading.Lock()
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._queue_file: Optional[Path] = None
        self._load_config()

        # Load existing tasks from disk
        self._load_queue()

        self._initialized = True

    def _load_config(self) -> None:
        """Load configuration and determine data directory."""
        try:
            from neocortex.config import get_config

            config = get_config()
            data_dir = config.data_dir
        except Exception as e:
            logger.warning(f"Failed to load config, using default data directory: {e}")
            data_dir = Path.cwd() / "data"

        data_dir.mkdir(parents=True, exist_ok=True)
        self._queue_file = data_dir / "task_queue.json"

    def _load_queue(self) -> None:
        """Load task queue from disk."""
        if self._queue_file is None or not self._queue_file.exists():
            return

        try:
            with open(self._queue_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self._tasks = data
                else:
                    self._tasks = {}
        except Exception as e:
            logger.error(f"Failed to load task queue from {self._queue_file}: {e}")
            self._tasks = {}

    def _save_queue(self) -> None:
        """Save task queue to disk."""
        if self._queue_file is None:
            return

        try:
            with open(self._queue_file, "w", encoding="utf-8") as f:
                json.dump(self._tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save task queue to {self._queue_file}: {e}")

    # Public API (compatible with NC-TOOL-FR-035-task.py)
    def register_task(
        self,
        task_id: str,
        port: int,
        task_data: Dict[str, Any],
        timeout_seconds: int = 30,
        subserver_role: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Register a new task for tracking.

        Args:
            task_id: Unique task identifier (provided by caller).
            port: Subserver port where the task was sent.
            task_data: Original task payload (JSONserializable).
            timeout_seconds: Timeout for polling (not yet used).
            subserver_role: Role of the subserver (courier/engineer/guardian).

        Returns:
            Dict with success flag.
        """
        task = {
            "task_id": task_id,
            "port": port,
            "role": subserver_role,
            "task_data": task_data,
            "status": "queued",
            "attempts": 0,
            "max_attempts": 3,
            "created_at": time.time(),
            "updated_at": time.time(),
            "result": None,
            "error": None,
            "timeout_seconds": timeout_seconds,
            "polling_url": f"http://127.0.0.1:{port}/task/{task_id}",
        }

        with self._lock:
            self._tasks[task_id] = task
            self._save_queue()

        logger.info(f"Registered task {task_id} for port {port}, role {subserver_role}")
        return {"success": True, "task_id": task_id}

    def update_task_status(
        self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update task status and optionally store result.

        Allowed statuses: queued, running, done, failed, timeout, cancelled.
        """
        allowed = {"queued", "running", "done", "failed", "timeout", "cancelled"}
        if status not in allowed:
            logger.error(f"Invalid status '{status}' for task {task_id}")
            return {"success": False, "error": f"Invalid status '{status}'"}

        with self._lock:
            if task_id not in self._tasks:
                logger.error(f"Task {task_id} not found")
                return {"success": False, "error": f"Task {task_id} not found"}

            task = self._tasks[task_id]
            task["status"] = status
            task["updated_at"] = time.time()
            if result is not None:
                task["result"] = result
            self._save_queue()

        logger.debug(f"Task {task_id} status updated to {status}")
        return {"success": True, "task_id": task_id, "status": status}

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Retrieve task status and result."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}
            return {
                "success": True,
                "task_id": task_id,
                "status": task.get("status", "unknown"),
                "result": task.get("result"),
                "port": task.get("port"),
                "created_at": task.get("created_at"),
            }

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a queued or running task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}
            current_status = task.get("status")
            if current_status in ("done", "failed", "cancelled"):
                return {
                    "success": False,
                    "error": f"Cannot cancel task with status '{current_status}'",
                }
            task["status"] = "cancelled"
            task["updated_at"] = time.time()
            self._save_queue()
        return {"success": True, "task_id": task_id, "cancelled": True}

    def list_queued_tasks(self, port: Optional[int] = None) -> Dict[str, Any]:
        """List all queued tasks, optionally filtered by port."""
        with self._lock:
            tasks = []
            for task in self._tasks.values():
                if task.get("status") != "queued":
                    continue
                if port is not None and task.get("port") != port:
                    continue
                tasks.append(
                    {
                        "task_id": task.get("task_id"),
                        "port": task.get("port"),
                        "role": task.get("role"),
                        "created_at": task.get("created_at"),
                    }
                )
            return {"success": True, "tasks": tasks}

    # Additional utility methods
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve raw task entry (internal use)."""
        with self._lock:
            return self._tasks.get(task_id)

    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all tasks with given status."""
        with self._lock:
            return [t for t in self._tasks.values() if t.get("status") == status]

    def increment_attempt(self, task_id: str) -> bool:
        """Increment attempt count for a task."""
        with self._lock:
            if task_id not in self._tasks:
                return False
            self._tasks[task_id]["attempts"] += 1
            self._save_queue()
        return True

    def poll_result(
        self, task_id: str, timeout_sec: int = 30, poll_interval: float = 2.0
    ) -> Optional[Dict[str, Any]]:
        """
        Poll subserver for task result with exponential backoff and retry.

        This method will attempt up to max_attempts with backoff 2s  4s  8s.
        If the subserver returns a result, the task status is updated to 'done'.
        If all attempts fail, status becomes 'failed'.

        Args:
            task_id: Task identifier.
            timeout_sec: Maximum total waiting time.
            poll_interval: Initial polling interval (doubles each attempt).

        Returns:
            Result dictionary if successful, None otherwise.
        """
        task = self.get_task(task_id)
        if task is None:
            logger.error(f"Cannot poll unknown task {task_id}")
            return None

        port = task["port"]
        attempts = task["attempts"]
        max_attempts = task["max_attempts"]

        # Update status to running
        self.update_task_status(task_id, "running")

        current_interval = poll_interval
        start_time = time.time()

        while attempts < max_attempts and (time.time() - start_time) < timeout_sec:
            try:
                # Poll subserver's /task/{task_id} endpoint (if exists)
                url = f"http://127.0.0.1:{port}/task/{task_id}"
                import urllib.request

                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        result = json.loads(resp.read().decode("utf-8"))
                        # Success
                        self.update_task_status(task_id, "done", result=result)
                        logger.info(f"Task {task_id} completed successfully")
                        return result
                    else:
                        logger.warning(
                            f"Poll for {task_id} returned HTTP {resp.status}"
                        )
            except Exception as e:
                logger.debug(f"Poll attempt {attempts + 1} for {task_id} failed: {e}")

            # Wait before next attempt
            time.sleep(current_interval)
            self.increment_attempt(task_id)
            attempts += 1
            current_interval *= 2  # Exponential backoff

        # All attempts exhausted or timeout
        self.update_task_status(
            task_id, "failed", result={"error": "Polling exhausted or timeout"}
        )
        logger.warning(f"Task {task_id} failed after {attempts} attempts")
        return None

    def cleanup_old_tasks(self, max_age_hours: int = 24) -> int:
        """
        Remove tasks older than max_age_hours (default 24h).

        Returns:
            Number of tasks removed.
        """
        cutoff = time.time() - (max_age_hours * 3600)
        to_delete = []
        with self._lock:
            for task_id, task in self._tasks.items():
                if task.get("created_at", 0) < cutoff:
                    to_delete.append(task_id)
            for task_id in to_delete:
                del self._tasks[task_id]
            if to_delete:
                self._save_queue()
        return len(to_delete)


# Singleton accessor
def get_task_broker() -> TaskBroker:
    """Get the singleton TaskBroker instance."""
    return TaskBroker()
