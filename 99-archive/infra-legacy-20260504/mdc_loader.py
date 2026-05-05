#!/usr/bin/env python3
"""---
NC-MOD-FR-001: Carregador de Regras .mdc para FastMCP
---
"""

"""---
NC-MOD-FR-001: Carregador de Regras .mdc para FastMCP
---
"""

"""
NC-MOD-FR-001: Carregador de Regras .mdc para FastMCP
Patch para injetar governança no servidor MCP real

Este módulo carrega todas as regras .mdc do diretório .agents/rules/
e as expõe como prompt do FastMCP para garantir que todos agentes
sigam a governança do NeoCortex.

@BOOT: R01-R21 compliance
@SSOT: NC-NAM-FR-001-naming-convention.md
@LOCKS: NC-SEC-FR-001-atomic-locks.yaml
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml
import re

def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    Encontra a raiz do projeto TURBOQUANT_V42.
    
    Args:
        start_path: Path inicial para busca. Se None, usa diretório atual.
    
    Returns:
        Path para a raiz do projeto.
    
    Raises:
        FileNotFoundError: Se não encontrar a raiz do projeto.
    """
    if start_path is None:
        start_path = Path(__file__).resolve()
    
    current = start_path
    max_depth = 10
    
    for _ in range(max_depth):
        # Verificar se é a raiz do TURBOQUANT_V42
        if current.name == "TURBOQUANT_V42":
            # Verificar estrutura esperada
            expected_dirs = [
                "01_neocortex_framework",
                ".agents",
                "02_memory_lobes"
            ]
            if all((current / dir_name).exists() for dir_name in expected_dirs):
                return current
        
        # Subir um nível
        parent = current.parent
        if parent == current:  # Chegou na raiz do filesystem
            break
        current = parent
    
    # Fallback: tentar encontrar pelo caminho conhecido
    known_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42")
    if known_path.exists():
        return known_path
    
    raise FileNotFoundError(
        "Não foi possível encontrar a raiz do projeto TURBOQUANT_V42. "
        "Verifique se o diretório .agents/rules/ existe."
    )

def load_mdc_rules(rules_dir: Optional[Path] = None) -> str:
    """
    Carrega todas as regras .mdc do diretório .agents/rules/
    
    Args:
        rules_dir: Diretório das regras. Se None, usa padrão do projeto.
    
    Returns:
        Texto consolidado de todas as regras formatado para prompt.
    
    Raises:
        FileNotFoundError: Se diretório de regras não existir.
    """
    if rules_dir is None:
        project_root = find_project_root()
        rules_dir = project_root / ".agents" / "rules"
    
    if not rules_dir.exists():
        raise FileNotFoundError(
            f"Diretório de regras não encontrado: {rules_dir}\n"
            f"Verifique se o projeto está configurado corretamente."
        )
    
    mdc_files = list(rules_dir.glob("*.mdc"))
    if not mdc_files:
        return "⚠️ Nenhum arquivo .mdc encontrado no diretório de regras."
    
    # Ordenar por número de regra (NC-RULE-001, NC-RULE-002, etc.)
    def extract_rule_number(filename: str) -> int:
        match = re.search(r'NC-RULE-(\d{3})', filename)
        return int(match.group(1)) if match else 999
    
    mdc_files.sort(key=lambda f: extract_rule_number(f.name))
    
    # Construir texto consolidado
    rules_text = "# REGRAS DE GOVERNANÇA NEOcORTEX\n\n"
    rules_text += "> **FONTE DA VERDADE**: Diretório `.agents/rules/`\n"
    rules_text += "> **CARREGADO AUTOMATICAMENTE** pelo servidor MCP\n"
    rules_text += "> **OBRIGATÓRIO PARA TODOS AGENTES** (R01-R21)\n\n"
    rules_text += "---\n\n"
    
    total_rules = 0
    total_files = 0
    
    for mdc_file in mdc_files:
        try:
            content = mdc_file.read_text(encoding='utf-8', errors='ignore')
            total_files += 1
            
            # Extrair metadados do frontmatter YAML
            title = mdc_file.stem.replace('NC-RULE-', 'Regra ').replace('-', ' ')
            description = ""
            priority = "medium"
            tags = []
            
            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    try:
                        metadata = yaml.safe_load(frontmatter)
                        if metadata:
                            title = metadata.get('title', title)
                            description = metadata.get('description', '')
                            priority = metadata.get('priority', 'medium')
                            tags = metadata.get('tags', [])
                    except yaml.YAMLError:
                        pass
            
            # Adicionar cabeçalho da regra
            rules_text += f"## {title}\n"
            rules_text += f"**Arquivo**: `{mdc_file.name}`\n"
            
            if description:
                rules_text += f"**Descrição**: {description}\n"
            
            if tags:
                rules_text += f"**Tags**: {', '.join(tags)}\n"
            
            rules_text += f"**Prioridade**: {priority.upper()}\n\n"
            
            # Adicionar conteúdo (excluir frontmatter)
            content_lines = content.split('\n')
            in_frontmatter = False
            in_content = False
            content_added = 0
            
            for line in content_lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                
                if not in_frontmatter and line.strip():
                    # Contar regras individuais (linhas que começam com R##)
                    if re.match(r'^R\d{2}:', line.strip()):
                        total_rules += 1
                    
                    rules_text += line + '\n'
                    content_added += 1
                    
                    # Limitar a 100 linhas por arquivo
                    if content_added >= 100:
                        rules_text += "...\n"
                        break
            
            rules_text += "\n---\n\n"
            
        except Exception as e:
            rules_text += f"⚠️ **ERRO** ao ler `{mdc_file.name}`: {e}\n\n"
            rules_text += "---\n\n"
    
    # Adicionar resumo
    rules_text += f"## RESUMO\n\n"
    rules_text += f"- **Arquivos .mdc carregados**: {total_files}\n"
    rules_text += f"- **Regras individuais (R##)**: {total_rules}\n"
    rules_text += f"- **Diretório fonte**: `{rules_dir}`\n\n"
    
    # Adicionar instruções de uso
    rules_text += "## INSTRUÇÕES DE COMPLIANCE\n\n"
    rules_text += "1. **TODOS AGENTES DEVEM SEGUIR ESTAS REGRAS**\n"
    rules_text += "2. **Violações são bloqueadas por @LOCKS**\n"
    rules_text += "3. **@SSOT deve ser atualizado após mudanças**\n"
    rules_text += "4. **STEP-0 obrigatório antes de qualquer ação**\n\n"
    
    # Adicionar referências críticas
    rules_text += "## REFERÊNCIAS CRÍTICAS\n\n"
    rules_text += "- **@BOOT**: `NC-BOOT-FR-001-system-manifest.md`\n"
    rules_text += "- **@SSOT**: `NC-NAM-FR-001-naming-convention.md`\n"
    rules_text += "- **@LOCKS**: `NC-SEC-FR-001-atomic-locks.yaml`\n"
    rules_text += "- **@ROADMAP**: `NC-PRJ-FR-001-roadmap.mdc`\n\n"
    
    rules_text += "---\n"
    rules_text += "> **Última atualização**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    rules_text += "> **Sistema**: NeoCortex Framework v4.2\n"
    
    return rules_text

def inject_rules_into_fastmcp(server_instance) -> bool:
    """
    Injeta as regras .mdc em uma instância do FastMCP.
    
    Args:
        server_instance: Instância do FastMCP Server.
    
    Returns:
        True se injetado com sucesso, False caso contrário.
    """
    try:
        # Verificar se é FastMCP
        if hasattr(server_instance, 'prompt'):
            # Carregar regras
            rules_content = load_mdc_rules()
            
            # Criar decorator dinamicamente
            @server_instance.prompt()
            def governance_rules():
                """Regras obrigatórias de governança do NeoCortex"""
                return rules_content
            
            return True
        else:
            print("⚠️ Instância não é FastMCP (sem método 'prompt')")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao injetar regras no FastMCP: {e}")
        return False

def get_rule_summary() -> Dict[str, any]:
    """
    Retorna um resumo das regras carregadas.
    
    Returns:
        Dicionário com estatísticas das regras.
    """
    try:
        rules_dir = find_project_root() / ".agents" / "rules"
        mdc_files = list(rules_dir.glob("*.mdc"))
        
        summary = {
            "total_files": len(mdc_files),
            "files": [],
            "rules_count": 0,
            "rules_dir": str(rules_dir)
        }
        
        for mdc_file in mdc_files:
            try:
                content = mdc_file.read_text(encoding='utf-8', errors='ignore')
                
                # Contar regras R##
                rule_matches = re.findall(r'^R\d{2}:', content, re.MULTILINE)
                
                file_info = {
                    "name": mdc_file.name,
                    "size": mdc_file.stat().st_size,
                    "rules_count": len(rule_matches),
                    "path": str(mdc_file)
                }
                
                summary["files"].append(file_info)
                summary["rules_count"] += len(rule_matches)
                
            except Exception as e:
                file_info = {
                    "name": mdc_file.name,
                    "error": str(e),
                    "path": str(mdc_file)
                }
                summary["files"].append(file_info)
        
        return summary
        
    except Exception as e:
        return {
            "error": str(e),
            "total_files": 0,
            "rules_count": 0
        }

# Import datetime para timestamp
from datetime import datetime

if __name__ == "__main__":
    """Testar carregamento de regras"""
    print("NC-MOD-FR-001: Teste de Carregamento de Regras .mdc")
    print("=" * 80)
    
    try:
        # Testar encontrar raiz do projeto
        project_root = find_project_root()
        print(f"Raiz do projeto: {project_root}")
        
        # Testar carregar regras
        rules = load_mdc_rules()
        print(f"Regras carregadas: {len(rules)} caracteres")
        
        # Mostrar resumo
        summary = get_rule_summary()
        print(f"\nRESUMO:")
        print(f"  • Arquivos .mdc: {summary.get('total_files', 0)}")
        print(f"  • Regras (R##): {summary.get('rules_count', 0)}")
        print(f"  • Diretório: {summary.get('rules_dir', 'N/A')}")
        
        if summary.get('files'):
            print(f"\nARQUIVOS:")
            for file_info in summary['files'][:5]:  # Mostrar primeiros 5
                if 'error' in file_info:
                    print(f"  • {file_info['name']}: ERRO - {file_info['error']}")
                else:
                    print(f"  • {file_info['name']}: {file_info['rules_count']} regras")
            
            if len(summary['files']) > 5:
                print(f"  • ... e mais {len(summary['files']) - 5} arquivos")
        
        print("\n" + "=" * 80)
        print("TESTE CONCLUÍDO COM SUCESSO")
        
    except Exception as e:
        print(f"ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)