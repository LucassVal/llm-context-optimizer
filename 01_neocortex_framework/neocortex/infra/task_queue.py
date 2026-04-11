#!/usr/bin/env python3
"""
TaskQueue - Persistent task queue for NeoCortex background operations.

Provides reliable task scheduling, execution, and monitoring with SQLite backend.
"""

import json
import logging
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Task status states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRY = "retry"


class TaskPriority(int, Enum):
    """Task priority levels."""

    LOW = 10
    NORMAL = 20
    HIGH = 30
    CRITICAL = 40


@dataclass
class Task:
    """Task definition."""

    id: str
    name: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        name: str,
        payload: Dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        max_retries: int = 3,
        schedule_delay_seconds: int = 0,
        **kwargs,
    ) -> "Task":
        """
        Create a new task.

        Args:
            name: Task name/type.
            payload: Task payload data.
            priority: Task priority.
            max_retries: Maximum retry attempts.
            schedule_delay_seconds: Delay before task becomes available.
            **kwargs: Additional task attributes.

        Returns:
            New Task instance.
        """
        task_id = str(uuid.uuid4())

        scheduled_for = None
        if schedule_delay_seconds > 0:
            scheduled_for = datetime.now() + timedelta(seconds=schedule_delay_seconds)

        return cls(
            id=task_id,
            name=name,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
            scheduled_for=scheduled_for,
            **kwargs,
        )


class TaskQueue:
    """
    Persistent task queue with SQLite backend.

    Features:
    - Persistent storage with SQLite
    - Priority-based scheduling
    - Retry logic with exponential backoff
    - Task dependencies
    - Progress tracking
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize task queue.

        Args:
            db_path: Path to SQLite database file.
        """
        if db_path is None:
            from ..config import get_config

            config = get_config()
            db_path = config.project_root / ".neocortex" / "cache" / "task_queue.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path

        # Thread safety
        self.lock = threading.RLock()

        # Initialize database
        self._init_database()

        # Worker thread control
        self._worker_thread = None
        self._stop_worker = threading.Event()
        self._worker_interval = 5.0  # seconds

        # Task handlers
        self._handlers = {}

        logger.info(f"TaskQueue initialized at {db_path}")

    def _init_database(self):
        """Initialize database schema."""
        with self.lock:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row

            # Tasks table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                priority INTEGER NOT NULL,
                max_retries INTEGER NOT NULL,
                retry_count INTEGER NOT NULL,
                created_at TIMESTAMP NOT NULL,
                scheduled_for TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                result_json TEXT,
                metadata_json TEXT,
                
                -- Indexes for common queries
                INDEX idx_status_priority (status, priority DESC),
                INDEX idx_scheduled_for (scheduled_for),
                INDEX idx_created_at (created_at DESC)
            )
            """)

            # Task dependencies table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS task_dependencies (
                task_id TEXT NOT NULL,
                depends_on_id TEXT NOT NULL,
                PRIMARY KEY (task_id, depends_on_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                FOREIGN KEY (depends_on_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
            """)

            # Task logs table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS task_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metadata_json TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            )
            """)

            conn.commit()
            conn.close()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with row factory."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def enqueue(self, task: Task) -> str:
        """
        Enqueue a task for execution.

        Args:
            task: Task to enqueue.

        Returns:
            Task ID.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                INSERT INTO tasks (
                    id, name, payload_json, status, priority, max_retries, retry_count,
                    created_at, scheduled_for, started_at, completed_at,
                    error_message, result_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        task.id,
                        task.name,
                        json.dumps(task.payload),
                        task.status.value,
                        task.priority.value,
                        task.max_retries,
                        task.retry_count,
                        task.created_at.isoformat(),
                        task.scheduled_for.isoformat() if task.scheduled_for else None,
                        task.started_at.isoformat() if task.started_at else None,
                        task.completed_at.isoformat() if task.completed_at else None,
                        task.error_message,
                        json.dumps(task.result) if task.result else None,
                        json.dumps(task.metadata),
                    ),
                )

                conn.commit()
                logger.debug(f"Enqueued task: {task.name} ({task.id})")
                return task.id

            except Exception as e:
                logger.error(f"Failed to enqueue task: {e}")
                raise
            finally:
                conn.close()

    def dequeue(self, worker_id: str = "default") -> Optional[Task]:
        """
        Dequeue the next available task for execution.

        Args:
            worker_id: Worker identifier for logging.

        Returns:
            Task to execute, or None if no tasks available.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                # Find next pending task that's scheduled for now or earlier
                now = datetime.now().isoformat()

                cursor = conn.execute(
                    """
                SELECT * FROM tasks 
                WHERE status = ? 
                AND (scheduled_for IS NULL OR scheduled_for <= ?)
                AND NOT EXISTS (
                    SELECT 1 FROM task_dependencies 
                    WHERE task_dependencies.task_id = tasks.id 
                    AND task_dependencies.depends_on_id IN (
                        SELECT id FROM tasks WHERE status != ?
                    )
                )
                ORDER BY priority DESC, created_at
                LIMIT 1
                FOR UPDATE
                """,
                    (TaskStatus.PENDING.value, now, TaskStatus.COMPLETED.value),
                )

                row = cursor.fetchone()
                if not row:
                    return None

                # Update task status
                task_id = row["id"]
                conn.execute(
                    """
                UPDATE tasks 
                SET status = ?, started_at = ?, retry_count = retry_count + 1
                WHERE id = ?
                """,
                    (TaskStatus.RUNNING.value, now, task_id),
                )

                conn.commit()

                # Convert row to Task object
                task = self._row_to_task(row)
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.fromisoformat(now)

                logger.debug(
                    f"Dequeued task: {task.name} ({task.id}) for worker {worker_id}"
                )
                return task

            except Exception as e:
                logger.error(f"Failed to dequeue task: {e}")
                return None
            finally:
                conn.close()

    def complete(self, task_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Mark task as completed.

        Args:
            task_id: Task ID.
            result: Task result data.

        Returns:
            True if successful.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                now = datetime.now().isoformat()

                conn.execute(
                    """
                UPDATE tasks 
                SET status = ?, completed_at = ?, result_json = ?
                WHERE id = ?
                """,
                    (
                        TaskStatus.COMPLETED.value,
                        now,
                        json.dumps(result) if result else None,
                        task_id,
                    ),
                )

                conn.commit()
                logger.debug(f"Completed task: {task_id}")
                return True

            except Exception as e:
                logger.error(f"Failed to complete task {task_id}: {e}")
                return False
            finally:
                conn.close()

    def fail(self, task_id: str, error_message: str) -> bool:
        """
        Mark task as failed.

        Args:
            task_id: Task ID.
            error_message: Error description.

        Returns:
            True if successful.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                task = self.get_task(task_id)
                if not task:
                    return False

                now = datetime.now().isoformat()
                new_status = TaskStatus.FAILED

                # Check if task should be retried
                if task.retry_count < task.max_retries:
                    new_status = TaskStatus.RETRY
                    # Schedule for retry with exponential backoff
                    backoff_seconds = min(300, 2**task.retry_count)  # Max 5 minutes
                    scheduled_for = datetime.now() + timedelta(seconds=backoff_seconds)

                    conn.execute(
                        """
                    UPDATE tasks 
                    SET status = ?, error_message = ?, scheduled_for = ?
                    WHERE id = ?
                    """,
                        (
                            new_status.value,
                            error_message,
                            scheduled_for.isoformat(),
                            task_id,
                        ),
                    )
                else:
                    # Max retries exceeded
                    conn.execute(
                        """
                    UPDATE tasks 
                    SET status = ?, error_message = ?, completed_at = ?
                    WHERE id = ?
                    """,
                        (
                            new_status.value,
                            error_message,
                            now,
                            task_id,
                        ),
                    )

                conn.commit()
                logger.warning(f"Task failed: {task_id} - {error_message}")
                return True

            except Exception as e:
                logger.error(f"Failed to mark task {task_id} as failed: {e}")
                return False
            finally:
                conn.close()

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get task by ID.

        Args:
            task_id: Task ID.

        Returns:
            Task if found, None otherwise.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                return self._row_to_task(row) if row else None
            finally:
                conn.close()

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Task]:
        """
        List tasks with optional filters.

        Args:
            status: Filter by status.
            name: Filter by task name.
            limit: Maximum results.
            offset: Result offset.

        Returns:
            List of tasks.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                query = "SELECT * FROM tasks WHERE 1=1"
                params = []

                if status:
                    query += " AND status = ?"
                    params.append(status.value)

                if name:
                    query += " AND name = ?"
                    params.append(name)

                query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                cursor = conn.execute(query, params)
                return [self._row_to_task(row) for row in cursor.fetchall()]
            finally:
                conn.close()

    def add_dependency(self, task_id: str, depends_on_id: str) -> bool:
        """
        Add task dependency.

        Args:
            task_id: Task ID.
            depends_on_id: ID of task this task depends on.

        Returns:
            True if successful.
        """
        with self.lock:
            conn = self._get_connection()
            try:
                conn.execute(
                    """
                INSERT OR IGNORE INTO task_dependencies (task_id, depends_on_id)
                VALUES (?, ?)
                """,
                    (task_id, depends_on_id),
                )

                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to add dependency: {e}")
                return False
            finally:
                conn.close()

    def register_handler(
        self, task_name: str, handler: Callable[[Task], Dict[str, Any]]
    ):
        """
        Register task handler.

        Args:
            task_name: Task name to handle.
            handler: Handler function.
        """
        self._handlers[task_name] = handler
        logger.debug(f"Registered handler for task type: {task_name}")

    def process_next(self, worker_id: str = "default") -> bool:
        """
        Process next available task.

        Args:
            worker_id: Worker identifier.

        Returns:
            True if a task was processed.
        """
        task = self.dequeue(worker_id)
        if not task:
            return False

        try:
            # Find handler
            handler = self._handlers.get(task.name)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task.name}")

            # Execute handler
            logger.info(f"Processing task: {task.name} ({task.id})")
            result = handler(task)

            # Mark as completed
            self.complete(task.id, result)
            logger.info(f"Task completed: {task.name} ({task.id})")

            return True

        except Exception as e:
            logger.error(f"Task processing failed: {e}")
            self.fail(task.id, str(e))
            return False

    def start_worker(self, worker_id: str = "default", interval: float = 5.0):
        """
        Start background worker thread.

        Args:
            worker_id: Worker identifier.
            interval: Polling interval in seconds.
        """
        if self._worker_thread and self._worker_thread.is_alive():
            logger.warning("Worker thread already running")
            return

        self._stop_worker.clear()
        self._worker_interval = interval

        def worker_loop():
            logger.info(f"Task worker started: {worker_id}")
            while not self._stop_worker.is_set():
                try:
                    processed = self.process_next(worker_id)
                    if not processed:
                        # No tasks, sleep for interval
                        time.sleep(self._worker_interval)
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                    time.sleep(self._worker_interval)

            logger.info(f"Task worker stopped: {worker_id}")

        self._worker_thread = threading.Thread(
            target=worker_loop,
            name=f"TaskQueueWorker-{worker_id}",
            daemon=True,
        )
        self._worker_thread.start()

    def stop_worker(self):
        """Stop background worker thread."""
        if self._worker_thread and self._worker_thread.is_alive():
            logger.info("Stopping task worker...")
            self._stop_worker.set()
            self._worker_thread.join(timeout=10.0)
            self._worker_thread = None

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self.lock:
            conn = self._get_connection()
            try:
                cursor = conn.execute("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    AVG((julianday(completed_at) - julianday(started_at)) * 86400) as avg_duration_seconds
                FROM tasks 
                WHERE started_at IS NOT NULL
                GROUP BY status
                """)

                stats = {"by_status": {}}
                for row in cursor.fetchall():
                    stats["by_status"][row["status"]] = {
                        "count": row["count"],
                        "avg_duration_seconds": row["avg_duration_seconds"],
                    }

                # Total counts
                cursor = conn.execute("SELECT COUNT(*) as total FROM tasks")
                stats["total_tasks"] = cursor.fetchone()["total"]

                # Pending tasks
                cursor = conn.execute(
                    """
                SELECT COUNT(*) as pending FROM tasks 
                WHERE status = ?
                """,
                    (TaskStatus.PENDING.value,),
                )
                stats["pending_tasks"] = cursor.fetchone()["pending"]

                # Average age of pending tasks
                cursor = conn.execute(
                    """
                SELECT AVG((julianday('now') - julianday(created_at)) * 86400) as avg_age_seconds
                FROM tasks 
                WHERE status = ?
                """,
                    (TaskStatus.PENDING.value,),
                )
                stats["avg_pending_age_seconds"] = (
                    cursor.fetchone()["avg_age_seconds"] or 0
                )

                return stats
            finally:
                conn.close()

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        """Convert database row to Task object."""
        return Task(
            id=row["id"],
            name=row["name"],
            payload=json.loads(row["payload_json"]),
            status=TaskStatus(row["status"]),
            priority=TaskPriority(row["priority"]),
            max_retries=row["max_retries"],
            retry_count=row["retry_count"],
            created_at=datetime.fromisoformat(row["created_at"]),
            scheduled_for=datetime.fromisoformat(row["scheduled_for"])
            if row["scheduled_for"]
            else None,
            started_at=datetime.fromisoformat(row["started_at"])
            if row["started_at"]
            else None,
            completed_at=datetime.fromisoformat(row["completed_at"])
            if row["completed_at"]
            else None,
            error_message=row["error_message"],
            result=json.loads(row["result_json"]) if row["result_json"] else None,
            metadata=json.loads(row["metadata_json"]) if row["metadata_json"] else {},
        )

    def close(self):
        """Close task queue and stop worker."""
        self.stop_worker()

    def __del__(self):
        """Cleanup on deletion."""
        self.close()


def create_task_queue(db_path: Optional[Path] = None) -> TaskQueue:
    """
    Create a TaskQueue instance.

    Args:
        db_path: Path to SQLite database file.

    Returns:
        TaskQueue instance.
    """
    return TaskQueue(db_path=db_path)
