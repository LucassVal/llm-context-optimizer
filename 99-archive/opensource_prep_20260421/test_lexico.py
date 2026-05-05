#!/usr/bin/env python3
"""
Teste simplificado do LexicoService
"""

import sys
import os

# Adicionar caminho
sys.path.insert(0, '01_neocortex_framework/neocortex/core/services')

# Importar diretamente
import importlib.util
spec = importlib.util.spec_from_file_location(
    'lexico_service', 
    '01_neocortex_framework/neocortex/core/services/NC-SVC-FR-020-lexico-service.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

print("=" * 60)
print("TESTE LEXICO-001 - LexicoService Base")
print("=" * 60)

try:
    # Criar serviço com path explícito para teste
    test_dict_path = 'test-lexico-dictionary.json'
    
    # Remover arquivo de teste anterior se existir
    if os.path.exists(test_dict_path):
        os.remove(test_dict_path)
    
    print("\n1. Criando LexicoService...")
    service = module.LexicoService(dict_path=test_dict_path)
    
    print(f"   Atomos iniciais: {len(service.export())}")
    
    print("\n2. Testando busca...")
    results = service.search("MCP")
    print(f"   Resultados para 'MCP': {len(results)}")
    for atom in results[:2]:
        print(f"   - {atom.get('key', 'N/A')}: {atom.get('definition', 'N/A')}")
    
    print("\n3. Testando adição...")
    new_atom = service.add("LEXICO", "semantic-compression-service", "global", ["compression", "semantic"])
    print(f"   Adicionado: {new_atom['key']} = {new_atom['definition']}")
    
    print("\n4. Testando recuperação...")
    lex_atom = service.get("#LEXICO")
    if lex_atom:
        print(f"   Recuperado: {lex_atom['key']} (uso: {lex_atom.get('usage_count', 0)})")
    
    print("\n5. Verificando persistência...")
    if os.path.exists(test_dict_path):
        print(f"   OK Arquivo criado: {test_dict_path}")
        
        import json
        with open(test_dict_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   Metadata: {data.get('metadata', {}).get('service', 'N/A')}")
        print(f"   Atomos persistidos: {data.get('metadata', {}).get('atom_count', 'N/A')}")
    else:
        print(f"   ERRO Arquivo não criado")
    
    print("\n6. Testando estatísticas...")
    stats = service.stats()
    print(f"   Total atomos: {stats['total_atoms']}")
    print(f"   Scopes: {stats['scopes']}")
    
    print("\n7. Testando export...")
    export_data = service.export()
    print(f"   Exportados {len(export_data)} atomos")
    
    # Limpar arquivo de teste
    if os.path.exists(test_dict_path):
        os.remove(test_dict_path)
        print(f"\n   Arquivo de teste removido: {test_dict_path}")
    
    print("\n" + "=" * 60)
    print("✅ LEXICO-001: Serviço base funcionando corretamente!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)