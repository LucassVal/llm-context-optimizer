# NC-PROMPT-DS-008  Auditoria Completa do Codebase: Zona B
# Gerado: 2026-04-13 | Para: Agente 2 (porta 44624)
# Cobertura: neocortex/mcp/tools/ (NC-TOOL-FR-001 a NC-TOOL-FR-020)

---

## MISSO: AUDITORIA E CORREO  ZONA B

Auditoria de qualidade dos tools MCP do NeoCortex. Validar, corrigir lint, verificar
padres R09 (importlib), R12 (register_tool). Sem criar cdigo novo.

**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\01_neocortex_framework\`

---

## STEP-0: VERIFICAR AMBIENTE

```powershell
python --version
python -m ruff --version 2>&1
```

---

## ZONA B  Arquivos a auditar

```
neocortex/mcp/tools/NC-TOOL-FR-000-brain.py
neocortex/mcp/tools/NC-TOOL-FR-001-checkpoint.py
neocortex/mcp/tools/NC-TOOL-FR-002-cortex.py
neocortex/mcp/tools/NC-TOOL-FR-003-lobes.py
neocortex/mcp/tools/NC-TOOL-FR-004-ledger.py
neocortex/mcp/tools/NC-TOOL-FR-005-manifest.py
neocortex/mcp/tools/NC-TOOL-FR-006-export.py
neocortex/mcp/tools/NC-TOOL-FR-007-init.py
neocortex/mcp/tools/NC-TOOL-FR-008-config.py
neocortex/mcp/tools/NC-TOOL-FR-009-search.py
neocortex/mcp/tools/NC-TOOL-FR-010-regression.py
neocortex/mcp/tools/NC-TOOL-FR-011-security.py
neocortex/mcp/tools/NC-TOOL-FR-012-governance.py
neocortex/mcp/tools/NC-TOOL-FR-013-context.py
neocortex/mcp/tools/NC-TOOL-FR-014-agent.py
neocortex/mcp/tools/NC-TOOL-FR-015-task.py
neocortex/mcp/tools/NC-TOOL-FR-016-orchestration.py
neocortex/mcp/tools/NC-TOOL-FR-017-subserver.py
neocortex/mcp/tools/NC-TOOL-FR-018-savepoint.py
neocortex/mcp/tools/NC-TOOL-FR-019-peers.py
```

---

## PROTOCOLO DE AUDITORIA

Para CADA arquivo:

```powershell
python -m py_compile ARQUIVO.py        # OBRIGATRIO
python -m ruff check --fix ARQUIVO.py  # auto-fix lint
python -m ruff check ARQUIVO.py        # confirmar 0 erros
```

**Verificao especial para tools MCP:**
1. Buscar `import NC-`  deve usar `importlib.util.spec_from_file_location` (R09)
2. Verificar que `register_tool(server)` existe em cada arquivo (R12)
3. Verificar que `logger = logging.getLogger(__name__)` est presente (R11)
4. Verificar que no h `print()` em produo (apenas logging)

**NUNCA modificar:** `server.py`, `sub_server.py` (@LOCKS)

---

## HANDOFF OBRIGATRIO

```yaml
# DIR-DS-002-audit-logs/NC-AUDIT-ZONA-B-{YYYYMMDD-HHMMSS}.yaml
tipo: AUDITORIA
zona: B
ticket_ref: NC-AUDIT-001
timestamp: "{ISO8601}"
agent_port: 44624
files_audited: 20
files_with_errors_before: {N}
files_with_errors_after: {N aps fix}
r09_violations: [lista de arquivos com import NC- direto]
r11_violations: [lista de arquivos sem logger = logging.getLogger(__name__)]
r12_violations: [lista de arquivos sem register_tool(server)]
errors_fixed:
  - {file, type, description}
files_unfixable: []
summary: |
  {descrio do encontrado}
checklist:
  py_compile_all_pass: true/false
  ruff_all_pass: true/false
  r09_compliant: true/false
  no_locked_files_modified: true
  handoff_complete: true
```
