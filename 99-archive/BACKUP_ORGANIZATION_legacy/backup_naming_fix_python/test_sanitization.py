#!/usr/bin/env python3
"""
Teste de sanitização YAML/JSON
Verifica vulnerabilidades e implementa sanitização segura
"""

import yaml
import json
import re
from pathlib import Path

class YamlSanitizer:
    """Sanitizador seguro para YAML"""
    
    DANGEROUS_PATTERNS = [
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
    
    @classmethod
    def sanitize_yaml(cls, content: str) -> str:
        """Remove padrões perigosos do YAML"""
        sanitized = content
        
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '# REMOVED: ' + pattern, sanitized, flags=re.IGNORECASE)
        
        return sanitized
    
    @classmethod
    def safe_load_yaml(cls, content: str):
        """Carrega YAML com sanitização"""
        sanitized = cls.sanitize_yaml(content)
        return yaml.safe_load(sanitized)

class JsonSanitizer:
    """Sanitizador seguro para JSON"""
    
    @classmethod
    def sanitize_json(cls, content: str) -> str:
        """Valida e sanitiza JSON"""
        try:
            # Primeiro valida se é JSON válido
            data = json.loads(content)
            
            # Remove possíveis scripts em strings
            def sanitize_value(value):
                if isinstance(value, str):
                    # Remove possíveis scripts embutidos
                    value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
                    value = re.sub(r'data:', '', value, flags=re.IGNORECASE)
                    value = re.sub(r'<script.*?>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
                elif isinstance(value, dict):
                    return {k: sanitize_value(v) for k, v in value.items()}
                elif isinstance(value, list):
                    return [sanitize_value(item) for item in value]
                return value
            
            sanitized_data = sanitize_value(data)
            return json.dumps(sanitized_data, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON inválido: {e}")

def test_yaml_sanitization():
    """Testa sanitização YAML com exemplos perigosos"""
    print("=== TESTE DE SANITIZAÇÃO YAML ===")
    
    dangerous_yaml = """
    # YAML perigoso com tags Python
    dangerous: !!python/object/apply:os.system ["echo 'hacked'"]
    safe_data: "dados seguros"
    another_danger: !!python/name:subprocess.call
    """
    
    print("YAML original (perigoso):")
    print(dangerous_yaml)
    
    sanitized = YamlSanitizer.sanitize_yaml(dangerous_yaml)
    print("\nYAML sanitizado:")
    print(sanitized)
    
    try:
        data = YamlSanitizer.safe_load_yaml(dangerous_yaml)
        print("\nYAML carregado com segurança:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\nErro ao carregar: {e}")

def test_json_sanitization():
    """Testa sanitização JSON"""
    print("\n=== TESTE DE SANITIZAÇÃO JSON ===")
    
    dangerous_json = '''
    {
        "name": "Teste",
        "script": "javascript:alert('xss')",
        "data": "data:text/html,<script>alert(1)</script>",
        "html": "<script>malicious</script>Seguro",
        "safe": "dados normais"
    }
    '''
    
    print("JSON original:")
    print(dangerous_json)
    
    try:
        sanitized = JsonSanitizer.sanitize_json(dangerous_json)
        print("\nJSON sanitizado:")
        print(sanitized)
        
        data = json.loads(sanitized)
        print("\nDados parseados:")
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"\nErro: {e}")

def test_real_files():
    """Testa sanitização em arquivos reais"""
    print("\n=== TESTE EM ARQUIVOS REAIS ===")
    
    brain_dir = Path("C:/Users/Lucas Valério/.gemini/antigravity/brain")
    
    # Testar alguns arquivos YAML
    yaml_files = list(brain_dir.glob("*.yaml"))[:3]
    
    for yaml_file in yaml_files:
        print(f"\nTestando: {yaml_file.name}")
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Verificar padrões perigosos
            dangerous_found = []
            for pattern in YamlSanitizer.DANGEROUS_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    dangerous_found.append(pattern)
            
            if dangerous_found:
                print(f"  [WARNING] Padrões perigosos encontrados: {dangerous_found}")
                sanitized = YamlSanitizer.sanitize_yaml(content)
                print(f"  [OK] Sanitização aplicada")
            else:
                print(f"  [OK] Nenhum padrão perigoso encontrado")
                
            # Tentar carregar com safe_load
            try:
                data = yaml.safe_load(content)
                print(f"  [OK] YAML válido (safe_load)")
            except yaml.YAMLError as e:
                print(f"  [ERROR] Erro no YAML: {e}")
                
        except Exception as e:
            print(f"  [ERROR] Erro ao processar: {e}")

def main():
    """Função principal"""
    print("TESTE DE SANITIZAÇÃO YAML/JSON - NeoCortex Security")
    print("=" * 50)
    
    test_yaml_sanitization()
    test_json_sanitization()
    test_real_files()
    
    print("\n" + "=" * 50)
    print("[OK] Testes de sanitização concluídos")

if __name__ == "__main__":
    main()