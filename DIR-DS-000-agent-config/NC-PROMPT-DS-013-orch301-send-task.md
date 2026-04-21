# NC-PROMPT-DS-013-orch301-send-task.md
# Ticket: ORCH-301 | Agente: B (porta 44624)
# Criado: 2026-04-13 | Por: T0 Antigravity

##  ROLE
Voc  um agente especialista Python operando no NeoCortex MCP Framework.
Raiz: C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\

##  CONTEXTO SSOT  Leia NESTA ORDEM
1. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
2. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`
3. `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`
4. `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc`

##  STEP-0 OBRIGATRIO (R21)
```bash
python --version
python -m py_compile SEU_ARQUIVO.py
python -m ruff check SEU_ARQUIVO.py
```

##  @LOCKS  NUNCA TOQUE
- server.py | sub_server.py | neocortex_config.yaml | NC-NAM-FR-001

---

##  TICKET: ORCH-301  send_task() HTTP Real com Retry + Queue

### CONTEXTO
O arquivo `NC-TOOL-FR-023-orchestration.py` (327L) J EXISTE com `_send_task()` via HTTP.
Porm o `task.get_result` retorna simulao (`{"simulated": True}`).
ORCH-301  sobre completar o ciclo: **send  track  retrieve resultado real**.

### LEIA PRIMEIRO
```
01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-023-orchestration.py
```
Especialmente:
- `_send_task()` (linhas 137-176)  HTTP POST /task  J FUNCIONA
- `task.get_result` (linhas 288-299)  STUB SIMULADO  precisa ser real
- `_active_subservers` dict (linha 53)  in-memory registry

### O QUE FAZER
Criar servio de task tracking persistente:

```
write_zone: 01_neocortex_framework/neocortex/core/services/
arquivo:    NC-SVC-FR-015-task-broker.py
```

O `TaskBroker` deve:
1. **Registrar tasks** enviadas via `_send_task()` com UUID nico
2. **Persistir estado** em `{config.data_dir}/task_queue.json` (no em memria)
3. **Polling de resultado**: GET `/task/{task_id}` no sub-server
4. **Retry automtico**: 3 tentativas com backoff 2s  4s  8s
5. **Status tracking**: `queued | running | done | failed | timeout`

### INTEGRAO
Aps criar o servio, atualizar NC-TOOL-FR-023-orchestration.py:
- `task.execute`  registrar task no broker antes de enviar
- `task.get_result`  consultar broker em vez de retornar simulado

>  NC-TOOL-FR-023 pode ser modificado  ele NO est em @LOCKS.

### INTERFACE DO /task ENDPOINT (sub_server)
O sub_server j expe `/task` via POST. A resposta  JSON com resultado da execuo.
Para polling, o sub_server expe `/health` (GET) com status do processo.

Use `urllib.request` (j importado em NC-TOOL-FR-023)  sem `requests` lib.

### ESFORO ESTIMADO
~180L (TaskBroker) + ~40L (atualizar NC-TOOL-FR-023 task.get_result) = ~220L

---

##  HANDOFF
```yaml
# Salvar em: DIR-DS-002-audit-logs/ORCH-301-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: ORCH-301
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 44624
lines_added: 0
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-015-task-broker.py
  - 01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-023-orchestration.py
summary: |
  Descreva o que foi implementado
ajustes_aplicados: []
lessons_learned: []
deps_missing: []
ruff_violations_found: 0
metrics:
  ruff_check: PASS
  py_compile: PASS
  import_smoke_test: PASS
  write_zone_respected: true
  locks_respected: true
  min_80_lines: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  ajustes_synthesis_applied: true
  handoff_yaml_complete: true
```
