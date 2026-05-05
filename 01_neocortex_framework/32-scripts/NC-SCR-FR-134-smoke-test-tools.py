#!/usr/bin/env python3
"""---
NC-SCR-FR-134 — NC-DS-134: Smoke Test 40 MCP Super-Tools
---
"""

"""---
NC-SCR-FR-134 — NC-DS-134: Smoke Test 40 MCP Super-Tools
---
"""

"""
NC-SCR-FR-134 — NC-DS-134: Smoke Test 40 MCP Super-Tools
Valida que todos os NC-SUPER-001..015 respondem sem erros críticos.

Resultado: score X/Y tools OK | relatório em .neocortex/smoke_test_report.json
"""
import importlib.util
import json
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT   = Path(__file__).resolve().parents[2]
FW_DIR = ROOT / "01_neocortex_framework"
TOOLS_DIR = FW_DIR / "neocortex" / "mcp" / "tools"

sys.path.insert(0, str(FW_DIR))

def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ── Caso de teste por tool ──────────────────────────────────────────────────

SMOKE_CASES = {
    "NC-SUPER-001-governance.py": [
        ("neocortex_governance", {"action": "rule.list"}),
        ("neocortex_governance", {"action": "compliance.report"}),
        ("neocortex_governance", {"action": "cf.status"}),
        ("neocortex_governance", {"action": "naming.check", "policy_name": "NC-SVC-FR-001-test.py"}),
    ],
    "NC-SUPER-002-orchestration.py": [
        ("neocortex_orchestration", {"action": "task.list"}),
        ("neocortex_orchestration", {"action": "agent.list"}),
    ],
    "NC-SUPER-003-memory.py": [
        ("neocortex_memory", {"action": "lobe.list"}),
        ("neocortex_memory", {"action": "cortex.get"}),
        ("neocortex_memory", {"action": "lexico.stats"}),
    ],
    "NC-SUPER-004-state.py": [
        ("neocortex_state", {"action": "checkpoint.list"}),
        ("neocortex_state", {"action": "savepoint.list"}),
        ("neocortex_state", {"action": "ledger.stats"}),
    ],
    "NC-SUPER-005-llm-router.py": [
        ("neocortex_llm_router", {"action": "gateway.health"}),
        ("neocortex_llm_router", {"action": "budget.status"}),
    ],
    "NC-SUPER-006-system.py": [
        ("neocortex_system", {"action": "config.list"}),
        ("neocortex_system", {"action": "pulse.status"}),
        ("neocortex_system", {"action": "health.agent"}),
    ],
    "NC-SUPER-007-brain.py": [
        ("neocortex_brain", {"action": "brain.think", "prompt": "ola", "max_tokens": 10}),
    ],
    "NC-SUPER-008-context.py": [
        ("neocortex_context", {"action": "context.budget_status"}),
        ("neocortex_context", {"action": "session.hot"}),
    ],
    "NC-SUPER-009-security.py": [
        ("neocortex_security", {"action": "lock.list"}),
        ("neocortex_security", {"action": "hook.list"}),
        ("neocortex_security", {"action": "access.validate", "resource": "test", "agent_role": "T0"}),
    ],
    "NC-SUPER-010-benchmark.py": [
        ("neocortex_benchmark", {"action": "benchmark.status"}),
    ],
    "NC-SUPER-011-notification.py": [
        ("neocortex_notification", {"action": "push.list"}),
    ],
    "NC-SUPER-012-akl.py": [
        ("neocortex_akl", {"action": "akl.search", "query": "test"}),
        ("neocortex_akl", {"action": "kg.stats"}),
    ],
    "NC-SUPER-013-health.py": [
        ("neocortex_health", {"action": "server.health"}),
        ("neocortex_health", {"action": "metrics.live"}),
        ("neocortex_health", {"action": "server.tools_count"}),
    ],
    "NC-SUPER-014-ledger.py": [
        ("neocortex_ledger", {"action": "ledger.read"}),
        ("neocortex_ledger", {"action": "ledger.stats"}),
    ],
    "NC-SUPER-015-memory-auto.py": [
        ("neocortex_memory_auto", {"action": "session.stats"}),
        ("neocortex_memory_auto", {"action": "catalog.now"}),
    ],
}

# ── Mock MCP server ────────────────────────────────────────────────────────

class MockMCP:
    """MCP stub para coletar a função registrada pelo tool."""
    def __init__(self):
        self._fn = None
        self._name = None

    def tool(self, name=None):
        self._name = name
        def decorator(fn):
            self._fn = fn
            return fn
        return decorator

    def call(self, **kwargs):
        if not self._fn:
            raise RuntimeError("Tool não registrado")
        return self._fn(**kwargs)


def load_and_call(tool_file: Path, tool_name: str, kwargs: dict) -> dict:
    """Carrega o módulo do tool, registra e chama com kwargs."""
    spec = importlib.util.spec_from_file_location(tool_file.stem, tool_file)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mcp = MockMCP()
    mod.register_tool(mcp)
    return mcp.call(**kwargs)


# ── Runner ─────────────────────────────────────────────────────────────────

def run_smoke_test() -> dict:
    print(f"\nNC-DS-134 SMOKE TEST — {_ts()}")
    print(f"Tools dir: {TOOLS_DIR}")
    print("=" * 60)

    results = {}
    total_cases = 0
    passed_cases = 0
    failed_tools = []

    for tool_file_name, cases in SMOKE_CASES.items():
        tool_path = TOOLS_DIR / tool_file_name
        tool_results = []
        tool_ok = True

        if not tool_path.exists():
            print(f"  ⚠️  {tool_file_name} — arquivo ausente")
            results[tool_file_name] = {"status": "MISSING", "cases": []}
            failed_tools.append(tool_file_name)
            continue

        for tool_name, kwargs in cases:
            total_cases += 1
            t0 = time.monotonic()
            try:
                r = load_and_call(tool_path, tool_name, kwargs)
                elapsed = round((time.monotonic() - t0) * 1000)
                ok = isinstance(r, dict)  # qualquer dict é OK (pode ser success:False mas retornou)
                fatal = not ok or r.get("error", "").startswith("Traceback")
                if not fatal:
                    passed_cases += 1
                    icon = "✅"
                else:
                    tool_ok = False
                    icon = "❌"
                action = kwargs.get("action", "?")
                print(f"  {icon} {tool_file_name[:35]:<36} {action:<30} {elapsed:>5}ms"
                      + (f" | err={r.get('error','')}" if fatal else ""))
                tool_results.append({
                    "action": kwargs.get("action"),
                    "ok": not fatal,
                    "ms": elapsed,
                    "error": r.get("error") if fatal else None,
                })
            except Exception as ex:
                elapsed = round((time.monotonic() - t0) * 1000)
                tool_ok = False
                print(f"  ❌ {tool_file_name[:35]:<36} {kwargs.get('action','?'):<30} {elapsed:>5}ms | EXCEPTION: {ex}")
                tool_results.append({
                    "action": kwargs.get("action"),
                    "ok": False,
                    "ms": elapsed,
                    "error": str(ex)[:120],
                })

        results[tool_file_name] = {
            "status": "OK" if tool_ok else "FAIL",
            "cases": tool_results,
        }
        if not tool_ok:
            failed_tools.append(tool_file_name)

    # ── Relatório ──────────────────────────────────────────────────────────
    score_pct = round(passed_cases / total_cases * 100) if total_cases else 0
    print("\n" + "=" * 60)
    print(f"SCORE: {passed_cases}/{total_cases} ({score_pct}%)")
    if failed_tools:
        print(f"FAILURES ({len(failed_tools)}): {', '.join(failed_tools)}")
    else:
        print("✅ TODOS OS TOOLS PASSARAM!")

    report = {
        "generated": _ts(),
        "score_pct": score_pct,
        "passed": passed_cases,
        "total": total_cases,
        "failed_tools": failed_tools,
        "tools": results,
    }

    report_path = FW_DIR / ".neocortex" / "smoke_test_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📋 Relatório: {report_path}")
    return report


if __name__ == "__main__":
    run_smoke_test()
