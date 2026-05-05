#!/usr/bin/env python3
"""
NC-SCR-FR-122 — White Label Anonymizer for Open Source Release
Script para criar versão anônima do projeto removendo dados pessoais

ALTA PERICULOSIDADE: Este script modifica arquivos em massa
SEMPRE executar com --dry-run primeiro
"""

import os
import re
import shutil
import json
import argparse
from datetime import datetime
from pathlib import Path

# Padrões de dados pessoais para remover
PERSONAL_PATTERNS = [
    # Nome do usuário
    (re.compile(r'Lucas Valério', re.IGNORECASE), 'ANONYMOUS_USER'),
    (re.compile(r'Lucas', re.IGNORECASE), 'ANONYMOUS_USER'),
    (re.compile(r'Valério', re.IGNORECASE), 'ANONYMOUS_USER'),
    
    # Caminhos de diretório pessoais
    (re.compile(r'C:\\\\Users\\\\Lucas Valério', re.IGNORECASE), 'C:\\\\Users\\\\ANONYMOUS_USER'),
    (re.compile(r'/home/lucas', re.IGNORECASE), '/home/anonymous'),
    (re.compile(r'/Users/lucas', re.IGNORECASE), '/Users/anonymous'),
    
    # Endereços de email
    (re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'), 'user@example.com'),
    
    # Números de telefone (formato brasileiro)
    (re.compile(r'\(\d{2}\) \d{4,5}-\d{4}'), '(00) 0000-0000'),
    (re.compile(r'\d{2} \d{4,5} \d{4}'), '00 0000 0000'),
    
    # CPF/CNPJ
    (re.compile(r'\d{3}\.\d{3}\.\d{3}-\d{2}'), '000.000.000-00'),
    (re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'), '00.000.000/0000-00'),
]

# Extensões de arquivo para processar
TEXT_FILE_EXTENSIONS = {
    '.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', 
    '.ini', '.cfg', '.conf', '.rst', '.html', '.css', '.js',
    '.ts', '.tsx', '.jsx', '.vue', '.svelte', '.rs', '.go',
    '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb',
    '.pl', '.pm', '.sh', '.bash', '.zsh', '.fish', '.ps1',
    '.bat', '.cmd', '.sql', '.graphql', '.gql', '.proto'
}

def should_process_file(filepath: Path) -> bool:
    """Determina se um arquivo deve ser processado."""
    # Ignorar arquivos ocultos
    if filepath.name.startswith('.'):
        return False
    
    # Ignorar diretórios especiais
    if any(part.startswith('.') for part in filepath.parts):
        return False
    
    # Verificar extensão
    if filepath.suffix.lower() in TEXT_FILE_EXTENSIONS:
        return True
    
    # Arquivos sem extensão mas com conteúdo textual conhecido
    if filepath.name in ['Dockerfile', 'Makefile', 'docker-compose.yml', 'README', 'LICENSE']:
        return True
    
    return False

def anonymize_content(content: str, dry_run: bool = True) -> tuple[str, int]:
    """Anonimiza conteúdo de texto."""
    replacements = 0
    anonymized = content
    
    for pattern, replacement in PERSONAL_PATTERNS:
        matches = list(pattern.finditer(anonymized))
        if matches:
            if not dry_run:
                anonymized = pattern.sub(replacement, anonymized)
            replacements += len(matches)
    
    return anonymized, replacements

def process_file(filepath: Path, dry_run: bool = True, verbose: bool = False) -> int:
    """Processa um único arquivo."""
    try:
        # Ler conteúdo original
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            original_content = f.read()
        
        # Anonimizar conteúdo
        anonymized_content, replacements = anonymize_content(original_content, dry_run)
        
        if replacements > 0:
            if verbose:
                print(f"  {filepath}: {replacements} substituições")
            
            if not dry_run:
                # Criar backup
                backup_path = filepath.with_suffix(filepath.suffix + '.backup')
                if not backup_path.exists():
                    shutil.copy2(filepath, backup_path)
                
                # Escrever conteúdo anonimizado
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(anonymized_content)
        
        return replacements
    
    except Exception as e:
        print(f"  ERRO processando {filepath}: {e}")
        return 0

def main():
    parser = argparse.ArgumentParser(description='Anonimizador White Label para Open Source')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Mostrar mudanças sem aplicar (RECOMENDADO)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostrar detalhes de cada arquivo')
    parser.add_argument('--output-dir', type=str,
                       help='Diretório de saída para cópia anonimizada (opcional)')
    parser.add_argument('--exclude', type=str, nargs='+',
                       help='Padrões para excluir (ex: "*.log" "tmp/*")')
    
    args = parser.parse_args()
    
    # Diretório raiz do projeto
    project_root = Path.cwd()
    print(f"Diretório raiz: {project_root}")
    print(f"Modo dry-run: {'SIM' if args.dry_run else 'NÃO'}")
    print(f"Verbose: {'SIM' if args.verbose else 'NÃO'}")
    print()
    
    # Coletar arquivos para processar
    files_to_process = []
    total_files = 0
    
    for root, dirs, files in os.walk(project_root):
        root_path = Path(root)
        
        # Pular diretórios ocultos
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            filepath = root_path / file
            
            # Verificar se deve processar
            if should_process_file(filepath):
                # Verificar exclusões
                if args.exclude:
                    exclude = False
                    for pattern in args.exclude:
                        if filepath.match(pattern):
                            exclude = True
                            break
                    if exclude:
                        continue
                
                files_to_process.append(filepath)
                total_files += 1
    
    print(f"Arquivos encontrados para processamento: {total_files}")
    print()
    
    # Processar arquivos
    total_replacements = 0
    processed_files = 0
    
    for i, filepath in enumerate(files_to_process, 1):
        if args.verbose or i % 100 == 0:
            print(f"Processando [{i}/{total_files}]: {filepath.relative_to(project_root)}")
        
        replacements = process_file(filepath, args.dry_run, args.verbose)
        
        if replacements > 0:
            processed_files += 1
            total_replacements += replacements
    
    print()
    print("=" * 60)
    print("RELATÓRIO DE ANONIMIZAÇÃO")
    print("=" * 60)
    print(f"Arquivos processados: {processed_files}/{total_files}")
    print(f"Substituições totais: {total_replacements}")
    print(f"Modo dry-run: {'SIM' if args.dry_run else 'NÃO'}")
    
    if args.dry_run:
        print("\n⚠️  MODO DRY-RUN: Nenhuma alteração foi aplicada.")
        print("Execute sem --dry-run para aplicar as mudanças.")
    
    # Criar cópia anonimizada se especificado
    if args.output_dir and not args.dry_run:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nCriando cópia anonimizada em: {output_path}")
        
        # Copiar estrutura do projeto
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            
            # Pular diretórios ocultos
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                src_path = root_path / file
                rel_path = src_path.relative_to(project_root)
                dst_path = output_path / rel_path
                
                # Criar diretório de destino
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                
                if should_process_file(src_path):
                    # Processar e copiar arquivo de texto
                    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    anonymized_content, _ = anonymize_content(content, dry_run=False)
                    
                    with open(dst_path, 'w', encoding='utf-8') as f:
                        f.write(anonymized_content)
                else:
                    # Copiar arquivo binário diretamente
                    shutil.copy2(src_path, dst_path)
        
        print(f"Cópia anonimizada criada com sucesso em: {output_path}")

if __name__ == '__main__':
    main()