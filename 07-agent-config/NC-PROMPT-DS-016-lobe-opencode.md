# NC-PROMPT-DS-016-lobe-opencode.md
# Ticket: LOBE-INT-002 | Agente: B (porta 44624)
# Criado: 2026-04-13 | Por: T0 Antigravity
# Objetivo: Criar lobe de documentao extensa do OpenCode

##  ROLE
Voc  um agente especialista em pesquisa e documentao tcnica no NeoCortex.
Raiz: C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\

##  CONTEXTO
O NeoCortex usa OpenCode (--port 59520/44624/32763) como agent layer de execuo.
Voc deve pesquisar toda a documentao do OpenCode e criar um lobe extenso
cobrindo a REST API, modo headless, TUI, MCP, configurao e integrao.

##  STEP-0 (R21)
```bash
python --version
```

##  @LOCKS  NUNCA TOQUE
- server.py | sub_server.py | neocortex_config.yaml | NC-NAM-FR-001

---

##  TAREFA: Criar NC-LBE-INT-002-opencode-architecture.mdc

### Onde criar
```
write_zone: 01_neocortex_framework/lobes/
arquivo:    NC-LBE-INT-002-opencode-architecture.mdc
```

### URLs para pesquisar (curl/fetch obrigatrio)
```
1. https://opencode.ai/docs                          intro + install
2. https://opencode.ai/docs/pt-br/tui/               TUI completo
3. https://opencode.ai/docs/mcp                      MCP config
4. https://opencode.ai/docs/headless                 API REST
5. https://github.com/opencode-ai/opencode           README + cdigo
6. https://opencode.ai/docs/configuration            opencode.json schema
7. https://opencode.ai/docs/keybinds                atalhos TUI
```

### Tpicos OBRIGATRIOS (mnimo 400L)

```yaml
---
name: NC-LBE-INT-002-opencode-architecture
description: Documentao arquitetural completa do OpenCode para integrao com NeoCortex
tags: [opencode, ide, rest-api, mcp, sessions, headless, tui, deepseek]
status: active
module: integration
---
```

**1. O que  OpenCode**
- Terminal AI coding assistant (Go CLI + TUI)
- Repositrio: opencode-ai/opencode
- Provider-agnostic: Claude, DeepSeek, GPT, Gemini

**2. Modos de Operao**
- TUI interativo: `opencode` (interface grfica terminal)
- Headless one-shot: `opencode run "prompt"` (sem TUI)
- Server mode: `opencode --port XXXX` (REST API + TUI)
- `opencode serve` (headless puro, sem TUI)

**3. REST API Completa (modo server)**
```
Base URL: http://127.0.0.1:PORT
GET  /session                     lista todas sesses
POST /session                     cria sesso {directory, ...}
GET  /session/:id                 detalhes de uma sesso
POST /session/:id/message         envia prompt, resposta via SSE
DELETE /session/:id               encerra sesso
GET  /session/:id/messages        histrico de mensagens
```
- SSE streaming: como parsear eventos
- SDK oficial @opencode-ai/sdk (TypeScript)
- Autenticao: OPENCODE_SERVER_PASSWORD

**4. TUI  Comandos Completos**
- `/connect`  adicionar provider
- `/models`  trocar modelo
- `/init`  inicializar contexto do projeto
- `/new`  nova sesso
- `/sessions`  listar sesses
- `/undo` `/redo`  desfazer changes
- `/share` `/unshare`  compartilhar sesso
- `/compact`  comprimir contexto
- `/thinking`  modo de raciocnio estendido
- `@arquivo`  referenciar arquivo no chat
- `!comando`  executar shell dentro do TUI
- Tecla lder: ctrl+x (configurvel)

**5. MCP  Configurao**
```json
// .opencode/opencode.json ou ~/.config/opencode/opencode.json
{
  "mcp": {
    "neocortex": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "neocortex.mcp.server"],
      "env": {"PYTHONPATH": "C:\\...\\TURBOQUANT_V42"}
    }
  }
}
```
- Suporte: stdio, sse, http
- Mltiplos servidores MCP simultneos

**6. Configurao Completa opencode.json**
- Schema completo com todos os campos
- Providers: como configurar DeepSeek (api_key, model, base_url)
- TUI: tema, editor, keybinds
- Autoshare, debug, log level

**7. Persistncia e Estado**
- SQLite para histrico de sesses
- Localizao dos dados (Windows: %APPDATA%)
- Como limpar/resetar estado
- session_stats.json

**8. Integrao com PicoClaw**
- opencode-controller skill: o que faz
- `opencode run` chamado pelo PicoClaw exec tool
- Como passar contexto de arquivos via @referencias

**9. Integrao com NeoCortex**
- NeoCortex como MCP server no opencode.json
- Configurao nos 3 agentes ativos (59520/44624/32763)
- Como T0 despacha task via POST /session/:id/message
- SSE parser para coletar resultado

**10. Limitaes e Edge Cases**
- Max tokens por sesso
- Timeout de sesses inativas
- Behavior quando LLM provider cai
- Windows: path escaping em --port e configs

---

##  HANDOFF
```yaml
ticket_id: LOBE-INT-002
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 44624
lines_added: 0
files_modified:
  - 01_neocortex_framework/lobes/NC-LBE-INT-002-opencode-architecture.mdc
summary: |
  Lobe criado com documentao completa do OpenCode
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
