"""---
_genealogy:
  injected_at: '2026-04-16T00:23:59.232901'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-WKR-FR-001-persistent-worker
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
"""
NC-WKR-FR-001-persistent-worker.py
FR-WKR-001  PersistentWorker: Worker assncrono persistente para processar
tickets NC-DS-XXX do diretrio DIR-DS-001-tickets/.

Loop contnuo: scan  claim  execute  handoff.
Backoff exponencial em falha: 10s  20s  40s (max).
Claim atmico: filelock no arquivo do ticket.
"""

import logging
import threading
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml
from filelock import FileLock

logger = logging.getLogger(__name__)


class WorkerState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


@dataclass
class WorkerConfig:
    tickets_dir: Path
    worker_id: str  # ex: "worker-59520-abc123"
    poll_interval: float = 10.0  # segundos entre scans
    backoff_base: float = 10.0  # backoff inicial (s)
    backoff_max: float = 40.0  # backoff mximo (s)
    max_retries: int = 3
    heartbeat_interval: float = 60.0  # segundos entre heartbeats


class PersistentWorker:
    """Worker persistente para processar tickets de forma assncrona.

    Interface pblica:
      start() -> None           # inicia loop em thread separada
      stop() -> None            # para graciosamente
      pause() -> None           # pausa o loop (tickets no so processados)
      resume() -> None          # retoma aps pause
      get_state() -> WorkerState
      register_handler(ticket_type, fn) -> None  # registra handler para tipo de ticket
    """

    def __init__(self, config: WorkerConfig):
        self.config = config
        self.state = WorkerState.IDLE
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # inicialmente no pausado
        self._state_lock = threading.Lock()
        self._handlers: Dict[str, Callable] = {}
        self._consecutive_errors = 0
        self._last_heartbeat = time.time()
        self._current_ticket: Optional[Dict[str, Any]] = None

    def start(self) -> None:
        """Inicia worker em thread dedicada (no-bloqueante)."""
        with self._state_lock:
            if self.state != WorkerState.IDLE:
                raise RuntimeError(
                    f"Worker no pode ser iniciado no estado {self.state}"
                )
            self.state = WorkerState.RUNNING
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            logger.info(f"Worker {self.config.worker_id} iniciado")

    def stop(self) -> None:
        """Para o worker graciosamente. Aguarda ticket atual terminar."""
        with self._state_lock:
            if self.state == WorkerState.STOPPED:
                return
            logger.info(f"Parando worker {self.config.worker_id}...")
            self.state = WorkerState.STOPPED
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=30)
            logger.info(f"Worker {self.config.worker_id} parado")

    def pause(self) -> None:
        """Pausa processamento. Worker continua rodando mas no pega tickets."""
        with self._state_lock:
            if self.state != WorkerState.RUNNING:
                raise RuntimeError(
                    f"Worker no pode ser pausado no estado {self.state}"
                )
            self.state = WorkerState.PAUSED
            self._pause_event.clear()
            logger.info(f"Worker {self.config.worker_id} pausado")

    def resume(self) -> None:
        """Retoma aps pause."""
        with self._state_lock:
            if self.state != WorkerState.PAUSED:
                raise RuntimeError(
                    f"Worker no pode ser retomado no estado {self.state}"
                )
            self.state = WorkerState.RUNNING
            self._pause_event.set()
            logger.info(f"Worker {self.config.worker_id} retomado")

    def get_state(self) -> WorkerState:
        with self._state_lock:
            return self.state

    def register_handler(self, ticket_type: str, handler: Callable) -> None:
        """Registra funo handler para um tipo de ticket."""
        self._handlers[ticket_type] = handler

    def _run_loop(self) -> None:
        """Loop principal do worker."""
        logger.info(f"Loop principal iniciado para worker {self.config.worker_id}")
        while not self._stop_event.is_set():
            # Verificar pause
            self._pause_event.wait()
            if self._stop_event.is_set():
                break

            # Heartbeat
            self._heartbeat()

            # Escanear e claim
            ticket = self._scan_and_claim()
            if ticket is None:
                time.sleep(self.config.poll_interval)
                continue

            # Executar ticket
            try:
                self._execute_ticket(ticket)
                self._consecutive_errors = 0
            except Exception as e:
                logger.error(f"Erro ao executar ticket {ticket.get('ticket_id')}: {e}")
                self._consecutive_errors += 1
                if self._consecutive_errors >= self.config.max_retries:
                    logger.error(
                        f"Mximo de retries ({self.config.max_retries}) atingido. Parando worker."
                    )
                    self.stop()
                    break
                self._backoff(self._consecutive_errors)
                # Liberar claim do ticket? (simplificao: deixar claim expirado)
                continue

            # Intervalo entre tickets
            time.sleep(self.config.poll_interval)

        logger.info(f"Loop principal finalizado para worker {self.config.worker_id}")

    def _heartbeat(self) -> None:
        """Loga heartbeat a cada intervalo configurado."""
        now = time.time()
        if now - self._last_heartbeat >= self.config.heartbeat_interval:
            logger.info(
                f"HEARTBEAT worker={self.config.worker_id} "
                f"state={self.state.value} "
                f"consecutive_errors={self._consecutive_errors}"
            )
            self._last_heartbeat = now

    def _scan_and_claim(self) -> Optional[Dict[str, Any]]:
        """Escaneia DIR-DS-001-tickets/ e faz claim atmico do primeiro AVAILABLE."""
        tickets_dir = self.config.tickets_dir
        if not tickets_dir.exists():
            logger.warning(f"Diretrio de tickets no existe: {tickets_dir}")
            return None

        for yaml_file in tickets_dir.glob("*.yaml"):
            lock_file = yaml_file.with_suffix(".yaml.lock")
            lock = FileLock(lock_file)
            try:
                # Tentar adquirir lock (timeout curto para evitar bloqueio prolongado)
                lock.acquire(timeout=1)
            except TimeoutError:
                continue  # outro worker est com o lock, pular

            try:
                # Ler contedo do YAML
                with open(yaml_file, "r", encoding="utf-8") as f:
                    ticket = yaml.safe_load(f)
                if not isinstance(ticket, dict):
                    logger.warning(f"Ticket {yaml_file} no  um dicionrio vlido")
                    continue

                # Verificar se est disponvel
                if ticket.get("status") != "AVAILABLE":
                    continue

                # Fazer claim
                ticket["status"] = "CLAIMED"
                ticket["claimed_by"] = self.config.worker_id
                ticket["claimed_at"] = time.time()

                # Escrever de volta
                with open(yaml_file, "w", encoding="utf-8") as f:
                    yaml.dump(ticket, f, default_flow_style=False)

                logger.info(
                    f"Ticket {ticket.get('ticket_id')} claimado por {self.config.worker_id}"
                )
                self._current_ticket = ticket
                return ticket
            except Exception as e:
                logger.error(f"Erro ao processar ticket {yaml_file}: {e}")
            finally:
                lock.release()

        return None

    def _execute_ticket(self, ticket: Dict[str, Any]) -> None:
        """Executa ticket e gera handoff em DIR-DS-002-audit-logs/."""
        ticket_id = ticket.get("ticket_id")
        logger.info(f"Executando ticket {ticket_id}")

        # Verificar se h handler registrado para o tipo de ticket
        # (simplificao: ticket_type pode ser inferido do ticket_id)
        ticket_type = ticket.get("type")
        if ticket_type is None:
            # Tentar inferir do ticket_id
            ticket_type = ticket_id.split("-")[2] if ticket_id else "unknown"

        handler = self._handlers.get(ticket_type)
        if handler is None:
            logger.warning(
                f"Nenhum handler registrado para tipo {ticket_type}, usando handler padro"
            )
            handler = self._default_handler

        # Executar handler
        try:
            result = handler(ticket)
        except Exception as e:
            logger.error(f"Handler falhou para ticket {ticket_id}: {e}")
            raise

        # Gerar handoff
        self._generate_handoff(ticket, result)

        # Marcar ticket como concludo
        self._mark_ticket_done(ticket)

    def _default_handler(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """Handler padro que apenas loga e retorna ticket."""
        logger.info(f"Handler padro executado para ticket {ticket.get('ticket_id')}")
        return {"processed": True, "ticket": ticket.get("ticket_id")}

    def _generate_handoff(self, ticket: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Gera arquivo de handoff no diretrio de audit-logs."""
        handoff_dir = Path("DIR-DS-002-audit-logs")
        handoff_dir.mkdir(exist_ok=True)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        ticket_id = ticket.get("ticket_id", "unknown")
        handoff_file = handoff_dir / f"{ticket_id}-handoff-{timestamp}.yaml"

        handoff_data = {
            "ticket_id": ticket_id,
            "status": "PENDING_REVIEW",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "agent_port": 59520,  # porta do agente atual
            "worker_id": self.config.worker_id,
            "result": result,
            "summary": f"Ticket {ticket_id} processado por PersistentWorker",
            "consecutive_errors": self._consecutive_errors,
        }

        with open(handoff_file, "w", encoding="utf-8") as f:
            yaml.dump(handoff_data, f, default_flow_style=False)

        logger.info(f"Handoff gerado: {handoff_file}")

    def _mark_ticket_done(self, ticket: Dict[str, Any]) -> None:
        """Atualiza status do ticket para DONE."""
        ticket_id = ticket.get("ticket_id")
        tickets_dir = self.config.tickets_dir
        yaml_file = tickets_dir / f"{ticket_id}.yaml"
        if not yaml_file.exists():
            # Pode ser que o arquivo tenha nome diferente (usar busca)
            yaml_file = next(tickets_dir.glob(f"*{ticket_id}*.yaml"), None)
            if yaml_file is None:
                logger.warning(f"Arquivo do ticket {ticket_id} no encontrado")
                return

        lock_file = yaml_file.with_suffix(".yaml.lock")
        lock = FileLock(lock_file)
        try:
            lock.acquire(timeout=5)
            with open(yaml_file, "r", encoding="utf-8") as f:
                ticket_data = yaml.safe_load(f)
            ticket_data["status"] = "DONE"
            ticket_data["completed_at"] = time.time()
            with open(yaml_file, "w", encoding="utf-8") as f:
                yaml.dump(ticket_data, f, default_flow_style=False)
            logger.info(f"Ticket {ticket_id} marcado como DONE")
        except Exception as e:
            logger.error(f"Erro ao marcar ticket {ticket_id} como DONE: {e}")
        finally:
            lock.release()

    def _backoff(self, attempt: int) -> None:
        """Espera com backoff exponencial: 10s  20s  40s."""
        delay = min(self.config.backoff_base * (2**attempt), self.config.backoff_max)
        logger.info(f"Backoff {delay}s (tentativa {attempt})")
        time.sleep(delay)


def create_worker(port: int, tickets_dir: Optional[Path] = None) -> PersistentWorker:
    """Factory: cria worker configurado para a porta dada."""
    if tickets_dir is None:
        tickets_dir = Path("DIR-DS-001-tickets")
    worker_id = f"worker-{port}-{uuid.uuid4().hex[:6]}"
    config = WorkerConfig(
        tickets_dir=tickets_dir,
        worker_id=worker_id,
        poll_interval=10.0,
        backoff_base=10.0,
        backoff_max=40.0,
        max_retries=3,
        heartbeat_interval=60.0,
    )
    return PersistentWorker(config)
