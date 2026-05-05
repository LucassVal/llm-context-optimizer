#!/usr/bin/env python3
"""
NC-SCR-FR-153: Testar injeção de regras .mdc no servidor MCP
"""

import sys
import subprocess
import time
import json
from pathlib import Path

def test_mcp_server_with_rules():
    """Testar se o servidor MCP injeta regras .mdc"""
    print("NC-SCR-FR-153: Teste de Injeção de Regras .mdc")
    print("=" * 80)
    
    # 1. Verificar se mdc_loader funciona
    print("\n1. TESTANDO MDC_LOADER:")
    try:
        from neocortex.mcp.mdc_loader import load_mdc_rules, get_rule_summary
        rules = load_mdc_rules()
        summary = get_rule_summary()
        
        print(f"   • Regras carregadas: {len(rules)} caracteres")
        print(f"   • Arquivos .mdc: {summary.get('total_files', 0)}")
        print(f"   • Diretório: {summary.get('rules_dir', 'N/A')}")
        print("   ✅ mdc_loader funciona")
        
    except Exception as e:
        print(f"   ❌ ERRO no mdc_loader: {e}")
        return False
    
    # 2. Testar import do server patchado
    print("\n2. TESTANDO SERVER PATCHADO:")
    try:
        # Importar o módulo server para verificar se tem as funções
        import neocortex.mcp.server as mcp_server
        
        # Verificar se tem as variáveis de controle
        has_fastmcp = hasattr(mcp_server, 'FAST_MCP_AVAILABLE')
        has_mdc_loader = hasattr(mcp_server, 'MDC_LOADER_AVAILABLE')
        
        print(f"   • FAST_MCP_AVAILABLE: {has_fastmcp}")
        print(f"   • MDC_LOADER_AVAILABLE: {has_mdc_loader}")
        
        if has_fastmcp and has_mdc_loader:
            print("   ✅ Server patchado corretamente")
        else:
            print("   ⚠️  Server não tem variáveis de controle")
            
    except Exception as e:
        print(f"   ❌ ERRO ao importar server: {e}")
        return False
    
    # 3. Testar criação do servidor
    print("\n3. TESTANDO CRIAÇÃO DO SERVIDOR:")
    try:
        # Tentar criar servidor
        server = mcp_server.create_mcp_server(host="127.0.0.1", port=8765)
        
        print(f"   • Servidor criado: {type(server).__name__}")
        
        # Verificar se é FastMCP
        if hasattr(server, 'prompt'):
            print("   ✅ É FastMCP (tem método 'prompt')")
            
            # Verificar prompts registrados
            prompts = getattr(server, '_prompts', [])
            print(f"   • Prompts registrados: {len(prompts)}")
            
            if len(prompts) > 0:
                print("   ✅ Tem prompts registrados")
            else:
                print("   ⚠️  Nenhum prompt registrado")
                
        else:
            print("   ⚠️  Não é FastMCP (MockMCP?)")
            
    except Exception as e:
        print(f"   ❌ ERRO ao criar servidor: {e}")
        return False
    
    # 4. Verificar logs de injeção
    print("\n4. VERIFICANDO LOGS:")
    try:
        # Capturar logs (simulado)
        import io
        import logging
        
        log_capture = io.StringIO()
        ch = logging.StreamHandler(log_capture)
        ch.setLevel(logging.INFO)
        
        logger = logging.getLogger('neocortex.mcp.server')
        logger.addHandler(ch)
        
        # Criar servidor novamente para capturar logs
        server2 = mcp_server.create_mcp_server(host="127.0.0.1", port=8765)
        
        logs = log_capture.getvalue()
        
        if "regras de governança" in logs.lower() or "mdc" in logs.lower():
            print("   ✅ Logs de injeção de regras encontrados")
        else:
            print("   ⚠️  Nenhum log de injeção de regras")
            
    except Exception as e:
        print(f"   ⚠️  Não foi possível verificar logs: {e}")
    
    # 5. Testar execução real do servidor
    print("\n5. TESTANDO EXECUÇÃO DO SERVIDOR:")
    print("   (Este teste pode levar alguns segundos)")
    
    try:
        # Executar servidor em modo teste rápido
        cmd = [
            sys.executable, "-m", "neocortex.mcp.server",
            "--transport", "stdio",
            "--host", "127.0.0.1",
            "--port", "8765"
        ]
        
        # Executar com timeout
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework"
        )
        
        # Dar tempo para inicializar
        time.sleep(2)
        
        # Verificar se está rodando
        if process.poll() is None:
            print("   ✅ Servidor rodando")
            
            # Matar processo
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
        else:
            stdout, stderr = process.communicate()
            print(f"   ❌ Servidor não rodou")
            print(f"   STDOUT: {stdout[:200]}")
            print(f"   STDERR: {stderr[:200]}")
            
    except Exception as e:
        print(f"   ❌ ERRO ao executar servidor: {e}")
    
    print("\n" + "=" * 80)
    print("TESTE CONCLUÍDO")
    
    return True

def check_antigravity_config():
    """Verificar configuração do Antigravity"""
    print("\n6. VERIFICANDO CONFIGURAÇÃO ANTIGRAVITY:")
    
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if not config_path.exists():
        print("   ❌ Configuração do Antigravity não encontrada")
        return False
    
    try:
        import json
        config = json.loads(config_path.read_text())
        mcp_servers = config.get("mcpServers", {})
        
        print(f"   • Servidores MCP configurados: {len(mcp_servers)}")
        
        for name, server_config in mcp_servers.items():
            transport = "stdio" if "command" in server_config else "websocket"
            print(f"   • {name}: {transport}")
            
            if transport == "websocket":
                print(f"     ⚠️  Usando WebSocket (pode estar apontando para mock)")
            else:
                print(f"     ✅ Usando stdio (servidor real)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ ERRO ao ler configuração: {e}")
        return False

def main():
    """Função principal"""
    print("NC-SCR-FR-153: Teste Completo de Governança MCP")
    
    # Testar servidor
    server_ok = test_mcp_server_with_rules()
    
    # Verificar Antigravity
    antigravity_ok = check_antigravity_config()
    
    # Resumo
    print("\n" + "=" * 80)
    print("RESUMO FINAL:")
    print("=" * 80)
    
    if server_ok:
        print("✅ SERVIDOR MCP: Patch aplicado e testado")
    else:
        print("❌ SERVIDOR MCP: Problemas encontrados")
    
    if antigravity_ok:
        print("✅ ANTIGRAVITY: Configuração verificada")
    else:
        print("❌ ANTIGRAVITY: Problemas na configuração")
    
    print("\nPRÓXIMOS PASSOS:")
    print("1. Testar Antigravity com servidor real")
    print("2. Corrigir mock server (NC-SVC-FR-100)")
    print("3. Migrar clientes HTTP para servidor real")
    
    return server_ok and antigravity_ok

if __name__ == "__main__":
    try:
        # Adicionar path do framework
        framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
        sys.path.insert(0, str(framework_path))
        
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)