# NC-PROMPT-DS-005  Agent Prompt: NC-DS-026 + NC-DS-021
# Gerado: 2026-04-13 | Sprint Pr-MCP Fase 2 | Template: Brockman v1
# Despachar para: 1 agente opencode livre

---

##  GOAL

Implementar **1 utilitrio Python** e fazer **upgrade de 1 servio existente**:
- **NC-DS-026:** `NC-UTL-FR-003-path-resolver.py`  PathResolver com resoluo de tickets, handoffs, lobes e tools via `get_config()`
- **NC-DS-021:** `NC-SVC-FR-005-event-bus.py` (UPGRADE)  adicionar event type constants exportveis, `publish_entity_expired()`, `get_subscribers_count()` e docstring atualizada

Zona de escrita:
- NC-DS-026  `01_neocortex_framework/neocortex/core/utils/`
- NC-DS-021  `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py` (apenas adicionar, no reescrever)

Restrio: NO modificar `server.py`, `sub_server.py` (@LOCKS).

---

##  RETURN FORMAT

Ao concluir, produzir **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:
- `NC-DS-026-handoff-{YYYYMMDD-HHMMSS}.yaml`
- `NC-DS-021-handoff-{YYYYMMDD-HHMMSS}.yaml`

Cada YAML deve conter:
- `ticket_id` | `status: PENDING_REVIEW` | `timestamp` (ISO8601)
- `agent_port` | `lines_added` (linhas novas apenas) | `files_modified`
- `summary` (1-3 linhas)
- `metrics.ruff_check: PASS` | `metrics.py_compile: PASS`
- `checklist_r20` completo

Para NC-DS-021: `lines_added` = apenas as linhas acrescentadas (arquivo partia de 163L).

---

##  WARNINGS

Execute o **STEP-0 ABAIXO** e reporte resultado no handoff.
Verificar:
- [ ] Python 3.12.x confirmado?
- [ ] Ruff disponvel?
- [ ] 12 deps importadas sem erro?
- [ ] `py_compile` em CADA arquivo?
- [ ] `ruff check` com 0 erros?

Evitar:
- Hardcode de qualquer path  SOMENTE `get_config()` como ncora de root
- `raise` quando arquivo no encontrado  retornar `None`
- Apagar linhas existentes no event-bus  apenas ADICIONAR
- `print()`  `logger = logging.getLogger(__name__)`
- Arquivo abaixo de 80 linhas (NC-DS-026: mnimo 120L)

---

##  CONTEXT DUMP

Projeto: NeoCortex MCP Framework em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Regras: `.agents/rules/neocortexrules.md` (R21 crtico)
EventBus existente tem 163L  entregar NC-DS-021 com 180L+ total
PathResolver deve usar `glob()` para busca por padro, nunca nome hardcoded
Sprint: Pr-MCP Fase 2  infraestrutura antes da consolidao do servidor MCP

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

Projeto NeoCortex em: `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`

**Arquivos de referncia  leia antes de codificar:**
- `01_neocortex_framework\neocortex\config.py`  use `get_config()` como base de paths
- `01_neocortex_framework\neocortex\core\utils\NC-UTL-FR-001-yaml-safe-parser.py`  modelo de util
- `01_neocortex_framework\neocortex\core\utils\NC-UTL-FR-002-hash-utils.py`  modelo de util
- `01_neocortex_framework\neocortex\core\services\NC-SVC-FR-005-event-bus.py`  EventBus existente (163L)

**Regras absolutas:**
- NUNCA modificar: `server.py`, `sub_server.py` (@LOCKS)
- Nomes: padro `NC-TIPO-SIGLA-NUM-desc.py`
- `logger = logging.getLogger(__name__)`  nunca `print()`
- Sem hardcode de paths  usar `get_config()` para tudo
- Mnimo: 80L de cdigo real por arquivo

---

## TAREFA A  NC-DS-026: PathResolver (UTIL-003)

**Ticket:** NC-DS-026
**Arquivo a criar:** `01_neocortex_framework/neocortex/core/utils/NC-UTL-FR-003-path-resolver.py`
**Esforo:** ~120L

### O que implementar:

```python
"""
NC-UTL-FR-003-path-resolver.py
UTIL-003  PathResolver: resoluo de paths respeitando get_config()
"""

from pathlib import Path
from typing import Optional, List

class PathResolver:
    """Resolve caminhos de recursos NeoCortex usando get_config() como ncora."""
    
    def __init__(self):
        from neocortex.config import get_config
        self._cfg = get_config()
    
    def resolve_ticket_path(self, ticket_id: str) -> Path:
        """Busca ticket YAML em DIR-DS-001-tickets/NC-{ticket_id}-*.yaml"""
        # Padro: DIR-DS-001-tickets/NC-DS-NNN-*.yaml
        ...
    
    def resolve_handoff_path(self, ticket_id: str) -> Optional[Path]:
        """Busca handoff mais recente em DIR-DS-002-audit-logs/ para o ticket."""
        # Padro: NC-{ticket_id}-handoff-*.yaml  retorna o mais recente por mtime
        ...
    
    def resolve_lobe_path(self, lobe_name: str) -> Optional[Path]:
        """Busca .mdc em 01_neocortex_framework/lobes/ ou 02_memory_lobes/"""
        ...
    
    def resolve_tool_path(self, tool_name: str) -> Optional[Path]:
        """Busca tool em neocortex/mcp/tools/NC-TOOL-FR-*-{tool_name}.py"""
        ...
    
    def list_zone_files(self, write_zone: str) -> List[Path]:
        """Lista arquivos Python em uma write_zone (path relativo ao root)."""
        ...
    
    def get_root(self) -> Path:
        """Retorna root do projeto via get_config()."""
        ...

def get_path_resolver() -> PathResolver:
    """Singleton do PathResolver."""
    ...
```

**Restries:**
- Usar `glob()` para busca por padro (nunca hardcode de nome completo)
- Retornar `None` (no raise) quando arquivo no encontrado
- Para `resolve_handoff_path`: se mltiplos, retornar o mais recente por `mtime`
- `get_config()` deve ser a nica fonte de `root_path`

---

## TAREFA B  NC-DS-021: EventBus Upgrade (ARCH-001)

**Ticket:** NC-DS-021
**Arquivo:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`
**Status:** ARQUIVO J EXISTE (163L)  faa upgrade, no reescrita

### O que adicionar ao arquivo existente:

O `NC-SVC-FR-005-event-bus.py` j implementa subscribe/publish/unsubscribe (163L). 

**Adicione apenas:**

1. **Event type constants acessveis via mdulo:**
```python
# J existem como strings no arquivo  garantir que esto EXPORTADAS:
TOOL_CALLED = "TOOL_CALLED"
TOOL_RESULT = "TOOL_RESULT"
AGENT_STATE_CHANGED = "AGENT_STATE_CHANGED"
HANDOFF_SUBMITTED = "HANDOFF_SUBMITTED"
# ADICIONAR (novos do claude-leak):
KAIROS_TICK = "kairos.tick"
ENTITY_EXPIRED = "entity_expired"
NOTIFICATION_SENT = "notification_sent"
CHANNEL_MESSAGE = "channel.notification"
```

2. **`publish_entity_expired()` convenience function** (modelo do `publish_tool_called` existente)

3. **`get_subscribers_count(event_type: str) -> int`**  til para debug

4. **Docstring do mdulo**  atualizar para incluir novos event types

**IMPORTANTE:** No apagar nada existente. Apenas adicionar. O arquivo tem 163L  entrega mnima deve ser 180L+.

---

## PROTOCOLO DE ENTREGA

Gere DOIS handoff YAMLs:

```yaml
# DIR-DS-002-audit-logs/NC-DS-026-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-026
status: PENDING_REVIEW
timestamp: "{ISO8601}"
agent_port: {porta}
lines_added: {linhas novas}
files_modified:
  - 01_neocortex_framework/neocortex/core/utils/NC-UTL-FR-003-path-resolver.py
summary: |
  {descrio}
ajustes_aplicados:
  - get_config() como nica ncora de root_path
  - glob() para resoluo por padro
  - singleton get_path_resolver()
  - retorna None em vez de raise quando no encontrado
metrics:
  lines_real: {N}
  files_created: 1
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

```yaml
# DIR-DS-002-audit-logs/NC-DS-021-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-021
status: PENDING_REVIEW
# ... mesmos campos
files_modified:
  - 01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py
# lines_added: apenas linhas acrescentadas (no contar as 163 existentes)
```

