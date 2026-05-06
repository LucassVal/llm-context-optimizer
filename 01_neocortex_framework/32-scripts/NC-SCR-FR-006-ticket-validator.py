from __future__ import annotations
# Fix encoding for Windows (UTF-8)
"""--- NC-SCR-FR-006 — Ticket Validator ---
NC-SCR-FR-006-ticket-validator.py
Valida YAMLs de ticket antes de enfileirar.

Executa: python NC-SCR-FR-006-ticket-validator.py [ticket.yaml | DIR-DS-001-tickets/]

Validaes por ticket:
  - Campos obrigatrios: ticket_id, write_zone, forbidden_zone, exit_state, methodology
  - ticket_id segue NC-DS-NNN formato
  - write_zone != forbidden_zone (sem overlap)
  - write_zone no contm @LOCKS (server.py, sub_server.py, neocortex_config.yaml)
  - Arquivo referenciado em exit_state.files_created no existe ainda (fresh)

Output: PASS / FAIL por ticket + relatrio final.
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


def validate_ticket(data: dict, ticket_path: Path) -> tuple[bool, list[str]]:
    """Valida um nico ticket YAML."""
    errors = []

    # 1. Campos obrigatrios
    required = [
        "ticket_id",
        "write_zone",
        "forbidden_zone",
        "exit_state",
        "methodology",
    ]
    for field in required:
        if field not in data:
            errors.append(f"Campo obrigatrio ausente: {field}")

    if errors:
        return False, errors

    ticket_id = data["ticket_id"]
    write_zone = data["write_zone"]
    forbidden_zone = data.get("forbidden_zone", [])
    exit_state = data.get("exit_state", {})

    # 2. Formato ticket_id: NC-DS-NNN
    if not re.match(r"^NC-DS-\d{3}$", ticket_id):
        errors.append(f"ticket_id '{ticket_id}' no segue formato NC-DS-NNN")

    # 3. write_zone no pode estar em forbidden_zone
    if isinstance(forbidden_zone, list):
        for zone in forbidden_zone:
            if write_zone.startswith(zone) or zone.startswith(write_zone):
                errors.append(
                    f"write_zone '{write_zone}' overlap com forbidden_zone '{zone}'"
                )

    # 4. write_zone no pode conter @LOCKS
    locks = ["server.py", "sub_server.py", "neocortex_config.yaml"]
    for lock in locks:
        if lock in write_zone:
            errors.append(f"write_zone contm @LOCK: {lock}")

    # 5. Arquivos em exit_state.files_created no devem existir (fresh) - warning apenas
    files_created = exit_state.get("files_created", [])
    for file_path in files_created:
        if Path(file_path).exists():
            logger.warning(f"Arquivo j existe (pode ser esperado): {file_path}")

    # 6. write_zone deve ser um path vlido (no vazio)
    if not write_zone.strip():
        errors.append("write_zone est vazio")

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
