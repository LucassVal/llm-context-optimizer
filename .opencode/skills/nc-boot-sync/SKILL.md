---
name: nc-boot-sync
description: Sincroniza @BOOT (NC-BOOT-FR-001) — atualiza frentes, tickets, estado construido, caminho critico, versao. Executar como ultimo passo de sprint.
compatibility: opencode
metadata:
  tier: T0
  rule: R16
  category: boot
  mcp_tools: [neocortex_governance.bootup.sync, neocortex_governance.catalog.refresh]
---

## What I do
Sincronizacao do boot manifest via MCP:
```
neocortex_governance action=bootup.sync
neocortex_governance action=catalog.refresh
```

### Atualizacoes manuais necessarias
1. Secao 6 (frentes operacionais) — adicionar NC-DS-* concluidos
2. Secao 7 (estado construido) — servicos, tools, hooks novos
3. Secao 8 (caminho critico) — fase atual, proximo passo
4. Hash e versao: v7 | 2026-05-03
5. Regerar `artifact_catalog.json` via NC-SCR-FR-064

## When to use me
- Fim de sprint
- Apos criar/modificar tickets
- Apos adicionar servicos/core/tools
- Ciclo 3 (encerramento de sessao)

## Integration
- Pipeline: nc-handoff → nc-boot-sync (ordem fixa)
- CICLO 3: executado automaticamente no encerramento de sessao
