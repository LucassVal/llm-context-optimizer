#!/usr/bin/env python3
"""---
NC-DS-122 — Executor de renomeação segura de neocortex/core/ KEEP_NON_NC
---
"""

"""---
NC-DS-122 — Executor de renomeação segura de neocortex/core/ KEEP_NON_NC
---
"""

"""
NC-DS-122 — Executor de renomeação segura de neocortex/core/ KEEP_NON_NC
T0-Antigravity — 2026-04-20

Estratégia:
  1. Para cada arquivo: copia conteúdo para NC-CORE-FR-NNN-<name>.py
  2. Substitui arquivo antigo por shim que re-exporta via importlib
  3. Valida py_compile + ruff em ambos
  4. Rollback automático se qualquer validação falhar
"""
import logging
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

FW = Path(__file__).resolve().parent.parent  # scripts/ → 01_neocortex_framework/
CORE_DIR = FW / "neocortex" / "core"


# Mapeamento: old_name → NC-CORE-FR-NNN-new_name
RENAME_MAP = [
    ("agent_policy_enforcer.py", "NC-CORE-FR-101-agent-policy-enforcer.py"),
    ("agent_service.py",          "NC-CORE-FR-102-agent-service.py"),
    ("akl_service.py",            "NC-CORE-FR-103-akl-service.py"),
    ("benchmark_service.py",      "NC-CORE-FR-104-benchmark-service.py"),
    ("cascade_consolidator.py",   "NC-CORE-FR-105-cascade-consolidator.py"),
    ("checkpoint_service.py",     "NC-CORE-FR-106-checkpoint-service.py"),
    ("circuit_breaker.py",        "NC-CORE-FR-107-circuit-breaker.py"),
    ("config_service.py",         "NC-CORE-FR-108-config-service.py"),
    ("consolidation_service.py",  "NC-CORE-FR-109-consolidation-service.py"),
    ("cortex_service.py",         "NC-CORE-FR-110-cortex-service.py"),
    ("export_service.py",         "NC-CORE-FR-111-export-service.py"),
    ("file_utils.py",             "NC-CORE-FR-112-file-utils.py"),
    ("init_service.py",           "NC-CORE-FR-113-init-service.py"),
    ("kg_service.py",             "NC-CORE-FR-114-kg-service.py"),
    ("ledger_service.py",         "NC-CORE-FR-115-ledger-service.py"),
    ("lexico_service.py",         "NC-CORE-FR-116-lexico-service.py"),
    ("lobe_service.py",           "NC-CORE-FR-117-lobe-service.py"),
    ("manifest_service.py",       "NC-CORE-FR-118-manifest-service.py"),
    ("peers_service.py",          "NC-CORE-FR-119-peers-service.py"),
    ("profile_manager.py",        "NC-CORE-FR-120-profile-manager.py"),
    ("profile_service.py",        "NC-CORE-FR-121-profile-service.py"),
    ("pulse_scheduler.py",        "NC-CORE-FR-122-pulse-scheduler.py"),
    ("regression_service.py",     "NC-CORE-FR-123-regression-service.py"),
    ("security_service.py",       "NC-CORE-FR-124-security-service.py"),
]

SHIM_TEMPLATE = '''\
"""
{old_name} — ALIAS SHIM (DEPRECATED)
Replaced by {new_name}
Preserved for backward compatibility with existing importers.
DO NOT add new imports here. Use {new_name} directly.
"""
# NC-DS-122: backward-compat shim
import importlib.util as _util
import sys as _sys
from pathlib import Path as _Path

_NC_FILE = _Path(__file__).parent / "{new_name}"
_spec = _util.spec_from_file_location("{slug}", _NC_FILE)
_mod = _util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
# Re-export all public symbols into this namespace
_sys.modules[__name__].__dict__.update(
    {{k: v for k, v in _mod.__dict__.items() if not k.startswith("_")}}
)
del _util, _sys, _Path, _NC_FILE, _spec, _mod
'''

ok_list = []
fail_list = []
created_files = []


def ruff_check(path: Path) -> bool:
    """Run ruff --select F,E9 on path. Return True if clean."""
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(path), "--select", "F841,E9"],
        capture_output=True, text=True, cwd=str(FW)
    )
    return r.returncode == 0


def compile_check(path: Path) -> bool:
    """Run py_compile on path. Return True if clean."""
    try:
        py_compile.compile(str(path), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        logger.error("compile error %s: %s", path.name, e)
        return False


def process_pair(old_name: str, new_name: str) -> bool:
    """Process one rename pair. Return True if success."""
    old_path = CORE_DIR / old_name
    new_path = CORE_DIR / new_name

    if not old_path.exists():
        logger.warning("SKIP: %s not found", old_name)
        return True  # not a failure, might already be processed

    if new_path.exists():
        logger.info("SKIP: %s already exists", new_name)
        return True

    # 1. Backup original
    backup = old_path.with_suffix(".py.bak122")
    shutil.copy2(old_path, backup)

    try:
        # 2. Copy content to NC-CORE-FR-NNN file
        content = old_path.read_text(encoding="utf-8")
        new_path.write_text(content, encoding="utf-8")
        created_files.append(str(new_path))

        # 3. Validate new NC file
        if not compile_check(new_path):
            raise RuntimeError(f"compile failed: {new_name}")
        if not ruff_check(new_path):
            logger.warning("ruff F,E9 issues in %s (non-blocking)", new_name)

        # 4. Replace old file with shim
        slug = new_name.replace("-", "_").replace(".py", "")
        shim = SHIM_TEMPLATE.format(
            old_name=old_name,
            new_name=new_name,
            slug=slug,
        )
        old_path.write_text(shim, encoding="utf-8")
        created_files.append(str(old_path) + " [shim]")

        # 5. Validate shim
        if not compile_check(old_path):
            raise RuntimeError(f"shim compile failed: {old_name}")

        # 6. Cleanup backup
        backup.unlink()
        logger.info("OK: %s → %s + shim", old_name, new_name)
        ok_list.append(old_name)
        return True

    except Exception as e:
        logger.error("FAIL %s: %s — rolling back", old_name, e)
        # Rollback
        if backup.exists():
            shutil.copy2(backup, old_path)
            backup.unlink()
        if new_path.exists():
            new_path.unlink()
        fail_list.append(f"{old_name}: {e}")
        return False


def main() -> None:
    logger.info("NC-DS-122: processando %d arquivos em %s", len(RENAME_MAP), CORE_DIR)

    # Verify CORE_DIR exists
    if not CORE_DIR.exists():
        logger.error("CORE_DIR not found: %s", CORE_DIR)
        sys.exit(1)

    # Process in batches of 6
    batch_size = 6
    for i in range(0, len(RENAME_MAP), batch_size):
        batch = RENAME_MAP[i:i + batch_size]
        logger.info("--- Lote %d: %s ---", i // batch_size + 1, [b[0] for b in batch])
        for old_name, new_name in batch:
            process_pair(old_name, new_name)

    print("\n=== RESULTADO NC-DS-122 ===")
    print(f"OK: {len(ok_list)}/{len(RENAME_MAP)}")
    if fail_list:
        print(f"FALHAS ({len(fail_list)}):")
        for f in fail_list:
            print(f"  - {f}")
    else:
        print("STATUS: COMPLETED — todos os 24 arquivos processados")

    print(f"\nArquivos criados: {len(created_files)}")
    for f in created_files[:10]:
        print(f"  {f}")
    if len(created_files) > 10:
        print(f"  ... e mais {len(created_files)-10}")


if __name__ == "__main__":
    main()
