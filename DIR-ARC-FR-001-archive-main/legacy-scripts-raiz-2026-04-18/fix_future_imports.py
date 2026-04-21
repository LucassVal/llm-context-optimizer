#!/usr/bin/env python3
from pathlib import Path

BASE_DIR = Path.cwd()

# Lista de arquivos com erro (extrada da sada anterior)
error_files = [
    "01_neocortex_framework/neocortex/core/hooks/NC-HK-FR-002-simple-hook.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-018-push-notification.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-019-project-manifest.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-021-memory.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-022-session.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-023-orchestration.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-024-governance.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-025-system.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-026-intelligence.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-027-knowledge.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-029-health.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-030-context.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-031-savepoint.py",
    "01_neocortex_framework/neocortex/mcp/tools/NC-TOOL-FR-037-hooks.py",
]

for rel_path in error_files:
    filepath = BASE_DIR / rel_path
    print(f"Processando {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ERRO leitura: {e}")
        continue

    # Encontrar linha com from __future__ import annotations
    future_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "from __future__ import annotations":
            future_idx = i
            break

    if future_idx == -1:
        print("  No encontrou importao futura")
        continue

    # Remover essa linha
    future_line = lines.pop(future_idx)

    # Inserir no incio (aps qualquer shebang ou encoding comment)
    # Mas vamos colocar logo aps o frontmatter? Vamos colocar antes do frontmatter.
    # Primeiro, encontrar o frontmatter (linhas que comeam com """---)
    front_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('"""---'):
            front_start = i
            break

    if front_start == -1:
        print("  No encontrou frontmatter")
        continue

    # Inserir future_line antes do frontmatter
    lines.insert(front_start, future_line)

    # Escrever de volta
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("  Corrigido")

print("Concludo.")
