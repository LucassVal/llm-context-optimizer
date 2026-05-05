# AGENT 2  Batch Sprint Pr-MCP [2026-04-13]
<!-- Tickets: NC-DS-030, NC-DS-032, NC-DS-037 -->
<!-- Base: NC-ANA-INT-001 @SYNTHESIS | Contexto: ~30k tokens estimado -->

## CONTEXTO OBRIGATRIO (leia antes de qualquer coisa)

**Projeto:** NeoCortex Multi-Agent Framework
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
**Sua identidade:** Agent 2  sprint Fase 1 Pr-MCP

**Arquivos SSOT a consultar antes de comear:**
- `@LOCKS` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`
- `@SSOT` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
- `@SYNTHESIS` = `DIR-RES-CC-001-claude-leak-workzone/NC-ANA-INT-001-synthesis-t0.md`
- `@RES002` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-002-validation-buddy-config-plugin.md`
- `@RES003` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md`

**PROIBIDO MODIFICAR:** `server.py`, `sub_server.py`, `NC-NAM-FR-001` (@LOCKS)
**PROIBIDO MODIFICAR:** `01_neocortex_framework/neocortex/neocortex_config.yaml` (campo `@LOCKED`)

**Dependncias Python necessrias (instalar se necessrio):**
```
pip install cachetools>=5.0 ruamel.yaml>=0.18 rich>=13.0 platformdirs>=4.0
```

---

## TAREFA A  NC-DS-030: SessionMate (Stats de Sesso Gamificadas)

**Ticket:** BUDDY-001
**Esforo:** ~80L
**Write zone:** `01_neocortex_framework/neocortex/core/services/`
**Arquivo a gerar:** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-009-session-buddy.py`
**Arquivo extra:** `.nc/session_stats.json` (template exemplo em `05_examples/.nc/`)

### O que entregar
Servio de estatsticas de sesso com gamificao leve usando `rich`:

```python
class SessionMate:
    def start_session(self) -> str           # retorna session_id
    def end_session(self) -> SessionStats    # persiste em .nc/session_stats.json
    def record_task(self, ticket_id: str, status: str, duration_s: float) -> None
    def get_stats(self) -> SessionStats      # stats em tempo real
    def check_achievements(self) -> list[Achievement]  # badges desbloqueados
    def display(self) -> None               # rich output gamificado
```

### Gamificao (conquistas iniciais  5 badges)
```python
ACHIEVEMENTS = [
    Achievement("first_task", "Primeira Task! ", lambda s: s.tasks_done >= 1),
    Achievement("speed_runner", "Speed Runner ", lambda s: s.avg_duration < 300),
    Achievement("budget_master", "Budget Master ", lambda s: s.estimated_cost < 0.50),
    Achievement("marathon", "Maratona ", lambda s: s.tasks_done >= 10),
    Achievement("quality_guard", "QA Guard ", lambda s: s.approved_rate >= 0.95),
]
```

### Integrao obrigatria com NC-SVC-FR-006
**Leia** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-006-metrics-collector.py` antes de implementar.
Consumir mtricas via API do metrics-collector, **no reimplementar** coleta.

### Persistncia
Stats em `.nc/session_stats.json`:
```json
{
  "session_id": "sess-20260413-004300",
  "started_at": "2026-04-13T00:43:00",
  "tasks_done": 0,
  "tasks_approved": 0,
  "estimated_cost_usd": 0.0,
  "achievements_unlocked": [],
  "history": []
}
```

Buscar `.nc/` subindo hierarquia de diretrios (projeto  pai  raiz).

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `rich` para output gamificado (tabelas + cores + progress bars)
- `.nc/session_stats.json` para histrico entre sesses
- 3-5 badges bsicos (no mais)
- Consumir NC-SVC-FR-006, no duplicar coleta

---

## TAREFA B  NC-DS-032: ProjectConfigLoader (.nc/ Config)

**Ticket:** CONFIG-001
**Esforo:** ~150L
**Write zone:** `01_neocortex_framework/neocortex/core/config/`
**Arquivos a gerar:**
- `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-004-project-loader.py`
- `05_examples/.nc/config.yaml` (template de configurao local)

### O que entregar
Loader de configurao por projeto com hierarquia:

**Precedncia:** `.nc/config.yaml` > `~/.config/neocortex/config.yaml` > defaults

```python
class ProjectConfigLoader:
    def load(self, start_path: Path = None) -> dict    # busca .nc/ subindo dirs
    def get(self, key: str, default=None)               # acesso com default
    def get_global_path(self) -> Path                   # XDG ou APPDATA Windows
    def get_project_path(self) -> Path | None           # .nc/config.yaml atual
    def reload(self) -> None                            # recarregar sem restart
```

### Cross-platform Windows (crtico para este projeto!)
```python
from platformdirs import user_config_dir

def get_global_path(self) -> Path:
    # Windows  %APPDATA%/neocortex/config.yaml
    # Linux/Mac  ~/.config/neocortex/config.yaml
    config_dir = os.environ.get("NEOCORTEX_CONFIG_DIR")
    if config_dir:
        return Path(config_dir) / "config.yaml"
    return Path(user_config_dir("neocortex")) / "config.yaml"
```

### Campos protegidos (@LOCKED  no sobrescrever)
```python
LOCKED_FIELDS = {"server_port", "sub_server_port", "log_level", "database_path"}

def _merge(self, base: dict, override: dict) -> dict:
    for key, value in override.items():
        if key in LOCKED_FIELDS:
            logger.warning(f"Campo protegido '{key}' ignorado em config local")
            continue
        base[key] = value
    return base
```

### Usar ruamel.yaml (no PyYAML puro)
```python
from ruamel.yaml import YAML
yaml = YAML()
yaml.preserve_quotes = True
```

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `ruamel.yaml` (preserva comentrios, suporta merge)
- `platformdirs` para XDG cross-platform Windows
- Env var `NEOCORTEX_CONFIG_DIR` para override
- Buscar `.nc/` subindo hierarquia
- Campos protegidos @LOCKED no sobrescrevem

---

## TAREFA C  NC-DS-037: FeatureFlagService (Flags com Cache TTL)

**Ticket:** FLAG-001
**Esforo:** ~120L
**Write zone:** `01_neocortex_framework/neocortex/core/config/`
**Arquivo a gerar:** `01_neocortex_framework/neocortex/core/config/NC-CFG-FR-002-feature-flags.py`

### O que entregar
Servio de feature flags com cache TTL 1 hora:

```python
from cachetools import TTLCache

class FeatureFlagService:
    _cache: TTLCache  # maxsize=100, ttl=3600

    def is_enabled(self, flag: str, default: bool = False) -> bool
    def get_value(self, flag: str, default=None)
    def set_flag(self, flag: str, value, ttl: int = None) -> None
    def list_flags(self) -> dict
    def reload_from_config(self) -> None   # recarregar neocortex_config.yaml
```

### Flags pr-definidas (inicializar com defaults)
```python
DEFAULT_FLAGS = {
    "KAIROS_PUSH_NOTIFICATION": False,   # PN desabilitado por padro
    "KAIROS_CHANNELS": False,            # Channels desabilitado
    "HOOK_SYSTEM_ENABLED": True,         # Hooks habilitados
    "SESSION_MATE_ENABLED": True,        # SessionMate habilitado
    "CONFIDENCE_REVIEW_STRICT": False,   # Review estrito desabilitado
    "FEATURE_FLAGS_DEBUG": False,        # Debug de flags
}
```

### Log de ativaes (para debug)
```python
logger.debug(f"[FeatureFlag] {flag}={value} (cache_hit={from_cache}, ttl=3600s)")
```

### Integrao com neocortex_config.yaml
Ler seo `feature_flags:` do config global. Se no existir, usar `DEFAULT_FLAGS`.
**No modificar** `neocortex_config.yaml` diretamente  apenas ler.

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `cachetools.TTLCache(maxsize=100, ttl=3600)`  biblioteca madura, no implementar manualmente
- Interface simples `is_enabled(flag)` primeiro
- Logging de ativaes para debug

---

## PROTOCOLO DE ENTREGA

Execute as 3 tarefas **em sequncia** (A  B  C), gerando handoff YAML ao final de cada uma.

### Handoff por tarefa
```yaml
# DIR-DS-002-audit-logs/NC-DS-{030|032|037}-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-030  # ou 032, 037
status: PENDING_REVIEW
lines_added: <N>
files_modified:
  - path/to/file.py
summary: |
  Uma linha descrevendo o que foi entregue.
ajustes_aplicados:
  - rich para display gamificado implementado
  - .nc/session_stats.json para histrico
  - 5 badges iniciais: first_task, speed_runner, budget_master, marathon, quality_guard
```

### Checklist antes de cada handoff (R20 adaptado)
- [ ] Arquivo criado na write_zone correta
- [ ] Nome segue conveno NC-TIPO-SIGLA-NUM
- [ ] Nenhum import de server.py ou sub_server.py
- [ ] Log via `logging.getLogger(__name__)` (no print)
- [ ] Mnimo 80L de cdigo real (no placeholder)
- [ ] `platformdirs` usado em NC-DS-032 (no hardcode de path)
- [ ] `cachetools` importado em NC-DS-037
- [ ] `ruamel.yaml` usado em NC-DS-032 (no PyYAML puro)
