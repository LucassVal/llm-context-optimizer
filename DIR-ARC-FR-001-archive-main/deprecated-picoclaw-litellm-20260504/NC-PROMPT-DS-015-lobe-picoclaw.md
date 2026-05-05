# NC-PROMPT-DS-015-lobe-picoclaw.md
# Ticket: LOBE-INT-001 | Agente: A (porta 59520)
# Criado: 2026-04-13 | Por: T0 Antigravity
# Objetivo: Criar lobe de documentao extensa do PicoClaw

##  ROLE
Voc  um agente especialista em pesquisa e documentao tcnica no NeoCortex.
Raiz: C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\

##  CONTEXTO
O NeoCortex vai integrar o PicoClaw como orquestrador de agentes.
Voc deve pesquisar a fundo a documentao do PicoClaw e criar um lobe extenso
que sirva como referncia permanente para T0 (Antigravity) e outros agentes.

##  STEP-0 (R21  antes de entregar)
```bash
python --version
python -m py_compile <arquivo>.py  # se criar scripts auxiliares
```
> Para .mdc no h py_compile  basta garantir YAML frontmatter vlido.

##  @LOCKS  NUNCA TOQUE
- server.py | sub_server.py | neocortex_config.yaml | NC-NAM-FR-001

---

##  TAREFA: Criar NC-LBE-INT-001-picoclaw-architecture.mdc

### Onde criar
```
write_zone: 01_neocortex_framework/lobes/
arquivo:    NC-LBE-INT-001-picoclaw-architecture.mdc
```

### O que pesquisar (URLs obrigatrias  use curl ou fetch)
```
1. https://github.com/sipeed/picoclaw               README principal
2. https://raw.githubusercontent.com/sipeed/picoclaw/main/docs/tools_configuration.md
3. https://raw.githubusercontent.com/sipeed/picoclaw/main/ROADMAP.md
4. https://picoclaw.io                              site oficial
5. https://clawhub.ai                               marketplace de skills
```

### Tpicos OBRIGATRIOS no lobe (mnimo 400L)

```yaml
---
name: NC-LBE-INT-001-picoclaw-architecture
description: Documentao arquitetural completa do PicoClaw para integrao com NeoCortex
tags: [picoclaw, orchestration, gateway, mcp, integration, deepseek]
status: active
module: integration
---
```

**1. O que  PicoClaw**
- Framework Go ultra-leve (<10MB RAM, <1s boot)
- Repositrio: sipeed/picoclaw (26K+ stars)
- Verso atual e changelog relevante

**2. Arquitetura Interna**
- Gateway (porta 18790): endpoints /health, /ready, roteamento
- Providers LLM: DeepSeek, Claude, GPT, Ollama  como configurar
- EventBus: como funciona, integrao com MCP
- Sub-agents: spawn, spawn_status, delegao de tasks
- Hooks: como registrar hooks pr/ps execuo

**3. Ferramentas Nativas**
- exec tool: configurao, permisses, commandos bloqueados
- file I/O: leitura e escrita de arquivos
- web search: Brave, DuckDuckGo, Perplexity
- cron tool: como agendar tarefas recorrentes
- vision pipeline: imagens para LLM multimodal

**4. MCP  integrao com servidores externos**
- Transport types: stdio, sse, http
- Config por servidor (enabled, deferred, command, url)
- Tool Discovery (lazy loading com BM25)
- Como conectar NeoCortex MCP: stdio via `python -m neocortex.mcp.server`
- Como conectar OpenCode MCP: sse via `http://127.0.0.1:59520/sse`

**5. Skills  opencode-controller especificamente**
- O que so Skills (SKILL.md no workspace)
- ClawHub: marketplace de skills
- opencode-controller: como instalar, quais slash commands oferece
- Como criar skill customizada para NeoCortex

**6. Gateway como Orquestrador**
- picoclaw gateway: configurao completa
- Roteamento de mensagens
- Mltiplos agentes em paralelo
- Como T0 chama o gateway via HTTP POST

**7. Configurao Completa para NeoCortex**
```json
// config.json exemplo completo com:
// - provider DeepSeek
// - MCP: neocortex + opencode
// - exec tool habilitado
// - gateway porta 18790
// - skill opencode-controller
```

**8. Integrao Windows**
- Instalao no Windows (binary ou WSL)
- PATH, variveis de ambiente
- Execuo como servio em background

**9. Limitaes e Riscos**
- exec tool: riscos de segurana
- opencode-controller: skill comunitria (no oficial)
- Boot time em Windows
- Diferenas PicoClaw vs OpenClaw vs ClawHub

**10. Roadmap PicoClaw**
- Prximas features relevantes para NeoCortex
- Verses planejadas

---

##  HANDOFF
```yaml
# Salvar em: DIR-DS-002-audit-logs/LOBE-INT-001-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: LOBE-INT-001
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 59520
lines_added: 0
files_modified:
  - 01_neocortex_framework/lobes/NC-LBE-INT-001-picoclaw-architecture.mdc
summary: |
  Lobe criado com documentao completa do PicoClaw
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
