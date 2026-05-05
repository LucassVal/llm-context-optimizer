"""---
Extrai nome do módulo do caminho do arquivo
---
"""


import json
from pathlib import Path

# Configurações
PROJECT_ROOT = Path("C:/Users/Lucas Valério/Desktop/TURBOQUANT_V42/01_neocortex_framework")
CORE_DIR = PROJECT_ROOT / "neocortex" / "core"
SERVICES_DIR = CORE_DIR / "services"

# Lista de arquivos sem prefixo NC (do relatório anterior)
files_without_nc = [
    "__init__.py",
    "agent_policy_enforcer.py",
    "agent_service.py",
    "akl_service.py",
    "benchmark_service.py",
    "cascade_consolidator.py",
    "checkpoint_service.py",
    "circuit_breaker.py",
    "config_service.py",
    "consolidation_service.py",
    "cortex_service.py",
    "export_service.py",
    "file_utils.py",
    "init_service.py",
    "kg_service.py",
    "ledger_service.py",
    "lexico_service.py",
    "lobe_service.py",
    "logging_config.py",
    "manifest_service.py",
    "peers_service.py",
    "profile_manager.py",
    "profile_service.py",
    "pulse_scheduler.py",
    "regression_service.py",
    "security_service.py"
]

# Arquivos com prefixo NC no core/
files_with_nc = [
    "NC-CFG-FR-001-logging-config.py",
    "NC-CORE-FR-014-lock-guard.py",
    "NC-CORE-FR-016-kg-service.py",
    "NC-CORE-FR-017-policy-loader.py",
    "NC-CORE-FR-022-save-point-service.py"
]

def get_module_name(file_path):
    """Extrai nome do módulo do caminho do arquivo"""
    rel_path = file_path.relative_to(PROJECT_ROOT)
    module_name = str(rel_path).replace('\\', '.').replace('/', '.').replace('.py', '')
    return module_name

def find_importers(file_name):
    """Conta quantos arquivos importam este módulo"""
    module_base = file_name.replace('.py', '')
    import_patterns = [
        f"import {module_base}",
        f"from {module_base} import",
        f"from .{module_base} import",
        f"from ..{module_base} import"
    ]

    importers_count = 0
    importers_files = []

    # Busca em todos os arquivos Python do projeto
    for py_file in PROJECT_ROOT.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            for pattern in import_patterns:
                if pattern in content:
                    importers_count += 1
                    importers_files.append(str(py_file.relative_to(PROJECT_ROOT)))
                    break  # Contar apenas uma vez por arquivo
        except (UnicodeDecodeError, PermissionError, OSError):
            continue

    return importers_count, importers_files[:10]  # Limitar a 10 arquivos para relatório

def find_equivalent_service(file_name):
    """Verifica se existe equivalente em core/services/"""
    base_name = file_name.replace('.py', '')

    # Padrões de correspondência
    patterns = [
        f"NC-SVC-FR-*-{base_name}.py",
        f"NC-SVC-FR-*-{base_name.replace('_', '-')}.py",
        f"NC-SVC-FR-*-{base_name.replace('_service', '')}.py",
        f"NC-SVC-FR-*-{base_name.replace('service', '')}.py"
    ]

    for pattern in patterns:
        for service_file in SERVICES_DIR.glob(pattern):
            return str(service_file.name)

    return None

def classify_file(file_name, importers_count, equivalent_svc):
    """Classifica o arquivo"""
    if equivalent_svc:
        return "DUPLICATE"
    elif importers_count == 0:
        return "ARCHIVE"
    else:
        return "KEEP_NC"

def main():
    results = []

    print("Analisando arquivos sem prefixo NC...")
    for file_name in files_without_nc:
        file_path = CORE_DIR / file_name

        if not file_path.exists():
            print(f"Arquivo não encontrado: {file_name}")
            continue

        print(f"  Analisando: {file_name}")

        # Contar importadores
        importers_count, importers_files = find_importers(file_name)

        # Verificar equivalente em services/
        equivalent_svc = find_equivalent_service(file_name)

        # Classificar
        classification = classify_file(file_name, importers_count, equivalent_svc)

        # Sugestão de ação
        if classification == "DUPLICATE":
            action_suggested = f"Remover e usar {equivalent_svc}"
        elif classification == "ARCHIVE":
            action_suggested = "Mover para arquivo morto"
        else:  # KEEP_NC
            action_suggested = "Renomear com prefixo NC-*"

        results.append({
            "name": file_name,
            "importers_count": importers_count,
            "importers_sample": importers_files,
            "classification": classification,
            "equivalent_svc": equivalent_svc,
            "action_suggested": action_suggested
        })

    # Gerar relatório JSON
    output_file = Path("05_examples/NC-RPT-117-core-audit-report.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "ticket_id": "NC-DS-117",
        "audit_date": "2026-04-20",
        "total_files_analyzed": len(results),
        "files": results,
        "summary": {
            "KEEP_NC": len([r for r in results if r["classification"] == "KEEP_NC"]),
            "ARCHIVE": len([r for r in results if r["classification"] == "ARCHIVE"]),
            "DUPLICATE": len([r for r in results if r["classification"] == "DUPLICATE"])
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nRelatório gerado: {output_file}")
    print(f"Resumo: KEEP_NC={report['summary']['KEEP_NC']}, ARCHIVE={report['summary']['ARCHIVE']}, DUPLICATE={report['summary']['DUPLICATE']}")

if __name__ == "__main__":
    main()
