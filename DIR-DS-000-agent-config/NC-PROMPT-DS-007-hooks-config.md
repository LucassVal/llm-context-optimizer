# NC-PROMPT-DS-007  Agent Prompt: NC-DS-031 + NC-DS-032
# Verso: 1.0 | Data: 2026-04-13 | Template: Brockman v1
# Despachar para: Agente A (porta 59520)

---

##  GOAL

Implementar **2 servios de extensibilidade Python**  do zero:

- **NC-DS-031 (PRIORIDADE HIGH):** Sistema de hooks reativos ps-ao
  - `01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-001-hook-registry.py` (~150L)
  - `01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-002-example-hook.py` (~60L)
  - `05_examples/.nc/hooks/ssot-guard.yaml` (~30L)

- **NC-DS-032 (PRIORIDADE HIGH):** Config local por projeto (`.nc/`)
  - `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-004-project-loader.py` (~150L)
  - `05_examples/.nc/config.yaml` (~30L)

Confirme que os arquivos no existem antes de criar:

```powershell
Test-Path "01_neocortex_framework\neocortex\core\hooks\NC-HK-FR-001-hook-registry.py"
Test-Path "01_neocortex_framework\neocortex\core\config\NC-CFG-FR-004-project-loader.py"
# Ambos devem retornar False
```

Restrio ABSOLUTA: NO modificar `server.py`, `sub_server.py` (@LOCKS).

---

##  RETURN FORMAT

Gerar **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:

```
NC-DS-031-handoff-{YYYYMMDD-HHMMSS}.yaml
NC-DS-032-handoff-{YYYYMMDD-HHMMSS}.yaml
```

Cada YAML deve conter:

```yaml
ticket_id: NC-DS-031
status: PENDING_REVIEW
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: 59520
lines_added: <N real>
files_modified:
  - 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-001-hook-registry.py
  - 01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-002-example-hook.py
  - 05_examples/.nc/hooks/ssot-guard.yaml
summary: |
  <1-3 linhas>
metrics:
  ruff_check: PASS
  py_compile: PASS
  write_zone_respected: true
  locks_respected: true
errors: []
warnings: []
checklist_r20:
  naming_convention: true
  no_print_statements: true
  handoff_yaml_complete: true
```

---

##  WARNINGS  STEP-0 OBRIGATRIO

```powershell
python --version        # 3.12.x esperado
python -m ruff --version

python -c "
deps = ['mcp','fastmcp','ruamel','rich','cachetools','platformdirs',
        'notifypy','diskcache','duckdb','msgspec','psutil','yaml']
import importlib
for d in deps:
    try: importlib.import_module(d); print(f'OK  {d}')
    except ImportError as e: print(f'ERR {d}: {e}')
"

# Aps cada arquivo:
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py && python -m ruff check ARQUIVO.py
```

**R21:** Se py_compile falhar  PARE. Se dep faltar  instale antes de avanar.

Evitar sempre:
- `print()`  `logger = logging.getLogger(__name__)`
- Import de mdulo com hfen  `importlib.util.spec_from_file_location` (R09)
- Hardcode de paths  `get_config()`

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Regras: `.agents/rules/neocortexrules.md` (R21 crtico)
Agent port: 59520

**Referncias essenciais  leia antes de codificar:**
- `DIR-RES-CC-001-claude-leak-workzone/analysis-session-b/NC-ANA-CC-003-plugin-patterns.md`  padres de hooks
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`  lista de locks (para ssot-guard.yaml)
- `01_neocortex_framework/neocortex/neocortex_config.yaml`  config global existente (base para NC-DS-032)
- EventBus: `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py` (integrar hooks com eventos)

---

## TAREFA A  NC-DS-031: HookRegistry (HOOK-001)

**Ticket:** NC-DS-031
**Zona:** `01_neocortex_framework/neocortex/core/hooks/`
**Esforo:** ~240L total (3 arquivos)

### Interface mnima  NC-HK-FR-001-hook-registry.py

```python
"""
NC-HK-FR-001-hook-registry.py
FR-HK-001  HookRegistry: Sistema de hooks reativos ps-ao para NeoCortex.

Suporta hooks YAML (declarativos) e Python (programticos).
Eventos: PreToolUse, PostToolUse, ToolError (padro MCP).
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class HookEvent(str, Enum):
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    TOOL_ERROR = "ToolError"


@dataclass
class HookDefinition:
    """Definio de um hook (YAML ou Python)."""
    name: str
    event: HookEvent
    handler: Callable          # funo Python
    timeout_seconds: float = 2.0
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)


class HookRegistry:
    """Registry de hooks reativos para eventos de tools MCP.

    Interface pblica:
      register(name, event, handler, timeout, enabled) -> None
      unregister(name) -> bool
      trigger(event, context) -> List[Dict]   # executa todos hooks do evento
      load_yaml(path) -> int                  # carrega hooks de arquivo YAML
      list_hooks(event=None) -> List[str]
    """

    def __init__(self):
        ...

    def register(
        self,
        name: str,
        event: HookEvent,
        handler: Callable,
        timeout_seconds: float = 2.0,
        enabled: bool = True,
    ) -> None:
        """Registra um hook Python."""
        ...

    def unregister(self, name: str) -> bool:
        """Remove um hook. Retorna True se existia."""
        ...

    def trigger(self, event: HookEvent, context: Dict[str, Any]) -> List[Dict]:
        """Dispara todos os hooks do evento. Timeout por hook: 2s.

        Returns:
            Lista de resultados [{name, status, result/error, duration_ms}]
        """
        ...

    def load_yaml(self, path: Path) -> int:
        """Carrega hooks de um arquivo YAML. Retorna N hooks carregados."""
        ...

    def list_hooks(self, event: Optional[HookEvent] = None) -> List[str]:
        """Lista nomes de hooks registrados (filtrado por evento se fornecido)."""
        ...


def get_hook_registry() -> HookRegistry:
    """Singleton do HookRegistry."""
    ...
```

**Restries:**
- Thread-safe: `threading.Lock`
- Timeout por hook: `concurrent.futures.ThreadPoolExecutor` com `timeout=2.0`
- Publicar evento `HOOK_TRIGGERED` no EventBus (importar com R09)
- Singleton `get_hook_registry()`
- YAML de hooks: suportar campos `name`, `event`, `script` (path Python), `enabled`

### NC-HK-FR-002-example-hook.py
Hook de exemplo que valida naming convention R01 no PostToolUse.
Deve ter `hook_handler(context: Dict) -> Dict` com `return {"status": "ok", ...}`.

### 05_examples/.nc/hooks/ssot-guard.yaml
Arquivo de configurao declarativa de hook:
```yaml
# ssot-guard.yaml  Hook guardio do SSOT
hooks:
  - name: ssot-naming-guard
    event: PostToolUse
    enabled: true
    script: hooks/NC-HK-FR-002-example-hook.py
    description: "Valida que arquivos criados seguem NC- naming convention"
```

---

## TAREFA B  NC-DS-032: ProjectConfigLoader (CONFIG-001)

**Ticket:** NC-DS-032
**Zona:** `01_neocortex_framework/neocortex/core/config/`
**Esforo:** ~180L (2 arquivos)

### Interface mnima  NC-CFG-FR-004-project-loader.py

```python
"""
NC-CFG-FR-004-project-loader.py
FR-CFG-004  ProjectConfigLoader: Config local por projeto (.nc/).

Faz merge de config local (.nc/config.yaml) com global (neocortex_config.yaml).
Local override global (precedncia: local > global > defaults).
Suporta NEOCORTEX_CONFIG_DIR env var para path customizado.
Usa platformdirs para paths Windows-first.
"""
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ProjectConfigLoader:
    """Carrega config local de projeto (.nc/config.yaml) com merge sobre global.

    Interface pblica:
      load(project_root) -> Dict          # merge local+global
      get(key, default=None) -> Any       # acesso por chave (dotted: "mcp.port")
      reload() -> Dict                    # fora re-leitura do disco
      get_config_path() -> Path           # path do .nc/config.yaml ativo
    """

    def __init__(self, project_root: Optional[Path] = None):
        ...

    def load(self, project_root: Optional[Path] = None) -> Dict:
        """Carrega e mergeia config local + global.

        Precedncia: .nc/config.yaml (local) > neocortex_config.yaml (global) > defaults.
        Suporta: NEOCORTEX_CONFIG_DIR env var.
        """
        ...

    def get(self, key: str, default: Any = None) -> Any:
        """Acesso por chave dotted (ex.: 'mcp.port', 'feature_flags.kairos')."""
        ...

    def reload(self) -> Dict:
        """Fora re-leitura do disco."""
        ...

    def get_config_path(self) -> Optional[Path]:
        """Retorna path do .nc/config.yaml ativo (None se no existir)."""
        ...


_loader: Optional[ProjectConfigLoader] = None

def get_project_config_loader(project_root: Optional[Path] = None) -> ProjectConfigLoader:
    """Singleton do ProjectConfigLoader."""
    ...
```

**Restries:**
- Usar `ruamel.yaml` para parse (no `yaml.safe_load`)
- Usar `platformdirs.user_config_dir("neocortex")` como fallback de path
- Env var `NEOCORTEX_CONFIG_DIR` tem precedncia sobre platformdirs
- Merge profundo (`dict.update` no  suficiente  implementar deep_merge)
- Singleton

### 05_examples/.nc/config.yaml
```yaml
# .nc/config.yaml  Exemplo de config local de projeto
# Override local: prevalece sobre neocortex_config.yaml global
project:
  name: "MeuProjeto"
  version: "1.0.0"

feature_flags:
  kairos_channels: false
  kairos_push_notification: false

mcp:
  timeout_seconds: 30

logging:
  level: "INFO"
```

---

## PROTOCOLO DE ENTREGA

1. STEP-0  confirme Python + ruff + deps
2. Crie diretrio `hooks/` se no existir: `New-Item -ItemType Directory -Force "01_neocortex_framework\neocortex\core\hooks"`
3. Implemente NC-DS-031 (3 arquivos)  py_compile + ruff 0 erros
4. Implemente NC-DS-032 (2 arquivos)  py_compile + ruff 0 erros
5. Gere 2 handoffs em `DIR-DS-002-audit-logs/`
6. NO modifique nenhum outro arquivo alm dos 5 listados + 2 YAMLs
