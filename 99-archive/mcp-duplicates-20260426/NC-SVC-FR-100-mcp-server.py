#!/usr/bin/env python3
"""
NC-SVC-FR-100-mcp-server.py - VERSÃO CORRIGIDA

CORREÇÃO: NC-SCR-FR-157
DATA: 2026-04-21
STATUS: Bypass de governança eliminado

Este servidor agora carrega regras .mdc e aplica governança
a todos os agentes conectados.
"""

import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GovernanceServer:
    def __init__(self):
        self.rules = self.load_rules()
        logger.info(f"Governança carregada: {len(self.rules)} caracteres")
    
    def load_rules(self):
        """Carregar regras .mdc"""
        try:
            rules_dir = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\.agents\rules")
            
            if not rules_dir.exists():
                return "ERRO: Diretório .agents/rules não encontrado"
            
            mdc_files = list(rules_dir.glob("*.mdc"))
            if not mdc_files:
                return "ERRO: Nenhum arquivo .mdc encontrado"
            
            text = "# REGRAS DE GOVERNANÇA NEOcORTEX\n\n"
            text += "> Servidor corrigido - Bypass eliminado\n\n"
            
            for mdc in sorted(mdc_files):
                try:
                    content = mdc.read_text(encoding='utf-8', errors='ignore')
                    text += f"## {mdc.stem}\n"
                    text += f"*Arquivo: {mdc.name}*\n\n"
                    
                    lines = content.split('\n')
                    added = 0
                    for line in lines:
                        if line.strip() and not line.strip().startswith('---'):
                            text += line + '\n'
                            added += 1
                            if added >= 15:
                                text += "...\n"
                                break
                    
                    text += "\n---\n\n"
                    
                except Exception as e:
                    text += f"ERRO: {mdc.name}: {e}\n\n"
            
            return text
            
        except Exception as e:
            return f"ERRO ao carregar regras: {e}"
    
    def handle(self, request):
        """Processar requisição"""
        method = request.get('method', '')
        params = request.get('params', {})
        req_id = request.get('id', 0)
        
        if method == 'tools/list':
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'tools': [
                        {
                            'name': 'neocortex_governance',
                            'description': 'Regras de governança (R01-R21)',
                            'inputSchema': {'type': 'object', 'properties': {}}
                        }
                    ]
                }
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name', '')
            
            if tool_name == 'neocortex_governance':
                return {
                    'jsonrpc': '2.0',
                    'id': req_id,
                    'result': {
                        'content': [{
                            'type': 'text',
                            'text': self.rules
                        }]
                    }
                }
            else:
                return {
                    'jsonrpc': '2.0',
                    'id': req_id,
                    'error': {
                        'code': -32601,
                        'message': f'Ferramenta {tool_name} requer servidor FastMCP real'
                    }
                }
        
        elif method == 'prompts/get':
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'result': {
                    'description': 'Regras de Governança',
                    'messages': [{
                        'role': 'user',
                        'content': {
                            'type': 'text',
                            'text': self.rules
                        }
                    }]
                }
            }
        
        else:
            return {
                'jsonrpc': '2.0',
                'id': req_id,
                'error': {
                    'code': -32601,
                    'message': f'Método {method} não suportado'
                }
            }

def main():
    server = GovernanceServer()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = server.handle(request)
            
            print(json.dumps(response), flush=True)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Erro: {e}")

if __name__ == "__main__":
    main()
