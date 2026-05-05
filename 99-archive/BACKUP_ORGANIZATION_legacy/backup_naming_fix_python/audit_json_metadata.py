#!/usr/bin/env python3
"""
Auditoria de metadados JSON duplicados
Identifica arquivos .metadata.json duplicados e sugere limpeza
"""

import json
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any
from collections import defaultdict

def calculate_file_hash(file_path: Path) -> str:
    """Calcula hash MD5 do conteúdo do arquivo"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def find_duplicate_metadata(directory: str) -> Dict[str, List[str]]:
    """Encontra arquivos .metadata.json duplicados"""
    path = Path(directory)
    
    # Encontrar todos os arquivos .metadata.json
    metadata_files = list(path.glob("**/*.metadata.json"))
    print(f"Encontrados {len(metadata_files)} arquivos .metadata.json")
    
    # Agrupar por hash
    hash_groups = defaultdict(list)
    
    for file_path in metadata_files:
        try:
            file_hash = calculate_file_hash(file_path)
            hash_groups[file_hash].append(str(file_path))
        except Exception as e:
            print(f"Erro ao processar {file_path}: {e}")
    
    # Filtrar apenas grupos com duplicatas
    duplicates = {hash_val: files for hash_val, files in hash_groups.items() if len(files) > 1}
    
    return duplicates

def analyze_metadata_structure(directory: str) -> Dict[str, Any]:
    """Analisa estrutura dos metadados JSON"""
    path = Path(directory)
    metadata_files = list(path.glob("**/*.metadata.json"))
    
    stats = {
        "total_files": len(metadata_files),
        "files_by_extension": defaultdict(int),
        "files_by_size": defaultdict(int),
        "common_fields": defaultdict(int),
        "invalid_json": 0,
        "empty_files": 0
    }
    
    for file_path in metadata_files:
        try:
            # Analisar extensão do arquivo original
            original_name = file_path.name.replace('.metadata.json', '')
            ext = Path(original_name).suffix.lower()
            stats["files_by_extension"][ext] += 1
            
            # Analisar tamanho
            file_size = file_path.stat().st_size
            size_category = "tiny" if file_size < 1024 else "small" if file_size < 10240 else "medium" if file_size < 102400 else "large"
            stats["files_by_size"][size_category] += 1
            
            if file_size == 0:
                stats["empty_files"] += 1
                continue
            
            # Analisar estrutura JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    
                    # Contar campos comuns
                    if isinstance(data, dict):
                        for key in data.keys():
                            stats["common_fields"][key] += 1
                    else:
                        stats["common_fields"]["non_dict"] += 1
                        
                except json.JSONDecodeError:
                    stats["invalid_json"] += 1
                    
        except Exception as e:
            print(f"Erro ao analisar {file_path}: {e}")
    
    return stats

def suggest_cleanup_actions(duplicates: Dict[str, List[str]], stats: Dict[str, Any]) -> List[str]:
    """Sugere ações de limpeza baseadas na análise"""
    suggestions = []
    
    # Sugestões baseadas em duplicatas
    total_duplicate_groups = len(duplicates)
    total_duplicate_files = sum(len(files) for files in duplicates.values())
    
    if total_duplicate_groups > 0:
        suggestions.append(f"Remover {total_duplicate_files - total_duplicate_groups} arquivos duplicados ({total_duplicate_groups} grupos)")
        
        # Exemplo de grupos grandes
        large_groups = [(hash_val, files) for hash_val, files in duplicates.items() if len(files) > 3]
        if large_groups:
            suggestions.append(f"Grupos grandes encontrados: {len(large_groups)} grupos com mais de 3 arquivos idênticos")
    
    # Sugestões baseadas em estatísticas
    if stats["empty_files"] > 0:
        suggestions.append(f"Remover {stats['empty_files']} arquivos vazios")
    
    if stats["invalid_json"] > 0:
        suggestions.append(f"Corrigir {stats['invalid_json']} arquivos JSON inválidos")
    
    # Sugestões baseadas em extensões
    for ext, count in stats["files_by_extension"].items():
        if count > 20:  # Muitos arquivos de um tipo
            suggestions.append(f"Consolidar {count} arquivos de metadados para extensão {ext}")
    
    return suggestions

def main():
    """Função principal"""
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    
    if not brain_dir.exists():
        print(f"Diretório não encontrado: {brain_dir}")
        return
    
    print("=== AUDITORIA DE METADADOS JSON ===")
    print(f"Diretório: {brain_dir}")
    print()
    
    # Encontrar duplicatas
    print("1. Buscando arquivos duplicados...")
    duplicates = find_duplicate_metadata(brain_dir)
    
    print(f"\n2. Análise de estrutura...")
    stats = analyze_metadata_structure(brain_dir)
    
    print(f"\n3. Gerando sugestões de limpeza...")
    suggestions = suggest_cleanup_actions(duplicates, stats)
    
    # Exibir resultados
    print(f"\n=== RESULTADOS ===")
    print(f"Total de arquivos .metadata.json: {stats['total_files']}")
    print(f"Arquivos vazios: {stats['empty_files']}")
    print(f"Arquivos JSON inválidos: {stats['invalid_json']}")
    print(f"Grupos de duplicatas: {len(duplicates)}")
    
    if duplicates:
        print(f"\n=== DUPLICATAS ENCONTRADAS ===")
        for i, (hash_val, files) in enumerate(list(duplicates.items())[:5], 1):  # Mostrar apenas 5 grupos
            print(f"\nGrupo {i} ({len(files)} arquivos):")
            for file_path in files[:3]:  # Mostrar apenas 3 arquivos por grupo
                print(f"  • {file_path}")
            if len(files) > 3:
                print(f"  ... e mais {len(files) - 3} arquivos")
    
    print(f"\n=== DISTRIBUIÇÃO POR EXTENSÃO ===")
    for ext, count in sorted(stats["files_by_extension"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext or '(sem extensão)'}: {count} arquivos")
    
    print(f"\n=== CAMPOS MAIS COMUNS ===")
    for field, count in sorted(stats["common_fields"].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {field}: {count} arquivos")
    
    print(f"\n=== SUGESTÕES DE LIMPEZA ===")
    if suggestions:
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")
    else:
        print("Nenhuma ação de limpeza necessária.")
    
    # Salvar relatório
    report = {
        "audit_date": "2026-04-22T12:55:00Z",
        "directory": str(brain_dir),
        "duplicates": {hash_val: files for hash_val, files in duplicates.items()},
        "statistics": stats,
        "suggestions": suggestions
    }
    
    report_file = brain_dir / "metadata_audit_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatório salvo em: {report_file}")

if __name__ == "__main__":
    main()