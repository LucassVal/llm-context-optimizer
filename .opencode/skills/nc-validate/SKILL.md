---
name: nc-validate
description: Pipeline R6 completo — ruff + mypy + pyright + bandit + yaml.safe_load + mdc frontmatter + md naming + json parse + @LOCKS + secret scan + ssot diff. Cobre TODOS os tipos de arquivo antes de commit/handoff.
compatibility: opencode
metadata:
  tier: T0
  rule: R6
  category: verification
  mcp_tools: [neocortex_governance.yaml.validate, neocortex_governance.mdc.validate, neocortex_governance.secret.scan, neocortex_governance.naming.check, neocortex_governance.lock.validate, neocortex_governance.ssot.diff]
---

## What I do
Pipeline R6 completo. Para cada tipo de arquivo:

### Python (.py) — via Bash
```bash
python -m ruff check --fix <file>
python -m ruff format <file>
python -m mypy <file> --ignore-missing-imports
python -m py_compile <file>
python -m bandit -q <file>
```

### YAML (.yaml, .yml) — via MCP
```
neocortex_governance action=yaml.validate
neocortex_governance action=secret.scan
neocortex_governance action=naming.check
```

### MDC (.mdc) — via MCP
```
neocortex_governance action=mdc.validate
neocortex_governance action=naming.check
```

### JSON (.json) — via Bash
```
python -c "import json; json.load(open('<file>'))"
```

### Geral (todos) — via MCP
```
neocortex_governance action=lock.validate
neocortex_governance action=ssot.diff
neocortex_governance action=secret.scan
```

## When to use me
ANTES de commit, handoff, merge. Se qualquer etapa falhar → STOP (R51).

## Integration
- Hook: `lexico_step0` (PreToolUse) dispara warning se detecta escrita sem validacao previa
- CICLO 4: `compliance.report` executa nc-validate em batch
