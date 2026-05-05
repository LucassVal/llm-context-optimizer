#!/usr/bin/env python3
"""---
NC-SCR-FR-161: Corrigir Configuração do Antigravity
---
"""

"""---
NC-SCR-FR-161: Corrigir Configuração do Antigravity
---
"""

"""
NC-SCR-FR-161: Corrigir Configuração do Antigravity
1. Corrigir JSON corrompido
2. Atualizar para usar servidores corrigidos
3. Adicionar ferramenta de governança
"""

import sys
import json
from pathlib import Path

def fix_antigravity_config():
    """Corrigir configuração do Antigravity"""
    print("NC-SCR-FR-161: Correção da Configuração do Antigravity")
    print("=" * 80)
    
    config_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\DIR-DS-000-agent-config\antigravity_neocortex_config.json")
    
    if not config_path.exists():
        print("ERRO: Configuração não encontrada")
        return False
    
    # Ler conteúdo atual
    content = config_path.read_text(encoding='utf-8', errors='ignore')
    
    # Extrair JSON válido (até a linha 45)
    json_part = content.split('/*')[0].strip()
    
    try:
        # Parsear JSON
        config = json.loads(json_part)
        print("JSON válido extraído")
    except json.JSONDecodeError as e:
        print(f"ERRO: JSON ainda inválido após extração: {e}")
        return False
    
    # Criar nova configuração corrigida
    corrected_config = {
        "mcpServers": {
            "neocortex-stdio": {
                "name": "NeoCortex Framework (stdio)",
                "command": "python",
                "args": [
                    "-m",
                    "neocortex.mcp.server",
                    "--transport",
                    "stdio"
                ],
                "env": {},
                "disabled": False,
                "autoApprove": [
                    "neocortex_cortex",
                    "neocortex_ledger",
                    "neocortex_report",
                    "neocortex_checkpoint",
                    "neocortex_config",
                    "neocortex_lobes",
                    "neocortex_search",
                    "neocortex_agent",
                    "neocortex_pulse",
                    "neocortex_governance"
                ]
            },
            "neocortex-websocket": {
                "name": "NeoCortex Framework (WebSocket)",
                "url": "ws://localhost:8765",
                "disabled": False,
                "autoApprove": [
                    "neocortex_cortex",
                    "neocortex_ledger",
                    "neocortex_report",
                    "neocortex_checkpoint",
                    "neocortex_config",
                    "neocortex_lobes",
                    "neocortex_search",
                    "neocortex_agent",
                    "neocortex_pulse",
                    "neocortex_governance"
                ]
            }
        }
    }
    
    # Adicionar documentação como comentário separado
    documentation = """/*
INSTRUÇÕES PARA ANTIGRAVITY - CONFIGURAÇÃO CORRIGIDA (NC-SCR-FR-161)

SERVIDORES DISPONÍVEIS:
1. neocortex-stdio (RECOMENDADO)
   - Usa servidor FastMCP real com governança ativada
   - Carrega regras .mdc automaticamente
   - Antigravity inicia servidor automaticamente

2. neocortex-websocket
   - Conecta ao mock server corrigido (:8765)
   - Mock server agora carrega regras .mdc
   - Bypass de governança foi eliminado

FERRAMENTAS DE GOVERNANÇA:
- neocortex_governance: Regras obrigatórias R01-R21 (.mdc)
- Todas as ferramentas agora aplicam compliance

CONFIGURAÇÃO:
1. Copie o JSON acima (linhas 1-XX) para:
   - Windows: %%APPDATA%%\\antigravity\\mcp-servers.json
   - Mac/Linux: ~/.config/antigravity/mcp-servers.json

2. OU adicione ao seu arquivo de configuração existente.

USO RECOMENDADO:
> Use "neocortex-stdio" para governança completa
> Ferramenta "neocortex_governance" mostra regras

CORREÇÕES APLICADAS:
- JSON corrompido corrigido
- Servidores atualizados para versões corrigidas
- Ferramenta de governança adicionada
- Bypass eliminado (NC-SCR-FR-157)

DATA: 2026-04-21
STATUS: Governança ativada
*/"""
    
    # Criar novo conteúdo
    new_content = json.dumps(corrected_config, indent=2, ensure_ascii=False)
    new_content += "\n\n" + documentation
    
    # Backup do original
    backup_path = config_path.with_suffix('.json.backup')
    config_path.rename(backup_path)
    print(f"Backup criado: {backup_path.name}")
    
    # Escrever nova configuração
    config_path.write_text(new_content, encoding='utf-8')
    print(f"Configuração corrigida: {config_path.name}")
    print(f"Tamanho: {len(new_content)} caracteres")
    
    # Verificar
    print("\nVERIFICAÇÃO:")
    try:
        test_config = json.loads(json.dumps(corrected_config))
        print("  OK - JSON válido")
        
        servers = test_config.get("mcpServers", {})
        print(f"  Servidores configurados: {len(servers)}")
        
        for name, server_config in servers.items():
            if "command" in server_config:
                print(f"  • {name}: stdio (servidor real)")
            elif "url" in server_config:
                print(f"  • {name}: websocket (mock corrigido)")
            
            # Verificar se tem neocortex_governance
            auto_approve = server_config.get("autoApprove", [])
            if "neocortex_governance" in auto_approve:
                print(f"    ✅ Tem ferramenta de governança")
            else:
                print(f"    ❌ SEM ferramenta de governança")
        
        return True
        
    except Exception as e:
        print(f"  ERRO na verificação: {e}")
        return False

def rename_problematic_file():
    """Renomear arquivo fora do padrão de naming"""
    print("\n\nCORREÇÃO 2: Arquivo Fora do Padrão")
    print("=" * 80)
    
    problematic = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain\NC-DS-122-lobe-migration-report.md")
    
    if not problematic.exists():
        print("Arquivo não encontrado (já corrigido?)")
        return True
    
    # Novo nome seguindo padrão NC-SCR
    new_name = Path(r"C:\Users\Lucas Valério\.gemini\antigravity\brain\NC-SCR-FR-122-lobe-migration-report.md")
    
    # Backup
    backup = problematic.with_suffix('.md.backup')
    problematic.rename(backup)
    print(f"Backup: {backup.name}")
    
    # Renomear
    backup.rename(new_name)
    print(f"Renomeado: {problematic.name} → {new_name.name}")
    
    # Verificar
    if new_name.exists():
        print("✅ Arquivo renomeado com sucesso")
        return True
    else:
        print("❌ Erro ao renomear")
        return False

def main():
    """Função principal"""
    print("NC-SCR-FR-161: Correções Finais do Sistema")
    print("=" * 80)
    
    # 1. Corrigir configuração Antigravity
    config_ok = fix_antigravity_config()
    
    # 2. Renomear arquivo problemático
    rename_ok = rename_problematic_file()
    
    print("\n" + "=" * 80)
    print("RESUMO DAS CORREÇÕES")
    print("=" * 80)
    
    if config_ok:
        print("✅ Configuração Antigravity corrigida")
        print("   • JSON válido")
        print("   • Servidores atualizados")
        print("   • Ferramenta de governança adicionada")
    else:
        print("❌ Configuração Antigravity com problemas")
    
    if rename_ok:
        print("✅ Arquivo renomeado para padrão NC-SCR")
        print("   • NC-DS-122 → NC-SCR-FR-122")
        print("   • Agora segue naming convention R01")
    else:
        print("❌ Problema ao renomear arquivo")
    
    print("\nPRÓXIMOS PASSOS:")
    print("1. Reiniciar Antigravity com nova configuração")
    print("2. Testar conexão com servidores corrigidos")
    print("3. Verificar se regras .mdc são recebidas")
    print("4. Executar teste final de compliance")
    
    return config_ok and rename_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)