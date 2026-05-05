---
name: nc-lint
description: Verificacao rapida — ruff check + ruff format + mypy + pyright em .py modificados. Uso durante desenvolvimento ativo. Complementa nc-validate (mais completo).
compatibility: opencode
metadata:
  tier: T1
  rule: R6
  category: lint
  mcp_tools: [neocortex_governance.naming.check]
---

## What I do
Via Bash (rapido, por arquivo):
```bash
python -m ruff check --fix <file>
python -m ruff format <file>
python -m ruff check <file>
python -m mypy <file> --ignore-missing-imports
```

Pyright: passivo via LSP (ja configurado no opencode.json).

## When to use me
Durante desenvolvimento ativo. Para validacao completa use `nc-validate`.

## Integration
- LSP pyright: diagnostico em tempo real (salvo automatico)
- Hook: nao bloqueia — apenas informativo
