from __future__ import annotations
# Fix encoding for Windows (UTF-8)
"""--- NC-SCR-FR-006 — Ticket Validator v2 ---
NC-SCR-FR-006-ticket-validator.py
Valida YAMLs de ticket antes de enfileirar.

Executa: python NC-SCR-FR-006-ticket-validator.py [ticket.yaml | 08-tickets/]

Validacoes por ticket (Template v2 — NC-DS-TICKET-TEMPLATE-v2.yaml):
  OBRIGATORIO (FAIL se ausente):
    ticket_id, title, status, priority, working_directory,
    three_w (who/what/why), step_0 (lista), write_zone
  RETROCOMPAT (WARNING se ausente — tickets v1 antigos):
    forbidden_zone, exit_state, methodology
  REGRAS:
    - ticket_id: NC-DS-NNN ou NC-DS-NNN-desc (kebab)
    - working_directory: deve conter 'TURBOQUANT_V42'
    - three_w: dict com campos who, what, why
    - step_0: lista nao vazia
    - write_zone: nao vazio, nao contem @LOCKS
    - status: OPEN|IN_PROGRESS|BLOCKED|DONE|CANCELLED

Output: PASS / FAIL por ticket + relatorio final.
"""

import importlib.util
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# ============================================================================
# Configurao
# ============================================================================


def get_config():
    """Obtm configurao via get_config() do NeoCortex."""
    try:
        spec = importlib.util.spec_from_file_location(
            "config",
            Path(__file__).parent.parent / "neocortex" / "core" / "config.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.get_config()
    except Exception:
        return None


def load_yaml_simple(path: Path) -> dict:
    """Parser YAML minimalista com fallback regex."""
    try:
        import yaml

        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # fallback: l linha a linha para campos simples
        data = {}
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]
                    elif val.startswith("'") and val.endswith("'"):
                        val = val[1:-1]
                    data[key] = val
        return data


# ============================================================================
# Validaes
# ============================================================================


# Campos obrigatorios template v2
_REQUIRED_V2 = ["ticket_id", "title", "status", "priority", "working_directory",
                "three_w", "step_0", "write_zone"]
# Campos do template v1 (retrocompat: WARNING apenas, nao FAIL)
_LEGACY_V1 = ["forbidden_zone", "exit_state", "methodology"]
# Valores validos de status
_VALID_STATUS = {"OPEN", "IN_PROGRESS", "BLOCKED", "DONE", "CANCELLED",
                 "PENDING_REVIEW", "RETROSPECTIVE", "APPROVED", "FAILED"}
# @LOCKS — write_zone nao pode referenciar
_LOCKS = ["server.py", "sub_server.py", "neocortex_config.yaml"]


def validate_ticket(data: dict, ticket_path: Path) -> tuple[bool, list[str]]:
    """Valida um ticket YAML contra o template v2. Retrocompat com v1 via warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Identificar tickets legados (v1) e relatorios (DIAG)
    is_legacy = False
    num_match = re.search(r"NC-DS-(\d+)", ticket_path.name)
    if num_match and int(num_match.group(1)) < 265:
        is_legacy = True
    elif any(x in ticket_path.name for x in ["FR-", "AGT-", "IMPL-", "TEMPLATE", "DIAG-"]):
        is_legacy = True

    if is_legacy:
        warnings.append(f"[WARN] Ticket legado V1 detectado ({ticket_path.name}). Pulando validacao estrita V2.")
        return True, warnings

    # 2. Campos obrigatorios v2
    for field in _REQUIRED_V2:
        if field not in data:
            errors.append(f"[FAIL] Campo obrigatorio ausente: {field}")

    # 2. Retrocompat: campos v1 ausentes sao warnings, nao erros
    for field in _LEGACY_V1:
        if field not in data:
            warnings.append(f"[WARN] Campo legado v1 ausente (ok para template v2): {field}")

    # Emitir warnings sem bloquear
    for w in warnings:
        logger.warning(w)

    if errors:
        return False, errors

    # --- Validacoes de conteudo ---
    ticket_id: str = str(data.get("ticket_id", ""))
    write_zone: str = str(data.get("write_zone", ""))
    three_w = data.get("three_w", {})
    step_0 = data.get("step_0", [])
    working_dir: str = str(data.get("working_directory", ""))
    status: str = str(data.get("status", "")).strip('"\'')

    # 3. ticket_id: NC-DS-NNN ou NC-DS-NNN-desc (aceita kebab apos o numero)
    if not re.match(r"^NC-DS-[A-Z0-9][A-Z0-9-]*$", ticket_id):
        errors.append(f"[FAIL] ticket_id '{ticket_id}' nao segue formato NC-DS-NNN ou NC-DS-NNN-desc")

    # 4. working_directory deve conter o workspace raiz
    if "TURBOQUANT_V42" not in working_dir:
        errors.append(f"[FAIL] working_directory deve conter 'TURBOQUANT_V42': '{working_dir}'")

    # 5. three_w deve ter who, what, why
    if isinstance(three_w, dict):
        for sub in ("who", "what", "why"):
            if not three_w.get(sub, "").strip():
                errors.append(f"[FAIL] three_w.{sub} esta vazio ou ausente")
    else:
        errors.append("[FAIL] three_w deve ser um dict com who/what/why")

    # 6. step_0 deve ser lista nao vazia
    if not isinstance(step_0, list) or len(step_0) == 0:
        errors.append("[FAIL] step_0 deve ser lista nao vazia (R21)")

    # 7. write_zone nao pode conter @LOCKS
    for lock in _LOCKS:
        if lock in write_zone:
            errors.append(f"[FAIL] write_zone contem @LOCK protegido: {lock}")

    # 8. write_zone nao pode ser vazio
    if not write_zone.strip():
        errors.append("[FAIL] write_zone esta vazio")

    # 9. status deve ser valor valido
    if status and status not in _VALID_STATUS:
        errors.append(f"[FAIL] status '{status}' invalido. Validos: {sorted(_VALID_STATUS)}")

    return len(errors) == 0, errors


def validate_ticket_file(ticket_path: Path) -> tuple[bool, list[str]]:
    """Valida um arquivo de ticket."""
    try:
        data = load_yaml_simple(ticket_path)
        return validate_ticket(data, ticket_path)
    except Exception as e:
        return False, [f"Erro ao carregar YAML: {e}"]


# ============================================================================
# CLI
# ============================================================================


def main():
    """Ponto de entrada da CLI."""
    logging.basicConfig(level=logging.WARNING, format="%(message)s")

    if len(sys.argv) < 2:
        print(
            "Uso: python NC-SCR-FR-006-ticket-validator.py [ticket.yaml | DIR-DS-001-tickets/]"
        )
        sys.exit(1)

    target = Path(sys.argv[1])
    ticket_paths = []

    if target.is_dir():
        ticket_paths = list(target.glob("*.yaml")) + list(target.glob("*.yml"))
    elif target.is_file():
        ticket_paths = [target]
    else:
        print(f"Arquivo ou diretrio no encontrado: {target}")
        sys.exit(1)

    if not ticket_paths:
        print(f"Nenhum arquivo .yaml/.yml encontrado em {target}")
        sys.exit(0)

    all_pass = True
    for ticket_path in ticket_paths:
        print(f"\n--- Validando {ticket_path.name} ---")
        valid, errors = validate_ticket_file(ticket_path)

        if valid:
            print("PASS")
        else:
            all_pass = False
            print("FAIL")
            for err in errors:
                print(f"   {err}")

    if all_pass:
        print("\n[OK] Todos os tickets PASSARAM na validao.")
        sys.exit(0)
    else:
        print("\n[ERRO] Alguns tickets FALHARAM na validao.")
        sys.exit(1)


if __name__ == "__main__":
    main()
