# NC-PROMPT-DS-009  Agent Prompt: NC-DS-034 + NC-DS-040
# Verso: 1.0 | Data: 2026-04-13 | Template: Brockman v1
# Despachar para: Agente B (porta 44624)

---

##  GOAL

Implementar **2 componentes de qualidade e notificao**:

- **NC-DS-034 (PRIORIDADE HIGH):** Confidence Review Score (validador de handoffs automtico)
  - `01_neocortex_framework/neocortex/core/review/NC-REV-FR-001-confidence-review.py` (~150L)
  - `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-001-naming-validator.py` (~80L)
  - `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-002-compile-validator.py` (~80L)
  - `01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-003-locks-validator.py` (~80L)

- **NC-DS-040 (PRIORIDADE MDIA):** Push Notification MCP Tool
  - `01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-030-push-notification.py` (~100L)
  - **ATENO:** `NC-TOOL-FR-030-context.py` J EXISTE  verifique nome exato antes de criar

Confirme antes de criar:

```powershell
Test-Path "01_neocortex_framework\neocortex\core\review\NC-REV-FR-001-confidence-review.py"
Test-Path "01_neocortex_framework\neocortex\mcp\tools\NC-TOOL-FR-030-push-notification.py"
# Verificar conflito de nome:
Get-ChildItem "01_neocortex_framework\neocortex\mcp\tools" -Filter "*030*"
```

Se NC-TOOL-FR-030 j existir com outro nome, use NC-TOOL-FR-033-push-notification.py.

Restrio ABSOLUTA: NO modificar `server.py`, `sub_server.py` (@LOCKS).

---

##  RETURN FORMAT

Gerar **2 handoff YAMLs** em `DIR-DS-002-audit-logs/`:

```
NC-DS-034-handoff-{YYYYMMDD-HHMMSS}.yaml
NC-DS-040-handoff-{YYYYMMDD-HHMMSS}.yaml
```

```yaml
ticket_id: NC-DS-034
status: PENDING_REVIEW
timestamp: "2026-04-13THH:MM:SS-03:00"
agent_port: 44624
lines_added: <N real  soma dos 4 arquivos>
files_modified:
  - 01_neocortex_framework/neocortex/core/review/NC-REV-FR-001-confidence-review.py
  - 01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-001-naming-validator.py
  - 01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-002-compile-validator.py
  - 01_neocortex_framework/neocortex/core/review/validators/NC-VAL-FR-003-locks-validator.py
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
python --version        # 3.12.x
python -m ruff --version
python -c "
deps=['mcp','fastmcp','ruamel','rich','cachetools','platformdirs','notifypy','diskcache','duckdb','msgspec','psutil','yaml']
import importlib
for d in deps:
    try: importlib.import_module(d); print(f'OK  {d}')
    except ImportError as e: print(f'ERR {d}: {e}')
"
# Aps cada arquivo:
python -m py_compile ARQUIVO.py
python -m ruff check --fix ARQUIVO.py && python -m ruff check ARQUIVO.py
```

**R11:** NUNCA `print()`  logger. **R21:** py_compile falhar = PARE.

---

##  CONTEXT DUMP

Projeto: NeoCortex em `C:\Users\Lucas Valrio\Desktop\TURBOQUANT_V42\`
SSOT: `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`
Agent port: 44624

**Referncias  leia antes:**
- `01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-SEC-FR-001-atomic-locks.yaml`  lista de locks para NC-VAL-FR-003
- `01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py`  modelo de tool MCP existente
- `01_neocortex_framework/neocortex/core/services/NC-SVC-FR-005-event-bus.py`  integrar no NC-TOOL-FR-030 (R09)

---

## TAREFA A  NC-DS-034: ConfidenceReview (REVIEW-001)

**Ticket:** NC-DS-034
**Zona:** `01_neocortex_framework/neocortex/core/review/`
**Esforo:** ~400L total (4 arquivos)

### Interface mnima  NC-REV-FR-001-confidence-review.py

```python
"""
NC-REV-FR-001-confidence-review.py
FR-REV-001  ConfidenceReviewService: Validador de handoffs com score 0-100.

Agrega mltiplos validadores e retorna score de confiana.
Score >= 80: APPROVED | Score 50-79: NEEDS_REVIEW | Score < 50: REJECTED
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ReviewVerdict(str, Enum):
    APPROVED = "APPROVED"       # score >= 80
    NEEDS_REVIEW = "NEEDS_REVIEW"  # 50-79
    REJECTED = "REJECTED"       # < 50


@dataclass
class ValidationResult:
    validator_name: str
    passed: bool
    score: int          # 0-100
    message: str
    details: Dict = field(default_factory=dict)


@dataclass
class ReviewReport:
    ticket_id: str
    final_score: int            # mdia ponderada
    verdict: ReviewVerdict
    validations: List[ValidationResult] = field(default_factory=list)
    timestamp: str = ""


class ConfidenceReviewService:
    """Valida handoffs com score 0-100 agregando mltiplos validadores.

    Interface pblica:
      review(handoff_path: Path) -> ReviewReport
      review_dict(data: Dict) -> ReviewReport
      add_validator(name, validator_func, weight) -> None
    """

    def __init__(self):
        ...

    def review(self, handoff_path: Path) -> ReviewReport:
        """Valida um handoff YAML e retorna ReviewReport."""
        ...

    def review_dict(self, data: Dict, ticket_id: str = "unknown") -> ReviewReport:
        """Valida dicionrio de handoff diretamente."""
        ...

    def add_validator(self, name: str, validator_func, weight: float = 1.0) -> None:
        """Registra validador customizado."""
        ...


def get_review_service() -> ConfidenceReviewService:
    """Singleton."""
    ...
```

### NC-VAL-FR-001-naming-validator.py
Valida que `files_modified` seguem padro `NC-TIPO-SIGLA-NUM-desc.ext`.
- Score 100 se todos OK, penalidade de 20 por arquivo fora do padro.
- Funo: `validate(data: Dict) -> ValidationResult`

### NC-VAL-FR-002-compile-validator.py
Valida que `metrics.py_compile == "PASS"` e `metrics.ruff_check == "PASS"` no handoff.
- Tenta tambm `python -m py_compile` real em cada arquivo listado.
- Score 100 se PASS, 0 se FAIL em qualquer arquivo.
- Funo: `validate(data: Dict) -> ValidationResult`

### NC-VAL-FR-003-locks-validator.py
Valida que `files_modified` NO contm arquivos da lista `@LOCKS`.
Carrega lista de locks de `NC-SEC-FR-001-atomic-locks.yaml`.
- Score 100 se nenhum lock violado, 0 se qualquer lock modificado.
- `metrics.locks_respected` deve ser `true`.
- Funo: `validate(data: Dict) -> ValidationResult`

---

## TAREFA B  NC-DS-040: PushNotification MCP Tool (TOOL-030)

**Ticket:** NC-DS-040
**ATENO:** Verificar se NC-TOOL-FR-030 j existe. Se sim, usar NC-TOOL-FR-033.
**Esforo:** ~100L

### Interface mnima:

```python
"""
NC-TOOL-FR-033-push-notification.py  (ou 030 se disponvel)
MCP Tool: Envia notificaes push via notifypy com fallback gracioso.

Actions: push.send | push.status
Integra com NC-SVC-FR-005-event-bus.py (publicar evento POST_NOTIFICATION).
Feature flag: KAIROS_PUSH_NOTIFICATION (env var, default=False).
"""
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)

KAIROS_PUSH = os.getenv("KAIROS_PUSH_NOTIFICATION", "false").lower() in ("true", "1", "yes")


def register_tool(server) -> None:
    """Registra tool no servidor MCP."""

    @server.tool()
    async def push_notification(action: str, title: str = "", message: str = "",
                                urgency: str = "normal") -> Dict[str, Any]:
        """Envia notificao push desktop (ao: push.send | push.status).

        - push.send: Envia notificao via notifypy. Requer KAIROS_PUSH_NOTIFICATION=true.
        - push.status: Retorna disponibilidade sem enviar.
        """
        ...
```

**Restries:**
- `notifypy` com `try/except ImportError`  fallback gracioso se no instalado
- Se `KAIROS_PUSH_NOTIFICATION=false`  no enviar, retornar `{"sent": false, "reason": "feature_flag_disabled"}`
- Publicar evento `NOTIFICATION_SENT` no EventBus aps sucesso (R09 para import)

---

## PROTOCOLO DE ENTREGA

1. STEP-0  confirmar ambiente
2. Criar diretrio review: `New-Item -ItemType Directory -Force "01_neocortex_framework\neocortex\core\review\validators"`
3. Implementar NC-DS-034 (4 arquivos)  py_compile + ruff 0 erros cada
4. Verificar conflito NC-TOOL-FR-030  implementar NC-DS-040
5. Gerar 2 handoffs em `DIR-DS-002-audit-logs/`
6. NO modificar nada alm dos arquivos listados + 2 YAMLs
