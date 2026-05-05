# NC-PROMPT-DS-008  Agent Prompt: NC-DS-033 + NC-DS-037
# Verso: 1.0 | Data: 2026-04-13 | Template: Brockman v1
# Despachar para: Agente B (porta 44624)

---

##  GOAL

Implementar **2 componentes de extensibilidade**:

- **NC-DS-033 (PRIORIDADE HIGH):** Template padronizado de plugin/tool MCP
  - Diretrio: `01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/`
  - Arquivos: `plugin.json` + `README.md` + `commands/NC-CMD-EXAMPLE.md` + `hooks/NC-HK-EXAMPLE.py`
  - Script: `01_neocortex_framework/scripts/NC-SCR-FR-012-new-tool.py` (~120L, scaffolding)

- **NC-DS-037 (PRIORIDADE MDIA):** FeatureFlagService com cache TTL 1h
  - `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-002-feature-flags.py` (~130L)

Confirme que os arquivos no existem antes de criar:

```powershell
Test-Path "01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE"
Test-Path "01_neocortex_framework\neocortex\core\config\NC-CFG-FR-002-feature-flags.py"
Test-Path "01_neocortex_framework\scripts\NC-SCR-FR-012-new-tool.py"
```

Restrio ABSOLUTA: NO modificar `server.py`, `sub_server.py`, `NC-NAM-FR-001` (@LOCKS).

---

##  RETURN FORMAT

Gerar **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:

```
NC-DS-033-handoff-{YYYYMMDD-HHMMSS}.yaml
NC-DS-037-handoff-{YYYYMMDD-HHMMSS}.yaml
```

Cada YAML:

```yaml
ticket_id: NC-DS-033
status: PENDING_REVIEW
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: 44624
lines_added: <N real  soma de todos os arquivos>
files_modified:
  - <lista de todos os arquivos criados>
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

# Aps cada arquivo .py:
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py && python -m ruff check ARQUIVO.py
```

**R21:** Se py_compile falhar  PARE. **R11:** NUNCA `print()`  `logger = logging.getLogger(__name__)`.

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Regras: `.agents/rules/neocortexrules.md`
Agent port: 44624

**Referncias  leia antes de codificar:**
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001a-tools-registry.md`  padro de naming para tools
- `01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py`  exemplo de tool MCP bem formatada
- `01_neocortex_framework/neocortex/neocortex_config.yaml`  config global (adicionar seo `feature_flags`)

---

## TAREFA A  NC-DS-033: Plugin Template (PLUGIN-001)

**Ticket:** NC-DS-033
**Esforo:** ~300L total (5 arquivos + 1 script)

### Estrutura a criar:

```
01_neocortex_framework/DIR-TMP-FR-001-templates-main/NC-TOOL-FR-TEMPLATE/
 NC-CFG-FR-001-plugin.json          manifesto do plugin
 README.md                          documentao do template
 commands/
    NC-CMD-EXAMPLE.md              exemplo de comando /slash
 hooks/
     NC-HK-EXAMPLE.py               exemplo de hook Python

01_neocortex_framework/scripts/
 NC-SCR-FR-012-new-tool.py          scaffolding CLI
```

### NC-CFG-FR-001-plugin.json (manifesto):

```json
{
  "schema_version": "1.0",
  "name": "NC-TOOL-FR-XXX-your-tool-name",
  "version": "1.0.0",
  "description": "Descrio da tool",
  "author": "NeoCortex Agent",
  "neocortex_min_version": "1.0.0",
  "entry_point": "NC-TOOL-FR-XXX-your-tool-name.py",
  "register_function": "register_tool",
  "hooks": [],
  "commands": [],
  "permissions": {
    "read_lobes": false,
    "write_lobes": false,
    "read_ssot": true,
    "write_ssot": false
  },
  "dependencies": []
}
```

### NC-SCR-FR-012-new-tool.py (scaffolding CLI):

```python
"""
NC-SCR-FR-012-new-tool.py
Script de scaffolding: cria nova tool MCP a partir do template NC-TOOL-FR-TEMPLATE.

Uso:
    python NC-SCR-FR-012-new-tool.py --name "minha-tool" --sigla "FR" --num 033

Gera:
    01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-033-minha-tool.py
    + manifesto plugin.json preenchido
    + Registra no NC-NAM-FR-001a-tools-registry.md (avisa o usurio, no escreve automaticamente)
"""
import argparse
import logging
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "DIR-TMP-FR-001-templates-main" / "NC-TOOL-FR-TEMPLATE"
TOOLS_DIR = Path(__file__).parent.parent / "neocortex" / "mcp" / "tools"


def create_tool(name: str, sigla: str, num: str) -> Path:
    """Cria estrutura de nova tool a partir do template."""
    ...


def main() -> None:
    """Entry point CLI."""
    ...


if __name__ == "__main__":
    main()
```

### NC-HK-EXAMPLE.py (exemplo de hook):

```python
"""
NC-HK-EXAMPLE.py  Exemplo de hook Python para NeoCortex.
Evento: PostToolUse
Objetivo: Demonstrar estrutura de um hook.
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def hook_handler(context: Dict) -> Dict:
    """Handler do hook de exemplo.

    Args:
        context: {tool_name, action, result, timestamp}
    Returns:
        {status: "ok"|"warning"|"error", message: str}
    """
    tool_name = context.get("tool_name", "unknown")
    logger.debug(f"Hook PostToolUse disparado para tool: {tool_name}")
    return {"status": "ok", "message": f"Hook executado para {tool_name}"}
```

---

## TAREFA B  NC-DS-037: FeatureFlagService (FLAG-001)

**Ticket:** NC-DS-037
**Arquivo:** `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-002-feature-flags.py`
**Esforo:** ~130L

### Interface mnima:

```python
"""
NC-CFG-FR-002-feature-flags.py
FR-CFG-002  FeatureFlagService: Flags de funcionalidade com cache TTL 1h.

L flags de neocortex_config.yaml (seo feature_flags).
Cache TTL 1h usando cachetools.TTLCache.
Suporta feature flags via env var (NEOCORTEX_FF_<FLAG>=true).
"""
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class FeatureFlagService:
    """Gerencia feature flags com cache TTL 1h.

    Interface pblica:
      is_enabled(flag_name: str) -> bool
      get_flag(flag_name: str, default=None) -> Any
      reload() -> None
      list_flags() -> Dict[str, Any]

    Flags padro do sistema (conforme @STRATEGY):
      - kairos_channels: bool (KAIROS_CHANNELS env var)
      - kairos_push_notification: bool
      - mentor_step0: bool (default True)
      - rate_limit_enabled: bool (default True)
    """

    # Flags padro (fallback se config no existir)
    _DEFAULTS: Dict[str, Any] = {
        "kairos_channels": False,
        "kairos_push_notification": False,
        "mentor_step0": True,
        "rate_limit_enabled": True,
    }

    def __init__(self):
        ...

    def is_enabled(self, flag_name: str) -> bool:
        """Retorna True se a flag est ativa (config ou env var)."""
        ...

    def get_flag(self, flag_name: str, default: Any = None) -> Any:
        """Retorna valor da flag (qualquer tipo)."""
        ...

    def reload(self) -> None:
        """Invalida cache e fora re-leitura."""
        ...

    def list_flags(self) -> Dict[str, Any]:
        """Retorna todas as flags com seus valores atuais."""
        ...


def get_feature_flags() -> FeatureFlagService:
    """Singleton do FeatureFlagService."""
    ...
```

**Restries:**
- `cachetools.TTLCache(maxsize=1, ttl=3600)` para cache do arquivo de config
- Env var `NEOCORTEX_FF_<FLAG_NAME_UPPER>=true` tem precedncia sobre config
- Ex: `os.getenv("NEOCORTEX_FF_KAIROS_CHANNELS")` sobrescreve `kairos_channels`
- Singleton thread-safe
- `get_config()` para obter path do config (no hardcode)

---

## PROTOCOLO DE ENTREGA

1. STEP-0  confirmao ambiente
2. Criar diretrio template: `New-Item -ItemType Directory -Force "01_neocortex_framework\DIR-TMP-FR-001-templates-main\NC-TOOL-FR-TEMPLATE\commands"` e `hooks`
3. Implementar NC-DS-033 (5+ arquivos)  py_compile + ruff nos .py
4. Implementar NC-DS-037 (1 arquivo .py)  py_compile + ruff 0 erros
5. Gerar 2 handoffs em `DIR-DS-002-audit-logs/`
6. NO modificar outros arquivos alm dos listados + 2 YAMLs
