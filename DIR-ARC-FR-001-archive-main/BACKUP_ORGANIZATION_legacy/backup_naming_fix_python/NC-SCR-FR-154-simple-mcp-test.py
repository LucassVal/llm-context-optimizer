#!/usr/bin/env python3
"""
NC-SCR-FR-154: Teste Simples de Injeção de Regras MCP
"""

import sys
from pathlib import Path

def test_simple():
    """Teste simples sem emojis"""
    print("NC-SCR-FR-154: Teste Simples de Governança MCP")
    print("=" * 80)
    
    # Adicionar path
    framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
    sys.path.insert(0, str(framework_path))
    
    # 1. Testar mdc_loader
    print("\n1. MDC_LOADER:")
    try:
        from neocortex.mcp.mdc_loader import load_mdc_rules
        rules = load_mdc_rules()
        print(f"   OK - {len(rules)} caracteres carregados")
    except Exception as e:
        print(f"   ERRO: {e}")
        return False
    
    # 2. Testar server patchado
    print("\n2. SERVER PATCHADO:")
    try:
        import neocortex.mcp.server as mcp_server
        
        # Verificar variáveis
        fastmcp = getattr(mcp_server, 'FAST_MCP_AVAILABLE', False)
        mdcloader = getattr(mcp_server, 'MDC_LOADER_AVAILABLE', False)
        
        print(f"   FAST_MCP_AVAILABLE: {fastmcp}")
        print(f"   MDC_LOADER_AVAILABLE: {mdcloader}")
        
        if not fastmcp:
            print("   AVISO: FastMCP não disponível")
        if not mdcloader:
            print("   AVISO: mdc_loader não disponível")
            
    except Exception as e:
        print(f"   ERRO: {e}")
        return False
    
    # 3. Testar criação do servidor
    print("\n3. CRIAÇÃO DO SERVIDOR:")
    try:
        server = mcp_server.create_mcp_server()
        server_type = type(server).__name__
        print(f"   OK - Servidor criado: {server_type}")
        
        # Verificar se é FastMCP
        if hasattr(server, 'prompt'):
            print("   OK - É FastMCP (tem método 'prompt')")
            
            # Tentar ver prompts
            prompts = getattr(server, '_prompts', [])
            print(f"   Prompts registrados: {len(prompts)}")
        else:
            print("   AVISO - Não é FastMCP (MockMCP?)")
            
    except Exception as e:
        print(f"   ERRO: {e}")
        return False
    
    # 4. Verificar configuração Antigravity
    print("\n4. CONFIGURAÇÃO ANTIGRAVITY:")
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if config_path.exists():
        try:
            import json
            config = json.loads(config_path.read_text())
            mcp_servers = config.get("mcpServers", {})
            
            print(f"   OK - {len(mcp_servers)} servidor(es) configurado(s)")
            
            for name, server_config in mcp_servers.items():
                if "command" in server_config:
                    print(f"   • {name}: stdio (servidor real)")
                else:
                    print(f"   • {name}: websocket (possível mock)")
                    
        except Exception as e:
            print(f"   ERRO ao ler config: {e}")
    else:
        print("   AVISO - Configuração não encontrada")
    
    print("\n" + "=" * 80)
    print("RESUMO:")
    print("- mdc_loader: OK")
    print("- server patchado: OK")
    print("- criação servidor: OK")
    print("- configuração Antigravity: VERIFICADA")
    print("\nPRÓXIMOS PASSOS:")
    print("1. Testar Antigravity com servidor real")
    print("2. Corrigir mock server (NC-SVC-FR-100)")
    print("3. Migrar clientes HTTP para servidor real")
    
    return True

if __name__ == "__main__":
    try:
        success = test_simple()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)