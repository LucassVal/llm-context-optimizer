# NC-PROMPT-DS-011  Agent Prompt: NC-DS-030 (SessionBuddy Stats)
# Verso: 1.0 | Data: 2026-04-13 | Template: Brockman v1
# Despachar para: Agente C (porta 32763)

---

##  GOAL

Expandir **NC-DS-030  SessionBuddy Stats (BUDDY-001)**.

O arquivo `NC-SVC-FR-009-session-buddy.py` J EXISTE em disco (12.695b).
Sua tarefa  **l-lo e expandir** com as funcionalidades faltantes:

1. Histrico persistente em `.nc/session_stats.json`
2. Sistema de conquistas/badges (3-5 iniciais)
3. Display com `rich` (tabela formatada de estatsticas)

Arquivo a MODIFICAR (no recriar):
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-009-session-buddy.py`

Confirme o estado atual:
```powershell
$f = "01_neocortex_framework\neocortex\core\services\NC-SVC-FR-009-session-buddy.py"
(Get-Content $f).Count   # ver quantas linhas atuais
Get-Content $f | Select-Object -First 30  # ver estrutura atual
```

@LOCKS ABSOLUTOS: NO modificar `server.py`, `sub_server.py`.

---

##  RETURN FORMAT

Handoff em `DIR-DS-002-audit-logs/NC-DS-030-handoff-{YYYYMMDD-HHMMSS}.yaml`:

```yaml
ticket_id: NC-DS-030
status: PENDING_REVIEW
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: 32763
lines_added: <N linhas adicionadas ao existente>
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-009-session-buddy.py
summary: |
  Expandido NC-SVC-FR-009: histrico JSON + badges + rich display.
ajustes_aplicados:
  - "rich para display com tabela formatada"
  - ".nc/session_stats.json para histrico entre sesses"
  - "3-5 badges iniciais implementados"
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

---

##  WARNINGS  STEP-0 OBRIGATRIO

```powershell
python --version
python -m ruff --version
python -c "
import importlib, sys
libs=['rich','cachetools','yaml','json']
for lib in libs:
    try: importlib.import_module(lib); print(f'OK  {lib}')
    except ImportError as e: print(f'ERR {lib}: {e}')
"
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py && python -m ruff check ARQUIVO.py
```

**R11:** NUNCA `print()`  `logger`. **ATENO:** Leia o arquivo existente antes de modificar.

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
Agent port: 32763 | Ticket: NC-DS-030
Zona: `01_neocortex_framework/neocortex/core/services/` (MODIFICAR existente)

Referncias:
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py`  integrar mtricas
- `05_examples/.nc/session_stats.json`  criar este arquivo de exemplo junto

---

## TAREFA  NC-DS-030: SessionBuddy Expand

**Ticket:** NC-DS-030
**Ao:** MODIFICAR arquivo existente NC-SVC-FR-009
**Esforo:** +100L ao existente

### Funcionalidades a adicionar:

**1. Histrico persistente** (`.nc/session_stats.json`):
```python
def save_session(self, session_data: Dict) -> None:
    """Persiste stats da sesso em .nc/session_stats.json (append)."""
    ...

def load_history(self, limit: int = 10) -> List[Dict]:
    """Carrega ltimas N sesses do histrico."""
    ...
```

**2. Badges/Conquistas:**
```python
BADGES = {
    "first_session": {"name": " First Time", "condition": "total_sessions == 1"},
    "century": {"name": " Century", "condition": "total_tokens >= 100_000"},
    "marathon": {"name": " Marathon", "condition": "session_duration_min >= 60"},
    "efficient": {"name": " Efficient", "condition": "tokens_saved_ratio >= 0.5"},
    "streak_3": {"name": " Streak 3", "condition": "consecutive_days >= 3"},
}

def check_badges(self, stats: Dict) -> List[str]:
    """Retorna lista de badges conquistados."""
    ...
```

**3. Display com rich:**
```python
def display_summary(self, stats: Dict) -> None:
    """Exibe tabela formatada com rich.Console."""
    # Tabela com: tokens usados, tokens economizados, durao, badges
    ...
```

**Restries:**
- `rich.console.Console()` para output (no `print()`)
- `.nc/` relativo ao `project_root` (usar `get_config()` para base path)
- JSON com append de sesses, no sobrescrever

---

## PROTOCOLO DE ENTREGA

1. STEP-0  confirmar ambiente
2. Ler NC-SVC-FR-009 atual completo antes de modificar
3. Adicionar as 3 funcionalidades sem quebrar API existente
4. py_compile + ruff 0 erros no arquivo final
5. Criar `05_examples/.nc/session_stats.json` (exemplo vazio)
6. Gerar handoff YAML em `DIR-DS-002-audit-logs/`
