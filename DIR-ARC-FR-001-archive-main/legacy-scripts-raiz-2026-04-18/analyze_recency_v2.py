import yaml
import json
from datetime import datetime, timedelta
import os


def load_renaming_plan():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    old_paths = set()
    for entry in data["renaming_plan"]:
        old_paths.add(entry["old_path"])
    return old_paths


def convert_to_catalog_path(old_path):
    # Converter caminho relativo (neocortex/...) para caminho do catlogo
    # O catlogo usa caminhos relativos  raiz com prefixo 01_neocortex_framework\
    # e separadores de acordo com o OS
    if old_path.startswith("neocortex/") or old_path.startswith("scripts/"):
        # Adicionar prefixo e normalizar separadores
        full = os.path.join("01_neocortex_framework", old_path)
    else:
        full = old_path
    # Normalizar separadores (pode ser \ ou /)
    return os.path.normpath(full)


def load_catalog():
    catalog_path = "DIR-DOC-FR-001-docs-main/artifact_catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Criar mapeamento path normalizado -> modified
    path_to_modified = {}

    # Processar python_files
    for py_file in data.get("python_files", []):
        path = py_file.get("path", "")
        modified_str = py_file.get("modified", "")
        if path and modified_str:
            norm_path = os.path.normpath(path)
            path_to_modified[norm_path] = modified_str

    # Processar yaml_files (se existir)
    for yaml_file in data.get("yaml_files", []):
        path = yaml_file.get("path", "")
        modified_str = yaml_file.get("modified", "")
        if path and modified_str:
            norm_path = os.path.normpath(path)
            path_to_modified[norm_path] = modified_str

    # Processar json_files (se existir)
    for json_file in data.get("json_files", []):
        path = json_file.get("path", "")
        modified_str = json_file.get("modified", "")
        if path and modified_str:
            norm_path = os.path.normpath(path)
            path_to_modified[norm_path] = modified_str

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
    found_files = []

    for old_path in sorted(old_paths):
        catalog_path = convert_to_catalog_path(old_path)
        if catalog_path in catalog:
            modified_str = catalog[catalog_path]
            mod_date = parse_date(modified_str)
            found_files.append((old_path, catalog_path, mod_date))
            if mod_date:
                if mod_date >= seven_days_ago:
                    recent_files.append((old_path, catalog_path, mod_date))
        else:
            missing_files.append((old_path, catalog_path))

    print(f"Total de arquivos nicos no plano: {len(old_paths)}")
    print(f"Arquivos encontrados no catlogo: {len(found_files)}")
    print(f"Arquivos NO encontrados no catlogo: {len(missing_files)}")
    print(f"Arquivos modificados nos ltimos 7 dias: {len(recent_files)}")

    if missing_files:
        print("\n=== ARQUIVOS NO ENCONTRADOS NO CATLOGO ===")
        for old_path, catalog_path in missing_files[:10]:  # limitar sada
            print(f"  - {old_path} (catalog path: {catalog_path})")
        if len(missing_files) > 10:
            print(f"  ... e mais {len(missing_files) - 10} arquivos")

    if recent_files:
        print("\n=== ARQUIVOS RECENTES (modificados nos ltimos 7 dias) ===")
        for old_path, catalog_path, mod_date in recent_files:
            print(f"  - {old_path} ({mod_date.date()})")

    # Salvar resultados em arquivo temporrio
    with open("recent_files_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Arquivos recentes (modificados desde {seven_days_ago.date()}):\n")
        for old_path, catalog_path, mod_date in recent_files:
            f.write(f"{old_path} | {catalog_path} | {mod_date}\n")


if __name__ == "__main__":
    main()
