# NC-DS-036  RE-ENTREGA: TTLManager (Cdigo Base Disponvel)
<!-- Ticket: NC-DS-036 | Esforo: ~150L | Re-entrega (stub 41L rejeitado) -->
<!-- Base: @RES003 linhas 150-179  USAR COMO BASE, no partir do zero -->

## CONTEXTO OBRIGATRIO

**Projeto:** NeoCortex Multi-Agent Framework
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`

**ATENO:** A entrega anterior (41L) foi rejeitada por ser stub insuficiente.
Esta re-entrega DEVE usar o cdigo base validado pela pesquisa internet.

**Arquivos SSOT a consultar:**
- `@LOCKS` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`
- `@RES003` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md`
- `@SYNTHESIS` = `DIR-RES-CC-001-claude-leak-workzone/NC-ANA-INT-001-synthesis-t0.md`

**PROIBIDO MODIFICAR:** `server.py`, `sub_server.py`, `NC-NAM-FR-001`

---

## TAREFA: NC-DS-036 TTLManager Completo

**Write zone:** `01_neocortex_framework/neocortex/core/services/`
**Arquivo:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-011-ttl-manager.py`
**Mnimo:** 150L de cdigo real

### PASSO 1  Leia o cdigo base em @RES003 linhas 150-179

O cdigo funcional j foi pesquisado e validado. Leia `NC-RES-CC-003-validation-scheduling-ttl-flags.md` seo TTLManager (linhas 150-179) e USE como ponto de partida.

### O que entregar (expanso do cdigo base)

```python
import heapq
import threading
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# TTLs validados pelo Claude Code (no alterar)
TTL_CONSTANTS = {
    "session": 18000,        # 5 horas (SESSION_LEASE_TTL)
    "token_refresh": 300,    # 5 min antes do vencimento
    "feature_flag": 3600,    # 1 hora
    "heartbeat": 60,         # 1 minuto
    "cache_default": 300,    # 5 minutos
}

@dataclass(order=True)
class TTLEntry:
    expires_at: float
    entity_id: str = field(compare=False)
    entity_type: str = field(compare=False)
    callback: Optional[Callable] = field(compare=False, default=None)

class TTLManager:
    def __init__(self):
        self._heap: list[TTLEntry] = []
        self._lock = threading.Lock()
        self._active: dict[str, TTLEntry] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def register(self, entity_id: str, entity_type: str,
                 ttl_s: int = None, callback: Callable = None) -> None
    def refresh(self, entity_id: str, ttl_s: int = None) -> bool
    def cancel(self, entity_id: str) -> bool
    def get_remaining(self, entity_id: str) -> Optional[float]
    def list_active(self) -> list[dict]          # para debug/display
    def start(self) -> None                       # inicia thread de checagem
    def stop(self) -> None                        # para thread graciosamente
    def _check_expirations(self) -> None          # loop interno
```

### Integrao com EventBus (evento de expirao)
```python
# Ao expirar, disparar evento via EventBus se disponvel
try:
    from neocortex.core.services import NC_SVC_FR_005_event_bus as eb
    eb.publish("entity_expired", {"entity_id": entry.entity_id,
                                   "entity_type": entry.entity_type,
                                   "expired_at": datetime.now().isoformat()})
except Exception:
    pass  # EventBus indisponvel no  fatal
```

### Checklist antes do handoff (R20 adaptado)
- [ ] Arquivo 150L de cdigo real (no stub)
- [ ] `heapq + threading.Lock` usado (no Redis, no bibliotecas externas)
- [ ] TTL_CONSTANTS definidas com os valores exatos
- [ ] Mtodo `start()/stop()` implementados
- [ ] Log de expirao: `entity_id`, `entity_type`, `expires_at`
- [ ] Evento `entity_expired` publicado via EventBus (com try/except)

### Handoff
```yaml
# DIR-DS-002-audit-logs/NC-DS-036-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-036
status: PENDING_REVIEW
lines_added: <N>   # deve ser >= 150
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-011-ttl-manager.py
summary: |
  TTLManager completo com heapq+threading, TTL_CONSTANTS, start/stop, EventBus integration.
ajustes_aplicados:
  - Cdigo base de @RES003 linhas 150-179 utilizado como partida
  - TTL_CONSTANTS: 18000s, 300s, 3600s, 60s, 300s
  - Evento entity_expired publicado via EventBus com try/except
re_entrega_motivo: "Entrega anterior 41L era stub  re-entrega com >=150L"
```
