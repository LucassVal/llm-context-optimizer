#!/usr/bin/env python3
"""
Validador de YAML para tickets NeoCortex
Verifica estrutura, campos obrigatórios e segurança
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

REQUIRED_FIELDS = [
    "ticket_id",
    "status",
    "title",
    "description",
    "priority"
]

OPTIONAL_FIELDS = [
    "created_at",
    "updated_at",
    "assigned_to",
    "category",
    "tags",
    "dependencies",
    "handoff_ready",
    "handoff_target"
]

def validate_yaml_structure(file_path: Path) -> Dict[str, Any]:
    """Valida estrutura de um arquivo YAML"""
    results = {
        "file": str(file_path),
        "valid": False,
        "errors": [],
        "warnings": [],
        "fields_present": [],
        "fields_missing": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Verificar se não contém tags YAML perigosas
        dangerous_patterns = [
            "!!python/",
            "!!python/object",
            "__import__",
            "eval(",
            "exec(",
            "subprocess"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content.lower():
                results["errors"].append(f"Conteúdo perigoso detectado: {pattern}")
        
        # Carregar YAML com loader seguro
        data = yaml.safe_load(content)
        
        if data is None:
            results["errors"].append("YAML vazio ou inválido")
            return results
        
        # Verificar campos obrigatórios
        for field in REQUIRED_FIELDS:
            if field not in data:
                results["fields_missing"].append(field)
                results["errors"].append(f"Campo obrigatório ausente: {field}")
            else:
                results["fields_present"].append(field)
        
        # Verificar campos opcionais presentes
        for field in OPTIONAL_FIELDS:
            if field in data:
                results["fields_present"].append(field)
        
        # Validações específicas
        if "ticket_id" in data:
            ticket_id = data["ticket_id"]
            if not isinstance(ticket_id, str):
                results["errors"].append("ticket_id deve ser string")
            elif not ticket_id.startswith("NC-DS-"):
                results["warnings"].append(f"ticket_id não segue padrão NC-DS-: {ticket_id}")
        
        if "priority" in data:
            valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
            if data["priority"] not in valid_priorities:
                results["warnings"].append(f"Prioridade inválida: {data['priority']}. Válidas: {valid_priorities}")
        
        if "status" in data:
            valid_statuses = ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED", "BLOCKED"]
            if data["status"] not in valid_statuses:
                results["warnings"].append(f"Status inválido: {data['status']}. Válidos: {valid_statuses}")
        
        if len(results["errors"]) == 0:
            results["valid"] = True
            
    except yaml.YAMLError as e:
        results["errors"].append(f"Erro de parsing YAML: {str(e)}")
    except Exception as e:
        results["errors"].append(f"Erro inesperado: {str(e)}")
    
    return results

def validate_all_yamls(directory: str) -> Dict[str, Any]:
    """Valida todos os arquivos YAML no diretório"""
    path = Path(directory)
    yaml_files = list(path.glob("**/*.yaml"))
    
    print(f"Encontrados {len(yaml_files)} arquivos YAML")
    
    results = {
        "total_files": len(yaml_files),
        "valid_files": 0,
        "invalid_files": 0,
        "files": [],
        "summary": {
            "errors": [],
            "warnings": []
        }
    }
    
    for yaml_file in yaml_files:
        print(f"Validando: {yaml_file.name}")
        file_result = validate_yaml_structure(yaml_file)
        results["files"].append(file_result)
        
        if file_result["valid"]:
            results["valid_files"] += 1
        else:
            results["invalid_files"] += 1
        
        # Coletar erros e warnings para resumo
        results["summary"]["errors"].extend([
            f"{yaml_file.name}: {error}" 
            for error in file_result["errors"]
        ])
        results["summary"]["warnings"].extend([
            f"{yaml_file.name}: {warning}" 
            for warning in file_result["warnings"]
        ])
    
    return results

def main():
    """Função principal"""
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    
    if not brain_dir.exists():
        print(f"Diretório não encontrado: {brain_dir}")
        return
    
    print("=== VALIDAÇÃO DE YAMLs NEOcortex ===")
    print(f"Diretório: {brain_dir}")
    print()
    
    results = validate_all_yamls(brain_dir)
    
    print(f"\n=== RESUMO ===")
    print(f"Total de arquivos: {results['total_files']}")
    print(f"Válidos: {results['valid_files']}")
    print(f"Inválidos: {results['invalid_files']}")
    
    if results['summary']['errors']:
        print(f"\n=== ERROS ({len(results['summary']['errors'])}) ===")
        for error in results['summary']['errors'][:10]:  # Limitar a 10 erros
            print(f"  • {error}")
        if len(results['summary']['errors']) > 10:
            print(f"  ... e mais {len(results['summary']['errors']) - 10} erros")
    
    if results['summary']['warnings']:
        print(f"\n=== WARNINGS ({len(results['summary']['warnings'])}) ===")
        for warning in results['summary']['warnings'][:10]:  # Limitar a 10 warnings
            print(f"  • {warning}")
        if len(results['summary']['warnings']) > 10:
            print(f"  ... e mais {len(results['summary']['warnings']) - 10} warnings")
    
    # Salvar relatório JSON
    report_file = brain_dir / "yaml_validation_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nRelatório salvo em: {report_file}")
    
    if results['invalid_files'] > 0:
        print("\n❌ VALIDAÇÃO FALHOU - Arquivos inválidos encontrados")
        sys.exit(1)
    else:
        print("\n✅ TODOS OS YAMLs VALIDADOS COM SUCESSO")

if __name__ == "__main__":
    main()