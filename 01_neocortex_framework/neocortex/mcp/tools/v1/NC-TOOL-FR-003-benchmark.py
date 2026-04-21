"""---
_genealogy:
  injected_at: '2026-04-16T00:24:00.224200'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""
#!/usr/bin/env python3
"""
NeoCortex Benchmark Tool

Ferramenta MCP para neocortex_benchmark.
"""

from typing import Any, Dict

from ...core import get_benchmark_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_benchmark no servidor MCP.
    """

    @mcp.tool(name="neocortex_benchmark")
    def tool_benchmark(action: str, benchmark_type: str = "") -> Dict[str, Any]:
        """Execucao de benchmarks.

        Actions:
        - run_drift: Executa benchmark Drift Exhaustion
        - run_titanomachy: Executa benchmark Titanomachy
        - get_last_report: Retorna o ultimo relatorio de benchmark"""
        service = get_benchmark_service()

        if action == "run_drift":
            return service.run_drift()
        elif action == "run_titanomachy":
            return service.run_titanomachy()
        elif action == "get_last_report":
            return service.get_last_report()

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_benchmark
