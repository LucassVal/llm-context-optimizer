import os
import re
import yaml


def load_mapping():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    mapping = {}
    for entry in data["renaming_plan"]:
        old = entry["old_path"]
        new = entry["new_path"]
        # Remover extenso .py se for Python
        if old.endswith(".py"):
            old_module = old[:-3].replace("/", ".")
            new_module = new[:-3].replace("/", ".")
            mapping[old_module] = new_module
        # Mapeamento para caminhos com extenso .json
        elif old.endswith(".json"):
            old_module = old  # manter caminho completo para substituio em strings
            new_module = new
            mapping[old_module] = new_module
        # Para outros arquivos, mapear caminho completo
        else:
            mapping[old] = new
    return mapping


def update_file(filepath, mapping):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    changed = False

    # Substituir ocorrncias de mdulos antigos por novos em strings (importlib)
    # Padro: import_module(".module", package=...)
    for old_mod, new_mod in mapping.items():
        # Se old_mod contm pontos (mdulo Python), podemos substituir em strings
        # Criar padro com escape
        pattern = re.compile(re.escape(old_mod))
        # Substituir apenas se no for parte de uma palavra maior
        # Usar lookarounds para garantir que no seja parte de identificador
        # Mas simplesmente substituir todas as ocorrncias pode ser perigoso.
        # Vamos fazer substituio apenas quando estiver entre aspas ou aps import_module
        # Vamos fazer uma abordagem mais simples: substituir em todo contedo
        # porque os nomes so nicos.
        new_content, count = pattern.subn(new_mod, content)
        if count > 0:
            content = new_content
            changed = True
            print(f"  Substitudo {old_mod} -> {new_mod} ({count} vezes)")

    # Tambm precisamos atualizar imports estticos (from ... import)
    # Exemplo: from neocortex.config import get_config
    # Padro: from ([\w\.]+) import
    # Vamos buscar linhas que contenham "from" e "import"
    # Isso  mais complexo; por enquanto faremos substituio simples de mdulos com pontos.
    # Para cada old_mod que termina com .py, tambm considerar o caminho relativo sem extenso
    # Mas vamos deixar para uma verso futura.

    if changed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    base_dst = "01_neocortex_framework_RENAMED"
    mapping = load_mapping()

    print(f"Mapeamento carregado: {len(mapping)} entradas")

    updated_count = 0
    total_files = 0

    for root, dirs, files in os.walk(base_dst):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                total_files += 1
                print(f"Processando: {filepath}")
                if update_file(filepath, mapping):
                    updated_count += 1

    print("\nResumo da atualizao de imports:")
    print(f"  - Arquivos Python processados: {total_files}")
    print(f"  - Arquivos atualizados: {updated_count}")


if __name__ == "__main__":
    main()
