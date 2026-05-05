---
name: nc-handoff
description: Gera handoff YAML no padrao NC-DS-{TICKET}-handoff-{TIMESTAMP}.yaml em DIR-DS-002-audit-logs/. Campos: ticket_id, status, summary, files_created, files_modified, locks_violated, checklist_r20.
compatibility: opencode
metadata:
  tier: T0
  rule: R12
  category: governance
  mcp_tools: [neocortex_governance.handoff.create]
---

## What I do
Gero handoff YAML via MCP:
```
neocortex_governance action=handoff.create ticket_id=<TICKET> summary="<resumo>"
```

### Checklist R20 (validar antes de gerar)
- [ ] Todos arquivos seguem NC-<TIPO>-<SIGLA>-<NUM>
- [ ] Zero print() — usar logger
- [ ] @SSOT atualizado (se criou artefato novo)
- [ ] Nenhum @LOCKS violado
- [ ] @ROADMAP marcado %DONE

### Campos do handoff
- ticket_id, status, submitted_at, submitted_by, summary
- files_created, files_modified
- validation_rounds, barriers_passed, locks_violated
- t0_review

### Destino
`DIR-DS-002-audit-logs/NC-DS-{TICKET_ID}-handoff-{YYYYMMDDTHHMMSS}.yaml`

## When to use me
SEMPRE ao concluir tarefa. Sem handoff = INCOMPLETA (R02).

## Integration
- Hook: `lexico_post_tokenization` (PostToolUse) dispara lembrete de handoff
- Pipeline: nc-validate → nc-ssot-update → nc-handoff → nc-boot-sync
