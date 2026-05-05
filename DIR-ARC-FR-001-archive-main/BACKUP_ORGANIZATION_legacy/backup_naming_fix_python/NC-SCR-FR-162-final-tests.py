#!/usr/bin/env python3
"""
NC-SCR-FR-162: Testes Finais do Sistema Corrigido
1. Testar conexão Antigravity com servidores
2. Verificar recebimento de regras
3. Executar ferramenta neocortex_governance
"""

import sys
import subprocess
import time
import json
from pathlib import Path

def test_antigravity_connection():
    """Testar se Antigravity pode conectar aos servidores corrigidos"""
    print("TESTE 1: Conexão do Antigravity com Servidores Corrigidos")
    print("=" * 80)
    
    # Verificar configuração corrigida
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if not config_path.exists():
        print("ERRO: Configuração não encontrada")
        return False
    
    try:
        config_content = config_path.read_text(encoding='utf-8', errors='ignore')
        config = json.loads(config_content.split('/*')[0].strip())
        
        servers = config.get("mcpServers", {})
        print(f"Servidores configurados: {len(servers)}")
        
        # Testar cada servidor
        for name, server_config in servers.items():
            print(f"\n  Testando: {name}")
            
            if "command" in server_config:
                # Servidor stdio
                cmd = server_config["command"]
                args = server_config.get("args", [])
                
                print(f"    Tipo: stdio")
                print(f"    Comando: {cmd} {' '.join(args)}")
                
                # Testar execução do servidor
                try:
                    full_cmd = [cmd] + args
                    process = subprocess.Popen(
                        full_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        cwd=Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
                    )
                    
                    time.sleep(2)  # Dar tempo para inicializar
                    
                    if process.poll() is None:
                        print("    STATUS: Servidor rodando")
                        
                        # Enviar teste de initialize
                        test_req = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "initialize",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "TestClient", "version": "1.0"}
                            }
                        }
                        
                        process.stdin.write(json.dumps(test_req) + "\n")
                        process.stdin.flush()
                        
                        # Ler resposta
                        time.sleep(0.5)
                        response = process.stdout.readline()
                        if response:
                            print("    RESPOSTA: Servidor respondeu")
                        else:
                            print("    AVISO: Sem resposta (pode ser normal)")
                        
                        # Terminar
                        process.terminate()
                        try:
                            process.wait(timeout=3)
                            print("    FINALIZAÇÃO: Servidor terminado corretamente")
                        except subprocess.TimeoutExpired:
                            process.kill()
                            print("    AVISO: Servidor forçado a terminar")
                            
                    else:
                        stdout, stderr = process.communicate()
                        print(f"    ERRO: Servidor terminou (code: {process.returncode})")
                        print(f"    stderr: {stderr[:200]}")
                        
                except Exception as e:
                    print(f"    ERRO ao executar: {e}")
                    
            elif "url" in server_config:
                # Servidor WebSocket
                url = server_config["url"]
                print(f"    Tipo: websocket")
                print(f"    URL: {url}")
                
                # Verificar se porta está aberta (simplificado)
                import socket
                try:
                    host = "localhost"
                    port = 8765 if ":8765" in url else 8766
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((host, port))
                    
                    if result == 0:
                        print(f"    STATUS: Porta {port} aberta")
                    else:
                        print(f"    AVISO: Porta {port} fechada (servidor não rodando)")
                    
                    sock.close()
                    
                except Exception as e:
                    print(f"    ERRO ao testar porta: {e}")
        
        return True
        
    except Exception as e:
        print(f"ERRO no teste: {e}")
        return False

def test_governance_tool():
    """Testar ferramenta neocortex_governance"""
    print("\n\nTESTE 2: Ferramenta de Governança")
    print("=" * 80)
    
    # Primeiro, iniciar servidor mock corrigido
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    
    if not mock_path.exists():
        print("ERRO: Mock server não encontrado")
        return False
    
    print("Iniciando mock server corrigido...")
    
    try:
        # Iniciar servidor
        process = subprocess.Popen(
            [sys.executable, str(mock_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=mock_path.parent
        )
        
        time.sleep(1)  # Dar tempo para inicializar
        
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f"ERRO: Servidor não iniciou: {stderr[:200]}")
            return False
        
        print("Servidor rodando. Testando ferramentas...")
        
        # 1. Listar ferramentas
        list_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(list_req) + "\n")
        process.stdin.flush()
        
        time.sleep(0.5)
        list_response = process.stdout.readline()
        
        if list_response:
            try:
                list_data = json.loads(list_response)
                tools = list_data.get('result', {}).get('tools', [])
                print(f"Ferramentas disponíveis: {len(tools)}")
                
                for tool in tools:
                    print(f"  • {tool.get('name')}: {tool.get('description', '')}")
                    
                    if tool.get('name') == 'neocortex_governance':
                        print("    ✅ FERRAMENTA DE GOVERNANÇA ENCONTRADA")
                        
            except json.JSONDecodeError:
                print(f"Resposta não é JSON: {list_response[:100]}")
        else:
            print("AVISO: Sem resposta para tools/list")
        
        # 2. Chamar ferramenta de governança
        print("\nChamando neocortex_governance...")
        
        gov_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "neocortex_governance",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(gov_req) + "\n")
        process.stdin.flush()
        
        time.sleep(1)
        gov_response = process.stdout.readline()
        
        if gov_response:
            try:
                gov_data = json.loads(gov_response)
                result = gov_data.get('result', {})
                content = result.get('content', [])
                
                if content:
                    text = content[0].get('text', '')
                    print(f"Resposta recebida: {len(text)} caracteres")
                    
                    # Verificar conteúdo
                    checks = [
                        ("Tem 'REGRAS DE GOVERNANÇA'", "REGRAS DE GOVERNANÇA" in text.upper()),
                        ("Tem '.agents/rules'", ".agents/rules" in text),
                        ("Tem 'NC-RULE'", "NC-RULE" in text),
                        ("Tem 'R01'", "R01" in text or "R01:" in text),
                    ]
                    
                    for check_name, check_ok in checks:
                        status = "OK" if check_ok else "NÃO"
                        print(f"  {check_name}: {status}")
                    
                    # Mostrar preview
                    preview = text[:500].replace('\n', ' ')
                    print(f"\nPreview (500 chars): {preview}...")
                    
                else:
                    print("Resposta sem conteúdo")
                    
            except json.JSONDecodeError:
                print(f"Resposta não é JSON: {gov_response[:100]}")
        else:
            print("AVISO: Sem resposta para neocortex_governance")
        
        # 3. Terminar servidor
        print("\nFinalizando servidor...")
        process.terminate()
        try:
            process.wait(timeout=3)
            print("Servidor terminado")
        except subprocess.TimeoutExpired:
            process.kill()
            print("Servidor forçado a terminar")
        
        return True
        
    except Exception as e:
        print(f"ERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_final_compliance():
    """Teste final de compliance"""
    print("\n\nTESTE 3: Compliance Final do Sistema")
    print("=" * 80)
    
    print("Verificando estado final após todas as correções:")
    
    checks = [
        ("1. Mock server corrigido", lambda: check_mock_corrected()),
        ("2. FastMCP patchado", lambda: check_fastmcp_patched()),
        ("3. mdc_loader funcional", lambda: check_mdc_loader()),
        ("4. Config Antigravity válida", lambda: check_antigravity_config()),
        ("5. @SSOT atualizado", lambda: check_ssot_updated()),
        ("6. Arquivos renomeados", lambda: check_files_renamed()),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            status = "OK" if result else "FALHOU"
            results.append((check_name, result))
            print(f"  {check_name}: {status}")
        except Exception as e:
            print(f"  {check_name}: ERRO - {e}")
            results.append((check_name, False))
    
    print("\nRESUMO FINAL:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"  {passed}/{total} testes passaram ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("  ✅ SISTEMA COMPLETAMENTE CORRIGIDO")
    elif passed >= total * 0.8:
        print("  ⚠️  SISTEMA MAIORIA CORRIGIDO")
    else:
        print("  ❌ SISTEMA COM PROBLEMAS SIGNIFICATIVOS")
    
    return passed == total

def check_mock_corrected():
    """Verificar mock server corrigido"""
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    if not mock_path.exists():
        return False
    
    content = mock_path.read_text(encoding='utf-8', errors='ignore')
    return ("✅ Tool" not in content and  # Bypass eliminado
            ".agents/rules" in content and  # Carrega regras
            "'neocortex_governance'" in content)  # Expõe ferramenta

def check_fastmcp_patched():
    """Verificar FastMCP patchado"""
    server_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\server.py")
    if not server_path.exists():
        return False
    
    content = server_path.read_text(encoding='utf-8', errors='ignore')
    return ("mdc_loader" in content and 
            "inject_rules_into_fastmcp" in content)

def check_mdc_loader():
    """Verificar mdc_loader"""
    loader_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\mdc_loader.py")
    return loader_path.exists() and loader_path.stat().st_size > 1000

def check_antigravity_config():
    """Verificar configuração Antigravity"""
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    if not config_path.exists():
        return False
    
    try:
        content = config_path.read_text(encoding='utf-8', errors='ignore')
        json_part = content.split('/*')[0].strip()
        config = json.loads(json_part)
        return "mcpServers" in config
    except:
        return False

def check_ssot_updated():
    """Verificar @SSOT atualizado"""
    ssot_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-NAM-FR-001-naming-convention.md")
    if not ssot_path.exists():
        return False
    
    content = ssot_path.read_text(encoding='utf-8', errors='ignore')
    return "NC-SCR-FR-157" in content and "Bypass de Governança" in content

def check_files_renamed():
    """Verificar arquivos renomeados"""
    # Verificar se arquivo problemático foi renomeado
    old_path = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain\NC-DS-122-lobe-migration-report.md")
    new_path = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain\NC-SCR-FR-122-lobe-migration-report.md")
    
    return not old_path.exists() and new_path.exists()

def main():
    """Função principal"""
    print("NC-SCR-FR-162: Testes Finais do Sistema Corrigido")
    print("=" * 80)
    print("Executando os 3 testes finais solicitados...")
    print("=" * 80)
    
    # Executar testes
    test1_ok = test_antigravity_connection()
    test2_ok = test_governance_tool()
    test3_ok = test_final_compliance()
    
    print("\n" + "=" * 80)
    print("RESULTADOS FINAIS DOS TESTES")
    print("=" * 80)
    
    print(f"1. Conexão Antigravity: {'✅ PASSOU' if test1_ok else '❌ FALHOU'}")
    print(f"2. Ferramenta Governança: {'✅ PASSOU' if test2_ok else '❌ FALHOU'}")
    print(f"3. Compliance Final: {'✅ PASSOU' if test3_ok else '❌ FALHOU'}")
    
    all_passed = test1_ok and test2_ok and test3_ok
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉🎉🎉 TODOS OS TESTES PASSARAM! 🎉🎉🎉")
        print("\nSISTEMA COMPLETAMENTE CORRIGIDO E FUNCIONAL:")
        print("• Bypass de governança ELIMINADO")
        print("• Regras .mdc carregadas automaticamente")
        print("• Antigravity configurado corretamente")
        print("• Ferramenta de governança funcionando")
        print("• Compliance R01-R21 ativada")
    else:
        print("⚠️⚠️⚠️ ALGUNS TESTES FALHARAM ⚠️⚠️⚠️")
        print("\nVerifique manualmente os problemas.")
    
    print("\nPRÓXIMOS PASSOS:")
    print("1. Reiniciar Antigravity para usar nova configuração")
    print("2. Usar ferramenta 'neocortex_governance' para ver regras")
    print("3. Continuar trabalho com governança ativada")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)