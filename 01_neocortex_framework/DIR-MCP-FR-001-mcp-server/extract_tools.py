#!/usr/bin/env python3
"""
Script para extrair ferramentas MCP do arquivo monolítico e gerar módulos.
"""

import re
from pathlib import Path

# Caminhos
SOURCE_FILE = Path(__file__).parent / "NC-MCP-FR-001-mcp-server.py"
TARGET_DIR = Path(__file__).parent.parent / "neocortex" / "mcp" / "tools"

# Garantir diretório de destino
TARGET_DIR.mkdir(parents=True, exist_ok=True)

# Ler conteúdo do arquivo fonte
with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Padrão para encontrar ferramentas MCP
# Procura por @mcp.tool(name="neocortex_...") seguido por def tool_...
pattern = r'(@mcp\.tool\(name="(neocortex_[a-z_]+)"\)\s*def\s+([a-z_]+)\([^)]*\)[^{]*\{[^}]+(?:\{[^}]*\}[^}]*)*\})'
# Pattern simplificado: captura desde @mcp.tool até a próxima ferramenta ou fim do arquivo
# Vamos usar uma abordagem mais simples: dividir por @mcp.tool

# Encontrar todas as ocorrências de @mcp.tool
tool_blocks = []
lines = content.split("\n")
i = 0
while i < len(lines):
    line = lines[i]
    if line.strip().startswith('@mcp.tool(name="neocortex_'):
        # Início de uma ferramenta
        start = i
        # Encontrar fim da função (linha que termina com '}' ou próxima ferramenta)
        brace_count = 0
        j = i
        while j < len(lines):
            brace_count += lines[j].count("{") - lines[j].count("}")
            if (
                brace_count == 0
                and j > start
                and (
                    lines[j].strip().startswith("@mcp.tool")
                    or lines[j].strip().startswith("def ")
                    or j == len(lines) - 1
                )
            ):
                break
            j += 1
        block = "\n".join(lines[start:j])
        tool_blocks.append(block)
        i = j
    else:
        i += 1

print(f"Encontradas {len(tool_blocks)} ferramentas")

# Processar cada bloco
for block in tool_blocks:
    # Extrair nome da ferramenta
    match = re.search(r'@mcp\.tool\(name="(neocortex_[a-z_]+)"\)', block)
    if not match:
        continue
    tool_name = match.group(1)
    print(f"Processando {tool_name}")

    # Extrair nome da função
    func_match = re.search(r"def\s+([a-z_]+)\(", block)
    func_name = (
        func_match.group(1)
        if func_match
        else f"tool_{tool_name.replace('neocortex_', '')}"
    )

    # Gerar conteúdo do módulo
    module_content = f'''#!/usr/bin/env python3
"""
NeoCortex {tool_name.replace("neocortex_", "").title()} Tool

Ferramenta MCP para {tool_name}.
"""

from typing import Dict, Any
from ...core.file_utils import read_cortex, write_cortex, read_ledger, write_ledger, find_lobes, get_lobe_content


def register_tool(mcp):
    """
    Registra a ferramenta {tool_name} no servidor MCP.
    """
{block}
    return {func_name}

'''
    # Salvar arquivo
    filename = f"{tool_name.replace('neocortex_', '')}.py"
    filepath = TARGET_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(module_content)
    print(f"  -> {filename}")

print("Extração concluída!")
