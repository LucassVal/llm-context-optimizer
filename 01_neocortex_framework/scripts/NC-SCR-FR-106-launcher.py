#!/usr/bin/env python3
"""---
NC-SCR-FR-106-launcher.py
---
"""

"""---
NC-SCR-FR-106-launcher.py
---
"""

"""
NC-SCR-FR-106-launcher.py

Launcher para orquestrar startup do stack completo (MCP + Mission Control + NeoCortex registration).
Verifica se o Mission Control está online; se não, inicia-o. Em seguida, executa o hook de startup.

Uso:
    python NC-SCR-FR-106-launcher.py [--dry-run] [--no-mc] [--no-hook]

Flags:
    --dry-run      Apenas simular, não executar comandos reais
    --no-mc        Não tentar iniciar Mission Control (assume já online)
    --no-hook      Não executar NC-SCR-FR-103-mc-startup-hook.py
    --mc-path      Caminho para diretório do Mission Control (opcional)
    --help         Exibir esta ajuda
"""

import argparse
import logging
import subprocess
import sys
import threading
import time
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
# Constantes
# -----------------------------------------------------------------------------

DEFAULT_MC_PATH = Path(
    "DIR-RES-CC-001-claude-leak-workzone/external-refs/mission-control"
)
MC_PORT = 3000
MC_URL = f"http://localhost:{MC_PORT}"
MAX_WAIT_SECONDS = 30
POLL_INTERVAL = 2

# -----------------------------------------------------------------------------
# Funções auxiliares
# -----------------------------------------------------------------------------


def is_mc_online() -> bool:
    """Verifica se o Mission Control responde na porta 3000."""
    import urllib.error
    import urllib.request

    try:
        req = urllib.request.Request(f"{MC_URL}/health", method="GET")
        urllib.request.urlopen(req, timeout=2)
        return True
    except urllib.error.URLError:
        return False
    except Exception:
        return False


def start_mission_control(mc_path: Path, dry_run: bool) -> Optional[subprocess.Popen]:
    """
    Inicia o Mission Control via pnpm dev.
    Retorna o processo Popen ou None se dry_run.
    """
    if not mc_path.exists():
        logger.error("Diretório do Mission Control não encontrado: %s", mc_path)
        return None
    logger.info("Iniciando Mission Control em %s", mc_path)
    if dry_run:
        logger.info("[DRY-RUN] Executaria: pnpm dev (cwd=%s)", mc_path)
        return None
    try:
        # pnpm dev geralmente inicia o servidor na porta 3000
        proc = subprocess.Popen(
            ["pnpm", "dev"],
            cwd=mc_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.info("Mission Control iniciado (PID=%d)", proc.pid)

        # Log em thread separada para não bloquear
        def log_stream(stream, prefix):
            for line in stream:
                if line.strip():
                    logger.debug("%s %s", prefix, line.strip())

        threading.Thread(
            target=log_stream, args=(proc.stdout, "[MC stdout]"), daemon=True
        ).start()
        threading.Thread(
            target=log_stream, args=(proc.stderr, "[MC stderr]"), daemon=True
        ).start()
        return proc
    except FileNotFoundError:
        logger.error(
            "pnpm não encontrado. Certifique-se de que o Node.js e pnpm estão instalados."
        )
        return None
    except Exception as e:
        logger.error("Erro ao iniciar Mission Control: %s", e)
        return None


def wait_for_mc_online(timeout: int = MAX_WAIT_SECONDS) -> bool:
    """Aguarda até o Mission Control ficar online ou timeout."""
    logger.info("Aguardando Mission Control ficar online (max %ds)...", timeout)
    start = time.time()
    while time.time() - start < timeout:
        if is_mc_online():
            logger.info("Mission Control online!")
            return True
        logger.debug("MC ainda offline, aguardando %ds...", POLL_INTERVAL)
        time.sleep(POLL_INTERVAL)
    logger.error("Timeout aguardando Mission Control ficar online")
    return False


def run_startup_hook(dry_run: bool) -> bool:
    """Executa NC-SCR-FR-103-mc-startup-hook.py como subprocess não bloqueante."""
    hook_path = Path(__file__).parent / "NC-SCR-FR-103-mc-startup-hook.py"
    if not hook_path.exists():
        logger.error("Hook de startup não encontrado: %s", hook_path)
        return False
    logger.info("Executando hook de startup: %s", hook_path)
    if dry_run:
        logger.info("[DRY-RUN] Executaria: python %s", hook_path)
        return True
    try:
        proc = subprocess.Popen(
            [sys.executable, str(hook_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logger.info("Hook de startup iniciado (PID=%d)", proc.pid)
        # Não bloqueia; podemos deixar rodando em background
        threading.Thread(
            target=lambda: logger.info("Hook stdout: %s", proc.stdout.read()),
            daemon=True,
        ).start()
        threading.Thread(
            target=lambda: logger.error("Hook stderr: %s", proc.stderr.read()),
            daemon=True,
        ).start()
        return True
    except Exception as e:
        logger.error("Erro ao executar hook de startup: %s", e)
        return False


# -----------------------------------------------------------------------------
# Fluxo principal
# -----------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Launcher para stack NeoCortex + Mission Control"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simular apenas")
    parser.add_argument(
        "--no-mc", action="store_true", help="Não iniciar Mission Control"
    )
    parser.add_argument(
        "--no-hook", action="store_true", help="Não executar hook de startup"
    )
    parser.add_argument(
        "--mc-path",
        type=Path,
        default=DEFAULT_MC_PATH,
        help="Caminho do Mission Control",
    )
    args = parser.parse_args()

    logger.info("Iniciando launcher (dry‑run=%s)", args.dry_run)

    mc_process = None
    hook_success = False

    # 1. Verificar se MC já está online
    if is_mc_online():
        logger.info("Mission Control já está online")
    else:
        logger.info("Mission Control offline")
        if args.no_mc:
            logger.warning("Flag --no-mc definida; não iniciará Mission Control")
            logger.error("Abortando porque MC está offline e não devemos iniciá-lo")
            sys.exit(1)
        # 2. Iniciar MC
        mc_process = start_mission_control(args.mc_path, args.dry_run)
        if mc_process is None and not args.dry_run:
            logger.error("Falha ao iniciar Mission Control")
            sys.exit(1)
        # 3. Aguardar MC online
        if not wait_for_mc_online():
            # Se timeout, tentar matar o processo (se existir)
            if mc_process:
                mc_process.terminate()
                mc_process.wait(timeout=5)
            sys.exit(1)

    # 4. Executar hook de startup
    if not args.no_hook:
        hook_success = run_startup_hook(args.dry_run)
        if not hook_success and not args.dry_run:
            logger.error("Falha ao executar hook de startup")
            sys.exit(1)
    else:
        logger.info("Hook de startup ignorado (--no-hook)")

    logger.info("Launcher concluído com sucesso")
    logger.info("Mission Control: %s", "online" if is_mc_online() else "offline")
    logger.info("Hook de startup: %s", "executado" if hook_success else "não executado")

    # Manter o processo vivo se MC foi iniciado por nós (para não matar o subprocesso)
    if mc_process and not args.dry_run:
        try:
            mc_process.wait()
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário, finalizando Mission Control...")
            mc_process.terminate()
            mc_process.wait()


if __name__ == "__main__":
    main()
