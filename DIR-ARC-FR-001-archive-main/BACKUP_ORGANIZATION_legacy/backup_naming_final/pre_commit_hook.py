#!/usr/bin/env python3
"""
Hook de pre-commit para sanitização proativa de YAML/JSON
Executa validação e sanitização antes de commits
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from typing import List, Tuple

class SecurityValidator:
    """Validador de segurança para YAML/JSON"""
    
    YAML_DANGEROUS_PATTERNS = [
        r'!!python/',
        r'!!python/object',
        r'__import__',
        r'eval\(',
        r'exec\(',
        r'subprocess\.',
        r'os\.system',
        r'pickle\.',
        r'marshal\.',
        r'compile\(',
        r'__.*__'
    ]
    
    JSON_DANGEROUS_PATTERNS = [
        r'javascript:',
        r'data:text/html',
        r'<script.*?>.*?</script>',
        r'onload=',
        r'onerror=',
        r'onclick='
    ]
    
    @classmethod
    def validate_yaml_file(cls, file_path: Path) -> Tuple[bool, List[str]]:
        """Valida arquivo YAML para segurança"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar padrões perigosos
            for pattern in cls.YAML_DANGEROUS_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"Padrão perigoso encontrado: {pattern}")
            
            # Tentar carregar com safe_load
            try:
                data = yaml.safe_load(content)
                if data is None:
                    errors.append("YAML vazio ou inválido")
            except yaml.YAMLError as e:
                errors.append(f"Erro de parsing YAML: {e}")
            
            # Validação adicional para tickets
            if file_path.name.startswith("NC-DS-") and file_path.suffix == '.yaml':
                if data and isinstance(data, dict):
                    # Campos obrigatórios para tickets
                    required_fields = ["ticket_id", "status", "title", "description", "priority"]
                    for field in required_fields:
                        if field not in data:
                            errors.append(f"Campo obrigatório faltante: {field}")
                    
                    # Valores válidos
                    if "status" in data:
                        valid_statuses = ["OPEN", "IN_PROGRESS", "COMPLETED", "CANCELLED", "BLOCKED"]
                        if data["status"].upper() not in valid_statuses:
                            errors.append(f"Status inválido: {data['status']}. Válidos: {valid_statuses}")
                    
                    if "priority" in data:
                        valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
                        if data["priority"].upper() not in valid_priorities:
                            errors.append(f"Prioridade inválida: {data['priority']}. Válidas: {valid_priorities}")
        
        except Exception as e:
            errors.append(f"Erro ao processar arquivo: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_json_file(cls, file_path: Path) -> Tuple[bool, List[str]]:
        """Valida arquivo JSON para segurança"""
        errors = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar padrões perigosos em strings
            for pattern in cls.JSON_DANGEROUS_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    errors.append(f"Padrão perigoso encontrado: {pattern}")
            
            # Validar JSON
            try:
                data = json.loads(content)
                
                # Validação adicional para opencode.json
                if file_path.name == "opencode.json":
                    if not isinstance(data, dict):
                        errors.append("opencode.json deve ser um objeto JSON")
                    elif "config_id" not in data:
                        errors.append("opencode.json deve ter campo config_id com padrão NC-")
                    elif not data.get("config_id", "").startswith("NC-"):
                        errors.append(f"config_id deve seguir padrão NC-: {data.get('config_id')}")
            
            except json.JSONDecodeError as e:
                errors.append(f"JSON inválido: {e}")
        
        except Exception as e:
            errors.append(f"Erro ao processar arquivo: {e}")
        
        return len(errors) == 0, errors
    
    @classmethod
    def sanitize_yaml_content(cls, content: str) -> str:
        """Sanitiza conteúdo YAML removendo padrões perigosos"""
        sanitized = content
        
        for pattern in cls.YAML_DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '# SECURITY: Removed dangerous pattern', 
                             sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def sanitize_json_content(cls, content: str) -> str:
        """Sanitiza conteúdo JSON removendo padrões perigosos"""
        try:
            data = json.loads(content)
            
            def sanitize_value(value):
                if isinstance(value, str):
                    # Remover padrões perigosos
                    for pattern in cls.JSON_DANGEROUS_PATTERNS:
                        value = re.sub(pattern, '', value, flags=re.IGNORECASE)
                elif isinstance(value, dict):
                    return {k: sanitize_value(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [sanitize_value(item) for item in value]
                return value
            
            sanitized_data = sanitize_value(data)
            return json.dumps(sanitized_data, indent=2, ensure_ascii=False)
        
        except json.JSONDecodeError:
            # Se não for JSON válido, retornar original
            return content

class PreCommitHook:
    """Implementação do hook de pre-commit"""
    
    def __init__(self):
        self.validator = SecurityValidator()
        self.failed_files = []
    
    def check_staged_files(self) -> bool:
        """Verifica arquivos staged para commit"""
        print("=== PRE-COMMIT HOOK: Validação de Segurança YAML/JSON ===")
        print()
        
        # Obter arquivos staged (simulação - em produção usar git diff)
        staged_files = self._get_staged_files()
        
        if not staged_files:
            print("Nenhum arquivo para validar.")
            return True
        
        print(f"Validando {len(staged_files)} arquivo(s):")
        
        all_valid = True
        
        for file_path in staged_files:
            print(f"\n  {file_path.name}:")
            
            if file_path.suffix in ['.yaml', '.yml']:
                is_valid, errors = self.validator.validate_yaml_file(file_path)
                
                if not is_valid:
                    all_valid = False
                    self.failed_files.append((file_path, errors))
                    print(f"    [FAIL] {len(errors)} erro(s):")
                    for error in errors:
                        print(f"      - {error}")
                else:
                    print(f"    [PASS] YAML válido e seguro")
            
            elif file_path.suffix == '.json':
                is_valid, errors = self.validator.validate_json_file(file_path)
                
                if not is_valid:
                    all_valid = False
                    self.failed_files.append((file_path, errors))
                    print(f"    [FAIL] {len(errors)} erro(s):")
                    for error in errors:
                        print(f"      - {error}")
                else:
                    print(f"    [PASS] JSON válido e seguro")
            
            else:
                print(f"    [SKIP] Tipo de arquivo não suportado")
        
        return all_valid
    
    def _get_staged_files(self) -> List[Path]:
        """Obtém lista de arquivos staged (simplificado)"""
        # Em produção, isso usaria: git diff --cached --name-only --diff-filter=ACM
        # Por enquanto, verificamos todos os YAML/JSON no diretório
        current_dir = Path.cwd()
        
        staged_files = []
        
        # YAML files
        for ext in ['.yaml', '.yml']:
            staged_files.extend(current_dir.glob(f"**/*{ext}"))
        
        # JSON files
        staged_files.extend(current_dir.glob("**/*.json"))
        
        # Filtrar apenas arquivos relevantes
        filtered_files = []
        for file_path in staged_files:
            # Ignorar arquivos em diretórios especiais
            if any(part.startswith('.') for part in file_path.parts):
                continue
            
            # Ignorar arquivos muito grandes
            if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
                continue
            
            filtered_files.append(file_path)
        
        return filtered_files[:20]  # Limitar para teste
    
    def auto_fix_problems(self):
        """Tenta corrigir problemas automaticamente"""
        if not self.failed_files:
            print("\nNenhum problema para corrigir.")
            return
        
        print(f"\n=== TENTATIVA DE CORREÇÃO AUTOMÁTICA ===")
        
        fixed_count = 0
        
        for file_path, errors in self.failed_files:
            print(f"\n  {file_path.name}:")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Aplicar sanitização baseada no tipo
                if file_path.suffix in ['.yaml', '.yml']:
                    sanitized = self.validator.sanitize_yaml_content(content)
                elif file_path.suffix == '.json':
                    sanitized = self.validator.sanitize_json_content(content)
                else:
                    continue
                
                # Salvar sanitizado
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(sanitized)
                
                print(f"    [FIXED] Arquivo sanitizado")
                fixed_count += 1
                
            except Exception as e:
                print(f"    [ERROR] Falha ao corrigir: {e}")
        
        print(f"\nCorrigidos {fixed_count} de {len(self.failed_files)} arquivo(s).")

def main():
    """Função principal do hook"""
    hook = PreCommitHook()
    
    # Verificar arquivos
    is_valid = hook.check_staged_files()
    
    if is_valid:
        print("\n" + "=" * 60)
        print("[SUCCESS] Todos os arquivos validados com sucesso!")
        print("Commit pode prosseguir.")
        return 0
    else:
        print("\n" + "=" * 60)
        print("[FAILURE] Arquivos com problemas de segurança encontrados!")
        print(f"Total: {len(hook.failed_files)} arquivo(s) com problemas")
        
        # Oferecer correção automática
        response = input("\nDeseja tentar correção automática? (s/n): ").strip().lower()
        
        if response == 's':
            hook.auto_fix_problems()
            print("\nExecute o hook novamente para verificar as correções.")
            return 1
        else:
            print("\nCorrija os problemas manualmente antes de commitar.")
            print("Arquivos problemáticos:")
            for file_path, errors in hook.failed_files:
                print(f"  - {file_path}: {len(errors)} erro(s)")
            return 1

if __name__ == "__main__":
    sys.exit(main())