# NC-PROMPT-DS-017-lobe-antigravity.md
# Ticket: LOBE-INT-003 | Agente: C (porta 32763)
# Criado: 2026-04-13 | Por: T0 Antigravity
# Objetivo: Criar lobe sobre Antigravity (T0) + NeoCortex como orquestrador

##  ROLE
Voc  um agente especialista em pesquisa e documentao tcnica no NeoCortex.
Raiz: C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\

##  CONTEXTO
Antigravity  o T0 (nvel mximo de inteligncia) do NeoCortex  o modelo Claude/DeepSeek
que orquestra todos os agentes. Voc deve documentar: quem  o T0, quais so suas
capacidades reais, como ele se integra com PicoClaw e OpenCode, e como os outros
agentes devem interagir com ele via NeoCortex MCP.

##  STEP-0 (R21)
```bash
python --version
```

##  @LOCKS  NUNCA TOQUE
- server.py | sub_server.py | neocortex_config.yaml | NC-NAM-FR-001

---

##  TAREFA: Criar NC-LBE-INT-003-antigravity-integration.mdc

### Onde criar
```
write_zone: 01_neocortex_framework/lobes/
arquivo:    NC-LBE-INT-003-antigravity-integration.mdc
```

### Arquivos OBRIGATRIOS para ler antes (j existentes no projeto)
```
1. DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md
2. 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md (resumo)
3. 01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md
4. DIR-DS-000-agent-config/NC-CFG-DS-005-step0-environment.md
5. NC-PROMPT-FR-001-master-context.md (raiz do projeto)
6. 01_neocortex_framework/neocortex/mcp/server.py (linhas 1-80)
7. 01_neocortex_framework/neocortex/mcp/sub_server.py (linhas 1-80)
8. integration_strategy.md (se disponvel em artifacts)
```

### URLs para pesquisar (para documentar capacidades Antigravity)
```
1. https://deepmind.google/technologies/gemini/  sobre o modelo base
2. https://docs.anthropic.com/en/docs/about-claude  capacidades Claude
3. https://modelcontextprotocol.io/docs            MCP spec completo
4. https://github.com/opencode-ai/opencode         como opencode v T0
```

### Tpicos OBRIGATRIOS (mnimo 400L)

```yaml
---
name: NC-LBE-INT-003-antigravity-integration
description: Documentao do papel de T0 (Antigravity) como orquestrador e sua integrao com PicoClaw/OpenCode/NeoCortex
tags: [antigravity, t0, orchestration, mcp, picoclaw, opencode, neocortex, deepseek]
status: active
module: integration
---
```

**1. Quem  Antigravity (T0)**
- Claude/Gemini atuando como T0 no NeoCortex
- Papel: orquestrador central  nunca executa trabalho braal
- Acesso via MCP server.py (stdio) com 34 tools e 12 services
- Capacidades: leitura de arquivos, busca web, terminal, browser

**2. Hierarquia de Agentes no NeoCortex**
```
T0: Antigravity (Claude/DeepSeek)  orquestra, valida, decide
T1: OpenCode agents (A/B/C)  DeepSeek via OpenCode IDE tools
T2: PicoClaw  DeepSeek via gateway, sub-agents, automao
T3: Scripts autnomos  Python puro, sem LLM
```

**3. Ferramentas MCP disponveis para T0**
Documentar todas as 34 tools do NeoCortex:
- neocortex_memory (lobe management)
- neocortex_session (checkpoint, savepoint, ledger)
- neocortex_orchestration (spawn, task.execute)
- neocortex_governance (policy, audit, compliance)
- neocortex_intelligence (brain.think, brain.plan)
- neocortex_health (server status, logs)
- neocortex_task (execute, poll, cancel)
- [listar todas do server.py TOOL_MODULE_MAP]

**4. Como T0 Delega Tasks**
- Via prompt manual  OpenCode TUI (atual)
- Via `neocortex_orchestration action=task.execute`  HTTP sub_server
- Via PicoClaw gateway POST :18790 (futuro)
- Ciclo: dispatch  poll  receber handoff.yaml  validar  %DONE

**5. Protocolo de Comunicao T0  Agentes**
- Formato de handoff: YAML em DIR-DS-002-audit-logs/
- STEP-0 que T0 exige: py_compile, ruff, import_smoke
- STEP-0 que T0 executa: Parser::ParseFile para .ps1
- Checklist R20 que T0 valida ao receber handoff

**6. Como T0 Usa o NeoCortex MCP**
- server.py: ponto de entrada stdio para Claude/OpenCode
- sub_server.py: instncias isoladas por role + HTTP
- neocortex_config.yaml: configuraes globais
- Lobes: memria persistente entre sesses
- Cortex: ndice central do sistema

**7. Integrao T0  PicoClaw**
- T0 chama gateway :18790 via neocortex_picoclaw tool (NC-TOOL-FR-036)
- Payload: JSON com task, contexto, tools permitidas
- PicoClaw responde com resultado + logs
- T0 valida resultado antes de %DONE

**8. Integrao T0  OpenCode**
- T0 chama POST /session/:id/message via neocortex_task
- Aguarda SSE stream com resultado
- Extrai handoff.yaml gerado pelo agente
- Valida py_compile + ruff antes de aprovar

**9. Prompt Engineering para Agentes**
- Estrutura dos prompts NC-PROMPT-DS-XXX
- O que DEVE conter: SSOT, @LOCKS, STEP-0, write_zone, handoff template
- O que NO deve conter: instrues vagas, sem ticket, sem handoff
- Templates em DIR-DS-000-agent-config/

**10. Limitaes de T0**
- Context window: gerenciamento via compact + lobes
- Amnsia entre sesses: mitigada pelo NC-PROMPT-FR-001
- No executa cdigo diretamente  sempre delega
- R21: nunca assume, sempre verifica

**11. Roadmap Integrao (desta conversa)**
- FASE 1: PicoClaw install + NC-TOOL-FR-036 (esta semana)
- FASE 2: Arq 4  NeoCortex orquestra PicoClaw + OpenCode (sprint 3)
- Tickets cancelados: ORCH-301 TaskBroker, ORCH-302 SSE tool
- Tickets mantidos: SAVE-005 (segurana), LOBE-INT-001/002/003 (este sprint)

**12. Referncias Cruzadas**
- NC-LBE-INT-001-picoclaw-architecture.mdc
- NC-LBE-INT-002-opencode-architecture.mdc
- NC-PROMPT-FR-001-master-context.md
- NC-CFG-DS-005-step0-environment.md
- NC-TODO-FR-001-project-roadmap-consolidated.md

---

##  HANDOFF
```yaml
ticket_id: LOBE-INT-003
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 32763
lines_added: 0
files_modified:
  - 01_neocortex_framework/lobes/NC-LBE-INT-003-antigravity-integration.mdc
summary: |
  Lobe criado com documentao completa do papel de T0 e integrao
metrics:
  write_zone_respected: true
  locks_respected: true
  min_80_lines: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  handoff_yaml_complete: true
```
