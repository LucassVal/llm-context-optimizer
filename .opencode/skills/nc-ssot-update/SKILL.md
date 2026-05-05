---
name: nc-ssot-update
description: Atualiza @SSOT (NC-NAM-FR-001) com changelog — registra arquivos criados/modificados com data [YYYY-MM-DD], tipo NC-, descricao. Tarefa sem update = INCOMPLETA (R02).
compatibility: opencode
metadata:
  tier: T0
  rule: R02
  category: ssot
  mcp_tools: [neocortex_governance.ssot.diff, neocortex_governance.naming.check]
---

## What I do
Via MCP:
```
neocortex_governance action=ssot.diff
neocortex_governance action=naming.check
```

### O que atualizar
1. Tabela de naming em NC-NAM-FR-001: novo arquivo → nova linha
2. Changelog: `[YYYY-MM-DD] NC-<TIPO>-<SIGLA>-<NUM> — <desc>` 
3. Tipos validos: TOOL, SCR, DOC, TODO, LBE, CFG, SEC, SOP, ARC, BAK, TST, BOOT, CORE, SUPER, SVC, UTL, HK

## When to use me
SEMPRE que criar ou modificar arquivo. R02: sem update = tarefa incompleta.

## Integration
- Hook: `lexico_post_tokenization` (PostToolUse) dispara sugestao de update
- Pipeline: criar arquivo → nc-validate → nc-ssot-update → nc-handoff → nc-boot-sync

