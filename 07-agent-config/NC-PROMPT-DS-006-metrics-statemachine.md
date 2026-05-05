# NC-PROMPT-DS-006  Agent Prompt: NC-DS-022 + NC-DS-023
# Verso: 2.0 | Reescrito: 2026-04-13 11:52 | Template: Brockman v1
# MOTIVO DA REESCRITA: Agente anterior se perdeu  sem entrega detectada.
# Despachar para: 1 agente opencode livre (porta 32763 ou nova sesso)

---

##  GOAL

Implementar **2 servios de observabilidade Python**  do zero, com cdigo completo.
Ambos **NO EXISTEM ainda**  confirme antes de comear:

```powershell
Test-Path "01_neocortex_framework\neocortex\core\services\NC-SVC-FR-006-metrics-collector.py"
Test-Path "01_neocortex_framework\neocortex\core\services\NC-SVC-FR-007-finite-state-machine.py"
# Ambos devem retornar False  se retornarem True, leia o arquivo antes de substituir
```

**NC-DS-022 (PRIORIDADE HIGH):**
Arquivo: `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py`
Esforo: ~180 linhas

**NC-DS-023:**
Arquivo: `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-007-finite-state-machine.py`
Esforo: ~160 linhas

Zona de escrita: `01_neocortex_framework/neocortex/core/services/`
Restrio ABSOLUTA: NO modificar `server.py`, `sub_server.py` (@LOCKS).

---

##  RETURN FORMAT

Ao concluir AMBAS as tarefas, produzir **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:

```
NC-DS-022-handoff-{YYYYMMDD-HHMMSS}.yaml
NC-DS-023-handoff-{YYYYMMDD-HHMMSS}.yaml
```

Cada YAML DEVE conter exatamente estes campos:

```yaml
ticket_id: NC-DS-022
status: PENDING_REVIEW
timestamp: "2026-04-13T12:XX:XX-03:00"
agent_port: 32763
lines_added: <N real>
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py
summary: |
  <1-3 linhas do que foi implementado>
metrics:
  lines_real: <N>
  files_created: 1
  ruff_check: PASS
  py_compile: PASS
  dependencies_used: []
  write_zone_respected: true
  locks_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  min_80_lines: true
  no_locked_files_modified: true
  handoff_yaml_complete: true
```

---

##  WARNINGS  STEP-0 OBRIGATRIO

Execute **agora, antes de qualquer cdigo**:

```powershell
# 1. Python disponvel?
python --version   # esperado: 3.12.x

# 2. Ferramentas de qualidade?
python -m ruff --version
python -m pytest --version

# 3. Dependncias instaladas? (ground truth 2026-04-13)
python -c "
deps = ['mcp','fastmcp','ruamel','rich','cachetools','platformdirs',
        'notifypy','diskcache','duckdb','msgspec','psutil','yaml']
import importlib
for d in deps:
    try: importlib.import_module(d); print(f'OK  {d}')
    except ImportError as e: print(f'ERR {d}: {e}')
"

# 4. Aps criar/modificar cada arquivo:
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py
python -m ruff check ARQUIVO.py   # deve mostrar 0 erros
```

**REGRA R21:** Se py_compile falhar  PARE. Se dep faltar  instale.
Consulte: `.agents/rules/NC-RULE-006-no-assumptions.mdc`

Evitar:
- `print()` em qualquer lugar  SEMPRE `logger = logging.getLogger(__name__)`
- Mdulos com hfen via `import` direto  usar `importlib.util.spec_from_file_location` (R09)
- Hardcode de paths  usar `get_config()`
- Dependncias externas fora das 12 validadas acima (stdlib  OK: threading, sched, collections)
- NC-SVC-FR-009 j usa MetricsCollector  no quebre a interface dele

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Regras: `.agents/rules/neocortexrules.md` (R21  a regra mais crtica)
EventBus existente: `NC-SVC-FR-005-event-bus.py`  integrar para publicar eventos
Session-Buddy: `NC-SVC-FR-009-session-buddy.py`  leia antes de implementar MetricsCollector
Sprint: Pr-MCP Fase 2  observabilidade  blocante para MCP consolidado
Agent port desta sesso: 32763

---

## TAREFA A  NC-DS-022: MetricsCollector

**Ticket:** NC-DS-022
**Arquivo:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py`
**Esforo:** ~180L

### Interface obrigatria (NC-SVC-FR-009 j depende desta):

```python
"""
NC-SVC-FR-006-metrics-collector.py
FR-006  MetricsCollector: Coleta de mtricas de execuo do NeoCortex.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

@dataclass
class ToolMetric:
    """Mtrica de uma execuo de tool MCP."""
    tool_name: str
    action: str
    duration_ms: float
    success: bool
    tokens_used: int = 0
    error_msg: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class MetricsCollector:
    """Coletora de mtricas de tools MCP, tokens, latncia e erros.
    
    Interface usada por NC-SVC-FR-009-session-buddy.py:
      - record_tool_call(tool_name, action, duration_ms, success, tokens, error)
      - get_session_metrics() -> Dict
      - get_tool_stats(tool_name) -> Dict
      - reset() -> None
    """
    
    def __init__(self):
        ...
    
    def record_tool_call(
        self,
        tool_name: str,
        action: str,
        duration_ms: float,
        success: bool = True,
        tokens_used: int = 0,
        error_msg: Optional[str] = None,
    ) -> None:
        """Registra execuo de uma tool."""
        ...
    
    def get_session_metrics(self) -> Dict:
        """Retorna mtricas agregadas da sesso atual."""
        # Deve retornar: total_calls, success_rate, total_tokens,
        # avg_duration_ms, error_count, tools_used (lista)
        ...
    
    def get_tool_stats(self, tool_name: str) -> Dict:
        """Retorna estatsticas por tool."""
        # Deve retornar: call_count, success_rate, avg_duration_ms, total_tokens
        ...
    
    def reset(self) -> None:
        """Reseta mtricas da sesso."""
        ...
    
    def get_recent_errors(self, limit: int = 10) -> List[ToolMetric]:
        """Retorna ltimos N erros registrados."""
        ...

def get_metrics_collector() -> MetricsCollector:
    """Singleton do MetricsCollector."""
    ...
```

**Restries:**
- Storage em memria (lista de `ToolMetric`)  sem disco, sem DB
- Thread-safe: `threading.Lock` em todas as operaes de escrita
- Publicar evento via EventBus quando `error_msg is not None` (usar R09 para import)
- Singleton `get_metrics_collector()`
- `collections.deque(maxlen=1000)` para limitar histrico

---

## TAREFA B  NC-DS-023: FSM Genrica

**Ticket:** NC-DS-023
**Arquivo:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-007-finite-state-machine.py`
**Esforo:** ~160L

### O que implementar:

```python
"""
NC-SVC-FR-007-finite-state-machine.py
FR-007  FiniteStateMachine: FSM genrica para controle de estado de agentes.
"""
import logging
from enum import Enum
from typing import Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

class FSMError(Exception):
    """Erro de transio invlida na FSM."""

class FiniteStateMachine:
    """FSM genrica reutilizvel para controle de estado de agentes NeoCortex.
    
    Uso tpico:
        fsm = FiniteStateMachine(name="agent-001", initial_state="IDLE")
        fsm.add_transition("IDLE", "RUNNING", trigger="start")
        fsm.add_transition("RUNNING", "IDLE", trigger="stop")
        fsm.trigger("start")   # IDLE  RUNNING
    """
    
    def __init__(self, name: str, initial_state: str):
        ...
    
    def add_transition(
        self,
        from_state: str,
        to_state: str,
        trigger: str,
        guard: Optional[Callable] = None,
        on_enter: Optional[Callable] = None,
    ) -> None:
        """Registra uma transio.
        
        Args:
            from_state: Estado de origem.
            to_state: Estado de destino.
            trigger: Evento que dispara a transio.
            guard: Funo opcional que retorna bool (True = permite transio).
            on_enter: Callback chamado ao entrar no novo estado.
        """
        ...
    
    def trigger(self, event: str, **kwargs) -> str:
        """Dispara evento e executa transio se vlida.
        
        Returns:
            Novo estado atual.
        Raises:
            FSMError: Se transio no existe ou guard retorna False.
        """
        ...
    
    @property
    def current_state(self) -> str:
        """Estado atual da FSM."""
        ...
    
    def get_valid_triggers(self) -> List[str]:
        """Retorna triggers vlidos no estado atual."""
        ...
    
    def get_history(self) -> List[Dict]:
        """Retorna histrico de transies: [{from, to, trigger, timestamp}]."""
        ...

def create_agent_fsm(agent_id: str) -> FiniteStateMachine:
    """Factory: cria FSM pr-configurada para agente NeoCortex.
    
    Estados: IDLE  RUNNING  PAUSED  STOPPED
    Tambm: RUNNING  ERROR  IDLE (recovery)
    """
    ...
```

**Restries:**
- Histrico de transies: `collections.deque(maxlen=500)`
- Thread-safe: `threading.RLock`
- Publicar evento `AGENT_STATE_CHANGED` no EventBus (R09 para import)
- `create_agent_fsm()` deve criar FSM com estados IDLE/RUNNING/PAUSED/STOPPED/ERROR pr-configurados
- Sem deps externas  apenas stdlib

---

## PROTOCOLO DE ENTREGA

1. Crie NC-SVC-FR-006, valide com py_compile + ruff (0 erros)
2. Crie NC-SVC-FR-007, valide com py_compile + ruff (0 erros)
3. Gere 2 handoff YAMLs em `DIR-DS-002-audit-logs/` com campos acima
4. NO modifique mais nada alm dos 2 arquivos + 2 YAMLs

Se encontrar qualquer dep ausente  registre em `warnings` do YAML, no trave.
