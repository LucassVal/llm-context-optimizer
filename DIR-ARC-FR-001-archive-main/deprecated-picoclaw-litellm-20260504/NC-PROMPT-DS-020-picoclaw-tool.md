# NC-PROMPT-DS-020  PIC-003: NC-TOOL-FR-036-picoclaw.py  Bridge T0PicoClaw
<!-- Agente: C | Porta: 32763 | Ticket: PIC-003 | Data: 2026-04-13 -->

## GOAL
Implemente a ferramenta MCP `neocortex_picoclaw` (NC-TOOL-FR-036) que permite ao T0 (Antigravity) chamar o gateway PicoClaw via HTTP POST. A ferramenta deve ter 3 aes: `task.send`, `gateway.health`, `gateway.status`.

## STEP-0 (OBRIGATRIO  execute primeiro)
```powershell
python --version
python -m ruff --version
python -c "import urllib.request; print('urllib OK')"
python -m py_compile "01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-035-task.py"
```
Reporte exatamente o que retornou. Se falhar, pare.

## LOCKS (@LOCKS  NO TOQUE)
- server.py, sub_server.py, neocortex_config.yaml, NC-NAM-FR-001

## WRITE ZONE (EXCLUSIVA)
- `01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-036-picoclaw.py`  NOVO

## CONTEXTO
- Leia PRIMEIRO: NC-LBE-INT-001-picoclaw-architecture.mdc (Seo 6  Gateway como Orquestrador)
- Leia PRIMEIRO: NC-LBE-INT-003-antigravity-integration.mdc (Seo 7  Integrao T0PicoClaw)
- Gateway PicoClaw: `http://127.0.0.1:18790`
- Endpoint de mensagem: `POST /message` com payload JSON
- Endpoint de health: `GET /health`
- Ferramenta similar de referncia: `NC-TOOL-FR-035-task.py` (leia como modelo de estrutura)
- Padro de registro: `register_tool(mcp)` + `TOOL_MODULE_MAP` entry

## INTERFACE DA FERRAMENTA

### Ao `gateway.health`
- Mtodo: GET http://127.0.0.1:18790/health
- Retorna: `{"status": "ok", "port": 18790}` ou erro com mensagem clara
- Timeout: 5 segundos

### Ao `gateway.status`
- Mtodo: GET http://127.0.0.1:18790/ready (fallback: /health)
- Retorna: status de prontido do gateway com timestamp

### Ao `task.send`
- Parmetros:
  - `task` (str, obrigatrio): descrio da tarefa a enviar
  - `context` (str, opcional): contexto adicional dos lobos
  - `session_id` (str, opcional): ID da sesso, gera uuid4 se vazio
  - `timeout_sec` (int, default=60): timeout da requisio
- Mtodo: POST http://127.0.0.1:18790/message
- Payload:
```json
{
  "channel": "mcp",
  "user": "T0-Antigravity",
  "text": "<task> \n\nCONTEXTO:\n<context>",
  "metadata": {
    "session_id": "<session_id>",
    "agent_id": "T0-Antigravity",
    "source": "neocortex_mcp"
  }
}
```
- Retorna: resposta do PicoClaw ou erro detalhado

## REQUISITOS TCNICOS
1. Use APENAS `urllib.request` e `json` (stdlib)  sem dependncias externas
2. ZERO `print()` em produo  use `logging.getLogger(__name__)`
3. Tratar timeout (`urllib.error.URLError`) com mensagem de erro clara
4. Tratar gateway offline (ConnectionRefusedError) separadamente
5. Mnimo 80 linhas de contedo real
6. `register_tool(mcp)` com FastMCP pattern igual aos outros tools

## VALIDAO OBRIGATRIA
```powershell
python -m py_compile "01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-036-picoclaw.py"
python -m ruff check "01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-036-picoclaw.py"
python -c "import ast; ast.parse(open('01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-036-picoclaw.py').read()); print('AST OK')"
```
Todos devem retornar zero erros. Inclua output no handoff.

## HANDOFF TEMPLATE
```yaml
ticket_id: PIC-003
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 32763
lines_added: 0   # preencha com contagem real
files_modified:
  - 01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-036-picoclaw.py
summary: |
  NC-TOOL-FR-036 implementada: neocortex_picoclaw com 3 aes (task.send, gateway.health,
  gateway.status). HTTP via urllib stdlib. Sem dependncias externas.
metrics:
  ruff_check: PASS
  py_compile: PASS
  import_smoke_test: PASS
  ruff_violations_found: 0
  write_zone_respected: true
  locks_respected: true
  min_80_lines: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  handoff_yaml_complete: true
```

Salve em: `DIR-DS-002-audit-logs/PIC-003-handoff-{YYYYMMDD-HHMMSS}.yaml`
