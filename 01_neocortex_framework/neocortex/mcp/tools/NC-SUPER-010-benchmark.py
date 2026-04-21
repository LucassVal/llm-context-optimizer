#!/usr/bin/env python3
"""
NC-SUPER-010 — neocortex_benchmark
FÓRUM — Benchmark e Workers

Funde: benchmark (003).

Actions:
  run.drift, run.titanomachy, run.omni
  benchmark.last_report, benchmark.status
"""
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)
TOOL_NAME = "neocortex_benchmark"


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _root() -> Path:
    # parents[4] = TURBOQUANT_V42/ (acima de tools/mcp/neocortex/01_neocortex_framework/)
    return Path(__file__).parents[4]


def register_tool(mcp) -> None:
    @mcp.tool(name=TOOL_NAME)
    def neocortex_benchmark(
        action: str,
        model: str = "qwen2.5-coder:1.5b",
        n_iterations: int = 3,
        timeout: int = 120,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """FÓRUM — Benchmark e Workers.
        Funde: benchmark (003).
        Actions: run.drift, run.titanomachy, run.omni,
                 benchmark.last_report, benchmark.status
        """
        ts = _ts()

        def _run_benchmark_test(test_name: str, prompt: str) -> Dict:
            if dry_run:
                return {"test": test_name, "dry_run": True, "result": "skipped"}
            try:
                import requests
                start = time.time()
                r = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=timeout,
                )
                elapsed = round(time.time() - start, 2)
                if r.ok:
                    data = r.json()
                    return {"test": test_name, "ok": True, "elapsed_sec": elapsed,
                            "tokens": data.get("eval_count", 0),
                            "tps": round(data.get("eval_count", 0) / max(elapsed, 0.1), 1)}
                return {"test": test_name, "ok": False, "elapsed_sec": elapsed,
                        "error": r.text[:100]}
            except Exception as e:
                return {"test": test_name, "ok": False, "error": str(e)}

        if action == "run.drift":
            results = [_run_benchmark_test(
                f"drift_{i+1}",
                f"Iteration {i+1}: Write a Python function to calculate fibonacci(n)."
            ) for i in range(n_iterations)]
            ok_count = sum(1 for r in results if r.get("ok"))
            avg_tps = sum(r.get("tps", 0) for r in results if r.get("ok")) / max(ok_count, 1)
            return {"success": True, "action": action, "model": model,
                    "iterations": n_iterations, "ok": ok_count,
                    "avg_tps": round(avg_tps, 1), "results": results, "timestamp": ts}

        elif action == "run.titanomachy":
            tests = [
                ("reasoning", "Explain O(1) context retrieval vs O(n) scanning. Give concrete examples."),
                ("code_gen", "Write a Python decorator that adds retry logic with exponential backoff."),
                ("analysis", "What are the tradeoffs of event-driven vs polling architectures?"),
            ]
            results = [_run_benchmark_test(name, prompt) for name, prompt in tests]
            ok_count = sum(1 for r in results if r.get("ok"))
            return {"success": True, "action": action, "model": model,
                    "tests_run": len(tests), "passed": ok_count,
                    "results": results, "timestamp": ts}

        elif action == "run.omni":
            all_results = []
            for i in range(n_iterations):
                r1 = _run_benchmark_test(f"omni_drift_{i}", "Fibonacci(10) in Python.")
                r2 = _run_benchmark_test(f"omni_reason_{i}", "What is O(1) context retrieval?")
                all_results.extend([r1, r2])
            ok = sum(1 for r in all_results if r.get("ok"))
            return {"success": True, "action": action, "model": model,
                    "total_tests": len(all_results), "passed": ok,
                    "results": all_results, "timestamp": ts}

        elif action == "benchmark.last_report":
            root = _root()
            reports = list((root / "reports" / "benchmark").rglob("*.json")) if (root / "reports").exists() else []
            if not reports:
                return {"success": True, "action": action, "report": None,
                        "note": "Nenhum relatório encontrado. Execute run.drift primeiro.", "timestamp": ts}
            latest = max(reports, key=lambda f: f.stat().st_mtime)
            try:
                data = json.loads(latest.read_text(encoding="utf-8"))
                return {"success": True, "action": action, "report": data,
                        "report_file": latest.name, "timestamp": ts}
            except Exception as e:
                return {"success": False, "error": str(e), "timestamp": ts}

        elif action == "benchmark.status":
            try:
                import requests
                r = requests.get("http://localhost:11434/api/tags", timeout=5)
                online = r.ok
                models = [m.get("name") for m in r.json().get("models", [])] if r.ok else []
            except Exception:
                online = False
                models = []
            return {"success": True, "action": action, "ollama_online": online,
                    "available_models": models, "benchmark_model": model, "timestamp": ts}

        else:
            return {"success": False, "error": f"action desconhecida: {action}",
                    "available": ["run.drift", "run.titanomachy", "run.omni",
                                  "benchmark.last_report", "benchmark.status"],
                    "timestamp": ts}
