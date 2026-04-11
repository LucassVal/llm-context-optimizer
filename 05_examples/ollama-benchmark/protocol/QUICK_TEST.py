#!/usr/bin/env python3
"""
Teste rapido das funcionalidades principais do benchmark_master_suite.py
Execute com: python QUICK_TEST.py
"""

import subprocess
import sys
import os
import json


def test_syntax():
    """Testar sintaxe do arquivo principal."""
    print(" Testando sintaxe...")
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "benchmark_master_suite.py"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(" Sintaxe OK")
        return True
    else:
        print(f" Erro de sintaxe: {result.stderr}")
        return False


def test_imports():
    """Testar importacao de modulos."""
    print(" Testando imports...")
    try:
        # Testar imports basicos
        test_code = """
import sys
import os
import requests
import json
import time
import random
import hashlib
import re
print(" Imports OK")
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code], capture_output=True, text=True
        )
        if "" in result.stdout:
            print(" Todos os imports funcionam")
            return True
        else:
            print(f" Erro nos imports: {result.stderr}")
            return False
    except Exception as e:
        print(f" Erro: {e}")
        return False


def test_health_check_dry_run():
    """Testar funcao de health check (dry run)."""
    print(" Testando health check (dry run)...")
    try:
        test_code = """
import sys
import os
sys.path.insert(0, '.')
# Mock da funcao requests para teste
import unittest.mock as mock

# Criar mock
with mock.patch('requests.get') as mock_get:
    with mock.patch('requests.post') as mock_post:
        # Configurar mocks
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "tinyllama:latest"}]}
        mock_get.return_value = mock_response
        
        mock_inf = mock.Mock()
        mock_inf.status_code = 200
        mock_inf.json.return_value = {"response": "OK"}
        mock_post.return_value = mock_inf
        
        # Importar e testar
        from benchmark_master_suite import check_ollama_health
        success, msg, models = check_ollama_health("tinyllama:latest")
        if success:
            print(" Health check mock OK")
        else:
            print(f" Health check falhou: {msg}")
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code], capture_output=True, text=True
        )
        if "" in result.stdout:
            print(" Health check funcional (mock)")
            return True
        else:
            print(f" Health check erro: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f" Erro no health check: {e}")
        return False


def test_regex_parser():
    """Testar parser regex."""
    print(" Testando parser regex...")
    test_code = """
import sys
sys.path.insert(0, '.')
from benchmark_master_suite import extract_with_regex

# Testes
tests = [
    ("This is OK for testing", "OK", True),
    ("RED-TIER security only", "RED-TIER", True),
    ("red-tier is lowercase", "RED-TIER", True),
    ("No match here", "OK", False),
    ("PrismaClient instance", "PrismaClient", True),
]

all_pass = True
for text, pattern, expected in tests:
    result = extract_with_regex(text, pattern)
    if result == expected:
        print(f"   '{pattern}' em '{text[:20]}...': {result}")
    else:
        print(f"   '{pattern}' em '{text[:20]}...': esperado {expected}, obtido {result}")
        all_pass = False

if all_pass:
    print(" Todos os testes regex passaram")
else:
    print(" Alguns testes regex falharam")
"""
    result = subprocess.run(
        [sys.executable, "-c", test_code], capture_output=True, text=True
    )
    print(result.stdout)
    return " Todos os testes regex passaram" in result.stdout


def test_menu_structure():
    """Verificar estrutura do menu."""
    print(" Verificando estrutura do menu...")
    with open("benchmark_master_suite.py", "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        ("Funcao main definida", "def main():" in content),
        ("Menu principal com opcoes", "Enter choice [0-8, H, K]:" in content),
        ("Health check no menu", "[H] Health Check LLM" in content),
        ("Killswitch no menu", "[K] Configurar Killswitch" in content),
        ("Teste 3 implementado", "def run_drift_gauntlet" in content),
        ("Parser regex definido", "def extract_with_regex" in content),
    ]

    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   {check_name}")
        else:
            print(f"   {check_name}")
            all_ok = False

    return all_ok


def test_file_structure():
    """Verificar estrutura de arquivos."""
    print(" Verificando estrutura de arquivos...")
    checks = []

    # Verificar arquivos existentes
    if os.path.exists("benchmark_master_suite.py"):
        checks.append(("Arquivo principal", True))
    else:
        checks.append(("Arquivo principal", False))

    if os.path.exists("protocol"):
        checks.append(("Pasta protocol", True))
        if os.path.exists("protocol/STATUS.md"):
            checks.append(("STATUS.md", True))
        else:
            checks.append(("STATUS.md", False))

        if os.path.exists("protocol/CONTINUE.md"):
            checks.append(("CONTINUE.md", True))
        else:
            checks.append(("CONTINUE.md", False))
    else:
        checks.append(("Pasta protocol", False))
        checks.append(("STATUS.md", False))
        checks.append(("CONTINUE.md", False))

    all_ok = True
    for check_name, check_result in checks:
        if check_result:
            print(f"   {check_name}")
        else:
            print(f"   {check_name}")
            all_ok = False

    return all_ok


def main():
    print("=" * 60)
    print("TESTE RAPIDO DO BENCHMARK MASTER SUITE")
    print("=" * 60)

    results = []

    # Executar testes
    results.append(("Sintaxe", test_syntax()))
    results.append(("Imports", test_imports()))
    results.append(("Health Check", test_health_check_dry_run()))
    results.append(("Parser Regex", test_regex_parser()))
    results.append(("Menu Structure", test_menu_structure()))
    results.append(("File Structure", test_file_structure()))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = " PASSOU" if result else " FALHOU"
        print(f"{status} {test_name}")

    print(f"\n {passed}/{total} testes passaram ({passed / total * 100:.0f}%)")

    if passed == total:
        print("\n TODOS OS TESTES PASSARAM! O benchmark esta funcional.")
        print("\nProximos passos:")
        print("1. Execute: python benchmark_master_suite.py")
        print("2. Teste as opcoes H (Health Check) e K (Killswitch)")
        print("3. Execute o Teste 3 (DRIFT 50T) para validar")
    else:
        print(f"\n  {total - passed} teste(s) falharam.")
        print("Verifique os erros acima antes de continuar.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
