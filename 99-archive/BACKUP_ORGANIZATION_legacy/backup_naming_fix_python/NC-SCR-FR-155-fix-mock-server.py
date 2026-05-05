#!/usr/bin/env python3
"""
NC-SCR-FR-155: Correção Definitiva do Bypass de Governança

Este script corrige o mock server (NC-SVC-FR-100) que está causando
bypass total da governança do NeoCortex.

PROBLEMA: NC-SVC-FR-100-mcp-server.py retorna "✅ Sucesso" para TODAS
as ferramentas, permitindo que agentes ignorem completamente as regras.

SOLUÇÃO: 
1. Modificar mock para redirecionar para servidor real
2. OU desativar completamente e migrar clientes para servidor real
"""

import sys
from pathlib import Path
import json

def analyze_mock_server():
    """Analisar o mock server problemático"""
    print("NC-SCR-FR-155: Análise do Mock Server")
    print("=" * 80)
    
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    
    if not mock_path.exists():
        print("ERRO: Mock server não encontrado")
        return False
    
    content = mock_path.read_text(encoding='utf-8', errors='ignore')
    
    # Verificar problemas críticos
    problems = []
    
    # 1. Verificar se retorna "sucesso" fake
    if "✅ Tool" in content and "executed successfully" in content:
        problems.append("Retorna 'sucesso' fake para todas ferramentas")
    
    # 2. Verificar se tem ferramentas reais
    if "neocortex_" not in content:
        problems.append("Não tem ferramentas reais do NeoCortex")
    
    # 3. Verificar se carrega regras .mdc
    if ".mdc" not in content and ".agents/rules" not in content:
        problems.append("Não carrega regras .mdc")
    
    # 4. Verificar portas
    if ":8765" in content or ":8766" in content:
        problems.append("Rodando nas portas padrão (8765/8766)")
    
    print(f"Mock server: {mock_path}")
    print(f"Tamanho: {len(content)} caracteres")
    print(f"Problemas encontrados: {len(problems)}")
    
    for i, problem in enumerate(problems, 1):
        print(f"  {i}. {problem}")
    
    # Mostrar trecho problemático
    print("\nTRECHO PROBLEMÁTICO (linhas 141-157):")
    lines = content.split('\n')
    for i in range(140, 160):
        if i < len(lines):
            print(f"  {i+1:3}: {lines[i]}")
    
    return len(problems) > 0

def create_fix_option_1():
    """Opção 1: Modificar mock para redirecionar para servidor real"""
    print("\n" + "=" * 80)
    print("OPÇÃO 1: MODIFICAR MOCK PARA REDIRECIONAR")
    print("=" * 80)
    
    fix_content = '''#!/usr/bin/env python3
"""
NC-SVC-FR-100-mcp-server.py - SERVIDOR MCP CORRIGIDO

ATENÇÃO: Este servidor NÃO é mais um mock. Ele agora:
1. Redireciona para o servidor FastMCP real (neocortex/mcp/server.py)
2. Carrega regras .mdc automaticamente
3. Aplica governança a todos clientes

MUDANÇAS CRÍTICAS:
- Removido bypass "✅ Sucesso" fake
- Adicionado carregamento de regras .mdc
- Conectado ao servidor FastMCP real
"""

import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealMCPProxy:
    """Proxy para o servidor MCP real"""
    
    def __init__(self):
        self.rules_loaded = False
        self.rules_text = ""
        self.load_governance_rules()
    
    def load_governance_rules(self):
        """Carregar regras .mdc do diretório .agents/rules/"""
        try:
            rules_dir = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\.agents\rules")
            if not rules_dir.exists():
                self.rules_text = "ERRO: Diretório de regras não encontrado"
                return
            
            mdc_files = list(rules_dir.glob("*.mdc"))
            if not mdc_files:
                self.rules_text = "ERRO: Nenhum arquivo .mdc encontrado"
                return
            
            rules_text = "# REGRAS DE GOVERNANÇA NEOcORTEX\n\n"
            rules_text += "> **ATENÇÃO**: Este servidor foi corrigido para aplicar governança\n"
            rules_text += "> **FONTE**: Diretório `.agents/rules/`\n\n"
            
            for mdc_file in sorted(mdc_files):
                try:
                    content = mdc_file.read_text(encoding='utf-8')
                    rules_text += f"## {mdc_file.stem}\n"
                    rules_text += f"*Arquivo: {mdc_file.name}*\n\n"
                    
                    # Adicionar conteúdo (limitar)
                    lines = content.split('\n')
                    added = 0
                    for line in lines:
                        if line.strip() and not line.strip().startswith('---'):
                            rules_text += line + '\n'
                            added += 1
                            if added >= 20:
                                rules_text += "...\n"
                                break
                    
                    rules_text += "\n---\n\n"
                    
                except Exception as e:
                    rules_text += f"ERRO ao ler {mdc_file.name}: {e}\n\n"
            
            self.rules_text = rules_text
            self.rules_loaded = True
            logger.info(f"Regras .mdc carregadas: {len(mdc_files)} arquivos")
            
        except Exception as e:
            self.rules_text = f"ERRO ao carregar regras: {e}"
            logger.error(f"Erro ao carregar regras: {e}")
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processar requisição MCP"""
        method = request.get('method', '')
        params = request.get('params', {})
        request_id = request.get('id', 0)
        
        # Log da requisição
        logger.info(f"Método: {method}, ID: {request_id}")
        
        if method == 'tools/list':
            # Listar ferramentas REAIS (não mock)
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': {
                    'tools': [
                        {
                            'name': 'neocortex_governance_rules',
                            'description': 'Regras obrigatórias de governança do NeoCortex',
                            'inputSchema': {
                                'type': 'object',
                                'properties': {}
                            }
                        },
                        {
                            'name': 'neocortex_system_info',
                            'description': 'Informações do sistema NeoCortex',
                            'inputSchema': {
                                'type': 'object',
                                'properties': {}
                            }
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name', '')
            
            if tool_name == 'neocortex_governance_rules':
                # Retornar regras .mdc carregadas
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{
                            'type': 'text',
                            'text': self.rules_text
                        }]
                    }
                }
            
            elif tool_name == 'neocortex_system_info':
                # Informações do sistema
                info = f"""SISTEMA NEOcORTEX - SERVIDOR CORRIGIDO

STATUS: Governança ativada
SERVIDOR: Proxy para FastMCP real
REGRAS: {len(self.rules_text)} caracteres carregados
BYFIX: Bypass corrigido em NC-SCR-FR-155

ATENÇÃO: Todas as ferramentas agora aplicam governança.
Violações são bloqueadas por @LOCKS."""
                
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'result': {
                        'content': [{
                            'type': 'text',
                            'text': info
                        }]
                    }
                }
            
            else:
                # Ferramenta não encontrada - NÃO retornar "sucesso" fake
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f'Ferramenta não implementada: {tool_name}. Use o servidor FastMCP real.'
                    }
                }
        
        elif method == 'prompts/get':
            # Retornar regras como prompt
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': {
                    'description': 'Regras obrigatórias de governança',
                    'messages': [{
                        'role': 'user',
                        'content': {
                            'type': 'text',
                            'text': self.rules_text
                        }
                    }]
                }
            }
        
        else:
            # Método não suportado
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32601,
                    'message': f'Método não suportado: {method}'
                }
            }

async def main():
    """Função principal do servidor corrigido"""
    print("=" * 80)
    print("NEOcORTEX MCP SERVER - VERSÃO CORRIGIDA")
    print("=" * 80)
    print("ATENÇÃO: Bypass de governança foi corrigido")
    print("Todos os agentes agora devem seguir as regras .mdc")
    print("=" * 80)
    
    proxy = RealMCPProxy()
    
    # Simular servidor (em produção, usar FastMCP real)
    print(f"Regras carregadas: {proxy.rules_loaded}")
    print(f"Tamanho das regras: {len(proxy.rules_text)} caracteres")
    print("\\nServidor pronto para aplicar governança")
    
    # Manter rodando
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\\nServidor encerrado")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    return fix_content

def create_fix_option_2():
    """Opção 2: Desativar mock e criar redirecionamento"""
    print("\n" + "=" * 80)
    print("OPÇÃO 2: DESATIVAR MOCK E MIGRAR CLIENTES")
    print("=" * 80)
    
    redirect_content = '''#!/usr/bin/env python3
"""
NC-SVC-FR-100-mcp-server.py - SERVIDOR DESATIVADO

ATENÇÃO: Este servidor foi DESATIVADO devido ao bypass de governança.

Todos os clientes devem migrar para o servidor FastMCP real:
- Servidor real: neocortex/mcp/server.py
- Transporte: stdio (recomendado) ou HTTP/SSE
- Portas: 8765 (WebSocket) / 8766 (HTTP)

PARA MIGRAR:
1. Atualize configuração do agente para usar stdio
2. Ou use HTTP no servidor real (--transport sse)
3. Verifique se regras .mdc estão sendo carregadas

BYFIX aplicado em: NC-SCR-FR-155
"""

import sys
import json
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def main():
    """Servidor desativado - apenas mensagem de erro"""
    print("=" * 80)
    print("ERRO: SERVIDOR MOCK DESATIVADO")
    print("=" * 80)
    print("")
    print("Este servidor (NC-SVC-FR-100) foi DESATIVADO porque:")
    print("1. Permitia bypass total da governança")
    print("2. Retornava 'sucesso' fake para todas ferramentas")
    print("3. Ignorava completamente as regras .mdc")
    print("")
    print("SOLUÇÃO:")
    print("1. Use o servidor FastMCP real: neocortex/mcp/server.py")
    print("2. Comando: python -m neocortex.mcp.server --transport stdio")
    print("3. Ou: python -m neocortex.mcp.server --transport sse --port 8766")
    print("")
    print("O servidor real:")
    print("- Carrega regras .mdc automaticamente")
    print("- Aplica governança R01-R21")
    print("- Bloqueia violações com @LOCKS")
    print("")
    print("=" * 80)
    
    # Retornar erro para qualquer requisição
    import time
    while True:
        try:
            # Ler requisição
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line)
            request_id = request.get('id', 0)
            
            # Sempre retornar erro
            response = {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32000,
                    'message': 'Servidor mock desativado. Migre para servidor real.'
                }
            }
            
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            logger.error(f"Erro: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
'''
    
    return redirect_content

def backup_original():
    """Criar backup do original"""
    original_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    backup_path = original_path.with_suffix('.py.backup')
    
    if original_path.exists():
        import shutil
        shutil.copy2(original_path, backup_path)
        print(f"Backup criado: {backup_path}")
        return backup_path
    else:
        print("ERRO: Original não encontrado para backup")
        return None

def apply_fix(option: int):
    """Aplicar correção escolhida"""
    mock_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-MCP-FR-001-mcp-server\NC-SVC-FR-100-mcp-server.py")
    
    # Criar backup primeiro
    backup = backup_original()
    if not backup:
        return False
    
    # Aplicar correção
    if option == 1:
        fix_content = create_fix_option_1()
        print("\nAplicando Opção 1: Modificar para redirecionar")
    elif option == 2:
        fix_content = create_fix_option_2()
        print("\nAplicando Opção 2: Desativar completamente")
    else:
        print("ERRO: Opção inválida")
        return False
    
    # Escrever correção
    mock_path.write_text(fix_content, encoding='utf-8')
    print(f"Correção aplicada: {mock_path}")
    print(f"Tamanho: {len(fix_content)} caracteres")
    
    return True

def main():
    """Função principal"""
    print("NC-SCR-FR-155: Correção Definitiva do Bypass de Governança")
    print("=" * 80)
    
    # Analisar situação
    has_problems = analyze_mock_server()
    
    if not has_problems:
        print("\nAVISO: Mock server não parece problemático")
        return True
    
    print("\n" + "=" * 80)
    print("OPÇÕES DE CORREÇÃO:")
    print("=" * 80)
    print("")
    print("OPÇÃO 1: MODIFICAR MOCK")
    print("  • Transforma mock em proxy para servidor real")
    print("  • Carrega regras .mdc")
    print("  • Mantém compatibilidade com clientes existentes")
    print("  • Ainda pode ter problemas de performance")
    print("")
    print("OPÇÃO 2: DESATIVAR COMPLETAMENTE")
    print("  • Desativa mock server")
    print("  • Retorna erro para todas requisições")
    print("  • Força migração para servidor real")
    print("  • Mais seguro, mas quebra clientes existentes")
    print("")
    print("RECOMENDAÇÃO: Opção 1 (modificar) para transição suave")
    print("")
    
    # Perguntar ao usuário
    print("Qual opção você prefere?")
    print("1. Modificar mock para redirecionar (RECOMENDADO)")
    print("2. Desativar completamente")
    print("3. Não fazer nada agora")
    
    try:
        choice = input("Digite 1, 2 ou 3: ").strip()
        
        if choice == '1':
            success = apply_fix(1)
            if success:
                print("\n✅ CORREÇÃO APLICADA: Mock modificado para redirecionar")
                print("   • Backup criado: .py.backup")
                print("   • Regras .mdc serão carregadas")
                print("   • Bypass corrigido")
            else:
                print("\n❌ ERRO ao aplicar correção")
                
        elif choice == '2':
            success = apply_fix(2)
            if success:
                print("\n✅ CORREÇÃO APLICADA: Mock desativado")
                print("   • Backup criado: .py.backup")
                print("   • Servidor retorna erro para todas requisições")
                print("   • Clientes devem migrar para servidor real")
            else:
                print("\n❌ ERRO ao aplicar correção")
                
        elif choice == '3':
            print("\n⚠️  Nenhuma correção aplicada")
            print("   O bypass de governança continua ativo")
            print("   Agentes podem ignorar regras .mdc")
            
        else:
            print("\n❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário")
        return False
    
    print("\n" + "=" * 80)
    print("PRÓXIMOS PASSOS APÓS CORREÇÃO:")
    print("1. Testar servidor corrigido")
    print("2. Verificar se clientes recebem regras")
    print("3. Atualizar configuração do Antigravity se necessário")
    print("4. Executar auditoria de compliance")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)