# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3
"""
NC-SCR-FR-120 — Batch Rename Fix for SSOT Compliance
Script para corrigir nomes de arquivos que não seguem padrão SSOT

 ALTA PERICULOSIDADE: Este script renomeia arquivos em massa
 SEMPRE executar com --dry-run primeiro
 Backup automático criado antes de qualquer renomeação
"""

import os
import re
import shutil
import json
import argparse
from datetime import datetime
from pathlib import Path

# Padrão SSOT correto: NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext
SSOT_PATTERN = re.compile(r'^NC-[A-Z]+-[A-Z]+-[0-9]{3}-.+\..+$')

# Padroes problematicos identificados na auditoria
PROBLEM_PATTERNS = [
    # 1. Arquivos LOBE sem FR/SV/SCR prefix (ex: NC-LBE-CEREBRAL-FRONTAL-001.mdc)
    # Problema: NC-LBE-CEREBRAL-FRONTAL-001.mdc -> deveria ser NC-LBE-FR-001-cerebral-frontal.mdc
    (re.compile(r'^NC-LBE-([A-Z]+)-([0-9]{3})\.(mdc)$'), 
     lambda m: "NC-LBE-FR-" + m.group(2) + "-" + m.group(1).lower().replace('_', '-') + "." + m.group(3)),
    
    # 2. Arquivos LOBE com FR/SV/SCR mas descricao e numero trocados (ex: NC-LBE-FR-ARCHITECTURE-001.mdc)
    # Problema: NC-LBE-FR-ARCHITECTURE-001.mdc -> deveria ser NC-LBE-FR-001-architecture.mdc
    (re.compile(r'^NC-(LBE-[A-Z]+)-([A-Z]+)-([0-9]{3})\.(mdc)$'),
     lambda m: "NC-" + m.group(1) + "-" + m.group(3) + "-" + m.group(2).lower() + "." + m.group(4)),
    
    # 3. Arquivos com timestamp no final (ex: NC-LBE-FR-ARCHITECTURE-001_20260410_155754.mdc)
    # Problema: timestamp no final -> remover timestamp
    (re.compile(r'^NC-(LBE-[A-Z]+)-([A-Z]+)-([0-9]{3})_(\d{8}_\d{6})\.(mdc)$'),
     lambda m: "NC-" + m.group(1) + "-" + m.group(3) + "-" + m.group(2).lower() + "." + m.group(5)),
    
    # 4. Arquivos LOBE sem FR/SV/SCR e com timestamp (ex: NC-LBE-CEREBRAL-FRONTAL-001_20260410_155754.mdc)
    (re.compile(r'^NC-LBE-([A-Z]+)-([0-9]{3})_(\d{8}_\d{6})\.(mdc)$'),
     lambda m: "NC-LBE-FR-" + m.group(2) + "-" + m.group(1).lower().replace('_', '-') + "." + m.group(4)),
    
    # 5. Arquivos RPT sem prefixo FR/SV/SCR (ex: NC-RPT-117-core-audit-report.json)
    # Problema: NC-RPT-117-core-audit-report.json -> deveria ser NC-RPT-FR-117-core-audit-report.json
    (re.compile(r'^NC-RPT-([0-9]{3})-([a-z0-9_-]+)\.(json|py|md)$'),
     lambda m: "NC-RPT-FR-" + m.group(1) + "-" + m.group(2) + "." + m.group(3)),
    
    # 6. Arquivos TEST sem prefixo (ex: NC-TEST-119-picoclaw-integration.py)
    # Problema: NC-TEST-119-picoclaw-integration.py -> deveria ser NC-TEST-FR-119-picoclaw-integration.py
    (re.compile(r'^NC-TEST-([0-9]{3})-([a-z0-9_-]+)\.py$'),
     lambda m: "NC-TEST-FR-" + m.group(1) + "-" + m.group(2) + ".py"),
    
    # 7. Arquivos DS sem prefixo (ex: NC-DS-118-fix-f841-metrics-store.yaml)
    # Problema: NC-DS-118-fix-f841-metrics-store.yaml -> deveria ser NC-DS-FR-118-fix-f841-metrics-store.yaml
    (re.compile(r'^NC-DS-([0-9]{3})-([a-z0-9_-]+)\.yaml$'),
     lambda m: "NC-DS-FR-" + m.group(1) + "-" + m.group(2) + ".yaml"),
    
    # 8. Arquivos SUPER sem 3-digit number (ex: NC-SUPER-001-governance.py esta correto)
    # NC-SUPER-001-governance.py -> ja esta correto
    
    # 9. Arquivos NAM com letra apos numero (ex: NC-NAM-FR-001a-tools-registry.md)
    # Problema: NC-NAM-FR-001a-tools-registry.md -> deveria ser NC-NAM-FR-001-tools-registry.md
    (re.compile(r'^NC-NAM-FR-([0-9]{3})([a-z])-([a-z0-9_-]+)\.(md|backup)$'),
     lambda m: "NC-NAM-FR-" + m.group(1) + "-" + m.group(3) + "." + m.group(4)),
    
    # 10. Arquivos CMD sem prefixo (ex: NC-CMD-EXAMPLE.md)
    (re.compile(r'^NC-CMD-([A-Za-z0-9_-]+)\.md$'),
     lambda m: "NC-CMD-FR-001-" + m.group(1).lower() + ".md"),
    
    # 11. Arquivos HK sem prefixo (ex: NC-HK-EXAMPLE.py)
    (re.compile(r'^NC-HK-([A-Za-z0-9_-]+)\.py$'),
     lambda m: "NC-HK-FR-001-" + m.group(1).lower() + ".py"),
    
    # 12. Arquivos SCR com extensao .ps1 (ex: NC-SCR-FR-103b-start-with-mc.ps1)
    # Problema: NC-SCR-FR-103b-start-with-mc.ps1 -> deveria ser NC-SCR-FR-103-start-with-mc.ps1
    (re.compile(r'^NC-SCR-FR-([0-9]{3})([a-z])-([a-z0-9_-]+)\.ps1$'),
     lambda m: "NC-SCR-FR-" + m.group(1) + "-" + m.group(3) + ".ps1"),
    
    # 13. Padrao geral para outros tipos: numero e descricao trocados
    (re.compile(r'^NC-([A-Z]+)-([A-Z]+)-([A-Z][a-zA-Z0-9]*)-([0-9]{3})\.([a-z]+)$'),
     lambda m: "NC-" + m.group(1) + "-" + m.group(2) + "-" + m.group(4) + "-" + m.group(3).lower().replace('_', '-') + "." + m.group(5)),
]

# Excecoes permitidas (nao renomear)
EXCEPTIONS = [
    r'^NC-CASC-REPORT-\d{8}-\d{6}\.md$',
    r'^NC-LEXICO-\d{8}-\d{6}\.json$',
    r'^NC-LEXICO-LATEST\.json$',
    r'^NC-[A-Z]+-FR-001-framework-ledger\.json$',  # LEDGER especial
    r'^NC-SUPER-\d{3}-[a-z0-9_-]+\.py$',  # SUPER tools ja estao corretos
    r'^NC-TOOL-FR-\d{3}-[a-z0-9_-]+\.py$',  # TOOL tools ja estao corretos
    r'^NC-GOV-FR-\d{3}-[a-z0-9_-]+\.(yaml|md)$',  # GOV docs ja estao corretos
    r'^NC-SCR-FR-\d{3}-[a-z0-9_-]+\.py$',  # SCR scripts ja estao corretos
    # Removed exceptions for RPT, TEST, DS - they need to be fixed
]

def is_exception(filename):
    """Verifica se arquivo é exceção permitida"""
    for pattern in EXCEPTIONS:
        if re.match(pattern, filename):
            return True
    return False

def analyze_directory(root_dir, dry_run=True):
    """Analisa diretório e identifica arquivos não conformes"""
    results = {
        'total_nc_files': 0,
        'conformant': 0,
        'non_conformant': 0,
        'exceptions': 0,
        'rename_candidates': [],
        'analysis_time': datetime.now().isoformat(),
        'root_dir': root_dir,
    }
    
    for root, dirs, files in os.walk(root_dir):
        # Ignorar diretórios especiais
        if any(x in root for x in ['archive', '.git', 'node_modules', '.ruff_cache', '.nc', '.agents']):
            continue
            
        for filename in files:
            if filename.startswith('NC-'):
                results['total_nc_files'] += 1
                
                # Verificar exceções
                if is_exception(filename):
                    results['exceptions'] += 1
                    continue
                
                # Verificar conformidade SSOT
                if SSOT_PATTERN.match(filename):
                    results['conformant'] += 1
                else:
                    results['non_conformant'] += 1
                    
                    # Tentar encontrar padrão problemático
                    new_name = None
                    problem_type = "unknown"
                    
                    for pattern, transformer in PROBLEM_PATTERNS:
                        match = pattern.match(filename)
                        if match:
                            new_name = transformer(match)
                            problem_type = pattern.pattern[:50]
                            break
                    
                    if new_name:
                        old_path = os.path.join(root, filename)
                        new_path = os.path.join(root, new_name)
                        
                        # Verificar se novo nome já existe
                        if os.path.exists(new_path):
                            new_name = f"{new_name.split('.')[0]}_fixed.{new_name.split('.')[1]}"
                            new_path = os.path.join(root, new_name)
                        
                        results['rename_candidates'].append({
                            'old_name': filename,
                            'new_name': new_name,
                            'old_path': old_path,
                            'new_path': new_path,
                            'problem_type': problem_type,
                            'directory': root,
                        })
    
    return results

def create_backup(root_dir, backup_dir):
    """Cria backup dos arquivos NC-*"""
    print(f"[BACKUP] Criando backup em: {backup_dir}")
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_log = []
    for root, dirs, files in os.walk(root_dir):
        if any(x in root for x in ['archive', '.git', 'node_modules', '.ruff_cache', '.nc']):
            continue
            
        for filename in files:
            if filename.startswith('NC-'):
                src = os.path.join(root, filename)
                rel_path = os.path.relpath(src, root_dir)
                dst = os.path.join(backup_dir, rel_path)
                
                # Criar diretório de destino se necessário
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                
                try:
                    shutil.copy2(src, dst)
                    backup_log.append({
                        'source': src,
                        'backup': dst,
                        'timestamp': datetime.now().isoformat(),
                    })
                except Exception as e:
                    print(f"[ERRO] Erro ao fazer backup de {src}: {e}")
    
    # Salvar log de backup
    backup_log_file = os.path.join(backup_dir, 'backup_log.json')
    with open(backup_log_file, 'w', encoding='utf-8') as f:
        json.dump(backup_log, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Backup completo: {len(backup_log)} arquivos copiados")
    print(f"[LOG] Log de backup: {backup_log_file}")
    
    return backup_log_file

def execute_renames(rename_candidates, dry_run=True):
    """Executa renomeações (ou simula se dry_run)"""
    results = {
        'successful': [],
        'failed': [],
        'skipped': [],
        'total': len(rename_candidates),
    }
    
    print(f"\n{' SIMULAÇÃO' if dry_run else ' EXECUTANDO'} RENOMEIAÇÃO")
    print(f"Arquivos a processar: {len(rename_candidates)}")
    
    for i, candidate in enumerate(rename_candidates, 1):
        old_path = candidate['old_path']
        new_path = candidate['new_path']
        
        print(f"\n[{i}/{len(rename_candidates)}] {candidate['old_name']}")
        print(f"   -> {candidate['new_name']}")
        print(f"   Tipo problema: {candidate['problem_type']}")
        print(f"   Diretorio: {candidate['directory']}")
        
        # Verificar se arquivo origem existe
        if not os.path.exists(old_path):
            print("    Arquivo origem não existe")
            results['failed'].append({**candidate, 'error': 'Source file not found'})
            continue
        
        # Verificar se arquivo destino já existe
        if os.path.exists(new_path):
            print("     Arquivo destino já existe (pulando)")
            results['skipped'].append({**candidate, 'error': 'Destination already exists'})
            continue
        
        if dry_run:
            print("    (SIMULAÇÃO) Seria renomeado")
            results['successful'].append(candidate)
        else:
            try:
                os.rename(old_path, new_path)
                print("    Renomeado com sucesso")
                results['successful'].append(candidate)
            except Exception as e:
                print(f"    Erro ao renomear: {e}")
                results['failed'].append({**candidate, 'error': str(e)})
    
    return results

def generate_report(analysis_results, rename_results, backup_file=None):
    """Gera relatório detalhado da operação"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"NC-RENAME-REPORT-{timestamp}.json"
    
    report = {
        'metadata': {
            'script': 'NC-SCR-FR-120-batch-rename-fix.py',
            'timestamp': datetime.now().isoformat(),
            'dry_run': rename_results.get('dry_run', True),
        },
        'analysis': analysis_results,
        'rename_results': rename_results,
        'backup_info': backup_file,
        'summary': {
            'total_nc_files': analysis_results['total_nc_files'],
            'conformant_before': analysis_results['conformant'],
            'non_conformant_before': analysis_results['non_conformant'],
            'exceptions': analysis_results['exceptions'],
            'rename_candidates': len(analysis_results['rename_candidates']),
            'successful_renames': len(rename_results.get('successful', [])),
            'failed_renames': len(rename_results.get('failed', [])),
            'skipped_renames': len(rename_results.get('skipped', [])),
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n RELATÓRIO GERADO: {report_file}")
    return report_file

def main():
    parser = argparse.ArgumentParser(description='Corrige nomes de arquivos NC-* para conformidade SSOT')
    parser.add_argument('--root-dir', default='01_neocortex_framework',
                       help='Diretório raiz para análise (padrão: 01_neocortex_framework)')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Apenas simular, não renomear (PADRÃO: True)')
    parser.add_argument('--execute', action='store_true',
                       help='Executar renomeações (PERIGOSO - use com cuidado)')
    parser.add_argument('--backup-dir', default='.rename_backup',
                       help='Diretório para backup (padrão: .rename_backup)')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Pular criação de backup (NÃO RECOMENDADO)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NC-SCR-FR-120 — BATCH RENAME FIX FOR SSOT COMPLIANCE")
    print("=" * 80)
    print(f"Diretório: {args.root_dir}")
    print(f"Modo: {'SIMULAÇÃO' if not args.execute else 'EXECUÇÃO (PERIGOSO)'}")
    print(f"Backup: {'DESATIVADO' if args.skip_backup else 'ATIVADO'}")
    print("=" * 80)
    
    # Verificar se diretório existe
    if not os.path.exists(args.root_dir):
        print(f" Diretório não encontrado: {args.root_dir}")
        return 1
    
    # 1. Análise
    print("\n ANALISANDO ARQUIVOS NC-*...")
    analysis_results = analyze_directory(args.root_dir, dry_run=True)
    
    print(f"\n RESULTADOS DA ANÁLISE:")
    print(f"  Total arquivos NC-*: {analysis_results['total_nc_files']}")
    print(f"  Conformes com SSOT: {analysis_results['conformant']} ({analysis_results['conformant']/analysis_results['total_nc_files']*100:.1f}%)")
    print(f"  Não conformes: {analysis_results['non_conformant']} ({analysis_results['non_conformant']/analysis_results['total_nc_files']*100:.1f}%)")
    print(f"  Exceções: {analysis_results['exceptions']}")
    print(f"  Candidatos a renomeação: {len(analysis_results['rename_candidates'])}")
    
    if len(analysis_results['rename_candidates']) == 0:
        print("\n Nenhum arquivo precisa ser renomeado!")
        return 0
    
    # 2. Mostrar exemplos
    print(f"\n EXEMPLOS DE RENOMEIAÇÃO (primeiros 5):")
    for i, candidate in enumerate(analysis_results['rename_candidates'][:5], 1):
        print(f"  {i}. {candidate['old_name']} -> {candidate['new_name']}")
    
    # 3. Se for execução real, criar backup
    backup_file = None
    if args.execute and not args.skip_backup:
        backup_file = create_backup(args.root_dir, args.backup_dir)
    
    # 4. Confirmar execução
    if args.execute:
        print("\n      ALERTA: MODO EXECUÇÃO ATIVADO     ")
        print("Esta operação renomeará arquivos permanentemente.")
        confirmation = input("Digite 'CONFIRMAR' para continuar: ")
        
        if confirmation != 'CONFIRMAR':
            print(" Operação cancelada pelo usuário.")
            return 0
    
    # 5. Executar renomeações
    rename_results = execute_renames(
        analysis_results['rename_candidates'], 
        dry_run=not args.execute
    )
    rename_results['dry_run'] = not args.execute
    
    # 6. Gerar relatório
    report_file = generate_report(analysis_results, rename_results, backup_file)
    
    # 7. Resumo final
    print("\n" + "=" * 80)
    print(" RESUMO FINAL DA OPERAÇÃO")
    print("=" * 80)
    print(f"Modo: {'SIMULAÇÃO' if not args.execute else 'EXECUÇÃO'}")
    print(f"Arquivos NC-* analisados: {analysis_results['total_nc_files']}")
    print(f"Conformidade inicial: {analysis_results['conformant']/analysis_results['total_nc_files']*100:.1f}%")
    
    if args.execute:
        new_conformant = analysis_results['conformant'] + len(rename_results['successful'])
        new_percentage = new_conformant / analysis_results['total_nc_files'] * 100
        print(f"Conformidade após: {new_percentage:.1f}%")
        print(f"Arquivos renomeados: {len(rename_results['successful'])}")
        print(f"Falhas: {len(rename_results['failed'])}")
        print(f"Pulados: {len(rename_results['skipped'])}")
        
        if backup_file and not args.skip_backup:
            print(f"\n  Backup criado em: {args.backup_dir}")
            print(f"   Log: {backup_file}")
    
    print(f"\n Relatório detalhado: {report_file}")
    
    if not args.execute:
        print("\n Para executar as renomeações, use: --execute")
        print(" Exemplo: python NC-SCR-FR-120-batch-rename-fix.py --execute")
    
    print("=" * 80)
    return 0

if __name__ == '__main__':
    exit(main())
