#!/usr/bin/env python3
"""
NC-SCR-FR-159: Testar FastMCP Real e Antigravity
"""

import sys
import subprocess
import time
import json
from pathlib import Path

def test_fastmcp_real():
    """Testar servidor FastMCP real com regras injetadas"""
    print("TESTE: FastMCP Real com Regras Injetadas")
    print("=" * 80)
    
    # 1. Verificar patches
    server_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\server.py")
    
    if not server_path.exists():
        print("ERRO: server.py não encontrado")
        return False
    
    content = server_path.read_text(encoding='utf-8', errors='ignore')
    
    critical_patches = [
        ("mdc_loader import", "from .mdc_loader import" in content),
        ("MDC_LOADER_AVAILABLE", "MDC_LOADER_AVAILABLE" in content),
        ("inject_rules_into_fastmcp", "inject_rules_into_fastmcp" in content),
        ("Regras injetadas log", "Regras de governança" in content),
    ]
    
    all_ok = True
    for patch_name, patch_ok in critical_patches:
        status = "OK" if patch_ok else "FALHOU"
        print(f"  {status} {patch_name}")
        if not patch_ok:
            all_ok = False
    
    # 2. Testar execução
    print("\nExecutando FastMCP Server...")
    
    try:
        cmd = [
            sys.executable, "-m", "neocortex.mcp.server",
            "--transport", "stdio"
        ]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=server_path.parent.parent.parent
        )
        
        # Dar tempo para inicializar
        time.sleep(2)
        
        # Verificar stderr para logs
        stderr_output = ""
        while True:
            line = process.stderr.readline()
            if not line:
                break
            stderr_output += line
            
            # Verificar logs importantes
            if "Regras de governança" in line:
                print("  OK - Log: Regras injetadas no FastMCP")
            if "mdc_loader" in line:
                print(f"  INFO - Log mdc_loader: {line.strip()}")
        
        # Processo ainda rodando?
        if process.poll() is None:
            print("  OK - Servidor rodando")
            
            # Enviar requisição de teste
            test_req = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "TestClient",
                        "version": "1.0"
                    }
                }
            }
            
            process.stdin.write(json.dumps(test_req) + "\n")
            process.stdin.flush()
            
            # Ler resposta
            time.sleep(0.5)
            stdout_line = process.stdout.readline()
            if stdout_line:
                print("  OK - Servidor responde a initialize")
            else:
                print("  AVISO - Sem resposta a initialize")
            
            # Terminar processo
            process.terminate()
            try:
                process.wait(timeout=3)
                print("  OK - Servidor terminado corretamente")
            except subprocess.TimeoutExpired:
                process.kill()
                print("  AVISO - Servidor forcado a terminar")
                
        else:
            print(f"  FALHOU - Servidor terminou (code: {process.returncode})")
            print(f"  stderr: {stderr_output[:500]}")
            all_ok = False
            
    except Exception as e:
        print(f"  FALHOU - Erro: {e}")
        all_ok = False
    
    return all_ok

def test_antigravity_config():
    """Verificar configuração do Antigravity"""
    print("\n\nTESTE: Configuração do Antigravity")
    print("=" * 80)
    
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if not config_path.exists():
        print("AVISO: Configuração não encontrada")
        return False
    
    try:
        config_content = config_path.read_text(encoding='utf-8', errors='ignore')
        
        # Tentar parsear JSON
        try:
            config = json.loads(config_content)
            print("  OK - JSON válido")
            
            # Verificar servidores MCP
            mcp_servers = config.get("mcpServers", {})
            print(f"  Servidores MCP configurados: {len(mcp_servers)}")
            
            for name, server_config in mcp_servers.items():
                if "command" in server_config:
                    cmd = server_config["command"]
                    print(f"  • {name}: stdio - {cmd}")
                    
                    # Verificar se aponta para servidor correto
                    if "neocortex.mcp.server" in cmd:
                        print(f"    OK - Aponta para servidor FastMCP real")
                    else:
                        print(f"    AVISO - Comando diferente: {cmd}")
                        
                elif "url" in server_config:
                    url = server_config["url"]
                    print(f"  • {name}: websocket - {url}")
                    
                    if "8765" in url or "8766" in url:
                        print(f"    AVISO - Pode estar apontando para mock server")
                    else:
                        print(f"    INFO - URL diferente: {url}")
                        
            return True
            
        except json.JSONDecodeError as e:
            print(f"  FALHOU - JSON inválido: {e}")
            print(f"  Primeiros 200 chars: {config_content[:200]}")
            return False
            
    except Exception as e:
        print(f"  ERRO ao ler config: {e}")
        return False

def test_antigravity_integration():
    """Testar integração do Antigravity com MCP"""
    print("\n\nTESTE: Integração Antigravity + MCP")
    print("=" * 80)
    
    # Verificar documentação de integração
    doc_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\02_memory_lobes\$parietal\NC-LBE-USR-002-antigravity-editor-mcp.mdc")
    
    if doc_path.exists():
        doc_content = doc_path.read_text(encoding='utf-8', errors='ignore')
        
        checks = [
            ("Menciona MCP?", "MCP" in doc_content.upper()),
            ("Menciona neocortex?", "neocortex" in doc_content.lower()),
            ("Tem configuração?", "config" in doc_content.lower()),
            ("Tem comandos?", "command" in doc_content.lower()),
        ]
        
        for check_name, check_ok in checks:
            status = "OK" if check_ok else "NÃO ENCONTRADO"
            print(f"  {status} {check_name}")
        
        print(f"  Documentação: {doc_path.name} ({len(doc_content)} chars)")
    else:
        print("  AVISO: Documentação de integração não encontrada")
    
    # Verificar se Antigravity está rodando
    print("\nVerificando processo Antigravity...")
    
    try:
        # Listar processos (simplificado)
        import psutil
        
        antigravity_processes = []
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('antigravity' in str(arg).lower() for arg in cmdline):
                    antigravity_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if antigravity_processes:
            print(f"  OK - {len(antigravity_processes)} processo(s) Antigravity encontrado(s)")
            for proc in antigravity_processes[:3]:  # Mostrar até 3
                print(f"    • PID {proc.pid}: {proc.info['name']}")
        else:
            print("  INFO - Nenhum processo Antigravity encontrado (pode ser normal)")
            
    except ImportError:
        print("  INFO - psutil não disponível, pulando verificação de processos")
    except Exception as e:
        print(f"  AVISO - Erro ao verificar processos: {e}")
    
    return True

def main():
    """Função principal"""
    print("NC-SCR-FR-159: Testes FastMCP e Antigravity")
    print("=" * 80)
    
    # Testar FastMCP
    fastmcp_ok = test_fastmcp_real()
    
    # Testar configuração Antigravity
    config_ok = test_antigravity_config()
    
    # Testar integração
    integration_ok = test_antigravity_integration()
    
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    print(f"FastMCP Real: {'OK' if fastmcp_ok else 'PROBLEMAS'}")
    print(f"Config Antigravity: {'OK' if config_ok else 'PROBLEMAS'}")
    print(f"Integração: {'OK' if integration_ok else 'VERIFICAR'}")
    
    print("\nRECOMENDAÇÕES:")
    
    if fastmcp_ok:
        print("1. ✅ FastMCP real está patchado e funcionando")
    else:
        print("1. ❌ FastMCP precisa de ajustes")
    
    if config_ok:
        print("2. ✅ Configuração do Antigravity verificada")
    else:
        print("2. ❌ Configuração do Antigravity pode estar corrompida")
        print("   • Verificar arquivo JSON")
        print("   • Corrigir ou recriar configuração")
    
    print("3. 🔄 Testar Antigravity com servidor real:")
    print("   • Reiniciar Antigravity se estiver rodando")
    print("   • Verificar logs de conexão MCP")
    print("   • Testar ferramentas neocortex_*")
    
    return fastmcp_ok and config_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)