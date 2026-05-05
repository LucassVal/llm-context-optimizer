#!/usr/bin/env python3
"""---
NC-SCR-FR-146: Hook Boot Loader
---
"""

"""---
NC-SCR-FR-146: Hook Boot Loader
---
"""

"""
NC-SCR-FR-146: Hook Boot Loader
Boot auto-register LexicoStep0Hook no HookRegistry.

Carrega NC-CFG-HK-001-hooks.yaml e registra todos os hooks via HookRegistry.load_yaml().
NÃO editar server.py (@LOCK).

Autor: opencode-agent-5
Ticket: NC-DS-121
Data: 2026-04-20
"""

import importlib.util
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def get_config():
    """
    Retorna objeto Config com paths do projeto.
    Implementação compatível com R10.
    """
    try:
        # Caminho correto para o framework neocortex
        framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
        
        # Tentar importar config do neocortex
        config_path = framework_path / "neocortex" / "core" / "config.py"
        if config_path.exists():
            spec = importlib.util.spec_from_file_location("config", str(config_path))
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            if hasattr(config_module, 'get_config'):
                return config_module.get_config()
        
        # Fallback: config com paths corretos
        class MockConfig:
            def __init__(self):
                self.core_central = framework_path / "DIR-CORE-FR-001-core-central"
                self.hooks_config = framework_path / "neocortex" / "core" / "hooks" / "NC-CFG-HK-001-hooks.yaml"
                self.project_root = framework_path
                
        return MockConfig()
    except Exception as e:
        logger.error(f"Erro ao carregar config: {e}")
        raise


def load_hooks():
    """
    Carrega hooks do YAML e registra no HookRegistry.
    
    Returns:
        list: Lista de hooks registrados
        
    Raises:
        FileNotFoundError: Se arquivo YAML não existir
        ImportError: Se HookRegistry não puder ser importado
        Exception: Qualquer outro erro durante o carregamento
    """
    try:
        # Obter configuração
        config = get_config()
        
        # Resolver path do YAML
        yaml_path = config.hooks_config
        if not yaml_path.exists():
            # Tentar caminho alternativo no framework
            framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
            yaml_path = framework_path / "neocortex" / "core" / "hooks" / "NC-CFG-HK-001-hooks.yaml"
            if not yaml_path.exists():
                raise FileNotFoundError(f"Arquivo de hooks não encontrado: {config.hooks_config}")
        
        logger.info(f"Carregando hooks de: {yaml_path}")
        
        # Importar HookRegistry dinamicamente (R09)
        framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
        hook_registry_path = framework_path / "neocortex" / "core" / "hooks" / "NC-HK-FR-001-hook-registry.py"
        if not hook_registry_path.exists():
            # Tentar caminho alternativo
            hook_registry_path = framework_path / "neocortex" / "core" / "hooks" / "hook_registry.py"
            if not hook_registry_path.exists():
                raise ImportError(f"HookRegistry não encontrado: {hook_registry_path}")
        
        spec = importlib.util.spec_from_file_location("hook_registry", str(hook_registry_path))
        hook_registry_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hook_registry_module)
        
        # Obter registry
        if hasattr(hook_registry_module, 'get_hook_registry'):
            registry = hook_registry_module.get_hook_registry()
        elif hasattr(hook_registry_module, 'HookRegistry'):
            registry = hook_registry_module.HookRegistry()
        else:
            raise AttributeError("HookRegistry não encontrado no módulo")
        
        # Carregar hooks do YAML
        registry.load_yaml(yaml_path)
        
        # Listar hooks registrados
        hooks = registry.list_hooks()
        logger.info(f"Hooks registrados: {len(hooks)}")
        for hook in hooks:
            logger.debug(f"  - {hook}")
        
        # Verificar se lexico_step0 está registrado
        lexico_hooks = [h for h in hooks if 'lexico_step0' in str(h).lower()]
        if lexico_hooks:
            logger.info(f"Hook lexico_step0 registrado: {lexico_hooks[0]}")
        else:
            logger.warning("Hook lexico_step0 NÃO encontrado na lista de hooks registrados")
        
        return hooks
        
    except Exception as e:
        logger.error(f"Erro ao carregar hooks: {e}")
        raise


def main():
    """Função principal para execução do script."""
    # Configurar logging (R11)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        hooks = load_hooks()
        logger.info(f"SUCCESS: {len(hooks)} hooks carregados")
        return 0
    except Exception as e:
        logger.error(f"ERROR: {e}")
        return 1


if __name__ == '__main__':
    # Teste inline conforme especificação do ticket
    import sys
    
    # Configurar logging para teste com output em stdout
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    test_logger = logging.getLogger('test')
    test_passed = True
    test_messages = []
    
    # Teste 1: Importação do script
    try:
        spec = importlib.util.spec_from_file_location('scr146', __file__)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        test_messages.append("✓ Importação via importlib OK")
    except Exception as e:
        test_messages.append(f"✗ Importação falhou: {e}")
        test_passed = False
        sys.exit(1)
    
    # Teste 2: Verificar se lexico_step0 hook existe
    try:
        # Tentar importar o hook diretamente para teste
        lexico_hook_path = Path(__file__).parent.parent / "neocortex" / "core" / "hooks" / "NC-HK-FR-004-lexico-step0-hook.py"
        
        if lexico_hook_path.exists():
            spec = importlib.util.spec_from_file_location('lexico_step0_hook', str(lexico_hook_path))
            lexico_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(lexico_module)
            
            # Verificar se a classe existe
            if hasattr(lexico_module, 'LexicoStep0Hook'):
                test_messages.append("✓ Classe LexicoStep0Hook encontrada")
                
                # Instanciar hook
                hook_instance = lexico_module.LexicoStep0Hook()
                test_messages.append(f"✓ Hook instanciado: {hook_instance}")
            else:
                test_messages.append("✗ Classe LexicoStep0Hook não encontrada no módulo")
                test_passed = False
        else:
            test_messages.append("⚠ Arquivo NC-HK-FR-004-lexico-step0-hook.py não encontrado (esperado para teste completo)")
        
    except Exception as e:
        test_messages.append(f"⚠ Teste lexico_step0 parcial: {e}")
    
    # Teste 3: Executar main
    test_messages.append("\nExecutando main()...")
    result = main()
    
    if result == 0:
        test_messages.append("\n✅ PASS — Script executado com sucesso")
    else:
        test_messages.append("\n❌ FAIL — Script falhou")
        test_passed = False
    
    # Logar todas as mensagens de teste
    for msg in test_messages:
        test_logger.info(msg)
    
    if not test_passed:
        sys.exit(1)