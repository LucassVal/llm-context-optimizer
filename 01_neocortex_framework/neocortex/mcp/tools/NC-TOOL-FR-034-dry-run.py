"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.323988'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-TOOL-FR-034-dry-run
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

#!/usr/bin/env python3
"""
NC-TOOL-FR-034-dry-run.py
SAVE-005  MCP Tool: neocortex_dry_run

Expe o DryRunPreviewService via MCP com 2 aes:
  - preview  calcula diff e retorna risco, linhas alteradas, prvia
  - check    executa preview e decide se deve bloquear (should_block)
"""

import importlib.util
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _get_dry_run_service():
    """Helper: retorna DryRunPreviewService ou None se indisponvel."""
    try:
        from neocortex.core import get_dry_run_preview_service

        return get_dry_run_preview_service()
    except Exception as e:
        logger.warning(f"[dry_run_tool] DryRunPreviewService no disponvel: {e}")
        return None


def _get_wal_service():
    """Helper: retorna WALService ou None se indisponvel."""
    try:
        # Carregar via importlib.util (R09)
        base_path = Path(__file__).resolve().parent.parent.parent
        wal_path = base_path / "core" / "services" / "NC-SVC-FR-016-wal-service.py"
        if not wal_path.exists():
            logger.warning(f"[dry_run_tool] WAL service not found at {wal_path}")
            return None
        spec = importlib.util.spec_from_file_location("wal_service", wal_path)
        if spec is None:
            logger.warning("[dry_run_tool] Failed to create spec for WAL service")
            return None
        if spec.loader is None:
            logger.warning("[dry_run_tool] Spec loader is None for WAL service")
            return None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.WALService()
    except Exception as e:
        logger.warning(f"[dry_run_tool] WALService unavailable: {e}")
        return None


def register_tool(mcp) -> None:
    """Registra neocortex_dry_run no servidor MCP."""

    @mcp.tool(name="neocortex_dry_run")
    def neocortex_dry_run(
        action: str,
        target_path: str = "",
        content: str = "",
        agent_role: str = "unknown",
    ) -> Dict[str, Any]:
        """
        Middleware de DryRun Preview (SAVE005).

        Aes disponveis:
          - preview  calcula diff entre contedo atual e novo.
                      Retorna: { risk, diff_lines, affected_files, preview }
          - check    executa preview e decide se deve bloquear.
                      Retorna: { block, reason, ... }

        Args:
            action:      Ao desejada (preview | check)
            target_path: Caminho do arquivo que ser modificado (obrigatrio)
            content:     Contedo novo (string, obrigatrio para preview/check)
            agent_role:  Papel do agente (para verificaes de lock; default unknown)

        Returns:
            Dict com resultado da operao.
        """
        dry_run = _get_dry_run_service()
        if dry_run is None:
            return {
                "success": False,
                "error": "DryRunPreviewService indisponvel (SAVE005 no inicializado).",
                "action": action,
            }

        # Validao bsica
        if not target_path:
            return {
                "success": False,
                "error": "target_path  obrigatrio.",
                "action": action,
            }
        if not content and action in ("preview", "check"):
            return {
                "success": False,
                "error": "content  obrigatrio para aes preview/check.",
                "action": action,
            }

        #  preview
        if action == "preview":
            result = dry_run.preview(
                action="file_write",  # ao genrica (pode ser refinada)
                target_path=target_path,
                content=content,
                agent_role=agent_role,
            )
            return {
                "success": True,
                "action": "preview",
                "risk": result.risk,
                "diff_lines": result.diff_lines,
                "affected_files": result.affected_files,
                "preview": result.preview,
            }

        #  check
        elif action == "check":
            result = dry_run.preview(
                action="file_write",
                target_path=target_path,
                content=content,
                agent_role=agent_role,
            )
            block = dry_run.should_block(result)
            response = {
                "success": True,
                "action": "check",
                "block": block,
                "risk": result.risk,
                "diff_lines": result.diff_lines,
                "affected_files": result.affected_files,
                "reason": "risco HIGH" if result.risk == "high" else "OK",
            }
            if block:
                response["warning"] = " Operao deve ser bloqueada (risco ALTO)."
                # Log to WAL
                wal_service = _get_wal_service()
                if wal_service is not None:
                    try:
                        import time

                        session_id = f"dryrun-block-{int(time.time())}"
                        wal_service.open_session(
                            session_id, "dry-run-tool", ticket_id=None
                        )
                        wal_service.log_operation(
                            session_id=session_id,
                            operation="DRY_RUN_BLOCK",
                            file_path=target_path,
                            ticket_id=None,
                            before_hash=None,
                            after_hash=None,
                        )
                        wal_service.commit_session(session_id)
                        logger.info(
                            f"[dry_run_tool] Blocked operation logged to WAL: {target_path}"
                        )
                    except Exception as e:
                        logger.warning(f"[dry_run_tool] Failed to log to WAL: {e}")
            return response

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'. Use: preview | check",
                "action": action,
            }
