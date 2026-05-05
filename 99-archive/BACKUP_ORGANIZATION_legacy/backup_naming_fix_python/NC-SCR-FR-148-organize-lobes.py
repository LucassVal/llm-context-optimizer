#!/usr/bin/env python3
"""
NC-SCR-FR-148: Organização de Lobes na Nova Estrutura
Organiza os lobes da pasta antiga 'lobes/' para a nova estrutura '02_memory_lobes/'
seguindo a taxonomia definida em NC-GOV-FR-008-lobe-taxonomy.yaml
"""

import os
import shutil
import yaml
import re
from pathlib import Path

def load_taxonomy():
    """Carrega a taxonomia dos lobes"""
    taxonomy_path = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework\DIR-DOC-FR-001-docs-main\NC-GOV-FR-008-lobe-taxonomy.yaml")
    
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        taxonomy = yaml.safe_load(f)
    
    return taxonomy

def categorize_lobe(filename):
    """Categoriza um lobe baseado no nome do arquivo"""
    name = filename.upper()
    
    # Mapeamento de prefixos para categorias
    category_map = {
        'NC-LBE-LEG': '01_legislative',
        'NC-LBE-EXE': '02_executive', 
        'NC-LBE-JUD': '03_judicial',
        'NC-LBE-AGT-T0': '04_agent_t0',
        'NC-LBE-AGT-T1': '05_agent_t1',
        'NC-LBE-AGT-T2': '06_agent_t2',
        'NC-LBE-AGT-PIC': '07_agent_picoclaw',
        'NC-LBE-USR': '08_user',
        'NC-LBE-FR': '09_framework',
        'NC-LBE-INT': '10_integration',
        'NC-LBE-CC': '11_core_components',
        'NC-LBE-DS': '12_deepseek'
    }
    
    for prefix, category in category_map.items():
        if name.startswith(prefix):
            return category
    
    # Fallback: analisar conteúdo do nome
    if 'FR' in name:
        return '09_framework'
    elif 'INT' in name:
        return '10_integration'
    elif 'CC' in name:
        return '11_core_components'
    elif 'DS' in name:
        return '12_deepseek'
    elif 'USR' in name:
        return '08_user'
    else:
        return '99_uncategorized'

def find_all_lobes():
    """Encontra todos os arquivos NC-LBE-*.mdc no framework"""
    framework_root = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
    
    # Locais onde lobes podem estar
    search_paths = [
        framework_root / "lobes",
        framework_root / "DIR-CORE-FR-001-core-central" / ".agents" / "rules",
        framework_root / "DIR-BAK-FR-001-backup-main" / "migration_backup" / "mdc_files" / ".agents" / "rules",
        framework_root / "DIR-TMP-FR-001-templates-main",
    ]
    
    all_lobes = []
    for search_path in search_paths:
        if search_path.exists():
            lobes = list(search_path.glob("NC-LBE-*.mdc"))
            if lobes:
                print(f"Encontrados {len(lobes)} lobes em {search_path.relative_to(framework_root)}")
                all_lobes.extend(lobes)
    
    return all_lobes

def organize_lobes():
    """Organiza os lobes na nova estrutura"""
    framework_root = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
    new_lobes_dir = framework_root / "02_memory_lobes"
    
    # Criar diretório principal se não existir
    new_lobes_dir.mkdir(exist_ok=True)
    
    # Carregar taxonomia
    taxonomy = load_taxonomy()
    print(f"Taxonomia carregada: {len(taxonomy.get('taxonomy', {}))} categorias principais")
    
    # Encontrar todos os arquivos NC-LBE-*.mdc
    mdc_files = find_all_lobes()
    print(f"Total de {len(mdc_files)} arquivos NC-LBE-*.mdc encontrados")
    
    # Organizar por categoria
    organized = {}
    for mdc_file in mdc_files:
        category = categorize_lobe(mdc_file.name)
        if category not in organized:
            organized[category] = []
        organized[category].append(mdc_file)
    
    # Criar estrutura de diretórios e mover arquivos
    moved_count = 0
    for category, files in organized.items():
        category_dir = new_lobes_dir / category
        category_dir.mkdir(exist_ok=True)
        
        print(f"\nCategoria: {category} ({len(files)} arquivos)")
        print("-" * 50)
        
        for mdc_file in files:
            dest_path = category_dir / mdc_file.name
            
            # Se já existe, criar versão com timestamp
            if dest_path.exists():
                timestamp = os.path.getmtime(mdc_file)
                from datetime import datetime
                dt = datetime.fromtimestamp(timestamp)
                new_name = f"{mdc_file.stem}_{dt.strftime('%Y%m%d_%H%M%S')}{mdc_file.suffix}"
                dest_path = category_dir / new_name
            
            try:
                shutil.copy2(mdc_file, dest_path)
                print(f"  [OK] {mdc_file.name} -> {category}/{dest_path.name}")
                moved_count += 1
            except Exception as e:
                print(f"  [ERRO] copiando {mdc_file.name}: {e}")
    
    # Criar arquivo de índice
    create_index(new_lobes_dir, organized, taxonomy)
    
    print(f"\n{'='*60}")
    print(f"RESUMO:")
    print(f"  Total de arquivos processados: {len(mdc_files)}")
    print(f"  Arquivos movidos: {moved_count}")
    print(f"  Categorias criadas: {len(organized)}")
    print(f"  Estrutura criada em: {new_lobes_dir}")
    
    return moved_count

def create_index(new_lobes_dir, organized, taxonomy):
    """Cria um arquivo de índice com a organização"""
    index_path = new_lobes_dir / "_INDEX.md"
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("# Índice de Lobes - Estrutura Organizada\n\n")
        f.write(f"*Data da organização: 2026-04-21*\n")
        f.write(f"*Total de lobes: {sum(len(files) for files in organized.values())}*\n\n")
        
        f.write("## Taxonomia Aplicada\n\n")
        f.write("Baseada em NC-GOV-FR-008-lobe-taxonomy.yaml\n\n")
        
        f.write("## Estrutura por Categoria\n\n")
        for category, files in sorted(organized.items()):
            f.write(f"### {category}\n\n")
            for mdc_file in sorted(files, key=lambda x: x.name):
                f.write(f"- `{mdc_file.name}`\n")
            f.write("\n")
        
        f.write("## Legenda de Prefixos\n\n")
        f.write("| Prefixo | Categoria | Descrição |\n")
        f.write("|---------|-----------|-----------|\n")
        f.write("| NC-LBE-LEG | Legislativo | Poder Legislativo |\n")
        f.write("| NC-LBE-EXE | Executivo | Poder Executivo |\n")
        f.write("| NC-LBE-JUD | Judiciário | Poder Judiciário |\n")
        f.write("| NC-LBE-AGT-* | Agentes | Por tier de agente |\n")
        f.write("| NC-LBE-USR | Usuário | Perfis e consciência |\n")
        f.write("| NC-LBE-FR | Framework | Componentes do framework |\n")
        f.write("| NC-LBE-INT | Integração | Integrações externas |\n")
        f.write("| NC-LBE-CC | Core Components | Componentes centrais |\n")
        f.write("| NC-LBE-DS | DeepSeek | Agentes DeepSeek |\n")
    
    print(f"\nÍndice criado: {index_path}")

def main():
    print("NC-SCR-FR-148: Organização de Lobes na Nova Estrutura")
    print("=" * 60)
    
    try:
        moved = organize_lobes()
        if moved > 0:
            print("\n[SUCESSO] Organização concluída com sucesso!")
        else:
            print("\n[AVISO] Nenhum arquivo foi movido.")
    except Exception as e:
        print(f"\n[ERRO] durante a organização: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()