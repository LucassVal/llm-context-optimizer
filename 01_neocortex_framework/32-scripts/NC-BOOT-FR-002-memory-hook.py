# @UBL @UBL @BOOT-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
# Script de boot para ativação automática do ConversationHook
# Gerado por NC-SCR-FR-152-activate-memory-hook.py

"""---
Módulo: NC BOOT FR 002 memory hook
---
"""

"""---
Módulo: NC BOOT FR 002 memory hook
---
"""

import sys
from pathlib import Path

# Adicionar caminho do framework
framework_path = Path(__file__).parents[2] / "01_neocortex_framework"
sys.path.insert(0, str(framework_path))

try:
    # Importar e ativar hook
    from neocortex.core.hooks.NC_HK_FR_004_conversation_hook import initialize
    
    result = initialize()
    if result.get("hook_registered"):
        print("✅ ConversationHook ativado no boot")
    else:
        print("⚠️ ConversationHook não pôde ser registrado")
        
except Exception as e:
    print(f"❌ Erro ao ativar ConversationHook: {e}")
    sys.exit(1)
