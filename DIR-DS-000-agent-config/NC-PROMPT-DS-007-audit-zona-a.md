# NC-PROMPT-DS-007  Auditoria Completa do Codebase: Zona A
# Gerado: 2026-04-13 | Para: Agente 1 (porta 59520)
# Cobertura: neocortex/core/ + neocortex/mcp/tools/ (primeiros 40 arquivos)

---

## MISSO: AUDITORIA E CORREO  ZONA A

Voc  um agente de qualidade. Sua misso  auditar, corrigir e reportar os arquivos
Python da Zona A do projeto NeoCortex. Sem inventar cdigo novo  apenas validar e corrigir.

**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\01_neocortex_framework\`

---

## STEP-0: VERIFICAR AMBIENTE

```powershell
python --version
python -m ruff --version 2>&1
python -m bandit --version 2>&1
```

Cole os resultados no handoff campo `environment:`.

---

## ZONA A  Arquivos a auditar

```
neocortex/__init__.py
neocortex/config.py
neocortex/core/__init__.py
neocortex/core/config/NC-CFG-FR-001-base.py
neocortex/core/config/NC-CFG-FR-002-feature-flags.py
neocortex/core/config/NC-CFG-FR-003-env-validator.py
neocortex/core/config/NC-CFG-FR-004-project-loader.py
neocortex/core/hooks/NC-HK-FR-001-hook-registry.py
neocortex/core/review/NC-REV-FR-001-confidence-review.py
neocortex/core/services/NC-SVC-FR-001-logging-service.py
neocortex/core/services/NC-SVC-FR-003-save-point.py
neocortex/core/services/NC-SVC-FR-004-cache-service.py
neocortex/core/services/NC-SVC-FR-005-event-bus.py
neocortex/core/services/NC-SVC-FR-009-session-buddy.py
neocortex/core/services/NC-SVC-FR-010-coordinator.py
neocortex/core/services/NC-SVC-FR-011-ttl-manager.py
neocortex/core/utils/NC-UTL-FR-001-yaml-safe-parser.py
neocortex/core/utils/NC-UTL-FR-002-hash-utils.py
neocortex/core/utils/NC-UTL-FR-004-id-validator.py
neocortex/logging_config.py
```

---

## PROTOCOLO DE AUDITORIA (por arquivo)

Para CADA arquivo:

```powershell
# 1. Compile
python -m py_compile ARQUIVO.py
# Se falhar: CORRIJA o erro de sintaxe antes de avanar

# 2. Ruff lint + auto-fix
python -m ruff check --fix ARQUIVO.py
python -m ruff check ARQUIVO.py  # verificar se passou

# 3. Verificar imports de mdulos com hfen (R09)
# Buscar: import NC-  -> ERR se existir fora de importlib.util
# Correto: importlib.util.spec_from_file_location(...)
```

**Regras de correo:**
- F401 (import no usado): remover import
- E401 (mltiplos imports): separar em linhas
- I001 (imports no ordenados): `ruff check --fix` resolve
- Erros de sintaxe: corrigir manualmente e testar
- NUNCA modificar `server.py`, `sub_server.py` (@LOCKS)
- NUNCA remover lgica existente  apenas corrigir imports/lint

---

## HANDOFF OBRIGATRIO

```yaml
# DIR-DS-002-audit-logs/NC-AUDIT-ZONA-A-{YYYYMMDD-HHMMSS}.yaml
tipo: AUDITORIA
zona: A
ticket_ref: NC-AUDIT-001
timestamp: "{ISO8601}"
agent_port: 59520
environment:
  python: "{python --version}"
  ruff: "{ruff --version}"
  bandit: "{bandit --version}"
files_audited: 20
files_with_errors_before: {N}
files_with_errors_after: 0  # meta
errors_fixed:
  - file: "nome_arquivo.py"
    type: "F401/I001/E401/SYNTAX"
    description: "descrio"
files_ok: [lista dos que passaram sem mudana]
files_fixed: [lista dos que foram corrigidos]
files_unfixable: [lista dos que precisam de interveno manual]
summary: |
  {1-3 linhas descrevendo o que foi encontrado e corrigido}
checklist:
  py_compile_all_pass: true/false
  ruff_all_pass: true/false
  no_locked_files_modified: true
  handoff_complete: true
```
