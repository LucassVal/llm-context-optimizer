# @UBL @UBL @ADP-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
NC-ADP-FR-001  Mission Control Generic Adapter Implementation

Adapter for connecting NeoCortex to Mission Control dashboard (localhost:3000).
Implements generic adapter interface: register, heartbeat, report, assignments.

Based on NC-LBE-INT-004-mission-control.mdc (INTEGRAO COM NEOCORTEX section).
"""

import concurrent.futures
import json
import logging
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class MissionControlAction(StrEnum):
    """Actions supported by Mission Control generic adapter endpoint."""

    REGISTER = "register"
    HEARTBEAT = "heartbeat"
    REPORT = "report"
    ASSIGNMENTS = "assignments"
    DISCONNECT = "disconnect"


@dataclass
class MissionControlConfig:
    """Configuration for Mission Control adapter."""

    base_url: str = "http://localhost:3000"
    api_endpoint: str = "/api/adapters"
    framework: str = "generic"
    agent_id: str = ""
    name: str = "neocortex-agent"
    role: str = "coder"
    capabilities: list | None = None
    metadata: dict | None = None
    heartbeat_interval_sec: int = 30
    timeout_sec: int = 3
    max_retries: int = 3
    circuit_breaker_failures: int = 5
    circuit_breaker_reset_sec: int = 60

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["mcp-tools", "code-generation", "debugging"]
        if self.metadata is None:
            self.metadata = {"neocortex_version": "v42", "port": 45132}


class MissionControlAdapter:
    """Adapter for Mission Control integration."""

    def __init__(self, config: MissionControlConfig | None = None):
        """
        Initialize Mission Control adapter.

        Args:
            config: Configuration object. If None, uses defaults.
        """
        self.config = config or MissionControlConfig()
        # No session with urllib; headers will be added per request
        self._failure_count = 0
        self._circuit_open_until = 0
        self._last_heartbeat = 0
        self._registered = False
        # Thread pool for fire-and-forget requests
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="MCAdapter",
        )
        self._shutdown_event = threading.Event()

    def _call_api(
        self, action: MissionControlAction, payload: dict[str, Any]
    ) -> dict[str, Any] | None:
        """
        Make API call to Mission Control generic adapter endpoint.

        Args:
            action: Action to perform
            payload: Payload for the action

        Returns:
            Response JSON as dict, or None if failed

        Raises:
            Exception: Only if circuit breaker is closed and max retries exceeded.
        """
        # Circuit breaker check
        if self._failure_count >= self.config.circuit_breaker_failures:
            current_time = time.time()
            if current_time < self._circuit_open_until:
                logger.warning(
                    "Circuit breaker open, skipping API call. Will reset at %s",
                    time.ctime(self._circuit_open_until),
                )
                return None
            else:
                # Reset circuit breaker after reset period
                logger.info("Circuit breaker reset after cooldown period")
                self._failure_count = 0
                self._circuit_open_until = 0

        url = f"{self.config.base_url}{self.config.api_endpoint}"
        data = {
            "framework": self.config.framework,
            "action": action.value,
            "payload": payload,
        }
        json_data = json.dumps(data).encode("utf-8")
        headers = {"Content-Type": "application/json"}

        for attempt in range(self.config.max_retries):
            try:
                req = urllib.request.Request(
                    url, data=json_data, headers=headers, method="POST"
                )
                # Set timeout (seconds)
                response = urllib.request.urlopen(req, timeout=self.config.timeout_sec)
                if response.status == 200:
                    response_data = response.read()
                    self._failure_count = 0  # Reset on success
                    return json.loads(response_data)
                else:
                    raise urllib.error.HTTPError(
                        url,
                        response.status,
                        response.reason,
                        response.headers,
                        response,
                    )
            except urllib.error.URLError as e:
                logger.warning(
                    "Mission Control API call failed (attempt %d/%d): %s",
                    attempt + 1,
                    self.config.max_retries,
                    str(e),
                )
                if attempt < self.config.max_retries - 1:
                    # Exponential backoff using threading.Event.wait to allow shutdown
                    backoff_seconds = 1 * (2**attempt)
                    self._shutdown_event.wait(timeout=backoff_seconds)
                    # If shutdown event is set, abort retries
                    if self._shutdown_event.is_set():
                        logger.info("Shutdown during backoff, aborting API call")
                        return None
                else:
                    self._failure_count += 1
                    if self._failure_count >= self.config.circuit_breaker_failures:
                        self._circuit_open_until = (
                            time.time() + self.config.circuit_breaker_reset_sec
                        )
                        logger.error(
                            "Circuit breaker opened after %d consecutive failures. "
                            "Will remain open for %d seconds.",
                            self._failure_count,
                            self.config.circuit_breaker_reset_sec,
                        )
                    raise
            except Exception as e:
                logger.warning(
                    "Mission Control API call failed (attempt %d/%d): %s",
                    attempt + 1,
                    self.config.max_retries,
                    str(e),
                )
                if attempt < self.config.max_retries - 1:
                    backoff_seconds = 1 * (2**attempt)
                    self._shutdown_event.wait(timeout=backoff_seconds)
                    if self._shutdown_event.is_set():
                        logger.info("Shutdown during backoff, aborting API call")
                        return None
                else:
                    self._failure_count += 1
                    if self._failure_count >= self.config.circuit_breaker_failures:
                        self._circuit_open_until = (
                            time.time() + self.config.circuit_breaker_reset_sec
                        )
                        logger.error(
                            "Circuit breaker opened after %d consecutive failures. "
                            "Will remain open for %d seconds.",
                            self._failure_count,
                            self.config.circuit_breaker_reset_sec,
                        )
                    raise

        return None

    def register_with_mission_control(self, **kwargs) -> bool:
        """
        Register NeoCortex agent with Mission Control.

        Args:
            **kwargs: Override any registration parameters

        Returns:
            True if registration successful, False otherwise
        """
        agent_id = kwargs.get("agent_id", self.config.agent_id)
        if not agent_id:
            logger.error("Cannot register without agent_id")
            return False

        payload = {
            "agentId": agent_id,
            "name": kwargs.get("name", self.config.name),
            "role": kwargs.get("role", self.config.role),
            "capabilities": kwargs.get("capabilities", self.config.capabilities),
            "metadata": kwargs.get("metadata", self.config.metadata),
        }

        try:
            result = self._call_api(MissionControlAction.REGISTER, payload)
            if result is not None:
                logger.info(
                    "Successfully registered agent %s with Mission Control", agent_id
                )
                self._registered = True
                return True
            else:
                logger.warning(
                    "Registration failed (circuit breaker open or no response)"
                )
                return False
        except Exception as e:
            logger.error("Registration failed with error: %s", str(e))
            return False

    def send_heartbeat(self, **kwargs) -> bool:
        """
        Send heartbeat to Mission Control.

        Args:
            **kwargs: Additional heartbeat data

        Returns:
            True if heartbeat successful, False otherwise
        """
        if not self._registered:
            logger.warning("Cannot send heartbeat: agent not registered")
            return False

        current_time = time.time()
        if current_time - self._last_heartbeat < self.config.heartbeat_interval_sec:
            logger.debug("Skipping heartbeat, too soon")
            return True

        agent_id = kwargs.get("agent_id", self.config.agent_id)
        payload = {
            "agentId": agent_id,
            "timestamp": int(current_time * 1000),
            "status": "online",
            **kwargs,
        }

        try:
            result = self._call_api(MissionControlAction.HEARTBEAT, payload)
            if result is not None:
                self._last_heartbeat = current_time
                logger.debug("Heartbeat sent successfully for agent %s", agent_id)
                return True
            else:
                logger.debug("Heartbeat skipped (circuit breaker open)")
                return False
        except Exception as e:
            logger.error("Heartbeat failed with error: %s", str(e))
            return False

    def report_task(
        self, task_id: str, status: str, details: dict[str, Any], **kwargs
    ) -> bool:
        """
        Report task status to Mission Control.

        Args:
            task_id: Mission Control task identifier
            status: Task status (e.g., "started", "completed", "failed")
            details: Additional task details
            **kwargs: Extra parameters

        Returns:
            True if report successful, False otherwise
        """
        if not self._registered:
            logger.warning("Cannot report task: agent not registered")
            return False

        agent_id = kwargs.get("agent_id", self.config.agent_id)
        payload = {
            "agentId": agent_id,
            "taskId": task_id,
            "status": status,
            "details": details,
            "timestamp": int(time.time() * 1000),
            **kwargs,
        }

        try:
            result = self._call_api(MissionControlAction.REPORT, payload)
            if result is not None:
                logger.info("Task %s reported with status %s", task_id, status)
                return True
            else:
                logger.warning("Task report failed (circuit breaker open)")
                return False
        except Exception as e:
            logger.error("Task report failed with error: %s", str(e))
            return False

    def report(self, event_type: str, data: dict[str, Any]) -> None:
        """
        Fire-and-forget report of an arbitrary event to Mission Control.
        This method does not block; it submits the report to a background thread.
        """
        if not self._registered:
            logger.warning("Cannot report event: agent not registered")
            return
        payload = {
            "agentId": self.config.agent_id,
            "eventType": event_type,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        # Submit to thread pool (fire-and-forget)
        self._executor.submit(self._call_api, MissionControlAction.REPORT, payload)
        logger.debug("Report submitted for event_type=%s", event_type)

    def fetch_assignments(self, **kwargs) -> dict[str, Any] | None:
        """
        Fetch assigned tasks from Mission Control.

        Args:
            **kwargs: Additional query parameters

        Returns:
            Assignments dictionary, or None if failed
        """
        if not self._registered:
            logger.warning("Cannot fetch assignments: agent not registered")
            return None

        agent_id = kwargs.get("agent_id", self.config.agent_id)
        payload = {"agentId": agent_id, "timestamp": int(time.time() * 1000), **kwargs}

        try:
            result = self._call_api(MissionControlAction.ASSIGNMENTS, payload)
            if result is not None:
                logger.debug("Fetched assignments for agent %s", agent_id)
                return result
            else:
                logger.debug("No assignments (circuit breaker open or empty)")
                return None
        except Exception as e:
            logger.error("Failed to fetch assignments: %s", str(e))
            return None

    def disconnect(self, **kwargs) -> bool:
        """
        Disconnect agent from Mission Control.

        Args:
            **kwargs: Additional disconnect parameters

        Returns:
            True if disconnect successful, False otherwise
        """
        if not self._registered:
            logger.warning("Cannot disconnect: agent not registered")
            return False

        agent_id = kwargs.get("agent_id", self.config.agent_id)
        payload = {"agentId": agent_id, "timestamp": int(time.time() * 1000), **kwargs}

        try:
            result = self._call_api(MissionControlAction.DISCONNECT, payload)
            if result is not None:
                logger.info("Agent %s disconnected from Mission Control", agent_id)
                self._registered = False
                return True
            else:
                logger.warning("Disconnect failed (circuit breaker open)")
                return False
        except Exception as e:
            logger.error("Disconnect failed with error: %s", str(e))
            return False

    def shutdown(self):
        """Shutdown adapter resources."""
        self._shutdown_event.set()
        self._executor.shutdown(wait=False)
        logger.info("MissionControlAdapter resources shutdown")


# Convenience function for easy access
def get_mission_control_adapter(
    config: MissionControlConfig | None = None,
) -> MissionControlAdapter:
    """
    Get a MissionControlAdapter instance.

    Usage:
        adapter = get_mission_control_adapter()
        adapter.register_with_mission_control(agent_id="neocortex-agent-001")
    """
    return MissionControlAdapter(config)
