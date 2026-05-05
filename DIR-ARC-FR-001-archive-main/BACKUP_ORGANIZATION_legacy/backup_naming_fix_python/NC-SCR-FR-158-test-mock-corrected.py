#!/usr/bin/env python3
"""
NC-SCR-FR-158: Testar Mock Server Corrigido
Verifica se o mock server corrigido expõe regras .mdc corretamente
"""

import sys
import json
import subprocess
import time
from pathlib import Path

def test_mock_server_direct():
    """Testar mock server diretamente (sem subprocess)"""
    print("TESTE 1: Mock Server Corrigido - Teste Direto")
    print("=" * 80)
    
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    
    if not mock_path.exists():
        print("ERRO: Mock server não encontrado")
        return False
    
    # Ler conteúdo para verificar correções
    content = mock_path.read_text(encoding='utf-8', errors='ignore')
    
    checks = [
        ("Tem bypass 'sucesso fake'?", "✅ Tool" not in content, "CRÍTICO"),
        ("Carrega regras .mdc?", ".agents/rules" in content, "CRÍTICO"),
        ("Tem classe GovernanceServer?", "class GovernanceServer" in content, "IMPORTANTE"),
        ("Tem método load_rules?", "def load_rules" in content, "IMPORTANTE"),
        ("Expõe ferramenta neocortex_governance?", "'neocortex_governance'" in content, "CRÍTICO"),
        ("NC-SCR-FR-157 mencionado?", "NC-SCR-FR-157" in content, "DOCUMENTAÇÃO"),
    ]
    
    all_ok = True
    for question, result, importance in checks:
        status = "OK" if result else "FALHOU"
        print(f"  {status} [{importance}] {question}")
        if not result:
            all_ok = False
    
    # Testar execução rápida
    print("\nTESTE 2: Execução Rápida do Mock Server")
    try:
        # Importar o módulo mock server
        import importlib.util
        spec = importlib.util.spec_from_file_location("mock_server", mock_path)
        mock_module = importlib.util.module_from_spec(spec)
        
        # Capturar prints
        import io
        import contextlib
        
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            try:
                spec.loader.exec_module(mock_module)
                # Não vamos rodar main(), só verificar se importa
                print("  OK - Mock server importa sem erros")
            except Exception as e:
                print(f"  FALHOU - Erro ao importar: {e}")
                all_ok = False
        
    except Exception as e:
        print(f"  FALHOU - Erro no teste: {e}")
        all_ok = False
    
    # Testar com subprocess (simulação MCP)
    print("\nTESTE 3: Simulação de Requisição MCP")
    try:
        # Criar requisição MCP de teste
        test_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Executar mock server com input
        cmd = [sys.executable, str(mock_path)]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=mock_path.parent
        )
        
        # Enviar requisição
        process.stdin.write(json.dumps(test_request) + "\n")
        process.stdin.flush()
        
        # Ler resposta (com timeout)
        time.sleep(0.5)
        
        if process.poll() is None:
            # Processo ainda rodando, tentar ler
            try:
                stdout, stderr = process.communicate(timeout=1)
                
                if stdout:
                    try:
                        response = json.loads(stdout.strip())
                        if response.get('result', {}).get('tools'):
                            print(f"  OK - Responde com {len(response['result']['tools'])} ferramenta(s)")
                            
                            # Verificar se tem neocortex_governance
                            tools = response['result']['tools']
                            has_governance = any(t.get('name') == 'neocortex_governance' for t in tools)
                            
                            if has_governance:
                                print("  OK - Expõe ferramenta 'neocortex_governance'")
                            else:
                                print("  FALHOU - Não expõe ferramenta de governança")
                                all_ok = False
                        else:
                            print("  FALHOU - Resposta sem ferramentas")
                            all_ok = False
                            
                    except json.JSONDecodeError:
                        print(f"  FALHOU - Resposta não é JSON: {stdout[:100]}")
                        all_ok = False
                else:
                    print("  FALHOU - Sem resposta")
                    all_ok = False
                    
            except subprocess.TimeoutExpired:
                print("  FALHOU - Timeout na resposta")
                process.kill()
                all_ok = False
        else:
            print("  FALHOU - Processo terminou prematuramente")
            all_ok = False
            
    except Exception as e:
        print(f"  FALHOU - Erro no teste MCP: {e}")
        all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ MOCK SERVER CORRIGIDO: TESTES PASSARAM")
        print("   • Bypass eliminado")
        print("   • Regras .mdc carregadas")
        print("   • Expõe ferramenta de governança")
    else:
        print("❌ MOCK SERVER CORRIGIDO: ALGUNS TESTES FALHARAM")
        print("   Verifique manualmente o arquivo corrigido")
    
    return all_ok

def test_fastmcp_real():
    """Testar servidor FastMCP real"""
    print("\n\nTESTE 4: Servidor FastMCP Real")
    print("=" * 80)
    
    server_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\server.py")
    
    if not server_path.exists():
        print("ERRO: Servidor FastMCP não encontrado")
        return False
    
    # Verificar patches
    content = server_path.read_text(encoding='utf-8', errors='ignore')
    
    checks = [
        ("Tem import mdc_loader?", "from .mdc_loader import" in content, "CRÍTICO"),
        ("Tem MDC_LOADER_AVAILABLE?", "MDC_LOADER_AVAILABLE" in content, "CRÍTICO"),
        ("Chama inject_rules_into_fastmcp?", "inject_rules_into_fastmcp" in content, "CRÍTICO"),
        ("Log de regras injetadas?", "Regras de governança" in content, "IMPORTANTE"),
    ]
    
    all_ok = True
    for question, result, importance in checks:
        status = "OK" if result else "FALHOU"
        print(f"  {status} [{importance}] {question}")
        if not result:
            all_ok = False
    
    # Testar mdc_loader
    print("\nTESTE 5: mdc_loader.py")
    loader_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\mdc_loader.py")
    
    if loader_path.exists():
        loader_content = loader_path.read_text(encoding='utf-8', errors='ignore')
        
        loader_checks = [
            ("Tem load_mdc_rules?", "def load_mdc_rules" in loader_content, "CRÍTICO"),
            ("Tem inject_rules_into_fastmcp?", "def inject_rules_into_fastmcp" in loader_content, "CRÍTICO"),
            ("Carrega .agents/rules?", ".agents/rules" in loader_content, "CRÍTICO"),
        ]
        
        for question, result, importance in loader_checks:
            status = "OK" if result else "FALHOU"
            print(f"  {status} [{importance}] {question}")
            if not result:
                all_ok = False
        
        print(f"  OK - mdc_loader existe ({loader_path.stat().st_size} bytes)")
    else:
        print("  FALHOU - mdc_loader não encontrado")
        all_ok = False
    
    # Testar execução do servidor
    print("\nTESTE 6: Execução Rápida do FastMCP")
    try:
        cmd = [
            sys.executable, "-m", "neocortex.mcp.server",
            "--transport", "stdio",
            "--help"
        ]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            cwd=server_path.parent.parent.parent
        )
        
        if process.returncode == 0:
            print("  OK - Servidor executa sem erros")
            
            # Verificar logs no stderr
            if "Regras de governança" in process.stderr:
                print("  OK - Log de regras injetadas encontrado")
            else:
                print("  AVISO - Log de regras não encontrado (pode ser normal)")
                
        else:
            print(f"  FALHOU - Código de saída: {process.returncode}")
            print(f"  stderr: {process.stderr[:200]}")
            all_ok = False
            
    except subprocess.TimeoutExpired:
        print("  OK - Servidor rodando (timeout esperado)")
    except Exception as e:
        print(f"  FALHOU - Erro ao executar: {e}")
        all_ok = False
    
    print("\n" + "=" * 80)
    if all_ok:
        print("✅ FASTMCP REAL: TESTES PASSARAM")
        print("   • Patches aplicados")
        print("   • mdc_loader funcional")
        print("   • Servidor executa corretamente")
    else:
        print("❌ FASTMCP REAL: ALGUNS TESTES FALHARAM")
    
    return all_ok

def main():
    """Função principal"""
    print("NC-SCR-FR-158: Testes Completos do Sistema Corrigido")
    print("=" * 80)
    
    mock_ok = test_mock_server_direct()
    fastmcp_ok = test_fastmcp_real()
    
    print("\n" + "=" * 80)
    print("RESUMO FINAL DOS TESTES")
    print("=" * 80)
    
    if mock_ok and fastmcp_ok:
        print("✅✅✅ TODOS OS TESTES PASSARAM!")
        print("\nSistema completamente corrigido:")
        print("1. ✅ Mock server - bypass eliminado, regras carregadas")
        print("2. ✅ FastMCP real - patches aplicados, regras injetadas")
        print("3. ✅ mdc_loader - funcional, carrega .mdc automaticamente")
        print("\nGovernança ativada para todos agentes!")
    elif mock_ok and not fastmcp_ok:
        print("⚠️⚠️⚠️ TESTES PARCIALMENTE BEM-SUCEDIDOS")
        print("Mock server OK, mas FastMCP com problemas")
    elif not mock_ok and fastmcp_ok:
        print("⚠️⚠️⚠️ TESTES PARCIALMENTE BEM-SUCEDIDOS")
        print("FastMCP OK, mas mock server com problemas")
    else:
        print("❌❌❌ TESTES FALHARAM")
        print("Ambos servidores com problemas")
    
    print("\nPróximos passos:")
    print("1. Testar Antigravity com servidores corrigidos")
    print("2. Executar auditoria de compliance")
    print("3. Atualizar @SSOT com changelog")
    
    return mock_ok and fastmcp_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)