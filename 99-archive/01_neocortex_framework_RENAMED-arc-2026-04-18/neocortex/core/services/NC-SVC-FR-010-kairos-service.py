"""---
domain: "core"
layer: "core"
type: "file"
tags: ["svc", "010", "kairos", "service"]
hash: "auto-generated"
---"""
"""
NC-SVC-FR-010-kairos-service.py
FR-010  KairosService: Event-driven scheduling service for NeoCortex.

Integrates with EventBus (NC-SVC-FR-005) to publish tick events.
Maintains compatibility with pulse_scheduler.py existing via duck-typing.
Provides a wrapper/extension for scheduling tasks with event-driven notifications.

Restriction: server.py, sub_server.py are @LOCKS.
This module is a standalone service that can be imported by any module.
"""

import importlib
import logging
import os
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Dynamic import for hyphenated module name (EventBus)
spec = importlib.util.spec_from_file_location(
    "event_bus", Path(__file__).parent / "NC-SVC-FR-005-event-bus.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
get_event_bus = module.get_event_bus
NeoCortexEvent = module.NeoCortexEvent


logger = logging.getLogger(__name__)


class KairosService:
    """Servio event-driven para scheduling de tarefas NeoCortex.

    Integra com EventBus (NC-SVC-FR-005) para publicar eventos de tick.
    Mantm compatibilidade com pulse_scheduler.py existente.
    """

    _instance: Optional["KairosService"] = None
    _lock: threading.Lock

    # Feature flags via env var
    KAIROS_PUSH_NOTIFICATION = os.getenv(
        "KAIROS_PUSH_NOTIFICATION", "false"
    ).lower() in ("true", "1", "yes")
    KAIROS_CHANNELS = os.getenv("KAIROS_CHANNELS", "false").lower() in (
        "true",
        "1",
        "yes",
    )

    # Event names
    EVENT_TICK = "kairos.tick"
    EVENT_STARTED = "kairos.started"
    EVENT_STOPPED = "kairos.stopped"
    EVENT_TASK_SCHEDULED = "kairos.task_scheduled"
    EVENT_TASK_EXECUTED = "kairos.task_executed"

    def __new__(cls) -> "KairosService":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._lock = threading.Lock()
            cls._instance._tasks: Dict[str, Dict] = {}  # task_id -> task dict
            cls._instance._running = False
            cls._instance._tick_thread: Optional[threading.Thread] = None
            cls._instance._tick_interval = 1.0  # seconds
            cls._instance._event_bus = get_event_bus()
            cls._instance._load_pulse_tasks()
        return cls._instance

    def _load_pulse_tasks(self) -> None:
        """Carrega tarefas do pulse_scheduler existente via duck-typing."""
        try:
            # Tentar importar pulse_scheduler dinamicamente
            spec = importlib.util.spec_from_file_location(
                "pulse_scheduler", Path(__file__).parent.parent / "pulse_scheduler.py"
            )
            pulse_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pulse_module)
            # Verificar se h uma instncia global do PulseScheduler
            # No h garantia, ento apenas logamos que tentamos.
            logger.info("PulseScheduler module loaded for compatibility.")
        except Exception as e:
            logger.debug(f"Could not load pulse_scheduler: {e}")

    def _publish_event(self, event_type: str, payload: Any = None) -> None:
        """Publica um evento no EventBus."""
        event = NeoCortexEvent(
            event_type=event_type,
            payload=payload,
            timestamp=datetime.now(),
            source_tool="KairosService",
        )
        self._event_bus.publish(event)

    def _tick_loop(self) -> None:
        """Loop principal que publica eventos de tick peridicos."""
        while self._running:
            self._publish_event(self.EVENT_TICK, {"timestamp": time.time()})
            time.sleep(self._tick_interval)

    def _schedule_task_internal(
        self, task_id: str, fn: Callable, interval_s: int
    ) -> None:
        """Agenda uma tarefa com threading.Timer."""

        def task_wrapper():
            try:
                self._publish_event(self.EVENT_TASK_EXECUTED, {"task_id": task_id})
                fn()
            except Exception as e:
                logger.error(f"Task {task_id} execution error: {e}")
            finally:
                # Re-schedule if still exists
                with self._lock:
                    if task_id in self._tasks:
                        self._tasks[task_id]["timer"] = threading.Timer(
                            interval_s, self._tasks[task_id]["wrapper"]
                        )
                        self._tasks[task_id]["timer"].daemon = True
                        self._tasks[task_id]["timer"].start()
                        self._tasks[task_id]["next_run"] = time.time() + interval_s

        with self._lock:
            self._tasks[task_id] = {
                "id": task_id,
                "name": task_id,  # placeholder, will be overridden if task_name provided
                "fn": fn,
                "interval_s": interval_s,
                "wrapper": task_wrapper,
                "timer": None,
                "next_run": time.time() + interval_s,
            }
            self._tasks[task_id]["timer"] = threading.Timer(interval_s, task_wrapper)
            self._tasks[task_id]["timer"].daemon = True
            self._tasks[task_id]["timer"].start()

    def schedule(self, task_name: str, fn: Callable, interval_s: int) -> str:
        """Agenda uma nova tarefa peridica.

        Args:
            task_name: Nome descritivo da tarefa.
            fn: Funo a ser executada.
            interval_s: Intervalo em segundos entre execues.

        Returns:
            ID nico da tarefa.
        """
        task_id = f"{task_name}_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._schedule_task_internal(task_id, fn, interval_s)
            self._tasks[task_id]["name"] = task_name
        self._publish_event(
            self.EVENT_TASK_SCHEDULED,
            {"task_id": task_id, "task_name": task_name, "interval_s": interval_s},
        )
        logger.info(f"Scheduled task '{task_name}' (id={task_id}) every {interval_s}s")
        return task_id

    def cancel(self, task_id: str) -> bool:
        """Cancela uma tarefa agendada.

        Args:
            task_id: ID da tarefa a cancelar.

        Returns:
            True se a tarefa foi cancelada, False se no encontrada.
        """
        with self._lock:
            if task_id not in self._tasks:
                return False
            task = self._tasks.pop(task_id)
            if task["timer"]:
                task["timer"].cancel()
        logger.info(f"Cancelled task '{task.get('name', task_id)}'")
        return True

    def start(self) -> None:
        """Inicia o servio Kairos (publica tick events)."""
        if self._running:
            logger.warning("KairosService j est rodando.")
            return
        self._running = True
        self._tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self._tick_thread.start()
        self._publish_event(self.EVENT_STARTED)
        logger.info("KairosService iniciado.")

    def stop(self) -> None:
        """Para o servio Kairos e cancela todas as tarefas."""
        if not self._running:
            return
        self._running = False
        if self._tick_thread:
            self._tick_thread.join(timeout=5)
        with self._lock:
            for _task_id, task in list(self._tasks.items()):
                if task["timer"]:
                    task["timer"].cancel()
            self._tasks.clear()
        self._publish_event(self.EVENT_STOPPED)
        logger.info("KairosService parado.")

    def list_tasks(self) -> List[Dict]:
        """Retorna lista de tarefas agendadas.

        Returns:
            Lista de dicionrios com informaes de cada tarefa.
        """
        with self._lock:
            return [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "interval_s": t["interval_s"],
                    "next_run": t["next_run"],
                }
                for t in self._tasks.values()
            ]

    def get_next_tick(self, task_id: str) -> Optional[float]:
        """Retorna o timestamp (Unix) da prxima execuo de uma tarefa.

        Args:
            task_id: ID da tarefa.

        Returns:
            Timestamp da prxima execuo, ou None se tarefa no encontrada.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            return task["next_run"] if task else None


def get_kairos_service() -> KairosService:
    """Retorna a instncia singleton do KairosService."""
    return KairosService()
