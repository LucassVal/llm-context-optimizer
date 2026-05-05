"""---
@Tool NC-CORE-FR-125-tool-guard mcp NC-CORE-FR-125-tool-guard.py — STEP 0 + LockGuard
---
"""


import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ToolGuard:
    """Middleware de governança para MCP tools."""

    def __init__(self):
        self.last_error = ""
        self.root = None
        self._lock_guard = None
        self._regression_svc = None
        self._savepoint_svc = None
        self._init_done = False

    def _init(self):
        if self._init_done:
            return
        import importlib.util
        base = Path(__file__).parent
        try:
            spec = importlib.util.spec_from_file_location(
                "lock_guard", str(base / "NC-CORE-FR-014-lock-guard.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._lock_guard = mod.get_lock_guard()
        except Exception:
            self._lock_guard = None
        try:
            spec = importlib.util.spec_from_file_location(
                "regression_service", str(base / "NC-CORE-FR-123-regression-service.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._regression_svc = mod.get_regression_service()
        except Exception:
            self._regression_svc = None
        try:
            spec = importlib.util.spec_from_file_location(
                "savepoint_service", str(base / "services" / "NC-SVC-FR-003-savepoint-stub.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self._savepoint_svc = mod  # SavePointService is the class
        except Exception:
            self._savepoint_svc = None
        self._init_done = True

    # ── G1 (LOCK-06): Pre-write LockGuard validation ─────────────────

    def validate_write(self, path: str, agent_role: str = "T0") -> bool:
        """Check if write is allowed by atomic locks. Returns True if permitted."""
        self._init()
        if not self._lock_guard:
            self.last_error = "LockGuard indisponivel"
            return True  # fail-open if guard unavailable

        try:
            allowed, reason = self._lock_guard.check_write(path, agent_role)
            if not allowed:
                self.last_error = reason or "Bloqueado por atomic lock"
                logger.warning(f"[ToolGuard] WRITE BLOCKED: {path} -> {self.last_error}")
                return False
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"[ToolGuard] LockGuard error: {e}")
            return True  # fail-open on error

    # ── G2 (STEP 0): Regression check ─────────────────────────────

    def step_zero(self, action_name: str) -> Dict[str, Any]:
        """Execute STEP 0 regression check before tool action."""
        self._init()
        if not self._regression_svc:
            return {"ok": True, "note": "RegressionService indisponível"}

        try:
            result = self._regression_svc.check()
            if result.get("buffer_size", 0) > 0:
                recent = result.get("recent_errors", [])
                # Verificar se ação atual é similar a algum erro passado
                for err in recent:
                    if any(word in err.lower() for word in action_name.lower().split("_")):
                        logger.warning(
                            f"[ToolGuard] STEP-0 WARNING: ação '{action_name}' "
                            f"similar a erro passado: '{err[:80]}'"
                        )
                        return {
                            "ok": False,
                            "warning": "STEP-0: similaridade com erro passado",
                            "matched_error": err[:120],
                        }
            return {"ok": True, "note": f"STEP-0 pass: buffer={result.get('buffer_size')}"}
        except Exception as e:
            return {"ok": True, "note": f"STEP-0 error (non-blocking): {e}"}

    # ── G3 (STEP -1): Auto savepoint before write ──────────────────

    def savepoint_before_write(self, context: str = "") -> Optional[str]:
        """Create savepoint before a write operation."""
        self._init()
        if not self._savepoint_svc:
            return None
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"auto_{context}_{ts}" if context else f"auto_{ts}"
            result = self._savepoint_svc.create_save_point(name)
            if result.get("success"):
                return name
        except Exception:
            pass
        return None

    # ── G5 (R01): Naming check ────────────────────────────────────

    def check_naming(self, filename: str) -> Dict[str, Any]:
        """Validate NC- naming convention against @ULQ dictionary."""
        if not filename.startswith("NC-"):
            full = f"NC-XXX-XX-000-{filename}"  # allow auto-prefix
            return {"valid": True, "note": f"Prefixo NC- será adicionado: {full}"}

        parts = filename.split("-")
        if len(parts) < 4:
            return {"valid": False, "error": "Formato: NC-<TIPO>-<SIGLA>-<NUM>-<desc>.<ext>"}

        tipo = parts[1].upper()
        sigla = parts[2].upper()

        # Consult @ULQ dictionary for valid types/siglas
        ulq_types = ["TOOL", "SVC", "LBE", "SCR", "DS", "LED", "BOOT", "GOV",
                     "CFG", "TPL", "TODO", "RULE", "WF", "ARC", "BAK", "NAM",
                     "AUD", "ALN", "PLN", "SES", "TKT", "PRF", "CORE", "INFRA",
                     "MCP", "SUPER", "IMPL", "RPT", "TEST", "REF", "CTX", "FIL"]
        ulq_siglas = ["FR", "WL", "USR", "CC", "OP", "INT", "DS"]

        warnings = []
        if tipo not in ulq_types:
            warnings.append(f"TIPO '{tipo}' não está no @ULQ")
        if sigla not in ulq_siglas:
            warnings.append(f"SIGLA '{sigla}' não está no @ULQ")

        if warnings:
            return {"valid": True, "warnings": warnings,
                    "note": "Nomes fora do @ULQ são permitidos mas devem ser registrados"}

        return {"valid": True}

    # ── GAP-002: CryptoHub signing ─────────────────────────────────

    def sign_action(self, action: str, agent_role: str = "T0") -> Dict[str, Any]:
        """Sign governance action via CryptoHub (CRYPTO-01/02)."""
        import importlib.util
        try:
            base = Path(__file__).parent
            spec = importlib.util.spec_from_file_location(
                "crypto_hub", str(base / "services" / "NC-SVC-FR-017-crypto-hub.py"))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            hub = mod.CryptoHub()
            payload = f"role={agent_role}|action={action}|ts={datetime.now().isoformat()}"
            result = hub.encrypt(payload)
            if hasattr(result, 'success') and result.success:
                return {"signed": True, "token_hash": result.token_hash[:16]}
            return {"signed": False, "error": "CryptoHub encrypt failed"}
        except Exception as e:
            return {"signed": False, "error": str(e)}

    # ── AUTO-REGRESSION: log failures for STEP 0 ─────────────────

    def log_failure(self, action: str, error: str) -> None:
        """Auto-log failure to regression buffer (STEP 0 auto-feed)."""
        self._init()
        if not self._regression_svc:
            return
        try:
            self._regression_svc.add_regression_entry(
                error=f"AUTO: {action} - {error[:200]}",
                severity="AUTO",
                context=f"ToolGuard auto-log from {action}",
            )
            logger.info(f"[ToolGuard] Regression logged: {action} -> {error[:80]}")
        except Exception:
            pass


# Singleton
_tool_guard_instance: Optional[ToolGuard] = None


def get_tool_guard() -> ToolGuard:
    global _tool_guard_instance
    if _tool_guard_instance is None:
        _tool_guard_instance = ToolGuard()
    return _tool_guard_instance
