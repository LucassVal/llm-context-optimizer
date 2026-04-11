#!/usr/bin/env python3
"""
Pulse Scheduler - Autonomous maintenance scheduler for NeoCortex.

This scheduler runs background tasks for pruning, consolidation, AKL assessment,
backups, and checkpoints to prevent context overflow and agent blindness.
"""

import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Callable, Dict, List
import logging
from ..config import get_config
from ..infra.metrics_store import create_metrics_store

logger = logging.getLogger(__name__)


class PulseScheduler:
    """
    Agendador de tarefas assíncronas para manutenção autônoma do NeoCortex.
    Executa pruning, consolidação, AKL e backups em intervalos configuráveis.
    """

    def __init__(
        self,
        consolidation_service,
        ledger_service,
        akl_service,
        export_service,
        checkpoint_service,
        metrics_store=None,
    ):
        self.consolidation = consolidation_service
        self.ledger = ledger_service
        self.akl = akl_service
        self.export = export_service
        self.checkpoint = checkpoint_service

        # Initialize metrics store
        if metrics_store is None:
            self.metrics = create_metrics_store()
        else:
            self.metrics = metrics_store

        self.tasks: List[Dict] = []
        self.running = False
        self.thread: threading.Thread | None = None

        self._schedule_tasks()

    def _schedule_tasks(self):
        """Define as tarefas periódicas."""
        config = get_config()
        self.tasks = [
            {
                "name": "pruning",
                "interval_minutes": config.pruning_interval_minutes,
                "func": self._run_pruning,
                "last_run": None,
            },
            {
                "name": "consolidation",
                "interval_minutes": config.consolidation_interval_minutes,
                "func": self._run_consolidation,
                "last_run": None,
            },
            {
                "name": "akl_assessment",
                "interval_hours": config.akl_assessment_interval_hours,
                "target_hour": config.akl_assessment_target_hour,
                "func": self._run_akl,
                "last_run": None,
            },
            {
                "name": "backup",
                "interval_hours": config.backup_interval_hours,
                "target_hour": config.backup_target_hour,
                "func": self._run_backup,
                "last_run": None,
            },
            {
                "name": "checkpoint",
                "interval_minutes": config.checkpoint_interval_minutes,
                "func": self._run_checkpoint,
                "last_run": None,
            },
        ]

    def _run_pruning(self):
        """Executa pruning de contexto (hot → cold)."""
        logger.info("[Pulse] Executando pruning de contexto...")
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}
        # TODO: Implement pruning logic in LedgerService
        # For now, log and call a placeholder method
        try:
            # Check if ledger has prune_context method
            if hasattr(self.ledger, "prune_context"):
                result = self.ledger.prune_context()
                details = result
            else:
                result = {"success": True, "message": "Pruning not implemented yet"}
                details = result
            logger.info(f"[Pulse] Pruning concluído: {result.get('message', 'OK')}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no pruning: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            try:
                self.metrics.record_pulse_health(
                    event_type="pruning",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Failed to record pruning metrics: {e}")

    def _run_consolidation(self):
        """Executa consolidação semântica."""
        logger.info("[Pulse] Executando consolidação semântica...")
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}
        try:
            import uuid

            session_id = f"session_pulse_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            result = self.consolidation.summarize_session(
                session_id=session_id,
                summary="Consolidação automática via PulseScheduler",
            )
            details = result
            logger.info(f"[Pulse] Consolidação concluída: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro na consolidação: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            try:
                self.metrics.record_pulse_health(
                    event_type="consolidation",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Failed to record consolidation metrics: {e}")

    def _run_akl(self):
        """Executa avaliação do Ciclo de Vida Adaptativo."""
        logger.info("[Pulse] Executando AKL assessment...")
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}
        try:
            result = self.akl.assess_importance()
            details = result
            logger.info(f"[Pulse] AKL concluído: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no AKL: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            try:
                self.metrics.record_pulse_health(
                    event_type="akl_assessment",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Failed to record AKL metrics: {e}")

    def _run_backup(self):
        """Executa backup completo."""
        logger.info("[Pulse] Executando backup completo...")
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}
        try:
            result = self.export.backup()
            details = result
            logger.info(f"[Pulse] Backup concluído: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no backup: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            try:
                self.metrics.record_pulse_health(
                    event_type="backup",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Failed to record backup metrics: {e}")

    def _run_checkpoint(self):
        """Executa checkpoint automático."""
        logger.info("[Pulse] Executando checkpoint automático...")
        start_time = datetime.now(timezone.utc)
        status = "success"
        details = {}
        try:
            result = self.checkpoint.force_checkpoint()
            details = result
            logger.info(f"[Pulse] Checkpoint concluído: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no checkpoint: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            )
            try:
                self.metrics.record_pulse_health(
                    event_type="checkpoint",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Failed to record checkpoint metrics: {e}")

    def _worker(self):
        """Thread worker que verifica e executa tarefas agendadas."""
        while self.running:
            now = datetime.now(timezone.utc)
            for task in self.tasks:
                if self._should_run(task, now):
                    try:
                        task["func"]()
                        task["last_run"] = now.isoformat()
                    except Exception as e:
                        logger.error(f"[Pulse] Erro na tarefa {task['name']}: {e}")
            time.sleep(60)  # Verifica a cada minuto

    def _should_run(self, task: Dict, now: datetime) -> bool:
        """Determina se uma tarefa deve ser executada agora."""
        last_run = task.get("last_run")
        if last_run:
            last_run_dt = datetime.fromisoformat(last_run)
        else:
            last_run_dt = None

        # Tarefas com horário alvo específico (ex: 00:00 UTC)
        if "target_hour" in task:
            target_hour = task["target_hour"]
            if now.hour != target_hour:
                return False
            # Já foi executada hoje?
            if last_run_dt and last_run_dt.date() == now.date():
                return False
            return True

        # Tarefas baseadas em intervalo
        if "interval_hours" in task:
            interval = timedelta(hours=task["interval_hours"])
        elif "interval_minutes" in task:
            interval = timedelta(minutes=task["interval_minutes"])
        else:
            return False

        if last_run_dt is None:
            return True
        return (now - last_run_dt) >= interval

    def start(self):
        """Inicia o agendador em uma thread separada."""
        if self.running:
            logger.warning("[Pulse] Agendador já está rodando.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()
        logger.info("[Pulse] PulseScheduler iniciado com sucesso.")

    def stop(self):
        """Para o agendador."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("[Pulse] PulseScheduler parado.")

    def get_status(self) -> Dict:
        """Retorna o status atual do pulso."""
        return {
            "running": self.running,
            "tasks": [
                {
                    "name": t["name"],
                    "last_run": t.get("last_run"),
                    "next_run_estimate": "a ser calculado",
                }
                for t in self.tasks
            ],
        }

    def force_task(self, task_name: str) -> Dict:
        """Força a execução imediata de uma tarefa."""
        for task in self.tasks:
            if task["name"] == task_name:
                try:
                    task["func"]()
                    task["last_run"] = datetime.now(timezone.utc).isoformat()
                    return {
                        "success": True,
                        "message": f"Tarefa {task_name} executada com sucesso.",
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": f"Tarefa {task_name} não encontrada."}
