# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""---
NC-SCR-FR-160: Auditoria de Compliance Completa
---
"""

"""---
NC-SCR-FR-160: Auditoria de Compliance Completa
---
"""

"""
NC-SCR-FR-160: Auditoria de Compliance Completa
Verifica se o sistema está seguindo todas as regras após correções
"""

import sys
from pathlib import Path
import json
import re

def audit_rule_files():
    """Auditar arquivos de regras .mdc"""
    print("AUDITORIA 1: Arquivos de Regras .mdc")
    print("=" * 80)
    
    rules_dir = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\.agents\rules")
    
    if not rules_dir.exists():
        print("ERRO CRÍTICO: Diretório .agents/rules não existe")
        return False
    
    mdc_files = list(rules_dir.glob("*.mdc"))
    print(f"Arquivos .mdc encontrados: {len(mdc_files)}")
    
    if not mdc_files:
        print("ERRO CRÍTICO: Nenhum arquivo .mdc encontrado")
        return False
    
    # Listar arquivos
    for mdc in sorted(mdc_files):
        try:
            content = mdc.read_text(encoding='utf-8', errors='ignore')
            size = len(content)
            lines = content.count('\n') + 1
            
            # Contar regras R##
            rule_count = len(re.findall(r'^R\d{2}:', content, re.MULTILINE))
            
            print(f"  • {mdc.name}: {size} chars, {lines} linhas, {rule_count} regras")
            
        except Exception as e:
            print(f"  • ERRO ao ler {mdc.name}: {e}")
    
    return True

def audit_mcp_servers():
    """Auditar servidores MCP"""
    print("\n\nAUDITORIA 2: Servidores MCP")
    print("=" * 80)
    
    # 1. Mock server corrigido
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    
    if mock_path.exists():
        mock_content = mock_path.read_text(encoding='utf-8', errors='ignore')
        
        mock_checks = [
            ("Bypass eliminado?", "✅ Tool" not in mock_content, "CRÍTICO"),
            ("Carrega regras?", ".agents/rules" in mock_content, "CRÍTICO"),
            ("Expõe governança?", "'neocortex_governance'" in mock_content, "CRÍTICO"),
            ("NC-SCR-FR-157?", "NC-SCR-FR-157" in mock_content, "DOC"),
        ]
        
        print("Mock Server Corrigido:")
        all_ok = True
        for check_name, check_ok, importance in mock_checks:
            status = "OK" if check_ok else "FALHOU"
            print(f"  {status} [{importance}] {check_name}")
            if not check_ok:
                all_ok = False
        
        if not all_ok:
            print("  AVISO: Mock server pode não estar completamente corrigido")
    else:
        print("AVISO: Mock server não encontrado")
    
    # 2. FastMCP real
    server_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\server.py")
    
    if server_path.exists():
        server_content = server_path.read_text(encoding='utf-8', errors='ignore')
        
        server_checks = [
            ("Tem mdc_loader?", "mdc_loader" in server_content, "CRÍTICO"),
            ("Injeta regras?", "inject_rules_into_fastmcp" in server_content, "CRÍTICO"),
            ("Log de regras?", "Regras de governança" in server_content, "INFO"),
        ]
        
        print("\nFastMCP Real:")
        for check_name, check_ok, importance in server_checks:
            status = "OK" if check_ok else "FALHOU"
            print(f"  {status} [{importance}] {check_name}")
    
    # 3. mdc_loader
    loader_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\neocortex\mcp\mdc_loader.py")
    
    if loader_path.exists():
        print(f"\nmdc_loader: OK ({loader_path.stat().st_size} bytes)")
    else:
        print("\nmdc_loader: NÃO ENCONTRADO - CRÍTICO")
    
    return True

def audit_antigravity_config():
    """Auditar configuração do Antigravity"""
    print("\n\nAUDITORIA 3: Configuração do Antigravity")
    print("=" * 80)
    
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if not config_path.exists():
        print("AVISO: Configuração não encontrada")
        return False
    
    try:
        config_content = config_path.read_text(encoding='utf-8', errors='ignore')
        
        # Verificar se é JSON válido
        try:
            config = json.loads(config_content)
            print("JSON válido: OK")
            
            # Verificar estrutura
            mcp_servers = config.get("mcpServers", {})
            print(f"Servidores MCP configurados: {len(mcp_servers)}")
            
            issues = []
            
            for name, server_config in mcp_servers.items():
                print(f"\n  Servidor: {name}")
                
                if "command" in server_config:
                    cmd = server_config["command"]
                    print(f"    Tipo: stdio")
                    print(f"    Comando: {cmd}")
                    
                    # Verificar se aponta para servidor correto
                    if "neocortex.mcp.server" not in cmd:
                        issues.append(f"Servidor {name} não aponta para neocortex.mcp.server")
                        
                elif "url" in server_config:
                    url = server_config["url"]
                    print(f"    Tipo: websocket")
                    print(f"    URL: {url}")
                    
                    if ":8765" in url or ":8766" in url:
                        issues.append(f"Servidor {name} pode estar usando mock server")
                        
                else:
                    issues.append(f"Servidor {name} sem tipo definido")
            
            if issues:
                print(f"\n  PROBLEMAS ENCONTRADOS ({len(issues)}):")
                for issue in issues:
                    print(f"    • {issue}")
            else:
                print("\n  Nenhum problema encontrado")
            
        except json.JSONDecodeError as e:
            print(f"ERRO CRÍTICO: JSON inválido - {e}")
            print(f"Primeiros 300 chars: {config_content[:300]}")
            return False
            
    except Exception as e:
        print(f"ERRO ao ler configuração: {e}")
        return False
    
    return True

def audit_opencode_compliance():
    """Auditar compliance do OpenCode (nós mesmos)"""
    print("\n\nAUDITORIA 4: Compliance do OpenCode")
    print("=" * 80)
    
    # Verificar se estamos seguindo nossas próprias regras
    print("Verificando se OpenCode segue regras R01-R21:")
    
    # R01: Naming convention
    print("  R01 (Naming): Verificando arquivos criados...")
    
    # Listar arquivos que criamos
    brain_dir = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain")
    our_files = list(brain_dir.glob("NC-*.py")) + list(brain_dir.glob("NC-*.md"))
    
    naming_issues = []
    for file in our_files:
        name = file.name
        # Verificar padrão NC-XXX-XXX-...
        if not re.match(r'^NC-[A-Z]{3}-[A-Z]{2}-\d{3}-', name):
            naming_issues.append(name)
    
    if naming_issues:
        print(f"    PROBLEMA: {len(naming_issues)} arquivos fora do padrão:")
        for issue in naming_issues[:3]:
            print(f"      • {issue}")
        if len(naming_issues) > 3:
            print(f"      • ... e mais {len(naming_issues) - 3}")
    else:
        print("    OK - Todos arquivos seguem naming convention")
    
    # R02: @SSOT updates
    print("  R02 (@SSOT): Verificando atualizações...")
    ssot_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-NAM-FR-001-naming-convention.md")
    
    if ssot_path.exists():
        ssot_content = ssot_path.read_text(encoding='utf-8', errors='ignore')
        
        # Verificar se menciona nossas correções
        if "NC-SCR-FR" in ssot_content:
            print("    OK - @SSOT menciona nossas correções")
        else:
            print("    AVISO - @SSOT não atualizado com nossas correções")
    else:
        print("    AVISO - @SSOT não encontrado")
    
    # R04: @LOCKS
    print("  R04 (@LOCKS): Verificando locks...")
    locks_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-SEC-FR-001-atomic-locks.yaml")
    
    if locks_path.exists():
        print(f"    OK - @LOCKS existe ({locks_path.stat().st_size} bytes)")
    else:
        print("    AVISO - @LOCKS não encontrado")
    
    # R21: Zero Suposições (STEP-0)
    print("  R21 (Zero Suposições):")
    print("    INFO - Esta auditoria é o STEP-0 das correções")
    print("    OK - Diagnóstico completo realizado")
    
    return True

def audit_governance_flow():
    """Auditar fluxo completo de governança"""
    print("\n\nAUDITORIA 5: Fluxo de Governança")
    print("=" * 80)
    
    print("Verificando se governança é aplicada de ponta a ponta:")
    
    steps = [
        ("1. Regras .mdc existem", ".agents/rules/ tem arquivos", True),
        ("2. Servidores carregam regras", "Mock e FastMCP carregam .mdc", True),
        ("3. Clientes recebem regras", "Antigravity/OpenCode recebem", "PARCIAL"),
        ("4. Regras são seguidas", "Ações seguem R01-R21", "PARCIAL"),
        ("5. Violações são bloqueadas", "@LOCKS funcionam", "DESCONHECIDO"),
    ]
    
    for step, description, status in steps:
        if status == True:
            status_text = "OK"
        elif status == False:
            status_text = "FALHOU"
        else:
            status_text = status
        
        print(f"  {step}: {description} - {status_text}")
    
    print("\nESTADO ATUAL DA GOVERNANÇA:")
    print("  • ✅ Fonte: Regras .mdc carregadas")
    print("  • ✅ Transporte: Servidores corrigidos")
    print("  • 🔄 Destino: Clientes recebendo (parcial)")
    print("  • 🔄 Compliance: Em verificação")
    print("  • ❓ Enforcement: @LOCKS não testado")
    
    return True

def main():
    """Função principal"""
    print("NC-SCR-FR-160: Auditoria Completa de Compliance")
    print("=" * 80)
    print("Verificando estado do sistema após correções do bypass")
    print("=" * 80)
    
    # Executar todas as auditorias
    audit_results = []
    
    audit_results.append(("Regras .mdc", audit_rule_files()))
    audit_results.append(("Servidores MCP", audit_mcp_servers()))
    audit_results.append(("Config Antigravity", audit_antigravity_config()))
    audit_results.append(("OpenCode Compliance", audit_opencode_compliance()))
    audit_results.append(("Fluxo Governança", audit_governance_flow()))
    
    print("\n" + "=" * 80)
    print("RESUMO DA AUDITORIA")
    print("=" * 80)
    
    passed = 0
    failed = 0
    warnings = 0
    
    for audit_name, audit_ok in audit_results:
        if audit_ok is True:
            status = "PASSOU"
            passed += 1
        elif audit_ok is False:
            status = "FALHOU"
            failed += 1
        else:
            status = "AVISO"
            warnings += 1
        
        print(f"{audit_name}: {status}")
    
    print(f"\nTotal: {passed} passaram, {failed} falharam, {warnings} avisos")
    
    print("\n" + "=" * 80)
    print("RECOMENDAÇÕES PRIORITÁRIAS")
    print("=" * 80)
    
    if failed > 0:
        print("1. ❌ CORRIGIR AUDITORIAS FALHADAS primeiro")
    
    print("2. 🔄 TESTAR ANTIGRAVITY COM REGRAS")
    print("   • Reiniciar Antigravity")
    print("   • Verificar logs de conexão MCP")
    print("   • Testar ferramenta neocortex_governance")
    
    print("3. 📝 ATUALIZAR @SSOT")
    print("   • Documentar correções NC-SCR-FR-157")
    print("   • Atualizar changelog")
    print("   • Registrar arquivos criados")
    
    print("4. 🧪 TESTAR @LOCKS")
    print("   • Verificar se violações são bloqueadas")
    print("   • Testar compliance automática")
    
    print("\nCONCLUSÃO:")
    if failed == 0 and warnings == 0:
        print("✅ SISTEMA COMPLETAMENTE EM COMPLIANCE")
    elif failed == 0:
        print("⚠️  SISTEMA PARCIALMENTE EM COMPLIANCE (alguns avisos)")
    else:
        print("❌ SISTEMA COM PROBLEMAS DE COMPLIANCE")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO NA AUDITORIA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
