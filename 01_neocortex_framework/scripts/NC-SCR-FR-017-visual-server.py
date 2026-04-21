#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.683382'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-017-visual-server
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-017-visual-server.py
Servidor visual unificado que orquestra Mission Control + Pixel Bridge + NeoCortex.

Interface:
  VisualServer.start_mission_control() -> subprocess.Popen
  VisualServer.start_pixel_bridge()    -> threading.Thread
  VisualServer.start_neocortex()       -> subprocess.Popen
  VisualServer.run_all()               -> None
  VisualServer.stop_all()              -> None
  VisualServer.health_check()          -> dict

Uso:
  python NC-SCR-FR-017-visual-server.py --start
  python NC-SCR-FR-017-visual-server.py --stop
  python NC-SCR-FR-017-visual-server.py --health

Regras:
  - Usar logger, nunca print()
  - Usar get_config() para paths, nunca hardcodar
  - Mnimo 150 linhas
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional

# Configurao do logger
logger = logging.getLogger(__name__)

# Importar configurao central
try:
    from neocortex.config import get_config
except ImportError as e:
    logger.error("Falha ao importar get_config: %s", e)
    sys.exit(1)


class VisualServer:
    """Orquestrador dos trs servios principais do NeoCortex."""

    # Portas padro
    MISSION_CONTROL_PORT = 3000
    PICOCLAW_PORT = 18790
    NEOCORTEX_SSE_PORT = 8765

    def __init__(self, config: Optional[Dict] = None) -> None:
        """Inicializa o servidor visual com configurao.

        Args:
            config: Dicionrio de configurao (opcional). Se no fornecido,
                usa get_config().
        """
        self._config = config or get_config()
        self._processes: Dict[str, subprocess.Popen] = {}
        self._threads: Dict[str, threading.Thread] = {}
        self._stop_event = threading.Event()

        # Carregar paths da configurao
        self._load_paths()

        logger.info("VisualServer inicializado")

    def _load_paths(self) -> None:
        """Carrega os caminhos dos servios a partir da configurao."""
        paths = self._config.get("PATHS", {})
        files = self._config.get("FILES", {})

        # Path para Mission Control (Next.js)
        self.mission_control_path = Path(
            paths.get(
                "mission_control",
                self._config.get("project_root", Path.cwd()) / "mission-control",
            )
        )

        # Path para Pixel Bridge (script de ponte JSONL)
        self.pixel_bridge_path = Path(
            paths.get(
                "pixel_bridge",
                self._config.get("project_root", Path.cwd()) / "pixel-bridge",
            )
        )

        # Path para NeoCortex MCP Server
        self.neocortex_path = Path(
            paths.get(
                "mcp_server",
                self._config.get("project_root", Path.cwd()) / "01_neocortex_framework",
            )
        )

        # Verificar existncia
        self._validate_paths()

    def _validate_paths(self) -> None:
        """Valida se os caminhos necessrios existem."""
        if not self.mission_control_path.exists():
            logger.warning(
                "Mission Control path no encontrado: %s", self.mission_control_path
            )
        if not self.pixel_bridge_path.exists():
            logger.warning(
                "Pixel Bridge path no encontrado: %s", self.pixel_bridge_path
            )
        if not self.neocortex_path.exists():
            logger.warning("NeoCortex path no encontrado: %s", self.neocortex_path)

    def start_mission_control(self) -> subprocess.Popen:
        """Inicia o Mission Control (Next.js) na porta 3000.

        Returns:
            Processo subprocess.Popen do servidor Mission Control.
        """
        if not self.mission_control_path.exists():
            raise FileNotFoundError(
                f"Mission Control path no existe: {self.mission_control_path}"
            )

        # Determinar comando de start (npm, pnpm, yarn)
        package_json = self.mission_control_path / "package.json"
        if not package_json.exists():
            logger.warning(
                "package.json no encontrado, usando npm start como fallback"
            )
            cmd = ["npm", "start"]
        else:
            # Ler scripts disponveis

            with open(package_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                scripts = data.get("scripts", {})
                if "dev" in scripts:
                    cmd = ["npm", "run", "dev"]
                elif "start" in scripts:
                    cmd = ["npm", "start"]
                else:
                    cmd = ["npm", "start"]

        logger.info(
            "Iniciando Mission Control em %s com comando: %s",
            self.mission_control_path,
            cmd,
        )
        env = {**os.environ, "PORT": str(self.MISSION_CONTROL_PORT)}
        process = subprocess.Popen(
            cmd,
            cwd=self.mission_control_path,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._processes["mission_control"] = process

        # Thread para ler stdout/stderr
        threading.Thread(
            target=self._log_stream,
            args=(process.stdout, "mission_control", "stdout"),
            daemon=True,
        ).start()
        threading.Thread(
            target=self._log_stream,
            args=(process.stderr, "mission_control", "stderr"),
            daemon=True,
        ).start()

        logger.info("Mission Control iniciado (PID: %d)", process.pid)
        return process

    def start_pixel_bridge(self) -> threading.Thread:
        """Inicia a ponte Pixel Agents (JSONL polling) como thread.

        Returns:
            Thread executando a ponte Pixel.
        """
        logger.info("Iniciando Pixel Bridge (thread)")

        def pixel_bridge_worker():
            """Worker da ponte Pixel: polling de arquivo JSONL."""

            jsonl_path = self.pixel_bridge_path / "events.jsonl"
            logger.info("Pixel Bridge observando %s", jsonl_path)

            while not self._stop_event.is_set():
                try:
                    if jsonl_path.exists():
                        with open(jsonl_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()
                            # Processar novas linhas (simulao)
                            for line in lines[-10:]:  # ltimas 10 linhas
                                try:
                                    event = json.loads(line.strip())
                                    logger.debug(
                                        "Pixel Bridge event: %s",
                                        event.get("type", "unknown"),
                                    )
                                except json.JSONDecodeError:
                                    pass
                    time.sleep(1.0)  # polling a cada segundo
                except Exception as e:
                    logger.error("Erro no Pixel Bridge: %s", e)
                    time.sleep(5.0)

            logger.info("Pixel Bridge finalizado")

        thread = threading.Thread(target=pixel_bridge_worker, name="pixel_bridge")
        thread.daemon = True
        thread.start()
        self._threads["pixel_bridge"] = thread

        logger.info("Pixel Bridge iniciado (thread)")
        return thread

    def start_neocortex(self) -> subprocess.Popen:
        """Inicia o servidor NeoCortex MCP (SSE/WebSocket) na porta 8765.

        Returns:
            Processo subprocess.Popen do servidor NeoCortex.
        """
        server_module = "neocortex.mcp.server"
        cmd = [
            sys.executable,
            "-m",
            server_module,
            "--transport",
            "sse",
            "--host",
            "127.0.0.1",
            "--port",
            str(self.NEOCORTEX_SSE_PORT),
        ]

        logger.info("Iniciando NeoCortex MCP Server: %s", cmd)
        process = subprocess.Popen(
            cmd,
            cwd=self.neocortex_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self._processes["neocortex"] = process

        # Threads para logs
        threading.Thread(
            target=self._log_stream,
            args=(process.stdout, "neocortex", "stdout"),
            daemon=True,
        ).start()
        threading.Thread(
            target=self._log_stream,
            args=(process.stderr, "neocortex", "stderr"),
            daemon=True,
        ).start()

        logger.info("NeoCortex MCP Server iniciado (PID: %d)", process.pid)
        return process

    def _log_stream(self, stream, service: str, stream_name: str):
        """L stream de subprocesso e loga com nvel apropriado."""
        try:
            for line in iter(stream.readline, ""):
                line = line.rstrip()
                if line:
                    logger.info("[%s %s] %s", service, stream_name, line)
        except Exception as e:
            logger.debug("Stream %s de %s fechado: %s", stream_name, service, e)

    def run_all(self) -> None:
        """Sobe todos os trs servios (Mission Control, Pixel Bridge, NeoCortex)."""
        logger.info("Iniciando todos os servios...")

        try:
            self.start_mission_control()
        except Exception as e:
            logger.error("Falha ao iniciar Mission Control: %s", e)

        try:
            self.start_pixel_bridge()
        except Exception as e:
            logger.error("Falha ao iniciar Pixel Bridge: %s", e)

        try:
            self.start_neocortex()
        except Exception as e:
            logger.error("Falha ao iniciar NeoCortex: %s", e)

        logger.info("Todos os servios iniciados. Pressione Ctrl+C para parar.")

        # Aguarda sinal de trmino
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupo recebida, parando servios...")
            self.stop_all()

    def _signal_handler(self, signum, frame):
        """Manipulador de sinal para graceful shutdown."""
        logger.info("Sinal %d recebido, finalizando...", signum)
        self.stop_all()
        sys.exit(0)

    def stop_all(self) -> None:
        """Para todos os servios gracefulmente."""
        logger.info("Parando todos os servios...")

        # Sinalizar threads para parar
        self._stop_event.set()

        # Terminar processos
        for name, process in self._processes.items():
            if process and process.poll() is None:
                logger.info("Terminando processo %s (PID: %d)", name, process.pid)
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info("Processo %s terminado", name)
                except subprocess.TimeoutExpired:
                    logger.warning("Processo %s no terminou em 5s, killando", name)
                    process.kill()

        # Aguardar threads
        for name, thread in self._threads.items():
            if thread.is_alive():
                logger.info("Aguardando thread %s...", name)
                thread.join(timeout=3)
                if thread.is_alive():
                    logger.warning("Thread %s ainda viva aps timeout", name)

        self._processes.clear()
        self._threads.clear()
        self._stop_event.clear()

        logger.info("Todos os servios parados.")

    def health_check(self) -> Dict[str, bool]:
        """Verifica a sade de cada servio.

        Returns:
            Dicionrio com status de cada servio.
        """
        # Tentar importar requests (opcional)
        requests = None
        try:
            import requests

            has_requests = True
        except ImportError:
            has_requests = False
            logger.debug("requests no instalado, health check HTTP desabilitado")

        health = {
            "mission_control": False,
            "pixel_bridge": False,
            "neocortex": False,
        }

        # Mission Control (HTTP)
        if has_requests and requests is not None:
            try:
                resp = requests.get(
                    f"http://127.0.0.1:{self.MISSION_CONTROL_PORT}/health",
                    timeout=2,
                )
                health["mission_control"] = resp.status_code == 200
            except Exception:
                pass

        # Pixel Bridge (verifica se thread est viva)
        thread = self._threads.get("pixel_bridge")
        health["pixel_bridge"] = thread is not None and thread.is_alive()

        # NeoCortex (SSE health endpoint)
        if has_requests and requests is not None:
            try:
                resp = requests.get(
                    f"http://127.0.0.1:{self.NEOCORTEX_SSE_PORT}/health",
                    timeout=2,
                )
                health["neocortex"] = resp.status_code == 200
            except Exception:
                pass

        logger.debug("Health check: %s", health)
        return health


def main():
    """Funo principal da CLI."""
    parser = argparse.ArgumentParser(description="Servidor visual unificado NeoCortex")
    parser.add_argument(
        "--start",
        action="store_true",
        help="Inicia todos os servios (Mission Control, Pixel Bridge, NeoCortex)",
    )
    parser.add_argument(
        "--stop",
        action="store_true",
        help="Para todos os servios gracefulmente",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="Verifica a sade dos servios e exibe status",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Habilita logging detalhado"
    )

    args = parser.parse_args()

    # Configurar logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    server = VisualServer()

    if args.start:
        server.run_all()
    elif args.stop:
        server.stop_all()
    elif args.health:
        health = server.health_check()
        print("Status dos servios:")
        for service, status in health.items():
            print(f"  {service}: {'OK' if status else 'FAIL'}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
