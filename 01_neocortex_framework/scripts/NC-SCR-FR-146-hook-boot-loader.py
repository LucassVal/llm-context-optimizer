#!/usr/bin/env python3
"""
NC-SCR-FR-146-hook-boot-loader.py
Script de boot para carregar hooks do YAML no HookRegistry.

Objetivo: Carregar automaticamente hooks definidos em NC-CFG-HK-001-hooks.yaml
no HookRegistry durante a inicialização do sistema.

Regras:
- R09: Usar importlib.util.spec_from_file_location para importar HookRegistry
- R10: Usar get_config() para resolver path do YAML
- R11: Usar logger = logging.getLogger(__name__) — NUNCA print()
"""

import importlib.util
import logging
import sys
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_config() -> dict:
    """Obtém configuração do sistema (R10).
    
    Returns:
        Dicionário com configurações, incluindo 'project_root'.
    """
    try:
        # Tentar importar config_service
        config_path = Path(__file__).parent.parent / "neocortex" / "core" / "config_service.py"
        spec = importlib.util.spec_from_file_location("config_service", config_path)
        if spec is None:
            raise ImportError(f"Não foi possível criar spec para {config_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Obter configuração
        config = module.get_config()
        return config
        
    except Exception as e:
        logger.warning(f"Falha ao obter configuração via config_service: {e}")
        # Fallback: configuração padrão
        return {
            "project_root": Path(__file__).parent.parent,
            "hooks": {
                "config_path": "neocortex/core/hooks/NC-CFG-HK-001-hooks.yaml"
            }
        }


def load_hooks() -> List[str]:
    """Carrega hooks do YAML no HookRegistry.
    
    Returns:
        Lista de nomes de hooks carregados.
        
    Raises:
        ImportError: Se HookRegistry não puder ser importado
        FileNotFoundError: Se arquivo YAML não for encontrado
        Exception: Para outros erros durante o carregamento
    """
    # Obter configuração
    config = get_config()
    project_root = Path(config.get("project_root", Path(__file__).parent.parent))
    
    # Resolver path do YAML
    yaml_relative = config.get("hooks", {}).get("config_path", "neocortex/core/hooks/NC-CFG-HK-001-hooks.yaml")
    yaml_path = project_root / yaml_relative
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração de hooks não encontrado: {yaml_path}")
    
    logger.info(f"Carregando hooks de: {yaml_path}")
    
    # Importar HookRegistry usando importlib (R09)
    hook_registry_path = project_root / "neocortex" / "core" / "hooks" / "NC-HK-FR-001-hook-registry.py"
    
    spec = importlib.util.spec_from_file_location("hook_registry", hook_registry_path)
    if spec is None:
        raise ImportError(f"Não foi possível criar spec para {hook_registry_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Obter instância do HookRegistry
    registry = module.get_hook_registry()
    
    # Carregar hooks do YAML
    hooks_loaded = registry.load_yaml(yaml_path)
    
    if hooks_loaded == 0:
        logger.warning(f"Nenhum hook carregado de {yaml_path}")
    else:
        logger.info(f"{hooks_loaded} hook(s) carregado(s) de {yaml_path}")
    
    # Listar hooks registrados
    registered_hooks = registry.list_hooks()
    logger.info(f"Hooks registrados: {registered_hooks}")
    
    return registered_hooks


def main() -> Optional[List[str]]:
    """Função principal para carregamento de hooks.
    
    Returns:
        Lista de hooks carregados ou None em caso de erro.
    """
    try:
        hooks = load_hooks()
        return hooks
    except ImportError as e:
        logger.error(f"Erro de importação: {e}")
        return None
    except FileNotFoundError as e:
        logger.error(f"Arquivo não encontrado: {e}")
        return None
    except Exception as e:
        logger.error(f"Erro ao carregar hooks: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    # Configurar logging para teste
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("Iniciando teste de carregamento de hooks")
    
    # Teste 1: Carregar hooks
    hooks_loaded = main()
    
    if hooks_loaded is None:
        logger.error("Falha no carregamento de hooks")
        sys.exit(1)
    
    # Teste 2: Verificar se lexico_step0 foi registrado
    if "lexico_step0" in hooks_loaded:
        logger.info("✅ PASS — lexico_step0 registrado no HookRegistry")
        
        # Teste 3: Verificar instância do hook
        try:
            # Importar lexico_step0 hook
            lexico_hook_path = Path(__file__).parent.parent / "neocortex" / "core" / "hooks" / "NC-HK-FR-004-lexico-step0-hook.py"
            spec = importlib.util.spec_from_file_location("lexico_hook", lexico_hook_path)
            if spec is None:
                logger.warning("Não foi possível importar lexico_step0 hook")
            else:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Verificar se a função hook_handler existe
                if hasattr(module, "hook_handler"):
                    logger.info("✅ lexico_step0 hook_handler disponível")
                else:
                    logger.warning("lexico_step0 hook_handler não encontrado")
                    
        except Exception as e:
            logger.warning(f"Erro ao verificar lexico_step0: {e}")
            
    else:
        logger.error("❌ FAIL — lexico_step0 NÃO registrado no HookRegistry")
        logger.error(f"Hooks registrados: {hooks_loaded}")
        sys.exit(1)
    
    logger.info("Teste concluído com sucesso")
    sys.exit(0)