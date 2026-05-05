#!/usr/bin/env python3
"""
NC-SCR-FR-152: Fix Governança MCP - Carregar regras .mdc no servidor real
Corrige bypass crítico identificado no sistema
"""

import sys
from pathlib import Path

# Adicionar path do framework
framework_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
sys.path.insert(0, str(framework_path))

def analyze_current_mcp():
    """Analisar estado atual do MCP"""
    print("=" * 80)
    print("NC-SCR-FR-152: ANÁLISE DO BYPASS DE GOVERNANÇA MCP")
    print("=" * 80)
    
    # 1. Verificar servidor mock
    mock_server = framework_path / "DIR-MCP-FR-001-mcp-server" / "NC-SVC-FR-100-mcp-server.py"
    print(f"\n1. SERVIDOR MOCK (HTTP :8765/8766):")
    print(f"   Path: {mock_server}")
    print(f"   Existe: {mock_server.exists()}")
    
    if mock_server.exists():
        content = mock_server.read_text(encoding='utf-8')
        if "✅ Tool" in content and "executed successfully" in content:
            print("   ❌ STATUS: MOCK CONFIRMADO - retorna 'sucesso' fake")
        else:
            print("   ⚠️  STATUS: Possível implementação real")
    
    # 2. Verificar servidor real FastMCP
    real_server = framework_path / "neocortex" / "mcp" / "server.py"
    print(f"\n2. SERVIDOR REAL (FastMCP stdio):")
    print(f"   Path: {real_server}")
    print(f"   Existe: {real_server.exists()}")
    
    if real_server.exists():
        content = real_server.read_text(encoding='utf-8', errors='ignore')
        if "fastmcp" in content.lower():
            print("   ✅ STATUS: FastMCP detectado")
        else:
            print("   ⚠️  STATUS: Não parece ser FastMCP")
        
        # Verificar se carrega .mdc
        if ".mdc" in content or ".agents/rules" in content:
            print("   ✅ Carrega regras .mdc")
        else:
            print("   ❌ NÃO carrega regras .mdc")
    
    # 3. Verificar regras .mdc
    rules_dir = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\.agents\rules")
    print(f"\n3. REGRAS .MDC:")
    print(f"   Path: {rules_dir}")
    print(f"   Existe: {rules_dir.exists()}")
    
    if rules_dir.exists():
        mdc_files = list(rules_dir.glob("*.mdc"))
        print(f"   Arquivos encontrados: {len(mdc_files)}")
        for mdc in mdc_files[:5]:
            print(f"   • {mdc.name}")
        if len(mdc_files) > 5:
            print(f"   ... e mais {len(mdc_files) - 5}")
    
    # 4. Configuração Antigravity
    print(f"\n4. CONFIGURAÇÃO ANTIGRAVITY:")
    antigravity_config = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    print(f"   Path: {antigravity_config}")
    print(f"   Existe: {antigravity_config.exists()}")
    
    if antigravity_config.exists():
        import json
        config = json.loads(antigravity_config.read_text())
        mcp_servers = config.get("mcpServers", {})
        print(f"   Servidores configurados: {len(mcp_servers)}")
        for name, server_config in mcp_servers.items():
            transport = "stdio" if "command" in server_config else "websocket"
            print(f"   • {name}: {transport}")
    
    print("\n" + "=" * 80)
    print("DIAGNÓSTICO COMPLETO")

def create_mdc_loader_patch():
    """Criar patch para carregar .mdc no servidor FastMCP"""
    patch_content = '''"""
NC-PATCH-FR-001: Carregador de Regras .mdc para FastMCP
Patch para injetar governança no servidor MCP real
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

def load_mdc_rules(rules_dir: Optional[Path] = None) -> str:
    """
    Carrega todas as regras .mdc do diretório .agents/rules/
    
    Args:
        rules_dir: Diretório das regras. Se None, usa padrão do projeto.
    
    Returns:
        Texto consolidado de todas as regras
    """
    if rules_dir is None:
        # Tentar encontrar diretório do projeto
        project_root = Path(__file__).parent.parent.parent.parent
        rules_dir = project_root / ".agents" / "rules"
    
    if not rules_dir.exists():
        return "⚠️ Diretório de regras não encontrado: .agents/rules/"
    
    rules_text = "# REGRAS DE GOVERNANÇA NEOcORTEX\\n\\n"
    rules_text += "> Carregadas automaticamente do diretório .agents/rules/\\n\\n"
    
    mdc_files = list(rules_dir.glob("*.mdc"))
    if not mdc_files:
        return "⚠️ Nenhum arquivo .mdc encontrado"
    
    for mdc_file in sorted(mdc_files):
        try:
            content = mdc_file.read_text(encoding='utf-8')
            # Extrair título do arquivo (primeira linha após ---)
            lines = content.split('\\n')
            title = mdc_file.stem
            for i, line in enumerate(lines):
                if line.strip().startswith('description:'):
                    # Extrair descrição do YAML frontmatter
                    desc = line.split('description:')[1].strip().strip('"')
                    title = desc
                    break
            
            rules_text += f"## {title}\\n"
            rules_text += f"*Arquivo: {mdc_file.name}*\\n\\n"
            
            # Adicionar conteúdo (limitar a 50 linhas por arquivo)
            content_lines = content.split('\\n')
            added_lines = 0
            in_frontmatter = False
            
            for line in content_lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                if in_frontmatter:
                    continue
                if line.strip() and not line.strip().startswith('<!--'):
                    rules_text += line + '\\n'
                    added_lines += 1
                    if added_lines >= 50:
                        rules_text += "...\\n\\n"
                        break
            
            rules_text += "\\n---\\n\\n"
            
        except Exception as e:
            rules_text += f"⚠️ Erro ao ler {mdc_file.name}: {e}\\n\\n"
    
    return rules_text

def inject_rules_into_fastmcp():
    """
    Função para injetar no servidor FastMCP existente
    
    Uso no server.py:
    
    # Adicionar no início do arquivo:
    from neocortex.mcp.mdc_loader import load_mdc_rules
    
    # Adicionar após criar o servidor FastMCP:
    @server.prompt()
    def governance_rules():
        return load_mdc_rules()
    """
    return {
        "load_mdc_rules": load_mdc_rules,
        "inject_rules_into_fastmcp": inject_rules_into_fastmcp
    }

if __name__ == "__main__":
    # Testar carregamento
    rules = load_mdc_rules()
    print(f"Regras carregadas ({len(rules)} caracteres):")
    print("=" * 80)
    print(rules[:500] + "..." if len(rules) > 500 else rules)
    print("=" * 80)
'''
    
    patch_path = framework_path / "neocortex" / "mcp" / "mdc_loader.py"
    
    print(f"\nCriando patch em: {patch_path}")
    
    # Verificar se diretório existe
    patch_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Escrever patch
    patch_path.write_text(patch_content, encoding='utf-8')
    
    print(f"✅ Patch criado: {patch_path}")
    
    return patch_path

def create_server_patch():
    """Criar patch para o server.py FastMCP"""
    server_path = framework_path / "neocortex" / "mcp" / "server.py"
    
    if not server_path.exists():
        print(f"❌ Servidor não encontrado: {server_path}")
        return None
    
    content = server_path.read_text(encoding='utf-8')
    
    # Verificar se já tem import do mdc_loader
    if "mdc_loader" in content:
        print("✅ Servidor já tem import do mdc_loader")
        return server_path
    
    # Encontrar onde adicionar o import
    lines = content.split('\n')
    new_lines = []
    import_added = False
    prompt_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # Adicionar import após outros imports do neocortex
        if not import_added and "from neocortex" in line and "mdc_loader" not in content:
            new_lines.append("from neocortex.mcp.mdc_loader import load_mdc_rules")
            import_added = True
        
        # Adicionar prompt após criação do servidor
        if not prompt_added and "fastmcp.Server(" in line:
            new_lines.append("")
            new_lines.append("# Injetar regras de governança")
            new_lines.append("@server.prompt()")
            new_lines.append("def governance_rules():")
            new_lines.append("    \"\"\"Regras obrigatórias do NeoCortex\"\"\"")
            new_lines.append("    return load_mdc_rules()")
            new_lines.append("")
            prompt_added = True
    
    if import_added or prompt_added:
        # Criar backup
        backup_path = server_path.with_suffix('.py.backup')
        server_path.rename(backup_path)
        print(f"✅ Backup criado: {backup_path}")
        
        # Escrever novo conteúdo
        server_path.write_text('\n'.join(new_lines), encoding='utf-8')
        print(f"✅ Servidor patchado: {server_path}")
        
        if import_added:
            print("   • Import do mdc_loader adicionado")
        if prompt_added:
            print("   • Prompt de governança adicionado")
        
        return server_path
    else:
        print("⚠️  Não foi possível aplicar patch (estrutura diferente)")
        return None

def create_fix_plan():
    """Criar plano completo de correção"""
    print("\n" + "=" * 80)
    print("PLANO DE CORREÇÃO DO BYPASS DE GOVERNANÇA")
    print("=" * 80)
    
    plan = """
ETAPA 1: CORRIGIR SERVIDOR REAL (CRÍTICO)
-----------------------------------------
1. Criar mdc_loader.py para carregar regras .mdc
2. Patch server.py FastMCP para injetar regras
3. Testar com Antigravity (stdio)

ETAPA 2: MIGRAR CLIENTES HTTP (IMPORTANTE)
------------------------------------------
1. Modificar NC-SVC-FR-100 para redirecionar para real
   OU
2. Implementar HTTP/SSE no servidor FastMCP real
3. Atualizar configuração de todos clientes

ETAPA 3: VALIDAÇÃO (ESSENCIAL)
------------------------------
1. Testar se Antigravity recebe regras
2. Testar se OpenCode (HTTP) recebe regras
3. Verificar compliance com @BOOT

ETAPA 4: DOCUMENTAÇÃO (MANUTENÇÃO)
----------------------------------
1. Atualizar @BOOT com arquitetura corrigida
2. Documentar fluxo de governança
3. Criar procedimento de auditoria
"""
    
    print(plan)
    
    # Ações imediatas
    print("\nAÇÕES IMEDIATAS (HOJE):")
    print("1. Executar análise atual (esta função)")
    print("2. Criar patch mdc_loader.py")
    print("3. Aplicar patch ao server.py")
    print("4. Testar carregamento de regras")
    
    return plan

def main():
    """Função principal"""
    print("NC-SCR-FR-152: Correção do Bypass de Governança MCP")
    
    # 1. Analisar situação atual
    analyze_current_mcp()
    
    # 2. Criar plano
    create_fix_plan()
    
    # 3. Perguntar ao usuário
    print("\n" + "=" * 80)
    print("PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("\nVocê quer que eu:")
    print("1. Crie o patch mdc_loader.py AGORA?")
    print("2. Aplique patch ao server.py AGORA?")
    print("3. Espere sua confirmação primeiro?")
    print("4. Teste o servidor atual primeiro?")
    
    # Por segurança, não aplicar patches automaticamente
    print("\n⚠️  RECOMENDAÇÃO: Testar primeiro, depois aplicar patches.")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)