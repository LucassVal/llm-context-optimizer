# NC-PROMPT-DS-014-orch302-neocortex-task.md
# Ticket: ORCH-302 | Agente: C (porta 32763)
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

##  TICKET: ORCH-302  neocortex_task MCP Tool (HTTP + Polling Real)

### CONTEXTO
`neocortex_task`  a tool MCP que permite ao T0 (Antigravity/Claude) despachar tasks
para sub-servidores locais via HTTP e aguardar resultado  **sem usar stdio**.

Atualmente existe `NC-TOOL-FR-022-session.py` (session management).
ORCH-302 cria uma **nova tool dedicada**: `neocortex_task`.

### LEIA PRIMEIRO
```
01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-023-orchestration.py
```
A nova tool ser uma **extenso do neocortex_orchestration** focada em:
`task.execute`  `task.poll`  `task.cancel` com timeout real.

### O QUE FAZER
Criar nova tool MCP dedicada para task execution:

```
write_zone: 01_neocortex_framework/neocortex/mcp/tools/
arquivo:    NC-TOOL-FR-035-task.py
```

A tool `neocortex_task` deve ter as aes:

```python
# action = "execute"
# Envia task para sub-servidor e registra UUID no broker
# Parmetros: port, task_data (JSON str), timeout_seconds (default 30)
# Retorna: { task_id, status: "queued", endpoint }

# action = "poll"  
# Consulta status de task via GET /health ou resultado via GET /task/{id}
# Parmetros: task_id, port
# Retorna: { task_id, status: queued|running|done|failed, result? }

# action = "cancel"
# Cancela task pendente (marca no broker como "cancelled")
# Parmetros: task_id
# Retorna: { task_id, cancelled: bool }

# action = "list_queued"
# Lista tasks em fila para um port especfico
# Parmetros: port (opcional)
# Retorna: { tasks: [...] }
```

### IMPLEMENTAO
- Use apenas `urllib.request` (stdlib) para HTTP  SEM `requests`
- Para polling com timeout: loop com `time.sleep(1)` at timeout_seconds
- Broker de tasks: integrar com `NC-SVC-FR-015-task-broker.py` se disponvel
  - Fallback: dict em memria `_task_registry: Dict[str, Dict]`
- UUID para task_id: `import uuid; str(uuid.uuid4())[:8]`

### ENDPOINT DO SUB-SERVER (j implementado)
```
POST http://127.0.0.1:{port}/task    envia task, retorna JSON resultado
GET  http://127.0.0.1:{port}/health  status do processo
```

### NOTA SOBRE SSE
SSE (Server-Sent Events)  ideal para streaming de resultados mas requer
modificao do sub_server.py (@LOCKED). Por isso ORCH-302 usa **polling** como
alternativa vivel para a v1. SSE pode ser adicionado em fase futura (ORCH-303).

### ESFORO ESTIMADO
~200-250 linhas (tool completa com 4 aes + polling + fallback broker)

---

##  HANDOFF
```yaml
# Salvar em: DIR-DS-002-audit-logs/ORCH-302-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: ORCH-302
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 32763
lines_added: 0
files_modified:
  - 01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-035-task.py
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
