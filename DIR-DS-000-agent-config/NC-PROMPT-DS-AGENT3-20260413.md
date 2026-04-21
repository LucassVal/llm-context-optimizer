# AGENT 3  Batch Sprint Pr-MCP [2026-04-13]
<!-- Tickets: NC-DS-034, NC-DS-038, NC-DS-040 -->
<!-- Base: NC-ANA-INT-001 @SYNTHESIS | Contexto: ~28k tokens estimado -->

## CONTEXTO OBRIGATRIO (leia antes de qualquer coisa)

**Projeto:** NeoCortex Multi-Agent Framework
**Raiz:** `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
**Sua identidade:** Agent 3  sprint Fase 1 Pr-MCP

**Arquivos SSOT a consultar antes de comear:**
- `@LOCKS` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`
- `@SSOT` = `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
- `@SYNTHESIS` = `DIR-RES-CC-001-claude-leak-workzone/NC-ANA-INT-001-synthesis-t0.md`
- `@RES001` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-001-validation-hooks-worker-review.md`
- `@RES003` = `DIR-RES-CC-001-claude-leak-workzone/NC-RES-CC-003-validation-scheduling-ttl-flags.md`

**PROIBIDO MODIFICAR:** `server.py`, `sub_server.py`, `NC-NAM-FR-001` (@LOCKS)
**DEPENDNCIA:** NC-SVC-FR-005-event-bus.py j existe  ler antes de implementar NC-DS-040

**Dependncia opcional (instalar com fallback gracioso):**
```
pip install notify-py>=0.5   # ImportError se ausente  silencia graciosamente
```

---

## TAREFA A  NC-DS-034: ConfidenceReviewService (Score 0-100)

**Ticket:** REVIEW-001
**Esforo:** ~400L
**Write zone:** `01_neocortex_framework/neocortex/core/review/`
**Arquivos a gerar:**
- `01_neocortex_framework/neocortex/core/review/NC-REV-FR-001-confidence-review.py`
- `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-001-naming-validator.py`
- `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-002-compile-validator.py`
- `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-003-locks-validator.py`

### O que entregar
Sistema de validao de handoffs com score de confiana 0-100:

```python
class ConfidenceReviewService:
    validators: list[BaseValidator]

    def review(self, handoff_path: Path) -> ReviewReport
    def add_validator(self, validator: BaseValidator) -> None
    def get_score(self, handoff_path: Path) -> float        # 0.0  100.0
    def is_approvable(self, score: float, threshold: float = 70.0) -> bool
```

### Escala e pesos (validados pela internet  no alterar)
```python
# Score = soma ponderada dos validadores / total de pesos possveis * 100
VALIDATOR_WEIGHTS = {
    "naming": 1.0,        # NC-VAL-FR-001: nome segue NC-TIPO-SIGLA-NUM?
    "compile": 2.0,       # NC-VAL-FR-002: arquivo Python compila sem erro?
    "locks": 2.0,         # NC-VAL-FR-003: no toca arquivos @LOCKS?
    "lines": 1.5,         # embutido: 80L de cdigo real?
    "handoff_format": 1.0 # embutido: YAML vlido + campos obrigatrios?
}
```

### Validadores a implementar

**NC-VAL-FR-001 (naming):**
```python
import re
PATTERN = re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}")
def validate(self, handoff: dict) -> ValidatorResult:
    files = handoff.get("files_modified", [])
    # verificar que cada arquivo segue o padro de naming
```

**NC-VAL-FR-002 (compile):**
```python
import ast
def validate(self, handoff: dict) -> ValidatorResult:
    # para cada .py em files_modified, tentar ast.parse()
    # retorna PASS se todos compilam, FAIL com detalhes de erro
```

**NC-VAL-FR-003 (locks):**
```python
LOCKED_FILES = ["server.py", "sub_server.py", "NC-NAM-FR-001-naming-convention.md"]
def validate(self, handoff: dict) -> ValidatorResult:
    # verificar que nenhum arquivo em files_modified est em @LOCKS
```

### Relatrio de sada
```python
@dataclass
class ReviewReport:
    score: float                    # 0.0  100.0
    passed: bool                    # score >= threshold
    validator_results: list[ValidatorResult]
    summary: str                    # "Score: 85.5/100  APPROVED"
    recommendations: list[str]      # sugestes de melhoria
```

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- Escala 0-100 com mdia ponderada (igual ao Claude Code)  no mudar
- Pesos configurveis via dict
- Relatrio detalhado: score por validador + comentrio + sugesto
- `radon` como plugin opcional **futuro**  NO implementar agora (apenas documentar como TODO)

### Referncias a ler ANTES de implementar
- `@RES001` seo C (ConfidenceReviewService)  padres validados
- `01_neocortex_framework/neocortex/scripts/NC-SCR-FR-005-auto-approve.py`  lgica atual (substituir)
- `batch_approve.py` (raiz)  referncia de lgica atual

---

## TAREFA B  NC-DS-038: IDValidator (Validador de IDs e Constantes)

**Ticket:** UTIL-004
**Esforo:** ~80L
**Write zone:** `01_neocortex_framework/neocortex/core/utils/`
**Arquivo a gerar:** `01_neocortex_framework/neocortex/core/utils/NC-UTL-FR-004-id-validator.py`

### O que entregar
Validador de IDs no formato NeoCortex + constantes compartilhadas:

```python
import re
import hashlib

# Constante compartilhada (importar de outros mdulos)
EXIT_CODE_PERMANENT = 42  # erros no-retentveis (padro Claude Code)

class IDValidator:
    # Padres de IDs vlidos
    PATTERNS = {
        "ticket": re.compile(r"^NC-DS-\d{3}$"),
        "worker": re.compile(r"^worker-\d{4,5}-[a-f0-9]{4}$"),
        "session": re.compile(r"^sess-\d{8}-\d{6}$"),
        "nc_file": re.compile(r"^NC-[A-Z]+-[A-Z]+-\d{3}"),
        "lobe": re.compile(r"^NC-LBE-[A-Z]+-[A-Z0-9-]+\.mdc$"),
    }

    def validate(self, id_str: str, id_type: str) -> bool
    def get_checksum(self, data: str) -> str        # SHA-256[:4] hex
    def generate_session_id(self) -> str            # sess-YYYYMMDD-HHMMSS
    def generate_worker_id(self, port: int) -> str  # worker-PORT-HASH4
    def is_permanent_error(self, exit_code: int) -> bool  # exit_code == 42
```

### Checksum para validao de integridade
```python
def get_checksum(self, data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()[:4]
```

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `re` para validar formatos NC-*  stdlib, sem deps
- `EXIT_CODE_PERMANENT = 42` exportado como constante de mdulo
- `hashlib.sha256()[:4]` para checksum lightweight

---

## TAREFA C  NC-DS-040: PushNotificationTool (MCP Tool)

**Ticket:** TOOL-030
**Esforo:** ~100L
**Write zone:** `01_neocortex_framework/neocortex/mcp/tools/`
**Arquivo a gerar:** `01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-030-push-notification.py`

### O que entregar
MCP Tool para notificaes push com fallback gracioso:

```python
# Fallback gracioso se notify-py no instalado
try:
    from notifypy import Notify
    NOTIFYPY_AVAILABLE = True
except ImportError:
    NOTIFYPY_AVAILABLE = False

class PushNotificationTool:
    urgency_levels = ["low", "normal", "high", "critical"]

    def send(self, title: str, message: str, urgency: str = "normal") -> bool
    def send_batch(self, notifications: list[dict]) -> list[bool]
    def is_available(self) -> bool    # retorna NOTIFYPY_AVAILABLE
```

### Integrao obrigatria com NC-SVC-FR-005 (EventBus)
**Leia** `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py` antes de implementar.

```python
# Publicar evento ao enviar notificao
from neocortex.core.services.NC_SVC_FR_005_event_bus import EventBus  # adaptar import

event_bus.publish("notification_sent", {
    "title": title,
    "urgency": urgency,
    "success": result,
    "timestamp": datetime.now().isoformat()
})
```

### Feature Flag Gate (verificar antes de enviar)
```python
# Verificar feature flag antes de enviar
# No importar diretamente FeatureFlagService para evitar circular import
# Usar env var como fallback: KAIROS_PUSH_NOTIFICATION=1
import os
def _is_enabled(self) -> bool:
    return os.environ.get("KAIROS_PUSH_NOTIFICATION", "0") == "1"
```

### Registro como MCP Tool
Seguir padro dos outros tools em `neocortex/mcp/tools/`:
```python
def register_tool(server):
    @server.tool("push_notification")
    async def push_notification(title: str, message: str, urgency: str = "normal") -> str:
        ...
```

### Ajustes confirmados pela internet (@SYNTHESIS CP-003)
- `notifypy` com `ImportError` fallback (se no instalado, silencia graciosamente)
- Feature flag `KAIROS_PUSH_NOTIFICATION` via env var (sem dep circular)
- Integrar NC-SVC-FR-005 EventBus para publicar evento
- Urgency levels: low / normal / high / critical
- Cdigo base disponvel em `@RES003` linhas 205-224

### Referncias a ler ANTES de implementar
- `@RES003` linhas 205-224  cdigo base entregue pelo Agent 3 anterior
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`  EventBus existente
- Outros tools em `neocortex/mcp/tools/` para seguir o padro de registro

---

## PROTOCOLO DE ENTREGA

Execute as 3 tarefas **em sequncia** (A  B  C), gerando handoff YAML ao final de cada uma.

### Handoff por tarefa
```yaml
# DIR-DS-002-audit-logs/NC-DS-{034|038|040}-handoff-{YYYYMMDD-HHMMSS}.yaml
ticket_id: NC-DS-034  # ou 038, 040
status: PENDING_REVIEW
lines_added: <N>
files_modified:
  - path/to/file.py
summary: |
  Uma linha descrevendo o que foi entregue.
ajustes_aplicados:
  - Escala 0-100 com pesos configurveis implementada
  - 3 validadores: naming, compile, locks
  - EXIT_CODE_PERMANENT=42 exportado como constante
```

### Checklist antes de cada handoff (R20 adaptado)
- [ ] Arquivo criado na write_zone correta
- [ ] Nome segue conveno NC-TIPO-SIGLA-NUM
- [ ] Nenhum import de server.py ou sub_server.py
- [ ] Log via `logging.getLogger(__name__)` (no print)
- [ ] Mnimo 80L de cdigo real (no placeholder)
- [ ] NC-DS-034: 3 validadores implementados (naming, compile, locks)
- [ ] NC-DS-038: EXIT_CODE_PERMANENT=42 exportado no nvel do mdulo
- [ ] NC-DS-040: ImportError fallback para notifypy implementado
