import os
import shutil
import yaml


def load_renaming_plan():
    plan_path = "01_neocortex_framework/DIR-DOC-FR-001-docs-main/renaming_plan_v2.yaml"
    with open(plan_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data["renaming_plan"]


def get_copied_set():
    plan = load_renaming_plan()
    copied = set()
    for entry in plan:
        old = entry["old_path"]
        # Normalizar caminho para comparao
        copied.add(os.path.normpath(old))
    return copied


def copy_remaining():
    base_src = "01_neocortex_framework"
    base_dst = "01_neocortex_framework_RENAMED"

    copied_set = get_copied_set()

    total_copied = 0
    total_skipped = 0

    for root, dirs, files in os.walk(base_src):
        # Determinar caminho relativo em relao a base_src
        rel_root = os.path.relpath(root, base_src)
        if rel_root == ".":
            rel_root = ""

        for file in files:
            # Caminho relativo do arquivo em relao a base_src
            if rel_root:
                rel_path = os.path.join(rel_root, file)
            else:
                rel_path = file

            norm_path = os.path.normpath(rel_path)

            # Se o arquivo est na lista de j copiados (renomeados), pular
            if norm_path in copied_set:
                total_skipped += 1
                continue

            src_file = os.path.join(root, file)
            dst_file = os.path.join(base_dst, rel_path)  # manter mesmo nome

            # Criar diretrio de destino se necessrio
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)

            try:
                shutil.copy2(src_file, dst_file)
                total_copied += 1
                print(f"Copiado: {rel_path}")
            except Exception as e:
                print(f"ERRO ao copiar {src_file}: {e}")

    print("\nResumo da cpia de arquivos no listados:")
    print(f"  - Arquivos copiados: {total_copied}")
    print(f"  - Arquivos ignorados (j no plano): {total_skipped}")


if __name__ == "__main__":
    copy_remaining()
