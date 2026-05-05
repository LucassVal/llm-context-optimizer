---
name: nc-audit
description: Auditoria 3 camadas (compile + runtime + operational) — ruff/mypy/bandit + ulq contract + pulse health/checkpoint/WAL freshness. Gera relatorio NC-AUDIT-FR-*.yaml.
compatibility: opencode
metadata:
  tier: T0
  rule: R6+R17+R51
  category: audit
  mcp_tools: [neocortex_governance.compliance.report, neocortex_governance.audit.full, neocortex_state.regression.check, neocortex_state.checkpoint.list, neocortex_health.server.health]
---

## What I do
Auditoria 3 camadas via MCP + Bash:

### Camada 1 — Compile-time (Bash + MCP)
```bash
# ruff + mypy + py_compile + bandit (batch no core + tools)
python -m neocortex.core.NC-CORE-FR-173-mcp-audit-3-levels
```
```
neocortex_governance action=audit.full
```

### Camada 2 — Runtime (MCP)
```
neocortex_governance action=ssot.diff      # ULQ cross-ref
neocortex_governance action=catalog.refresh # artifact integrity
neocortex_governance action=naming.check   # NC- prefix scan
```

### Camada 3 — Operational (MCP)
```
neocortex_state action=regression.check    # buffer freshness
neocortex_state action=checkpoint.list     # ultimo checkpoint
neocortex_health action=server.health      # MCP server status
neocortex_health action=server.tools_count # tools ativas
neocortex_context action=context.budget_status  # token budget
```

### Relatorio
Salvar como `DIR-DS-002-audit-logs/NC-AUDIT-FR-*-governance-ssot-audit-{date}.yaml`

## When to use me
- CICLO 4 semanal (compliance.report)
- Antes de release
- Quando compliance < 80%
- Quando regression buffer tem entradas novas

## Integration
- Hook: CICLO 4 — `neocortex_governance action=compliance.report` roda automaticamente
- PulseScheduler (C): checkpoint a cada 300s
- SCHEDULE (S): execucao semanal via PulseOrbital
