#!/usr/bin/env python3
"""
NC-SCR-FR-103-mc-startup-hook.py

Startup hook para registrar NeoCortex no Mission Control e manter heartbeat.
Executado como processo separado após o servidor MCP iniciar.

Uso:
    python NC-SCR-FR-103-mc-startup-hook.py

Flags:
    --config <path>   Caminho para configuração JSON (opcional)
    --agent-id <id>   ID do agente (padrão: gerado automaticamente)
    --no-wal          Não registrar startup no WAL
    --dry-run         Simular apenas, sem chamadas reais
"""

import argparse
import importlib.util
import logging
import signal
import sys
import threading
import uuid
from pathlib import Path
from typing import Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Importação dinâmica do adapter Mission Control (R09)
# -----------------------------------------------------------------------------


def load_adapter_module():
    """Carrega NC-ADP-FR-001-mission-control.py via importlib.util."""
    adapter_path = (
        Path(__file__).parent.parent
        / "neocortex"
        / "core"
        / "adapters"
        / "NC-ADP-FR-001-mission-control.py"
    )
    if not adapter_path.exists():
        logger.error("Adapter não encontrado em %s", adapter_path)
        return None
    try:
        spec = importlib.util.spec_from_file_location(
            "mission_control_adapter", adapter_path
        )
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para adapter")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info("Adapter carregado com sucesso")
        return module
    except Exception as e:
        logger.error("Erro ao carregar adapter: %s", e, exc_info=True)
        return None


def load_wal_service_module():
    """Carrega NC-SVC-FR-016-wal-service.py via importlib.util."""
    service_path = (
        Path(__file__).parent.parent
        / "neocortex"
        / "core"
        / "services"
        / "NC-SVC-FR-016-wal-service.py"
    )
    if not service_path.exists():
        logger.error("WAL service não encontrado em %s", service_path)
        return None
    try:
        spec = importlib.util.spec_from_file_location("wal_service", service_path)
        if spec is None or spec.loader is None:
            logger.error("Falha ao criar spec para WAL service")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        logger.info("WAL service carregado com sucesso")
        return module
    except Exception as e:
        logger.error("Erro ao carregar WAL service: %s", e, exc_info=True)
        return None


# -----------------------------------------------------------------------------
# Classe principal do hook
# -----------------------------------------------------------------------------


class MissionControlStartupHook:
    """Gerencia registro e heartbeat com Mission Control."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        agent_id: Optional[str] = None,
        dry_run: bool = False,
    ):
        self.dry_run = dry_run
        self.agent_id = agent_id or f"neocortex-{uuid.uuid4().hex[:8]}"
        self.adapter_module = load_adapter_module()
        self.wal_module = load_wal_service_module()
        self.adapter = None
        self.heartbeat_thread = None
        self.shutdown_event = threading.Event()
        self.registered = False

        if self.adapter_module is None:
            raise RuntimeError("Não foi possível carregar o adapter Mission Control")

    def _create_adapter(self):
        """Instancia o MissionControlAdapter com configuração padrão."""
        try:
            config_class = self.adapter_module.MissionControlConfig
            adapter_class = self.adapter_module.MissionControlAdapter
        except AttributeError as e:
            logger.error("Adapter não possui classes esperadas: %s", e)
            return None

        config = config_class(
            base_url="http://localhost:3000",
            api_endpoint="/api/adapters",
            agent_id=self.agent_id,
            name="neocortex-agent",
            role="coder",
            capabilities=["mcp-tools", "code-generation", "debugging"],
            metadata={"neocortex_version": "v42", "port": 45132},
            heartbeat_interval_sec=30,
            timeout_sec=10,
        )
        adapter = adapter_class(config)
        logger.info("Adapter criado para agent_id=%s", self.agent_id)
        return adapter

    def register(self) -> bool:
        """Registra o NeoCortex no Mission Control."""
        if self.dry_run:
            logger.info("[DRY-RUN] Registraria NeoCortex no Mission Control")
            self.registered = True
            return True

        if self.adapter is None:
            self.adapter = self._create_adapter()
            if self.adapter is None:
                return False

        try:
            # O adapter atual usa register_with_mission_control
            success = self.adapter.register_with_mission_control()
            if success:
                logger.info("NeoCortex registrado no Mission Control")
                self.registered = True
                return True
            else:
                logger.error("Falha ao registrar NeoCortex no Mission Control")
                return False
        except Exception as e:
            logger.error("Erro durante registro: %s", e, exc_info=True)
            return False

    def heartbeat_loop(self):
        """Loop de heartbeat a cada 30 segundos."""
        logger.info("Heartbeat loop iniciado (intervalo: 30s)")
        while not self.shutdown_event.is_set():
            try:
                if self.registered and self.adapter:
                    if self.dry_run:
                        logger.debug("[DRY-RUN] Enviaria heartbeat")
                    else:
                        success = self.adapter.send_heartbeat()
                        if not success:
                            logger.warning("Heartbeat falhou (MC offline?)")
                else:
                    logger.debug(
                        "Heartbeat skip: não registrado ou adapter não disponível"
                    )
            except Exception as e:
                logger.error("Erro no heartbeat: %s", e, exc_info=False)
            # Aguarda 30 segundos ou shutdown
            self.shutdown_event.wait(timeout=30)
        logger.info("Heartbeat loop finalizado")

    def log_startup_to_wal(self):
        """Registra o startup no WAL (Write-Ahead Log)."""
        if self.dry_run:
            logger.info("[DRY-RUN] Registraria startup no WAL")
            return
        if self.wal_module is None:
            logger.warning("WAL service não carregado, skip")
            return
        try:
            wal_service = self.wal_module.WALService()
            session_id = f"mc-startup-{uuid.uuid4().hex[:8]}"
            wal_service.open_session(
                session_id=session_id,
                agent="NC-SCR-FR-103",
                ticket_id="NC-DS-103",
            )
            wal_service.log_operation(
                session_id=session_id,
                operation="STARTUP",
                file_path="neocortex_mc_startup",
                ticket_id="NC-DS-103",
                before_hash=None,
                after_hash=None,
            )
            wal_service.commit_session(session_id)
            logger.info("Startup registrado no WAL (session_id=%s)", session_id)
        except Exception as e:
            logger.error("Erro ao registrar startup no WAL: %s", e, exc_info=True)

    def start(self):
        """Executa o fluxo completo de startup."""
        logger.info(
            "Iniciando Mission Control startup hook (agent_id=%s)", self.agent_id
        )

        # 1. Registrar no WAL
        self.log_startup_to_wal()

        # 2. Registrar no Mission Control
        if not self.register():
            logger.error("Falha no registro, continuando sem heartbeat")
            return

        # 3. Iniciar thread de heartbeat
        self.heartbeat_thread = threading.Thread(
            target=self.heartbeat_loop,
            daemon=True,
            name="MC-Heartbeat",
        )
        self.heartbeat_thread.start()
        logger.info("Heartbeat thread iniciada")

        # 4. Aguardar sinal de shutdown
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("Startup hook ativo. Aguardando sinal de shutdown...")
        try:
            # Mantém a thread principal viva
            while self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=1)
        except KeyboardInterrupt:
            self._handle_shutdown(None, None)
        finally:
            self.shutdown()

    def _handle_shutdown(self, signum, frame):
        """Manipulador de sinal para graceful shutdown."""
        logger.info("Sinal de shutdown recebido (sig=%s)", signum)
        self.shutdown_event.set()

    def shutdown(self):
        """Finaliza recursos."""
        logger.info("Finalizando Mission Control startup hook...")
        self.shutdown_event.set()
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        logger.info("Hook finalizado")


# -----------------------------------------------------------------------------
# Ponto de entrada
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Mission Control startup hook")
    parser.add_argument("--config", help="Caminho para configuração JSON")
    parser.add_argument("--agent-id", help="ID do agente")
    parser.add_argument(
        "--no-wal", action="store_true", help="Não registrar startup no WAL"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Simular sem chamadas reais"
    )
    args = parser.parse_args()

    try:
        hook = MissionControlStartupHook(
            config_path=args.config,
            agent_id=args.agent_id,
            dry_run=args.dry_run,
        )
        if args.no_wal:
            hook.log_startup_to_wal = lambda: None  # noop
        hook.start()
    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error("Erro fatal: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
