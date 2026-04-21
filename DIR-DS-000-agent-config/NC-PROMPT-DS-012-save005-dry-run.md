# NC-PROMPT-DS-012-save-point-dry-run.md
# Ticket: SAVE-005 | Agente: A (porta 59520)
# Criado: 2026-04-13 | Por: T0 Antigravity

##  ROLE
Voc  um agente especialista Python operando no NeoCortex MCP Framework.
Raiz: C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\

##  CONTEXTO SSOT  Leia NESTA ORDEM antes de qualquer ao
1. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`  naming + changelog
2. `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`  @LOCKS (intocveis)
3. `DIR-BOOT-FR-001-bootup-main/NC-BOOT-FR-001-system-manifest.md`  estado atual
4. `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc`  STEP-0 + regression buffer

##  STEP-0 OBRIGATRIO (R21  antes de qualquer entrega)
```powershell
# Python
python --version
python -m py_compile SEU_ARQUIVO.py
python -m ruff check SEU_ARQUIVO.py
python -c "import SEU_MODULO"
```

##  @LOCKS  NUNCA TOQUE
- server.py | sub_server.py | neocortex_config.yaml | NC-NAM-FR-001

---

##  TICKET: SAVE-005  SavePoint Dry-Run Preview Middleware

### O QUE FAZER
Implementar middleware de **Dry-Run Preview** no sub-servidor MCP (`sub_server.py`).

O middleware SAVE-005 deve:
1. **Antes** de qualquer tool call que modifica estado: calcular DIFF do que ser alterado
2. **Exibir prvia** (dry-run) com: arquivos afetados, linhas alteradas, risco estimado
3. **Bloquear execuo** se risco for ALTO e no houver confirmao explcita
4. **No bloquear** sub_server.py diretamente  criar servio separado que  chamado

### ONDE IMPLEMENTAR
```
write_zone: 01_neocortex_framework/neocortex/core/services/
arquivo:    NC-SVC-FR-014-dry-run-preview.py
```

### ESPECIFICAO TCNICA
```python
# Interface esperada do servio
class DryRunPreviewService:
    def preview(self, action: str, target_path: str, content: str) -> DryRunResult:
        """
        Calcula diff entre contedo atual e novo.
        Retorna: { risk: low|medium|high, diff_lines: int, affected_files: list, preview: str }
        """

    def should_block(self, result: DryRunResult) -> bool:
        """
        Bloqueia se:
        - risk == 'high' (afeta @LOCKS)
        - diff_lines > 500 (mudana massiva)
        - Sem fallback disponvel
        """
```

### INTEGRAO
Aps criar o servio, criar tool wrapper em:
```
arquivo: 01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-034-dry-run.py
```
Registrar como `neocortex_dry_run` com action=`preview` e action=`check`.

### DEPENDNCIAS DISPONVEIS
- `difflib` (stdlib)  para calcular diffs
- `pathlib` (stdlib)  para paths
- `filelock` (instalado)  caso precise de locks temporrios

### REFERNCIAS
- `01_neocortex_framework/neocortex/mcp/sub_server.py` linhas 31-36  stubs SAVE-002/003 j existem
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-TODO-FR-001-project-roadmap-consolidated.md` linha 33  SAVE-005 no roadmap
- `01_neocortex_framework/lobes/NC-LBE-FR-QUALITY-001-env-quality.mdc`  STEP-0 completo

### ESFORO ESTIMADO
~150-200 linhas (servio) + ~80 linhas (tool wrapper) = ~230L total

---

##  HANDOFF  Preencher ao concluir
```yaml
# Salvar em: DIR-DS-002-audit-logs/NC-DS-SAVE005-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: SAVE-005
status: PENDING_REVIEW
timestamp: "YYYY-MM-DDTHH:MM:SS-03:00"
agent_port: 59520
lines_added: 0
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-014-dry-run-preview.py
  - 01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-034-dry-run.py
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
