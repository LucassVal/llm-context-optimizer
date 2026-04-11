#!/usr/bin/env python3
"""
Teste rápido das ferramentas MCP modularizadas.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar o servidor (isso registrará as ferramentas)
from neocortex.mcp.server import mcp

print(f"Total de ferramentas registradas: {len(mcp.tools)}")
print("Ferramentas:", list(mcp.tools.keys()))

# Testar algumas ferramentas
if "neocortex_cortex" in mcp.tools:
    print("\nTestando neocortex_cortex...")
    func = mcp.tools["neocortex_cortex"]
    result = func("get_full")
    print(f"Resultado: {result['success']}")
    if result["success"]:
        print("Cortex carregado com sucesso")
else:
    print("Ferramenta cortex não encontrada")

if "neocortex_lobes" in mcp.tools:
    print("\nTestando neocortex_lobes...")
    func = mcp.tools["neocortex_lobes"]
    result = func("list_active")
    print(f"Resultado: {result['success']}")
    if result["success"]:
        print(f"Lobes encontrados: {len(result.get('all_lobes', []))}")

if "neocortex_checkpoint" in mcp.tools:
    print("\nTestando neocortex_checkpoint...")
    func = mcp.tools["neocortex_checkpoint"]
    result = func("get_current")
    print(f"Resultado: {result['success']}")
    if result["success"]:
        print(f"Checkpoint atual: {result.get('current_checkpoint')}")

print("\nTeste concluído!")
