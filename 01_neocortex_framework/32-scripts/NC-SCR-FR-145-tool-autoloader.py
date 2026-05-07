# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-SCR-FR-145: Auto-loader de ferramentas extras para MCP server
---
"""

"""---
NC-SCR-FR-145: Auto-loader de ferramentas extras para MCP server
---
"""

"""
NC-SCR-FR-145: Auto-loader de ferramentas extras para MCP server

Este script carrega dinamicamente ferramentas definidas em NC-CFG-FR-005-tool-autoload.yaml
sem modificar os arquivos @LOCK (server.py, sub_server.py).

Uso:
    from scripts.NC_SCR_FR_145_tool_autoloader import autoload
    loaded_tools = autoload(server_instance)
"""

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Configuração de logging conforme R11
logger = logging.getLogger(__name__)


def get_config() -> Dict[str, Any]:
    """
    Obtém configuração do framework conforme R10.
    
    Returns:
        Dicionário com configurações do framework
    """
    try:
        # Usar get_config do módulo config
        from neocortex.config import get_config as framework_get_config
        
        config_obj = framework_get_config()
        
        # Converter para dicionário se necessário
        if hasattr(config_obj, 'to_dict'):
            return config_obj.to_dict()
        elif hasattr(config_obj, '__dict__'):
            return config_obj.__dict__
        else:
            return {}
            
    except ImportError as e:
        logger.warning(f"Não foi possível importar neocortex.config: {e}")
        return {}


def load_yaml_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Carrega configuração YAML de ferramentas extras.
    
    Args:
        config_path: Caminho para o arquivo YAML. Se None, usa caminho padrão.
        
    Returns:
        Dicionário com configuração de ferramentas extras
    """
    if config_path is None:
        # Usar get_config para obter caminho (R10)
        config = get_config()
        project_root = config.get('project_root', Path.cwd())
        
        # Caminho padrão relativo ao projeto
        config_path = Path(project_root) / "neocortex" / "mcp" / "NC-CFG-FR-005-tool-autoload.yaml"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        if not isinstance(data, dict):
            logger.error(f"Configuração YAML inválida em {config_path}")
            return {}
            
        logger.info(f"Configuração YAML carregada de {config_path}")
        return data
        
    except FileNotFoundError:
        logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Erro ao analisar YAML {config_path}: {e}")
        return {}


def load_module_dynamic(module_path: Path, module_name: str = "dynamic_tool"):
    """
    Carrega um módulo dinamicamente usando importlib (R09).
    
    Args:
        module_path: Caminho completo para o arquivo .py
        module_name: Nome para o módulo carregado
        
    Returns:
        Módulo carregado ou None em caso de erro
    """
    if not module_path.exists():
        logger.error(f"Arquivo de módulo não encontrado: {module_path}")
        return None
    
    try:
        # Usar importlib.util conforme R09
        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        if spec is None:
            logger.error(f"Não foi possível criar spec para {module_path}")
            return None
            
        module = importlib.util.module_from_spec(spec)
        
        # Adicionar ao sys.modules para evitar recarregamento
        sys.modules[module_name] = module
        
        # Executar o módulo
        spec.loader.exec_module(module)
        
        logger.debug(f"Módulo carregado: {module_path}")
        return module
        
    except Exception as e:
        logger.error(f"Erro ao carregar módulo {module_path}: {e}")
        return None


def autoload(server_instance, config_path: Optional[Path] = None) -> List[str]:
    """
    Carrega e registra ferramentas extras definidas no YAML de configuração.
    
    Args:
        server_instance: Instância do servidor MCP (FastMCP)
        config_path: Caminho opcional para arquivo de configuração
        
    Returns:
        Lista de nomes de ferramentas carregadas com sucesso
    """
    loaded_tools = []
    
    # Carregar configuração
    config_data = load_yaml_config(config_path)
    extra_tools = config_data.get('extra_tools', [])
    
    if not extra_tools:
        logger.info("Nenhuma ferramenta extra configurada para carregar")
        return loaded_tools
    
    logger.info(f"Encontradas {len(extra_tools)} ferramentas extras para carregar")
    
    # Obter configuração do framework para caminhos
    framework_config = get_config()
    project_root = Path(framework_config.get('project_root', Path.cwd()))
    
    for tool_config in extra_tools:
        tool_name = tool_config.get('name')
        module_rel_path = tool_config.get('module_path')
        register_fn_name = tool_config.get('register_fn', 'register_tool')
        
        if not tool_name or not module_rel_path:
            logger.warning(f"Configuração de ferramenta incompleta: {tool_config}")
            continue
        
        # Construir caminho absoluto
        module_path = project_root / module_rel_path
        
        # Carregar módulo dinamicamente
        module = load_module_dynamic(module_path, f"extra_tool_{tool_name}")
        
        if module is None:
            logger.error(f"Falha ao carregar módulo para {tool_name}")
            continue
        
        # Verificar se a função de registro existe
        if not hasattr(module, register_fn_name):
            logger.error(f"Módulo {module_rel_path} não tem função '{register_fn_name}'")
            continue
        
        # Obter função de registro
        register_fn = getattr(module, register_fn_name)
        
        try:
            # Registrar ferramenta no servidor
            register_fn(server_instance)
            loaded_tools.append(tool_name)
            logger.info(f"Ferramenta '{tool_name}' registrada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao registrar ferramenta '{tool_name}': {e}")
    
    logger.info(f"Total de ferramentas carregadas: {len(loaded_tools)}")
    return loaded_tools


def main():
    """Função principal para testes."""
    # Esta função é apenas para testes de desenvolvimento
    # Em produção, use autoload() diretamente
    
    # Configurar logging para stdout
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("NC-SCR-FR-145: Teste do auto-loader de ferramentas")
    
    # Testar carregamento de configuração
    config_data = load_yaml_config()
    
    if config_data:
        extra_tools = config_data.get('extra_tools', [])
        logger.info(f"Configuração carregada: {len(extra_tools)} ferramentas extras")
        
        for tool in extra_tools:
            logger.info(f"  - {tool.get('name')}: {tool.get('description', 'Sem descrição')}")
    else:
        logger.warning("Nenhuma configuração carregada")
    
    logger.info("Teste concluído")


if __name__ == "__main__":
    main()
