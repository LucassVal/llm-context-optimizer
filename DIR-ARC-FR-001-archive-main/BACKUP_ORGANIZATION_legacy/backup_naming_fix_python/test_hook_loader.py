#!/usr/bin/env python3
"""
Teste simplificado do hook boot loader
"""

import sys
import logging

# Configurar logging sem Unicode
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("Testando NC-SCR-FR-146-hook-boot-loader.py...")
print("=" * 60)

try:
    # Importar o módulo
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "hook_loader", 
        r"C:\Users\Lucas Valério\.gemini\antigravity\brain\NC-SCR-FR-146-hook-boot-loader.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    print("[OK] Modulo importado via importlib")
    
    # Testar get_config
    print("\nTestando get_config()...")
    config = module.get_config()
    print(f"[OK] Config carregado")
    print(f"  Project root: {getattr(config, 'project_root', 'N/A')}")
    print(f"  Hooks config: {getattr(config, 'hooks_config', 'N/A')}")
    
    # Verificar se arquivo YAML existe
    yaml_path = getattr(config, 'hooks_config', None)
    if yaml_path and hasattr(yaml_path, 'exists') and yaml_path.exists():
        print(f"[OK] Arquivo YAML encontrado: {yaml_path}")
    else:
        print(f"[ERROR] Arquivo YAML nao encontrado: {yaml_path}")
        
    # Testar load_hooks
    print("\nTestando load_hooks()...")
    try:
        hooks = module.load_hooks()
        print(f"[OK] {len(hooks)} hooks carregados")
        
        # Verificar se tem lexico_step0
        lexico_hooks = [h for h in hooks if 'lexico_step0' in str(h).lower()]
        if lexico_hooks:
            print(f"[OK] lexico_step0 encontrado nos hooks")
        else:
            print(f"[WARN] lexico_step0 nao encontrado nos hooks")
            
    except Exception as e:
        print(f"[ERROR] Erro ao carregar hooks: {e}")
        
    print("\n" + "=" * 60)
    print("[SUCCESS] Testes completos executados")
    
except Exception as e:
    print(f"[ERROR] Teste falhou: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)