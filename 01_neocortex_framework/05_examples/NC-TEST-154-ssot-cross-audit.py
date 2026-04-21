#!/usr/bin/env python3
"""
NC-TEST-154-ssot-cross-audit.py
SSOT Cross-Audit Script for NC-DS-154 Compliance Audit.

Objetivo: Realizar auditoria cruzada entre o SSOT (NC-NAM-FR-001-naming-convention.md)
e os arquivos existentes no disco, identificando:
1. MISSING: Arquivos no SSOT que não existem no disco
2. UNLISTED: Arquivos no disco que não estão no SSOT
3. Calcular porcentagem de conformidade

Regras:
- R09: Usar importlib.util para importar módulos com hífen
- R10: Usar get_config() para resolver paths
- R11: Usar logger = logging.getLogger(__name__) — NUNCA print()
- Usar yaml.safe_load() para YAMLs
- Regex para parsear tabela markdown: r'\\|\\s*([^|]+)\\s*\\|' (com escape)
- Ignorar linhas de cabeçalho e separadores
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


def get_config() -> Dict:
    """Obtém configuração do sistema (R10).
    
    Returns:
        Dicionário com configurações incluindo project_root.
    """
    try:
        # Tentar importar config_service
        import importlib.util
        
        config_path = Path(__file__).parent.parent / "neocortex" / "core" / "config_service.py"
        spec = importlib.util.spec_from_file_location("config_service", config_path)
        if spec is None:
            raise ImportError(f"Não foi possível criar spec para {config_path}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Obter configuração
        config = module.get_config()
        return config
        
    except Exception as e:
        logger.warning(f"Falha ao obter configuração via config_service: {e}")
        # Fallback: configuração padrão
        return {
            "project_root": Path(__file__).parent.parent,
            "ssot_path": "DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md"
        }


def parse_ssot_table(ssot_content: str) -> List[Dict[str, str]]:
    """Analisa tabela markdown do SSOT e extrai entradas.
    
    Args:
        ssot_content: Conteúdo do arquivo SSOT markdown
        
    Returns:
        Lista de dicionários com entradas SSOT
    """
    entries = []
    
    # Encontrar a seção da tabela SSOT
    lines = ssot_content.split('\n')
    in_table = False
    header_processed = False
    
    for i, line in enumerate(lines):
        # Verificar se é início da tabela SSOT
        if "SSOT Geral do Sistema" in line or "| Nome |" in line:
            in_table = True
            continue
        
        if in_table:
            # Ignorar linhas de separador (|---|)
            if re.match(r'^\|[-:| ]+\|$', line):
                header_processed = True
                continue
            
            # Ignorar linhas vazias ou fim da tabela
            if not line.strip() or line.startswith('#') or line.startswith('---'):
                if header_processed and line.strip():
                    # Provavelmente fim da tabela
                    break
                continue
            
            # Processar linha da tabela
            if '|' in line and header_processed:
                # Extrair células usando regex
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if len(cells) >= 3:  # Nome, Descrição, Local
                    entry = {
                        "name": cells[0],
                        "description": cells[1] if len(cells) > 1 else "",
                        "path": cells[2] if len(cells) > 2 else "",
                        "keywords": cells[3] if len(cells) > 3 else ""
                    }
                    entries.append(entry)
    
    return entries


def scan_disk_files(base_path: Path, patterns: List[str] = None) -> Set[str]:
    """Escaneia arquivos no disco.
    
    Args:
        base_path: Caminho base para escanear
        patterns: Padrões de arquivo para incluir
        
    Returns:
        Conjunto de caminhos relativos de arquivos
    """
    if patterns is None:
        patterns = ["**/*.py", "**/*.yaml", "**/*.yml", "**/*.md", 
                   "**/*.json", "**/*.txt", "**/*.bat", "**/*.ps1",
                   "**/*.toml", "**/*.db", "**/*.wal", "**/*.mdc"]
    
    disk_files = set()
    
    for pattern in patterns:
        for file_path in base_path.glob(pattern):
            # Converter para caminho relativo
            try:
                rel_path = file_path.relative_to(base_path)
                disk_files.add(str(rel_path).replace('\\', '/'))
            except ValueError:
                # Arquivo fora do base_path
                continue
    
    return disk_files


def normalize_path(path: str, base_path: Path) -> Path:
    """Normaliza caminho para comparação.
    
    Args:
        path: Caminho do SSOT (pode começar com \\ ou /)
        base_path: Caminho base do projeto (01_neocortex_framework)
        
    Returns:
        Caminho normalizado absoluto
    """
    # Remover barras iniciais
    clean_path = path.lstrip('\\/')
    
    # Se NÃO começar com 01_neocortex_framework/, adicionar
    if not clean_path.startswith('01_neocortex_framework/'):
        # Verificar se é um arquivo na raiz do TURBOQUANT_V42
        if clean_path in ['antigravity_neocortex_config.json', 'README.md', 
                         'start_neocortex_mcp.bat', 'start_neocortex_mcp.ps1']:
            # Esses arquivos estão na raiz do TURBOQUANT_V42, não em 01_neocortex_framework
            # Subir um nível
            return base_path.parent / clean_path
        else:
            # Adicionar prefixo 01_neocortex_framework/
            clean_path = '01_neocortex_framework/' + clean_path
    
    # Construir caminho absoluto
    return base_path.parent / clean_path


def perform_cross_audit(ssot_entries: List[Dict], disk_files: Set[str], 
                       base_path: Path) -> Dict:
    """Realiza auditoria cruzada entre SSOT e disco.
    
    Args:
        ssot_entries: Entradas do SSOT
        disk_files: Arquivos no disco
        base_path: Caminho base do projeto
        
    Returns:
        Dicionário com resultados da auditoria
    """
    ssot_paths = set()
    missing = []
    unlisted = set(disk_files)
    external_paths = []
    
    for entry in ssot_entries:
        path = entry.get("path", "")
        if not path:
            continue
        
        # Normalizar caminho
        norm_path = normalize_path(path, base_path)
        
        # Verificar se o caminho está dentro do projeto
        try:
            rel_path = norm_path.relative_to(base_path)
            rel_path_str = str(rel_path).replace('\\', '/')
            
            # Adicionar ao conjunto de paths SSOT (apenas os dentro do projeto)
            ssot_paths.add(rel_path_str)
            
            # Verificar se arquivo existe
            if norm_path.exists():
                # Remover do conjunto unlisted (está listado no SSOT)
                if rel_path_str in unlisted:
                    unlisted.remove(rel_path_str)
            else:
                missing.append({
                    "name": entry.get("name", ""),
                    "ssot_path": path,
                    "normalized_path": str(norm_path)
                })
                
        except ValueError:
            # Caminho fora do projeto (ex: C:\Program Files\...)
            external_paths.append(str(norm_path))
            continue
    
    # Converter unlisted para lista ordenada
    unlisted_list = sorted(list(unlisted))
    
    # Calcular conformidade
    total_ssot = len(ssot_paths)
    total_disk = len(disk_files)
    
    if total_ssot > 0:
        # Arquivos SSOT que existem no disco
        ssot_exists = total_ssot - len(missing)
        compliance_pct = (ssot_exists / total_ssot) * 100
    else:
        compliance_pct = 0.0
    
    logger.debug(f"SSOT paths: {total_ssot}, Exists: {ssot_exists}, Missing: {len(missing)}")
    
    return {
        "total_ssot": total_ssot,
        "total_disk": total_disk,
        "missing_count": len(missing),
        "unlisted_count": len(unlisted_list),
        "compliance_pct": round(compliance_pct, 2),
        "missing": missing,
        "unlisted": unlisted_list,
        "timestamp": datetime.now().isoformat(),
        "audit_type": "SSOT cross-audit"
    }


def main() -> Dict:
    """Função principal da auditoria SSOT.
    
    Returns:
        Resultados da auditoria
    """
    try:
        # Obter configuração
        config = get_config()
        project_root = Path(config.get("project_root", Path(__file__).parent.parent))
        ssot_relative = config.get("ssot_path", "DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md")
        ssot_path = project_root / ssot_relative
        
        logger.info(f"Iniciando auditoria SSOT: {ssot_path}")
        
        # Verificar se SSOT existe
        if not ssot_path.exists():
            logger.error(f"Arquivo SSOT não encontrado: {ssot_path}")
            return {"error": "SSOT file not found"}
        
        # Ler SSOT
        ssot_content = ssot_path.read_text(encoding='utf-8', errors='ignore')
        
        # Parsear tabela SSOT
        ssot_entries = parse_ssot_table(ssot_content)
        logger.info(f"Encontradas {len(ssot_entries)} entradas no SSOT")
        
        # Escanear arquivos no disco
        disk_files = scan_disk_files(project_root)
        logger.info(f"Encontrados {len(disk_files)} arquivos no disco")
        
        # Realizar auditoria cruzada
        audit_results = perform_cross_audit(ssot_entries, disk_files, project_root)
        
        # Logar resultados
        logger.info(f"Conformidade SSOT: {audit_results['compliance_pct']}%")
        logger.info(f"Missing: {audit_results['missing_count']} arquivos")
        logger.info(f"Unlisted: {audit_results['unlisted_count']} arquivos")
        
        # Salvar resultados em JSON
        output_path = project_root / "05_examples" / "NC-RPT-154-ssot-cross-audit.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Relatório salvo em: {output_path}")
        
        return audit_results
        
    except Exception as e:
        logger.error(f"Erro na auditoria SSOT: {e}", exc_info=True)
        return {"error": str(e)}


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Executar auditoria
    results = main()
    
    # Exibir resumo
    print("\n" + "=" * 60)
    print("RESUMO DA AUDITORIA SSOT")
    print("=" * 60)
    
    if "error" in results:
        print(f"ERRO: {results['error']}")
        sys.exit(1)
    
    print(f"Total SSOT: {results['total_ssot']}")
    print(f"Total Disco: {results['total_disk']}")
    print(f"Missing (SSOT -> Disco): {results['missing_count']}")
    print(f"Unlisted (Disco -> SSOT): {results['unlisted_count']}")
    print(f"Conformidade: {results['compliance_pct']}%")
    print("=" * 60)
    
    # Exibir alguns exemplos se houver problemas
    if results['missing_count'] > 0:
        print("\nTOP 5 MISSING (arquivos no SSOT que não existem):")
        for i, item in enumerate(results['missing'][:5]):
            print(f"  {i+1}. {item['name']} -> {item['ssot_path']}")
    
    if results['unlisted_count'] > 0:
        print("\nTOP 5 UNLISTED (arquivos no disco não listados no SSOT):")
        for i, path in enumerate(results['unlisted'][:5]):
            print(f"  {i+1}. {path}")
    
    print("\nRelatório completo salvo em: 05_examples/NC-RPT-154-ssot-cross-audit.json")
    
    sys.exit(0 if results['compliance_pct'] > 50 else 1)