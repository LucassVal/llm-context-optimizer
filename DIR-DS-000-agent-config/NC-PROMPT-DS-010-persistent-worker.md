# NC-PROMPT-DS-010  Agent Prompt: NC-DS-029 (PersistentWorker)
# Verso: 1.0 | Data: 2026-04-13 | Template: Brockman v1
# Despachar para: Agente A (porta 59520)

---

##  GOAL

Implementar **NC-DS-029  Worker Persistente (WORKER-001)**.

Arquivo a criar:
- `01_neocortex_framework/neocortex/core/workers/NC-WKR-FR-001-persistent-worker.py` (~200L)

Este  o componente que executa tickets de forma assncrona e persistente, com:
- Loop contnuo de escaneamento de tickets AVAILABLE
- Claim atmico via file lock (R14: isolamento entre workers)
- Backoff exponencial (10s  20s  40s) em caso de falha
- Classe `PersistentWorker` com `start()`, `stop()`, `pause()`, `resume()`

Confirme antes de criar:
```powershell
Test-Path "01_neocortex_framework\neocortex\core\workers\NC-WKR-FR-001-persistent-worker.py"
# Deve retornar False
New-Item -ItemType Directory -Force "01_neocortex_framework\neocortex\core\workers"
```

@LOCKS ABSOLUTOS: NO modificar `server.py`, `sub_server.py`.

---

##  RETURN FORMAT

Handoff em `DIR-DS-002-audit-logs/NC-DS-029-handoff-{YYYYMMDD-HHMMSS}.yaml`:

```yaml
ticket_id: NC-DS-029
status: PENDING_REVIEW
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: 59520
lines_added: <N real>
files_modified:
  - 01_neocortex_framework/neocortex/core/workers/NC-WKR-FR-001-persistent-worker.py
summary: |
  <1-3 linhas>
ajustes_aplicados:
  - "Backoff exponencial 102040s implementado"
  - "PersistentWorker com start/stop/pause/resume"
  - "Claim atmico via filelock"
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
libs=['mcp','fastmcp','filelock','cachetools','yaml']
for lib in libs:
    try: importlib.import_module(lib); print(f'OK  {lib}')
    except ImportError as e: print(f'ERR {lib}: {e}')
"
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py && python -m ruff check ARQUIVO.py
```

**R11:** NUNCA `print()`  `logger`. **R09:** import com hfen  `importlib.util`.

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
Agent port: 59520 | Ticket: NC-DS-029 | Zona: `01_neocortex_framework/neocortex/core/workers/`

Referncias:
- `DIR-DS-000-agent-config/NC-PROMPT-DS-003-persistent-worker.md`  design do PersistentWorker
- `01_neocortex_framework/lobes/NC-LBE-DS-003-worker-patterns.mdc`  REG-001010, claim protocol
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`  locks a respeitar

---

## TAREFA  NC-DS-029: PersistentWorker

**Ticket:** NC-DS-029
**Zona:** `01_neocortex_framework/neocortex/core/workers/`
**Esforo:** ~200L

### Interface mnima:

```python
"""
NC-WKR-FR-001-persistent-worker.py
FR-WKR-001  PersistentWorker: Worker assncrono persistente para processar
tickets NC-DS-XXX do diretrio DIR-DS-001-tickets/.

Loop contnuo: scan  claim  execute  handoff.
Backoff exponencial em falha: 10s  20s  40s (max).
Claim atmico: filelock no arquivo do ticket.
"""
import logging
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class WorkerState(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


@dataclass
class WorkerConfig:
    tickets_dir: Path
    worker_id: str          # ex: "worker-59520-abc123"
    poll_interval: float = 10.0         # segundos entre scans
    backoff_base: float = 10.0          # backoff inicial (s)
    backoff_max: float = 40.0           # backoff mximo (s)
    max_retries: int = 3


class PersistentWorker:
    """Worker persistente para processar tickets de forma assncrona.

    Interface pblica:
      start() -> None           # inicia loop em thread separada
      stop() -> None            # para graciosamente
      pause() -> None           # pausa o loop (tickets no so processados)
      resume() -> None          # retoma aps pause
      get_state() -> WorkerState
      register_handler(ticket_type, fn) -> None  # registra handler para tipo de ticket
    """

    def __init__(self, config: WorkerConfig):
        ...

    def start(self) -> None:
        """Inicia worker em thread dedicada (no-bloqueante)."""
        ...

    def stop(self) -> None:
        """Para o worker graciosamente. Aguarda ticket atual terminar."""
        ...

    def pause(self) -> None:
        """Pausa processamento. Worker continua rodando mas no pega tickets."""
        ...

    def resume(self) -> None:
        """Retoma aps pause."""
        ...

    def get_state(self) -> WorkerState:
        ...

    def register_handler(self, ticket_type: str, handler: Callable) -> None:
        """Registra funo handler para um tipo de ticket."""
        ...

    def _scan_and_claim(self) -> Optional[Dict]:
        """Escaneia DIR-DS-001-tickets/ e faz claim atmico do primeiro AVAILABLE."""
        ...

    def _execute_ticket(self, ticket: Dict) -> None:
        """Executa ticket e gera handoff em DIR-DS-002-audit-logs/."""
        ...

    def _backoff(self, attempt: int) -> None:
        """Espera com backoff exponencial: 10s  20s  40s."""
        delay = min(self.config.backoff_base * (2 ** attempt), self.config.backoff_max)
        logger.info(f"Backoff {delay}s (tentativa {attempt})")
        time.sleep(delay)


def create_worker(port: int, tickets_dir: Optional[Path] = None) -> PersistentWorker:
    """Factory: cria worker configurado para a porta dada."""
    ...
```

**Restries:**
- `filelock.FileLock` para claim atmico (R09 para import se necessrio)
- Thread-safe: `threading.Lock` para mudanas de estado
- Publicar evento `WORKER_STARTED`/`WORKER_STOPPED` no EventBus (se disponvel)
- `worker_id` = `f"worker-{port}-{uuid4().hex[:6]}"`

---

## PROTOCOLO DE ENTREGA

1. STEP-0  confirmar ambiente
2. `New-Item -ItemType Directory -Force "01_neocortex_framework\neocortex\core\workers"`
3. Implementar NC-WKR-FR-001  py_compile + ruff 0 erros
4. Gerar handoff YAML em `DIR-DS-002-audit-logs/`
5. NO modificar nada alm do arquivo listado + YAML
