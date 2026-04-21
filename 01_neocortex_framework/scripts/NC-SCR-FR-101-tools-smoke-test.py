#!/usr/bin/env python3

import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T11:45:00.000000'
  injected_by: NC-SCR-FR-101-tools-smoke-test.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-101-tools-smoke-test
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-101-tools-smoke-test.py
FR-101 — Smoke test automatizado das 38 tools MCP.

Descobre todos os NC-TOOL-FR-*.py em neocortex/mcp/tools/ via glob.
Para cada tool:
  a. py_compile — verificar sintaxe
  b. importlib.util.spec_from_file_location + exec_module em contexto isolado
     (adicionar neocortex ao sys.path para resolver relative imports)
  c. Verificar presença de register_tool() function
  d. Registrar: OK / FAIL_SYNTAX / FAIL_IMPORT / FAIL_NO_REGISTER
Output: tabela com status por tool + resumo final
Exit code 0 se todas OK, exit code 1 se qualquer FAIL
Suportar flag --json para output machine-readable
Registrar resultado via NC-SVC-FR-016-wal-service (WAL log)
Salvar relatório em reports/smoke-test-YYYYMMDD.json
"""

import argparse
import importlib.util
import json
import logging
import py_compile
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# ------------------------------------------------------------------
# Import WALService via importlib.util (R09)
# ------------------------------------------------------------------


def load_wal_service():
    """Load NC-SVC-FR-016-wal-service.py via importlib."""
    base_path = Path(__file__).resolve().parent.parent
    wal_path = (
        base_path / "neocortex" / "core" / "services" / "NC-SVC-FR-016-wal-service.py"
    )
    if not wal_path.exists():
        logger.warning(
            f"WAL service not found at {wal_path}, continuing without WAL logging"
        )
        return None
    spec = importlib.util.spec_from_file_location("wal_service", wal_path)
    if spec is None:
        logger.warning("Failed to create spec for WAL service")
        return None
    if spec.loader is None:
        logger.warning("Spec loader is None for WAL service")
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.WALService()


# ------------------------------------------------------------------
# Smoke test core logic
# ------------------------------------------------------------------


def discover_tools() -> List[Path]:
    """Find all NC-TOOL-FR-*.py files."""
    tools_dir = Path(__file__).resolve().parent.parent / "neocortex" / "mcp" / "tools"
    if not tools_dir.exists():
        logger.error(f"Tools directory not found: {tools_dir}")
        return []
    tool_files = list(tools_dir.glob("NC-TOOL-FR-*.py"))
    logger.info(f"Found {len(tool_files)} tool files in {tools_dir}")
    return tool_files


def test_tool(tool_path: Path) -> Dict[str, Any]:
    """Test a single tool file."""
    tool_name = tool_path.name
    result = {
        "tool": tool_name,
        "path": str(tool_path),
        "status": "UNKNOWN",
        "error": None,
        "details": None,
    }

    # 1. py_compile syntax check
    try:
        py_compile.compile(str(tool_path), doraise=True)
        result["syntax"] = "OK"
    except py_compile.PyCompileError as e:
        result["status"] = "FAIL_SYNTAX"
        result["error"] = str(e)
        return result
    except Exception as e:
        result["status"] = "FAIL_SYNTAX_UNEXPECTED"
        result["error"] = str(e)
        return result

    # 2. importlib load
    try:
        # Add neocortex to sys.path for relative imports
        import sys

        neocortex_root = tool_path.parent.parent.parent.parent
        if str(neocortex_root) not in sys.path:
            sys.path.insert(0, str(neocortex_root))

        # Import as proper package module (same as server)
        stem = tool_path.stem  # e.g., NC-TOOL-FR-001-cortex
        module_name = f"neocortex.mcp.tools.{stem}"
        module = importlib.import_module(module_name)
        result["import"] = "OK"
    except Exception as e:
        result["status"] = "FAIL_IMPORT"
        result["error"] = str(e)
        return result

    # 3. Check register_tool function
    if not hasattr(module, "register_tool"):
        result["status"] = "FAIL_NO_REGISTER"
        result["error"] = "Missing register_tool() function"
        return result

    result["status"] = "OK"
    result["details"] = {
        "has_register_tool": True,
        "module_loaded": True,
    }
    return result


def run_smoke_test(json_output: bool = False) -> Dict[str, Any]:
    """Run smoke test on all tools."""
    tools = discover_tools()
    if not tools:
        return {"success": False, "error": "No tools found"}

    results = []
    ok_count = 0
    fail_count = 0

    for tool_path in tools:
        result = test_tool(tool_path)
        results.append(result)
        if result["status"] == "OK":
            ok_count += 1
        else:
            fail_count += 1
        if not json_output:
            status_display = "✓" if result["status"] == "OK" else "✗"
            print(f"{status_display} {result['tool']}: {result['status']}")
            if result["error"]:
                print(f"    Error: {result['error']}")

    summary = {
        "total_tools": len(tools),
        "ok": ok_count,
        "fail": fail_count,
        "success_rate": ok_count / len(tools) if len(tools) > 0 else 0,
        "all_ok": fail_count == 0,
    }

    # Generate report file
    reports_dir = Path(__file__).resolve().parent.parent.parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"smoke-test-{timestamp}.json"
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
        "results": results,
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    logger.info(f"Report saved to {report_path}")

    # Log to WAL
    wal_service = load_wal_service()
    if wal_service is not None:
        try:
            session_id = f"smoke-test-{int(time.time())}"
            wal_service.open_session(session_id, "smoke-test", ticket_id=None)
            wal_service.log_operation(
                session_id=session_id,
                operation="SMOKE_TEST_RUN",
                file_path=str(report_path),
                ticket_id=None,
                before_hash=None,
                after_hash=None,
            )
            wal_service.commit_session(session_id)
            logger.info(f"Smoke test result logged to WAL session {session_id}")
        except Exception as e:
            logger.warning(f"Failed to log to WAL: {e}")

    return {"summary": summary, "results": results, "report_path": str(report_path)}


def main():
    parser = argparse.ArgumentParser(description="Smoke test for MCP tools")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    result = run_smoke_test(json_output=args.json)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        summary = result["summary"]
        print("\n" + "=" * 60)
        print("SMOKE TEST SUMMARY")
        print("=" * 60)
        print(f"Total tools: {summary['total_tools']}")
        print(f"OK: {summary['ok']}")
        print(f"FAIL: {summary['fail']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"All OK: {summary['all_ok']}")
        print("=" * 60)

    # Exit code
    if result["summary"]["all_ok"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
