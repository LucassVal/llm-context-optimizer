# NC-PROMPT-DS-004  Agent Prompt: NC-DS-035 + NC-DS-039
# Gerado: 2026-04-13 | Sprint Pr-MCP Fase 2 | Template: Brockman v1
# Despachar para: 1 agente opencode livre

---

##  GOAL

Implementar **2 servios Python** no projeto NeoCortex:
- **NC-DS-035:** `NC-SVC-FR-010-kairos-service.py`  KairosService event-driven wrapper do pulse_scheduler
- **NC-DS-039:** `NC-SVC-FR-012-channel-notifier.py`  ChannelNotifier com feature flag KAIROS_CHANNELS

Zona de escrita: `01_neocortex_framework/neocortex/core/services/`
Restrio: NO modificar `server.py`, `sub_server.py`, `pulse_scheduler.py` (@LOCKS).

---

##  RETURN FORMAT

Ao concluir, produzir **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:
- `NC-DS-035-handoff-{YYYYMMDD-HHMMSS}.yaml`
- `NC-DS-039-handoff-{YYYYMMDD-HHMMSS}.yaml`

Cada YAML deve conter obrigatoriamente:
- `ticket_id` | `status: PENDING_REVIEW` | `timestamp` (ISO8601)
- `agent_port` | `lines_added` (real) | `files_modified` (lista)
- `summary` (1-3 linhas do que foi implementado)
- `metrics.ruff_check: PASS` | `metrics.py_compile: PASS`
- `checklist_r20` completo (todos os campos true)

---

##  WARNINGS

Execute o **STEP-0 ABAIXO antes de qualquer cdigo** e reporte o resultado no handoff.
Verificar:
- [ ] `python --version`  3.12.x confirmado?
- [ ] `python -m ruff --version`  disponvel?
- [ ] Todas as 12 deps importadas sem erro?
- [ ] `py_compile` passou em CADA arquivo antes de entregar?
- [ ] Ruff com 0 erros aps `--fix`?

Evitar:
- `print()` em qualquer lugar  usar `logger = logging.getLogger(__name__)`
- Hardcode de paths  usar `get_config()`
- Import direto de mdulos com hfen  usar `importlib.util.spec_from_file_location` (R09)
- Modificar qualquer @LOCK
- Arquivos abaixo de 80 linhas de cdigo real

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT ativo: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Regras de governana: `.agents/rules/neocortexrules.md` (R21  a regra mais crtica)
EventBus existente: `NC-SVC-FR-005-event-bus.py` (163L)  integrar sem reescrever
PulseScheduler: `pulse_scheduler.py`  manter compatibilidade, no substituir
Sprint contexto: Pr-MCP Fase 2  servios de infraestrutura antes de conectar MCP

---

## STEP-0 OBRIGATRIO  EXECUTE ANTES DE QUALQUER CDIGO (v2.0)

```powershell
# 1. Python disponvel?
python --version   # esperado: 3.12.x

# 2. Ferramentas de qualidade disponveis?
python -m ruff --version 2>&1
python -m pytest --version 2>&1

# 3. Dependncias do projeto instaladas? (ground truth 2026-04-13)
python -c "
deps = ['mcp','fastmcp','ruamel','rich','cachetools','platformdirs',
        'notifypy','diskcache','duckdb','msgspec','psutil','yaml']
import importlib
for d in deps:
    try: importlib.import_module(d); print(f'OK  {d}')
    except ImportError as e: print(f'ERR {d}: {e}')
"

# 4. Aps criar/modificar cada arquivo:
python -m py_compile ARQUIVO.py                  # sintaxe OK?
python -m ruff check --fix ARQUIVO.py            # lint + auto-fix
python -m ruff check ARQUIVO.py                  # confirmar 0 erros
```

**REGRA R21:** Se py_compile falhar  PARE. Se dep faltar  instale antes de avanar.
**NUNCA assuma** que ruff/deps esto disponveis sem verificar. Consulte: `NC-RULE-006-no-assumptions.mdc`.

---

## CONTEXTO OBRIGATRIO  LEIA PRIMEIRO

Voc est no projeto NeoCortex em:
`C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`

**Arquivos de referncia  leia antes de codificar:**
- `DIR-RES-CC-001-claude-leak-workzone\NC-ANA-INT-001-synthesis-t0.md`  @SYNTHESIS CP-001 a CP-006
- `01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py`  EventBus existente
- `01_neocortex_framework\neocortex\core\pulse_scheduler.py`  Pulse atual (manter compatibilidade)

**Regras absolutas:**
- NUNCA modificar: `server.py`, `sub_server.py` (@LOCKS)
- Nomes de arquivo: padro `NC-TIPO-SIGLA-NUM-desc.py`
- Logger: `logger = logging.getLogger(__name__)`  nunca `print()`
- Mdulos com hfen: usar `importlib.util.spec_from_file_location` (R09)
- Mnimo: 80L de cdigo real por arquivo

---

## TAREFA A  NC-DS-035: KairosService (Event-driven Pulse)

**Ticket:** NC-DS-035
**Arquivo a criar:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-010-kairos-service.py`
**Esforo:** ~200L

### O que implementar:

```python
# KairosService  refatorao event-driven do pulse_scheduler
# No substituir pulse_scheduler.py  criar como wrapper/extenso

class KairosService:
    """ServioEvent-driven para scheduling de tarefas NeoCortex.
    
    Integra com EventBus (NC-SVC-FR-005) para publicar eventos de tick.
    Mantm compatibilidade com pulse_scheduler.py existente.
    """
    
    # Feature flags via env var:
    # KAIROS_PUSH_NOTIFICATION  habilita notificaes
    # KAIROS_CHANNELS  habilita channel notifier
    
    # Eventos publicados (nomes obrigatrios):
    # "kairos.tick"     a cada ciclo do scheduler
    # "kairos.started"  ao iniciar
    # "kairos.stopped"  ao parar
    # "kairos.task_scheduled"  quando tarefa  agendada
    # "kairos.task_executed"   quando tarefa  executada
    
    def schedule(self, task_name: str, fn: Callable, interval_s: int) -> str: ...
    def cancel(self, task_id: str) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def list_tasks(self) -> List[Dict]: ...
    def get_next_tick(self, task_id: str) -> Optional[float]: ...
```

**Restries tcnicas:**
- Usar `threading.Timer` ou `sched.scheduler` (stdlib  sem deps externas)
- Thread daemon = True para no bloquear shutdown
- `threading.Lock` em todas as operaes de escrita no dicionrio de tasks
- Publicar eventos via EventBus usando `importlib.util.spec_from_file_location` (R09)
- Singleton com `get_kairos_service() -> KairosService`
- Compat: ao iniciar, ler tarefas do `pulse_scheduler.py` existente via duck-typing

---

## TAREFA B  NC-DS-039: ChannelNotifier (KAIROS_CHANNELS)

**Ticket:** NC-DS-039
**Arquivo a criar:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-012-channel-notifier.py`
**Esforo:** ~150L

### O que implementar:

```python
# ChannelNotifier  sistema de canais de notificao
# Feature flag: KAIROS_CHANNELS (env var, default=False)
# Integra com EventBus (NC-SVC-FR-005)

KAIROS_CHANNELS = os.getenv("KAIROS_CHANNELS", "false").lower() in ("true", "1", "yes")

class ChannelNotifier:
    """Roteador de notificaes por canal.
    
    Canais disponveis: log, console, eventbus
    Extendvel via register_channel().
    """
    
    def notify(self, channel: str, message: str, level: str = "info",
               metadata: Dict = None) -> Dict: ...
    def register_channel(self, name: str, handler: Callable) -> None: ...
    def list_channels(self) -> List[str]: ...
    
    # Fallback gracioso: se KAIROS_CHANNELS=False, apenas loga
    # Canais padro (sempre registrados):
    #   "log"      logger.info/warning/error por level
    #   "console"  print colorido via rich (se disponvel) ou print simples
    #   "eventbus" publica evento "channel.notification" no EventBus
```

**Restries tcnicas:**
- `rich`  opcional: `try: from rich.console import Console` com fallback para `print()`
- EventBus via `importlib.util.spec_from_file_location` (R09)
- Singleton `get_channel_notifier() -> ChannelNotifier`
- ImportError fallback para TUDO externo

---

## PROTOCOLO DE ENTREGA

Ao concluir AMBAS as tarefas, gere TWO handoff YAMLs separados:

```yaml
# DIR-DS-002-audit-logs/NC-DS-035-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-035
status: PENDING_REVIEW
timestamp: "{ISO8601 com timezone}"
agent_port: {sua porta}
lines_added: {total real}
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-010-kairos-service.py
summary: |
  {1-3 linhas descrevendo o que foi implementado}
ajustes_aplicados:
  - {cada ajuste da @SYNTHESIS que aplicou}
metrics:
  lines_real: {linhas de cdigo}
  files_created: 1
  dependencies_used: [] # apenas stdlib
  write_zone_respected: true
  locks_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  min_80_lines: true
  no_locked_files_modified: true
  ajustes_synthesis_applied: true
  handoff_yaml_complete: true
```

```yaml
# DIR-DS-002-audit-logs/NC-DS-039-handoff-{YYYYMMDD-HHMMSS}.yaml
# (mesmos campos, ticket_id: NC-DS-039, files_modified: NC-SVC-FR-012)
```

