import yaml
import json
from datetime import datetime, timedelta


def load_renaming_plan():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    old_paths = set()
    for entry in data["renaming_plan"]:
        old_paths.add(entry["old_path"])
    return old_paths


def convert_to_full_path(old_path):
    # Adiciona prefixo 01_neocortex_framework/ se necessrio
    if old_path.startswith("neocortex/") or old_path.startswith("scripts/"):
        return f"01_neocortex_framework/{old_path}"
    return old_path


def load_catalog():
    catalog_path = "DIR-DOC-FR-001-docs-main/artifact_catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Criar mapeamento path -> modified
    path_to_modified = {}

    # Processar python_files
    for py_file in data.get("python_files", []):
        path = py_file.get("path", "")
        modified_str = py_file.get("modified", "")
        if path and modified_str:
            path_to_modified[path] = modified_str

    # Processar yaml_files (se existir)
    for yaml_file in data.get("yaml_files", []):
        path = yaml_file.get("path", "")
        modified_str = yaml_file.get("modified", "")
        if path and modified_str:
            path_to_modified[path] = modified_str

    # Processar json_files (se existir)
    for json_file in data.get("json_files", []):
        path = json_file.get("path", "")
        modified_str = json_file.get("modified", "")
        if path and modified_str:
            path_to_modified[path] = modified_str

    return path_to_modified


def parse_date(date_str):
    # Formato: 2026-04-14T01:38:52.805180
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        # Tentar outro formato se necessrio
        return None


def main():
    old_paths = load_renaming_plan()
    catalog = load_catalog()

    today = datetime(2026, 4, 14)
    seven_days_ago = today - timedelta(days=7)

    recent_files = []
    missing_files = []

    for old_path in sorted(old_paths):
        full_path = convert_to_full_path(old_path)
        if full_path in catalog:
            modified_str = catalog[full_path]
            mod_date = parse_date(modified_str)
            if mod_date:
                if mod_date >= seven_days_ago:
                    recent_files.append((old_path, full_path, mod_date))
            else:
                print(f"WARNING: No consegui analisar data: {modified_str}")
        else:
            missing_files.append((old_path, full_path))

    print(f"Total de arquivos nicos no plano: {len(old_paths)}")
    print(f"Arquivos encontrados no catlogo: {len(old_paths) - len(missing_files)}")
    print(f"Arquivos NO encontrados no catlogo: {len(missing_files)}")
    print(f"Arquivos modificados nos ltimos 7 dias: {len(recent_files)}")

    if missing_files:
        print("\n=== ARQUIVOS NO ENCONTRADOS NO CATLOGO ===")
        for old_path, full_path in missing_files:
            print(f"  - {old_path} (caminho completo: {full_path})")

    if recent_files:
        print("\n=== ARQUIVOS RECENTES (modificados nos ltimos 7 dias) ===")
        for old_path, full_path, mod_date in recent_files:
            print(f"  - {old_path} ({mod_date.date()})")

    # Salvar resultados em arquivo temporrio
    with open("recent_files_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Arquivos recentes (modificados desde {seven_days_ago.date()}):\n")
        for old_path, full_path, mod_date in recent_files:
            f.write(f"{old_path} | {full_path} | {mod_date}\n")


if __name__ == "__main__":
    main()
