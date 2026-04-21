import yaml
import os
import shutil


def load_renaming_plan():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["renaming_plan"]


def create_mirror():
    base_src = "01_neocortex_framework"
    base_dst = "01_neocortex_framework_RENAMED"

    # Garantir que destino existe
    os.makedirs(base_dst, exist_ok=True)

    plan = load_renaming_plan()

    # Mapeamento old_path -> new_path (relativos a base_src)
    mapping = {}
    for entry in plan:
        old = entry["old_path"]
        new = entry["new_path"]
        mapping[old] = new

    # Copiar arquivos listados no plano
    copied_count = 0
    skipped_count = 0
    error_count = 0

    for old_rel, new_rel in mapping.items():
        src_path = os.path.join(base_src, old_rel)
        dst_path = os.path.join(base_dst, new_rel)

        # Verificar se arquivo de origem existe
        if not os.path.exists(src_path):
            print(f"AVISO: Arquivo de origem no encontrado: {src_path}")
            skipped_count += 1
            continue

        # Criar diretrio de destino se necessrio
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        try:
            shutil.copy2(src_path, dst_path)  # copy2 preserva metadados
            copied_count += 1
            print(f"Copiado: {old_rel} -> {new_rel}")
        except Exception as e:
            print(f"ERRO ao copiar {src_path}: {e}")
            error_count += 1

    print("\nResumo da cpia:")
    print(f"  - Arquivos copiados com sucesso: {copied_count}")
    print(f"  - Arquivos no encontrados: {skipped_count}")
    print(f"  - Erros: {error_count}")
    print(f"  - Total de entradas no plano: {len(mapping)}")

    return mapping


if __name__ == "__main__":
    create_mirror()
