# @UBL @UBL @CORE-FR | LEXICO: #SYSTEM
#!/usr/bin/env python3
"""
Pulse Scheduler - Autonomous maintenance scheduler for NeoCortex.

This scheduler runs background tasks for pruning, consolidation, AKL assessment,
backups, and checkpoints to prevent context overflow and agent blindness.
"""

import logging
import threading
import time
from datetime import UTC, datetime, timedelta

from ..config import get_config
from ..infra.metrics_store import create_metrics_store

logger = logging.getLogger(__name__)


class PulseScheduler:
    """
    Agendador de tarefas assncronas para manuteno autnoma do NeoCortex.
    Executa pruning, consolidao, AKL e backups em intervalos configurveis.
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

        self.tasks: list[dict] = []
        self.running = False
        self.thread: threading.Thread | None = None

        self._schedule_tasks()

    def _schedule_tasks(self):
        """Define as tarefas peridicas."""
        config = get_config()
        self.tasks = [
            {
                "name": "thermal_decay_gc",
                "interval_minutes": config.pruning_interval_minutes,
                "func": self._run_thermal_decay_gc,
                "last_run": None,
            },
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

    def _run_thermal_decay_gc(self):
        """Executa GC de Lóbulos Memória com Decaimento Térmico TTL."""
        logger.info("[Pulse] Executando Thermal Context Decay GC...")
        start_time = datetime.now(UTC)
        status = "success"
        details = {}
        try:
            import re
            from pathlib import Path
            root = Path(__file__).parents[3] # TURBOQUANT_V42
            lobes_dir = root / "02_memory_lobes"
            archived_count, decayed_count = 0, 0

            if lobes_dir.exists():
                for mdc in lobes_dir.rglob("*.mdc"):
                    content = mdc.read_text(encoding="utf-8")
                    temp_match = re.search(r"^temperature:\s*(\d+)$", content, re.MULTILINE)
                    current_temp = int(temp_match.group(1)) if temp_match else 100

                    if current_temp > 0:
                        new_temp = max(0, current_temp - 5) # decai 5 pts
                        if temp_match:
                            content = re.sub(r"^temperature:\s*\d+$", f"temperature: {new_temp}", content, flags=re.MULTILINE)
                        else:
                            content = re.sub(r"^(---[\s\S]*?)(\n---)", f"\\1\ntemperature: {new_temp}\\2", content, count=1)
                        if new_temp == 0:
                            content = re.sub(r"^(---[\s\S]*?)(\n---)", "\\1\nstatus: archived\\2", content, count=1)
                            archived_count += 1

                        mdc.write_text(content, encoding="utf-8")
                        decayed_count += 1

            details = {"lobes_decayed": decayed_count, "lobes_archived": archived_count}
            logger.info(f"[Pulse] Thermal Decay GC concluido: {details}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no Thermal GC: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)
            try:
                self.metrics.record_pulse_health(
                    event_type="thermal_gc",
                    status=status,
                    duration_ms=duration_ms,
                    details=details,
                )
            except Exception as e:
                logger.warning(f"[Pulse] Falha metrics thermal_gc: {e}")

    def _run_pruning(self):
        """Executa pruning de contexto (hot  cold)."""
        logger.info("[Pulse] Executando pruning de contexto...")
        start_time = datetime.now(UTC)
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
            logger.info(f"[Pulse] Pruning concludo: {result.get('message', 'OK')}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no pruning: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
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
        """Executa consolidao semntica."""
        logger.info("[Pulse] Executando consolidao semntica...")
        start_time = datetime.now(UTC)
        status = "success"
        details = {}
        try:
            import uuid

            session_id = f"session_pulse_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
            result = self.consolidation.summarize_session(
                session_id=session_id,
                summary="Consolidao automtica via PulseScheduler",
            )
            details = result
            logger.info(f"[Pulse] Consolidao concluda: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro na consolidao: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
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
        """Executa avaliao do Ciclo de Vida Adaptativo."""
        logger.info("[Pulse] Executando AKL assessment...")
        start_time = datetime.now(UTC)
        status = "success"
        details = {}
        try:
            result = self.akl.assess_importance()
            details = result
            logger.info(f"[Pulse] AKL concludo: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no AKL: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
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
        start_time = datetime.now(UTC)
        status = "success"
        details = {}
        try:
            result = self.export.backup()
            details = result
            logger.info(f"[Pulse] Backup concludo: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no backup: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
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
        """Executa checkpoint automtico."""
        logger.info("[Pulse] Executando checkpoint automtico...")
        start_time = datetime.now(UTC)
        status = "success"
        details = {}
        try:
            result = self.checkpoint.force_checkpoint()
            details = result
            logger.info(f"[Pulse] Checkpoint concludo: {result}")
        except Exception as e:
            logger.error(f"[Pulse] Erro no checkpoint: {e}")
            status = "failure"
            details = {"error": str(e)}
        finally:
            duration_ms = int(
                (datetime.now(UTC) - start_time).total_seconds() * 1000
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
            now = datetime.now(UTC)
            for task in self.tasks:
                if self._should_run(task, now):
                    try:
                        task["func"]()
                        task["last_run"] = now.isoformat()
                    except Exception as e:
                        logger.error(f"[Pulse] Erro na tarefa {task['name']}: {e}")
            time.sleep(60)  # Verifica a cada minuto

    def _should_run(self, task: dict, now: datetime) -> bool:
        """Determina se uma tarefa deve ser executada agora."""
        last_run = task.get("last_run")
        last_run_dt = datetime.fromisoformat(last_run) if last_run else None

        # Tarefas com horrio alvo especfico (ex: 00:00 UTC)
        if "target_hour" in task:
            target_hour = task["target_hour"]
            if now.hour != target_hour:
                return False
            # J foi executada hoje?
            return not (last_run_dt and last_run_dt.date() == now.date())

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
            logger.warning("[Pulse] Agendador j est rodando.")
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

    def get_status(self) -> dict:
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

    def force_task(self, task_name: str) -> dict:
        """Fora a execuo imediata de uma tarefa."""
        for task in self.tasks:
            if task["name"] == task_name:
                try:
                    task["func"]()
                    task["last_run"] = datetime.now(UTC).isoformat()
                    return {
                        "success": True,
                        "message": f"Tarefa {task_name} executada com sucesso.",
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
        return {"success": False, "error": f"Tarefa {task_name} no encontrada."}
