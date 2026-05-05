import yaml


def load_renaming_plan():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["renaming_plan"]


def extract_category(new_path):
    # Extrai o prefixo da categoria do novo nome
    # Exemplo: neocortex/NC-CORE-FR-001-config.py -> NC-CORE
    # Exemplo: neocortex/mcp/NC-CORE-FR-026-server.py -> NC-CORE
    # Exemplo: neocortex/infra/NC-INFRA-FR-001-backup-restore.py -> NC-INFRA
    parts = new_path.split("/")
    for part in parts:
        if part.startswith("NC-"):
            # NC-CORE-FR-001-config.py -> NC-CORE
            category_part = part.split("-")[0] + "-" + part.split("-")[1]
            return category_part
    return None


def expected_category(old_path):
    # Mapeia diretrio para categoria esperada
    if old_path.startswith("neocortex/core/") or old_path == "neocortex/config.py":
        return "NC-CORE"
    elif old_path.startswith("neocortex/infra/"):
        return "NC-INFRA"
    elif old_path.startswith("neocortex/mcp/"):
        # Dentro de mcp, pode ser NC-CORE ou NC-MCP?
        # Vamos verificar se  tools ou no
        if old_path.startswith("neocortex/mcp/tools/"):
            return "NC-TOOL"
        else:
            return "NC-CORE"  # server.py, sub_server.py so CORE?
    elif old_path.startswith("neocortex/agent/"):
        return "NC-AGENT"
    elif old_path.startswith("neocortex/cli/"):
        return "NC-CLI"
    elif old_path.startswith("neocortex/repositories/"):
        return "NC-REPO"
    elif old_path.startswith("neocortex/schemas/"):
        return "NC-SCHEMA"
    elif old_path.startswith("scripts/"):
        return "NC-SCR"
    else:
        return None


def main():
    plan = load_renaming_plan()
    discrepancies = []

    for entry in plan:
        old_path = entry["old_path"]
        new_path = entry["new_path"]
        actual_cat = extract_category(new_path)
        expected_cat = expected_category(old_path)

        if expected_cat and actual_cat and actual_cat != expected_cat:
            discrepancies.append((old_path, new_path, expected_cat, actual_cat))

    print(f"Total de entradas no plano: {len(plan)}")
    print(f"Discrepncias de categoria encontradas: {len(discrepancies)}")

    if discrepancies:
        print("\n=== DISCREPNCIAS DE CATEGORIA ===")
        for old, new, exp, act in discrepancies:
            print(f"  - {old}")
            print(f"    Esperado: {exp}, Atual: {act}")
            print(f"    Novo caminho: {new}")
            print()

    # Verificar tambm arquivos crticos especficos
    critical_files = [
        "neocortex/config.py",
        "neocortex/mcp/server.py",
        "neocortex/core/agent_service.py",
        "neocortex/infra/ledger_store.py",
        "neocortex/mcp/tools/NC-TOOL-FR-000-brain.py",
    ]

    print("\n=== ARQUIVOS CRTICOS ===")
    for crit in critical_files:
        for entry in plan:
            if entry["old_path"] == crit:
                print(
                    f"{crit} -> {entry['new_path']} (categoria: {extract_category(entry['new_path'])})"
                )
                break


if __name__ == "__main__":
    main()
