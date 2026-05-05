#!/usr/bin/env python3
"""
Script para iniciar MCP server corretamente
"""

import sys
import os

# Adicionar o caminho do framework ao PYTHONPATH
framework_path = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
sys.path.insert(0, framework_path)

# Definir variáveis de ambiente
os.environ["PYTHONPATH"] = framework_path
os.environ["NEOCORTEX_PROJECT_ROOT"] = framework_path
os.environ["NC_ROOT"] = r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42"
os.environ["PYTHONUTF8"] = "1"

print("Iniciando MCP Server NeoCortex...")

try:
    # Importar e executar o server
    from neocortex.mcp.server import main
    main()
except Exception as e:
    print(f"Erro ao iniciar MCP server: {e}")
    import traceback
    traceback.print_exc()