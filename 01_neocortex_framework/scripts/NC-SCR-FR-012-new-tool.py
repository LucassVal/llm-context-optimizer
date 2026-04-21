#!/usr/bin/env python3

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.671041'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-CFG-FR-001-plugin
related_ssot:
  - NC-TOOL-FR-031-meu-tool
  - NC-SCR-FR-012-new-tool
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-012-new-tool.py
Script de scaffolding para criar um novo plugin (tool) a partir do template.

Uso:
    python NC-SCR-FR-012-new-tool.py NC-TOOL-FR-031-meu-tool

Cria uma cpia do diretrio template `NC-TOOL-FR-TEMPLATE` com o nome fornecido,
substituindo placeholders e ajustando metadados.
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

# Caminhos
ROOT = Path(__file__).parent.parent  # raiz do projeto NeoCortex
TEMPLATE_DIR = ROOT / "DIR-TMP-FR-001-templates-main" / "NC-TOOL-FR-TEMPLATE"
PLUGINS_BASE = ROOT / "neocortex" / "mcp" / "tools"  # destino sugerido para tools MCP


def validate_tool_name(name: str) -> bool:
    """Verifica se o nome segue o padro NC-TOOL-FR-NUM-*."""
    pattern = r"^NC-TOOL-FR-\d{3}-[a-z0-9\-]+$"
    return re.match(pattern, name) is not None


def copy_template(dest_dir: Path, tool_name: str) -> None:
    """Copia o template para dest_dir, substituindo placeholders."""
    if not TEMPLATE_DIR.exists():
        print(f"ERRO: Template no encontrado em {TEMPLATE_DIR}")
        sys.exit(1)

    if dest_dir.exists():
        print(f"ERRO: Diretrio destino j existe: {dest_dir}")
        sys.exit(1)

    # Copia recursivamente
    shutil.copytree(TEMPLATE_DIR, dest_dir, dirs_exist_ok=False)
    print(f"Template copiado para {dest_dir}")

    # Atualiza plugin.json
    plugin_json = dest_dir / "NC-CFG-FR-001-plugin.json"
    if plugin_json.exists():
        import json

        with open(plugin_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["name"] = tool_name
        data["version"] = "0.1.0"
        data["neocortex_min_version"] = "1.0.0"
        data["commands"] = [f"{tool_name.lower().replace('-', '_')}_command"]
        data["write_zones"] = [
            f"DIR-{tool_name.split('-')[3].upper()}/"
        ]  # ex: DIR-031/

        with open(plugin_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"  -> {plugin_json.name} atualizado")

    # Renomeia arquivos de exemplo (opcional)
    example_files = [
        dest_dir / "commands" / "NC-CMD-EXAMPLE.md",
        dest_dir / "hooks" / "NC-HK-EXAMPLE.py",
        dest_dir / "tests" / "test_example.py",
    ]
    for old_path in example_files:
        if old_path.exists():
            new_name = old_path.name.replace("EXAMPLE", tool_name.replace("-", "_"))
            new_path = old_path.parent / new_name
            old_path.rename(new_path)
            print(f"  -> {old_path.name} renomeado para {new_path.name}")

    # Atualiza referncias internas nos arquivos .py e .md
    update_file_contents(dest_dir, tool_name)


def update_file_contents(dest_dir: Path, tool_name: str) -> None:
    """Substitui placeholders 'EXAMPLE' pelo nome real do tool."""

    # Mapeamento de placeholders
    placeholders = {
        "EXAMPLE": tool_name.replace("-", "_"),
        "NC-TOOL-FR-XXX": tool_name,
        "example-command": f"{tool_name.lower().replace('-', '_')}_command",
        "DIR-EXAMPLE": f"DIR-{tool_name.split('-')[3].upper()}",
    }

    for file_path in dest_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix in (
            ".py",
            ".md",
            ".json",
            ".yaml",
            ".yml",
        ):
            try:
                content = file_path.read_text(encoding="utf-8")
                updated = content
                for old, new in placeholders.items():
                    updated = updated.replace(old, new)
                if updated != content:
                    file_path.write_text(updated, encoding="utf-8")
                    print(f"  -> placeholders substitudos em {file_path.name}")
            except UnicodeDecodeError:
                # Ignora arquivos binrios
                pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria um novo plugin a partir do template."
    )
    parser.add_argument(
        "tool_name",
        help="Nome do tool no padro NC-TOOL-FR-NUM-meu-tool (ex.: NC-TOOL-FR-031-meu-tool)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Diretrio de destino (padro: neocortex/mcp/tools/TOOL_NAME)",
    )
    args = parser.parse_args()

    if not validate_tool_name(args.tool_name):
        print(
            "ERRO: Nome invlido. Use o padro NC-TOOL-FR-NUM-meu-tool (ex.: NC-TOOL-FR-031-meu-tool)"
        )
        sys.exit(1)

    if args.output:
        dest_dir = Path(args.output).resolve()
    else:
        dest_dir = PLUGINS_BASE / args.tool_name
        dest_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"Criando plugin '{args.tool_name}' em {dest_dir}")
    copy_template(dest_dir, args.tool_name)
    print("\nPrximos passos:")
    print(f"  1. Edite o cdigofonte em {dest_dir}/")
    print(f"  2. Ajuste os metadados em {dest_dir}/NC-CFG-FR-001-plugin.json")
    print(
        "  3. Adicione o plugin ao sistema (local: .nc/plugins/, externo: entry points)"
    )
    print(f"  4. Execute os testes: pytest {dest_dir}/tests/ -v")


if __name__ == "__main__":
    main()
