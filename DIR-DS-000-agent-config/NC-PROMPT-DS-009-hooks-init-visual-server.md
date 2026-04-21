# NC-PROMPT-DS-009  3 Agente | hooks/__init__.py + VisualServer
# v1.0 | 2026-04-14 | T0 Antigravity
#
# COLE ESTE PROMPT INTEIRO NO 3 AGENTE
---

Voc  agente T1 (DeepSeek) do NeoCortex. Fase: PR-MCP.

## TICKET: NC-DS-009

Duas entregas independentes, sem dependncia entre si.

## CONTEXTO

```
neocortex/core/hooks/
  NC-HK-FR-001-hook-registry.py   existe (285L)
  NC-HK-FR-002-simple-hook.py    existe (151L)
  __init__.py                    FALTANDO  confirmado por T0
```

O NeoCortex Core precisa de:
- `from neocortex.core.hooks import HookRegistry` funcionando
- Um servidor unificado que sobe Mission Control + Pixel Bridge + NeoCortex

## PASSO 0  STEP-0 (R21: nunca suponha)

```powershell
# Verificar que os hooks existem:
Test-Path "01_neocortex_framework\neocortex\core\hooks\NC-HK-FR-001-hook-registry.py"
Test-Path "01_neocortex_framework\neocortex\core\hooks\NC-HK-FR-002-simple-hook.py"
Test-Path "01_neocortex_framework\neocortex\core\hooks\__init__.py"
# __init__.py DEVE retornar False

# Verificar Python:
python --version
```

## ENTREGA 1  hooks/__init__.py

**Destino:** `01_neocortex_framework\neocortex\core\hooks\__init__.py`

Use importlib.util para importar os mdulos com hfen no nome (R09):

```python
"""
neocortex/core/hooks/__init__.py
Exporta HookRegistry e hooks pr-fabricados.
"""
import importlib.util
import sys
from pathlib import Path

_hooks_dir = Path(__file__).parent

def _load(filename):
    stem = filename.replace(".py", "")
    spec = importlib.util.spec_from_file_location(stem, _hooks_dir / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[stem] = mod
    spec.loader.exec_module(mod)
    return mod

_reg = _load("NC-HK-FR-001-hook-registry.py")
_smpl = _load("NC-HK-FR-002-simple-hook.py")

HookRegistry = _reg.HookRegistry
HOOK_BEFORE_TOOL_CALL   = _reg.HOOK_BEFORE_TOOL_CALL
HOOK_AFTER_TOOL_CALL    = _reg.HOOK_AFTER_TOOL_CALL
HOOK_ON_ERROR           = _reg.HOOK_ON_ERROR
HOOK_ON_SESSION_START   = _reg.HOOK_ON_SESSION_START
HOOK_ON_SESSION_END     = _reg.HOOK_ON_SESSION_END
HOOK_ON_CHECKPOINT      = _reg.HOOK_ON_CHECKPOINT

LoggingHook   = _smpl.LoggingHook
TimingHook    = _smpl.TimingHook
RateLimitHook = _smpl.RateLimitHook
AuditHook     = _smpl.AuditHook

__all__ = [
    "HookRegistry",
    "HOOK_BEFORE_TOOL_CALL", "HOOK_AFTER_TOOL_CALL",
    "HOOK_ON_ERROR", "HOOK_ON_SESSION_START",
    "HOOK_ON_SESSION_END", "HOOK_ON_CHECKPOINT",
    "LoggingHook", "TimingHook", "RateLimitHook", "AuditHook",
]
```

**Validao:**
```powershell
python -m py_compile 01_neocortex_framework\neocortex\core\hooks\__init__.py
# exit 0 = OK
```

## ENTREGA 2  NC-SCR-FR-017-visual-server.py

**Destino:** `01_neocortex_framework\scripts\NC-SCR-FR-017-visual-server.py`
**Mnimo:** 150 linhas

Criar a classe `VisualServer` que orquestra os 3 servios:

```python
class VisualServer:
    MISSION_CONTROL_PORT = 3000
    PICOCLAW_PORT = 18790
    NEOCORTEX_SSE_PORT = 8765

    def start_mission_control(self) -> subprocess.Popen
    def start_pixel_bridge(self) -> threading.Thread
    def start_neocortex(self) -> subprocess.Popen
    def run_all(self) -> None      # sobe os 3 + fica monitorando
    def stop_all(self) -> None     # SIGTERM graceful em todos
    def health_check(self) -> dict # {"mission_control": bool, "neocortex": bool, "picoclaw": bool}
```

CLI entry:
```
python NC-SCR-FR-017-visual-server.py --start
python NC-SCR-FR-017-visual-server.py --stop
python NC-SCR-FR-017-visual-server.py --health
```

Usar: `logger = logging.getLogger(__name__)`  NUNCA print()
Usar: `get_config()` para paths  NUNCA hardcodar

**Validao:**
```powershell
python -m py_compile 01_neocortex_framework\scripts\NC-SCR-FR-017-visual-server.py
(Get-Content 01_neocortex_framework\scripts\NC-SCR-FR-017-visual-server.py).Count
# >= 150
```

## HANDOFF YAML (OBRIGATRIO)

Criar: `DIR-DS-002-audit-logs\NC-DS-009-handoff-YYYYMMDD-HHMMSS.yaml`

```yaml
ticket_id: NC-DS-009
status: PENDING_REVIEW
timestamp: "<atual>"
agent_port: <porta>
lines_added: <N1 + N2>
files_modified:
  - "neocortex/core/hooks/__init__.py"
  - "01_neocortex_framework/scripts/NC-SCR-FR-017-visual-server.py"
summary: |
  __init__.py criado: imports dinmicos via importlib.util
  NC-SCR-FR-017: VisualServer com start/stop/health para Mission Control + PicoClaw + NeoCortex
```

## REGRAS
- R09: use importlib.util para NC- com hfen
- R10: get_config() para paths, nunca hardcodar
- R11: logger, nunca print()
- R21: STEP-0 sempre
- SEM handoff = ENTREGA INVLIDA
