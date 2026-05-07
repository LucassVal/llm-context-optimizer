# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""
NC-SCR-FR-121 — Update File References After SSOT Rename
Script para atualizar referencias a arquivos renomeados
"""

import os
import re
import argparse
from datetime import datetime
from pathlib import Path

# Mapeamento de renomeacoes
RENAME_MAPPINGS = [
    # Padrao antigo -> Novo padrao
    # IMPORTANTE: Ja aplicamos FR prefix, entao so precisamos atualizar referencias
    # que ainda usam o padrao antigo SEM FR
    (r'NC-RPT-(?!FR-)(\d{3}-)', r'NC-RPT-FR-\1'),
    (r'NC-TEST-(?!FR-)(\d{3}-)', r'NC-TEST-FR-\1'),
    (r'NC-DS-(?!FR-)(\d{3}-)', r'NC-DS-FR-\1'),
    (r'NC-NAM-FR-001a-', r'NC-NAM-FR-001-'),
    (r'NC-NAM-FR-001b-', r'NC-NAM-FR-001-'),
    (r'NC-NAM-FR-001c-', r'NC-NAM-FR-001-'),
    (r'NC-NAM-FR-001d-', r'NC-NAM-FR-001-'),
    (r'NC-CMD-EXAMPLE\.md', r'NC-CMD-FR-001-example.md'),
    (r'NC-HK-EXAMPLE\.py', r'NC-HK-FR-001-example.py'),
    (r'NC-SCR-FR-103b-', r'NC-SCR-FR-103-'),
]

# Extensoes de arquivos para analisar
FILE_EXTENSIONS = ['.py', '.md', '.yaml', '.yml', '.json', '.txt', '.ps1', '.bat']

def find_references(root_dir, dry_run=True):
    """Encontra e atualiza referencias a arquivos renomeados"""
    results = {
        'total_files_scanned': 0,
        'files_with_references': 0,
        'total_replacements': 0,
        'replacements_by_pattern': {},
        'updated_files': [],
        'errors': [],
        'timestamp': datetime.now().isoformat(),
    }
    
    for old_pattern, new_pattern in RENAME_MAPPINGS:
        results['replacements_by_pattern'][old_pattern] = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Ignorar diretorios especiais
        if any(x in root for x in ['.git', 'node_modules', '.ruff_cache', '.nc', '__pycache__', '.rename_backup']):
            continue
            
        for filename in files:
            if any(filename.endswith(ext) for ext in FILE_EXTENSIONS):
                filepath = os.path.join(root, filename)
                results['total_files_scanned'] += 1
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    original_content = content
                    replacements_made = 0
                    
                    # Aplicar cada mapeamento
                    for old_pattern, new_pattern in RENAME_MAPPINGS:
                        # Contar ocorrencias
                        try:
                            count_before = len(re.findall(old_pattern, content))
                            if count_before > 0:
                                # Fazer substituicao
                                content = re.sub(old_pattern, new_pattern, content)
                                count_after = len(re.findall(old_pattern, content))
                                replacements = count_before - count_after
                                
                                if replacements > 0:
                                    results['replacements_by_pattern'][old_pattern] += replacements
                                    results['total_replacements'] += replacements
                                    replacements_made += replacements
                        except re.error as e:
                            print(f"  ERRO regex em {filepath}: {old_pattern} -> {e}")
                            continue
                    
                    # Se houve alteracoes, atualizar arquivo
                    if replacements_made > 0 and content != original_content:
                        results['files_with_references'] += 1
                        
                        if not dry_run:
                            # Fazer backup antes de modificar
                            backup_path = filepath + '.backup'
                            with open(backup_path, 'w', encoding='utf-8') as f:
                                f.write(original_content)
                            
                            # Escrever novo conteudo
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            results['updated_files'].append({
                                'file': filepath,
                                'backup': backup_path,
                                'replacements': replacements_made,
                            })
                        else:
                            results['updated_files'].append({
                                'file': filepath,
                                'replacements': replacements_made,
                                'dry_run': True,
                            })
                            
                except Exception as e:
                    results['errors'].append({
                        'file': filepath,
                        'error': str(e),
                    })
    
    return results

def generate_report(results, dry_run=True):
    """Gera relatorio da operacao"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"NC-REF-UPDATE-REPORT-{timestamp}.json"
    
    import json
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return report_file

def main():
    parser = argparse.ArgumentParser(description='Atualiza referencias a arquivos renomeados')
    parser.add_argument('--root-dir', default='01_neocortex_framework',
                       help='Diretorio raiz para analise (padrao: 01_neocortex_framework)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Apenas simular, nao modificar arquivos (PADRAO: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Executar atualizacoes (PERIGOSO - use com cuidado)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NC-SCR-FR-121 — UPDATE FILE REFERENCES AFTER SSOT RENAME")
    print("=" * 80)
    print(f"Diretorio: {args.root_dir}")
    print(f"Modo: {'SIMULACAO' if not args.execute else 'EXECUCAO (PERIGOSO)'}")
    print("=" * 80)
    
    # Verificar se diretorio existe
    if not os.path.exists(args.root_dir):
        print(f" Diretorio nao encontrado: {args.root_dir}")
        return 1
    
    # Executar busca por referencias
    print("\n ANALISANDO REFERENCIAS...")
    results = find_references(args.root_dir, dry_run=not args.execute)
    
    print(f"\n RESULTADOS DA ANALISE:")
    print(f"  Arquivos escaneados: {results['total_files_scanned']}")
    print(f"  Arquivos com referencias: {results['files_with_references']}")
    print(f"  Total de substituicoes: {results['total_replacements']}")
    
    if results['total_replacements'] > 0:
        print(f"\n SUBSTITUICOES POR PADRAO:")
        for pattern, count in results['replacements_by_pattern'].items():
            if count > 0:
                print(f"  {pattern}: {count}")
        
        print(f"\n ARQUIVOS A SEREM ATUALIZADOS (primeiros 5):")
        for i, file_info in enumerate(results['updated_files'][:5], 1):
            print(f"  {i}. {file_info['file']}")
            print(f"     Substituicoes: {file_info['replacements']}")
        
        # Confirmar execucao
        if args.execute:
            print("\n      ALERTA: MODO EXECUCAO ATIVADO     ")
            print("Esta operacao modificara arquivos permanentemente.")
            confirmation = input("Digite 'CONFIRMAR' para continuar: ")
            
            if confirmation != 'CONFIRMAR':
                print(" Operacao cancelada pelo usuario.")
                return 0
            
            # Executar atualizacoes reais
            print("\n EXECUTANDO ATUALIZACOES...")
            results = find_references(args.root_dir, dry_run=False)
    
    # Gerar relatorio
    report_file = generate_report(results, dry_run=not args.execute)
    
    print(f"\n RELATORIO GERADO: {report_file}")
    
    if results['errors']:
        print(f"\n ERROS ENCONTRADOS: {len(results['errors'])}")
        for error in results['errors'][:3]:
            print(f"  {error['file']}: {error['error']}")
    
    print("\n" + "=" * 80)
    print(" RESUMO FINAL")
    print("=" * 80)
    print(f"Modo: {'SIMULACAO' if not args.execute else 'EXECUCAO'}")
    print(f"Arquivos escaneados: {results['total_files_scanned']}")
    print(f"Substituicoes identificadas: {results['total_replacements']}")
    
    if not args.execute and results['total_replacements'] > 0:
        print(f"\n Para executar as atualizacoes, use: --execute")
        print(f" Exemplo: python NC-SCR-FR-121-update-references.py --execute")
    
    print("=" * 80)
    return 0

if __name__ == '__main__':
    exit(main())
