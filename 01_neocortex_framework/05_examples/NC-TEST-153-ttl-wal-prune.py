#!/usr/bin/env python3
"""
NC-TEST-153-ttl-wal-prune.py
Teste de integração para NC-SCR-FR-148-wal-ttl-pruner.py

Ticket: NC-DS-153-ttl-wal-pruner.yaml
Verifica execução do script de prune WAL TTL.

Uso:
  python NC-TEST-153-ttl-wal-prune.py
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Configurar encoding para Unicode no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuração
PROJECT_ROOT = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
SCRIPT_PATH = PROJECT_ROOT / "scripts/NC-SCR-FR-148-wal-ttl-pruner.py"
AUDIT_LOG_DIR = PROJECT_ROOT / "DIR-DS-002-audit-logs"


def run_test_step(description: str, test_func, *args, **kwargs) -> bool:
    """Executar um passo de teste e reportar resultado"""
    print(f"\n{description}...")
    try:
        result = test_func(*args, **kwargs)
        if result:
            print("  [OK] PASS")
        else:
            print("  [FAIL] FAIL")
        return result
    except Exception as e:
        print(f"  [ERROR] ERROR: {e}")
        return False


def test_script_exists() -> bool:
    """Teste 1: Verificar se script existe"""
    return SCRIPT_PATH.exists()


def test_script_compilation() -> bool:
    """Teste 2: Verificar compilação do script"""
    try:
        import py_compile
        py_compile.compile(str(SCRIPT_PATH), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"    Erro de compilação: {e}")
        return False


def test_script_execution() -> bool:
    """Teste 3: Executar script via subprocess"""
    try:
        # Executar script com --days 1 para teste rápido
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--days", "1"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=30
        )
        
        print(f"    Exit code: {result.returncode}")
        print(f"    Stdout: {result.stdout[:200]}...")
        if result.stderr:
            print(f"    Stderr: {result.stderr[:200]}...")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("    Timeout após 30 segundos")
        return False
    except Exception as e:
        print(f"    Exception: {e}")
        return False


def test_report_generation() -> bool:
    """Teste 4: Verificar se relatório JSON foi gerado"""
    if not AUDIT_LOG_DIR.exists():
        print(f"    Diretório não existe: {AUDIT_LOG_DIR}")
        return False
    
    # Buscar arquivos de relatório mais recentes
    report_files = list(AUDIT_LOG_DIR.glob("NC-RPT-153-wal-prune-*.json"))
    if not report_files:
        print("    Nenhum relatório encontrado")
        return False
    
    # Pegar o mais recente
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    print(f"    Relatório mais recente: {latest_report.name}")
    
    # Verificar conteúdo
    try:
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        required_fields = [
            "execution_id", "timestamp", "days_threshold",
            "entries_removed", "status"
        ]
        
        for field in required_fields:
            if field not in report_data:
                print(f"    Campo obrigatório faltando: {field}")
                return False
        
        print(f"    Entries removed: {report_data.get('entries_removed')}")
        print(f"    Days threshold: {report_data.get('days_threshold')}")
        print(f"    Status: {report_data.get('status')}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"    JSON inválido: {e}")
        return False
    except Exception as e:
        print(f"    Erro ao ler relatório: {e}")
        return False


def test_report_content() -> bool:
    """Teste 5: Verificar conteúdo do relatório"""
    report_files = list(AUDIT_LOG_DIR.glob("NC-RPT-153-wal-prune-*.json"))
    if not report_files:
        return False
    
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    
    try:
        with open(latest_report, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # Verificar tipos de dados
        checks = [
            ("execution_id", str),
            ("timestamp", str),
            ("days_threshold", int),
            ("entries_removed", int),
            ("status", str)
        ]
        
        all_checks_passed = True
        for field, expected_type in checks:
            value = report_data.get(field)
            if not isinstance(value, expected_type):
                print(f"    Campo {field} tem tipo {type(value)}, esperado {expected_type}")
                all_checks_passed = False
        
        # Verificar formato do timestamp (ISO 8601)
        timestamp = report_data.get("timestamp", "")
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            print(f"    Timestamp inválido: {timestamp}")
            all_checks_passed = False
        
        # Verificar que entries_removed é não-negativo
        entries_removed = report_data.get("entries_removed", -1)
        if entries_removed < 0:
            print(f"    entries_removed negativo: {entries_removed}")
            all_checks_passed = False
        
        return all_checks_passed
        
    except Exception as e:
        print(f"    Erro: {e}")
        return False


def test_help_option() -> bool:
    """Teste 6: Verificar opção --help"""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=10
        )
        
        return result.returncode == 0 and "usage:" in result.stdout.lower()
    except Exception as e:
        print(f"    Erro: {e}")
        return False


def test_invalid_days() -> bool:
    """Teste 7: Verificar comportamento com dias inválidos"""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--days", "0"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=10
        )
        
        # Script deve aceitar dias=0 (prune tudo)
        # Ou pode rejeitar - depende da implementação
        # Vamos apenas verificar que não crasha
        return result.returncode in [0, 1]
    except Exception as e:
        print(f"    Erro: {e}")
        return False


def main() -> int:
    """Função principal do teste"""
    print("=" * 60)
    print("NC-TEST-153: TTL WAL Prune Integration Test")
    print("=" * 60)
    
    tests = [
        ("Script existe", test_script_exists),
        ("Script compila", test_script_compilation),
        ("Script executa (--days 1)", test_script_execution),
        ("Relatório gerado", test_report_generation),
        ("Conteúdo do relatório", test_report_content),
        ("Opção --help funciona", test_help_option),
        ("Dias inválidos tratados", test_invalid_days),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if run_test_step(test_name, test_func):
            passed += 1
    
    # Resultado final
    print("\n" + "=" * 60)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    print("=" * 60)
    
    if passed == total:
        print("✅ TODOS os testes passaram!")
        return 0
    else:
        print(f"⚠️  {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    # Criar diretório de audit logs se não existir
    AUDIT_LOG_DIR.mkdir(exist_ok=True)
    
    exit_code = main()
    sys.exit(exit_code)