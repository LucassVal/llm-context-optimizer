# NC-PROMPT-DS-009  Auditoria Completa do Codebase: Zona C
# Gerado: 2026-04-13 | Para: Agente 3 (porta 32763)
# Cobertura: mcp/tools NC-TOOL-FR-020 a FR-032 + scripts + DIR-MCP

---

## MISSO: AUDITORIA E CORREO  ZONA C

Auditoria dos tools MCP novos (FR-018 a FR-032), scripts e cdigo de suporte.
Prioridade: detectar erros de sintaxe, imports no usados, violaes de R09.

**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\01_neocortex_framework\`

---

## STEP-0: VERIFICAR AMBIENTE

```powershell
python --version
python -m ruff --version 2>&1
```

---

## ZONA C  Arquivos a auditar

```
neocortex/mcp/tools/NC-TOOL-FR-020-health.py
neocortex/mcp/tools/NC-TOOL-FR-021-agents.py
neocortex/mcp/tools/NC-TOOL-FR-022-session.py
neocortex/mcp/tools/NC-TOOL-FR-023-memory.py
neocortex/mcp/tools/NC-TOOL-FR-024-knowledge.py
neocortex/mcp/tools/NC-TOOL-FR-025-system.py
neocortex/mcp/tools/NC-TOOL-FR-026-intelligence.py
neocortex/mcp/tools/NC-TOOL-FR-027-benchmark.py
neocortex/mcp/tools/NC-TOOL-FR-028-report.py
neocortex/mcp/tools/NC-TOOL-FR-029-health.py
neocortex/mcp/tools/NC-TOOL-FR-030-context.py
neocortex/mcp/tools/NC-TOOL-FR-031-push-notification-OLD.py   verificar se existe, pode ser arquivo morto
neocortex/mcp/tools/NC-TOOL-FR-032-push-notification.py
DIR-MCP-FR-001-mcp-server/clean_utf0.py           KNOWN ERR: C401 set comprehension
scripts/NC-SCR-FR-001-populate-lobes-ssot.py
scripts/NC-SCR-FR-006-ticket-validator.py
scripts/NC-SCR-FR-007-queue-monitor.py
scripts/NC-SCR-FR-008-queue-repair.py
scripts/NC-SCR-FR-010-sync-queue.py
scripts/NC-SCR-FR-012-new-tool.py
scripts/NC-SCR-FR-013-validate-file.py
```

---

## PROTOCOLO DE AUDITORIA

```powershell
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py
python -m ruff check ARQUIVO.py
```

**Prioridade especial:**
- `DIR-MCP-FR-001-mcp-server/clean_utf0.py`: erro C401 conhecido (set comprehension)
   Corrigir `set(x for x in ...)` para `{x for x in ...}`
- Verificar se `NC-TOOL-FR-031-push-notification-OLD.py` existe  se sim, mover para DIR-ARC
- Para scripts (NC-SCR-FR-*): `print()`  PERMITIDO (T201 ignorado para scripts CLI)

**NUNCA modificar:** `server.py`, `sub_server.py` (@LOCKS)

---

## HANDOFF OBRIGATRIO

```yaml
# DIR-DS-002-audit-logs/NC-AUDIT-ZONA-C-{YYYYMMDD-HHMMSS}.yaml
tipo: AUDITORIA
zona: C
ticket_ref: NC-AUDIT-001
timestamp: "{ISO8601}"
agent_port: 32763
files_audited: {N verificados}
files_with_errors_before: {N}
files_with_errors_after: {N}
known_errors_fixed:
  - file: "DIR-MCP-FR-001-mcp-server/clean_utf0.py"
    type: C401
    fix: "set comprehension replacement"
dead_files_found: [arquivos mortos/duplicados encontrados]
errors_fixed:
  - {file, type, description}
files_unfixable: []
summary: |
  {descrio}
checklist:
  py_compile_all_pass: true/false
  ruff_all_pass: true/false
  dead_files_archived: true/false
  no_locked_files_modified: true
  handoff_complete: true
```
