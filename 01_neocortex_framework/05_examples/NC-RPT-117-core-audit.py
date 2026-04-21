#!/usr/bin/env python3
"""
NC-RPT-117-core-audit.py
Audit core/ raiz — classificar 31 arquivos sem prefixo NC

Ticket: NC-DS-117-audit-core-noprefix.yaml
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any

# Configurar encoding para Unicode no Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ── Configuração ────────────────────────────────────────────────────────────
FW_ROOT = Path(r"C:\Users\Lucas Valério\Desktop\TURBOQUANT_V42\01_neocortex_framework")
CORE_DIR = FW_ROOT / "neocortex" / "core"
SERVICES_DIR = FW_ROOT / "neocortex" / "core" / "services"
OUTPUT_FILE = FW_ROOT / "05_examples" / "NC-RPT-117-core-audit-report.json"


def count_importers(file_path: Path) -> int:
    """Contar quantos arquivos importam este módulo em todo o projeto."""
    if not file_path.exists():
        return 0
    
    file_name = file_path.stem
    # Para arquivos com hífen no nome (NC-*), usar o nome base
    if "-" in file_name:
        # Extrair parte após último hífen
        base_name = file_name.split("-")[-1]
    else:
        base_name = file_name
    
    # Padrões de importação a procurar
    patterns = [
        f"import.*{file_name}",           # import module
        f"from.*{file_name}.*import",     # from module import
        f"import.*{base_name}",           # import base_name
        f"from.*{base_name}.*import",     # from base_name import
    ]
    
    count = 0
    try:
        # Procurar em todos os arquivos Python
        for py_file in FW_ROOT.rglob("*.py"):
            if py_file == file_path:
                continue  # pular o próprio arquivo
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        count += 1
                        break  # contar apenas uma vez por arquivo
            except:
                continue
    except:
        pass
    
    return count


def find_equivalent_service(file_name: str) -> str:
    """Verificar se existe um NC-SVC-FR-* equivalente em core/services/."""
    # Extrair nome base (sem .py e sem prefixo NC-)
    base_name = file_name.replace(".py", "")
    if base_name.startswith("NC-"):
        # Remover prefixo NC- e qualquer coisa até o último hífen
        parts = base_name.split("-")
        if len(parts) > 2:
            base_name = parts[-1]
    
    # Procurar por arquivos em services/ que contenham o base_name
    try:
        for svc_file in SERVICES_DIR.glob("*.py"):
            svc_name = svc_file.stem
            if base_name.lower() in svc_name.lower():
                return svc_file.name
    except:
        pass
    
    return ""


def classify_file(file_name: str, importers_count: int, equivalent_svc: str) -> Dict[str, Any]:
    """Classificar arquivo conforme critérios."""
    classification = "UNKNOWN"
    action_suggested = "REVIEW"
    
    if file_name.startswith("NC-"):
        classification = "KEEP_NC"
        action_suggested = "KEEP"
    elif importers_count == 0:
        classification = "ARCHIVE"
        action_suggested = "ARCHIVE"
    elif equivalent_svc:
        classification = "DUPLICATE"
        action_suggested = "CONSIDER_MERGING"
    else:
        classification = "KEEP_NON_NC"
        action_suggested = "KEEP"
    
    return {
        "classification": classification,
        "action_suggested": action_suggested
    }


def main() -> int:
    """Função principal."""
    print("=" * 60)
    print("NC-RPT-117: Core Directory Audit")
    print("=" * 60)
    
    # Coletar arquivos
    core_files = list(CORE_DIR.glob("*.py"))
    print(f"Encontrados {len(core_files)} arquivos Python em {CORE_DIR}")
    
    # Processar cada arquivo
    audit_results = []
    
    for file_path in sorted(core_files):
        file_name = file_path.name
        print(f"\nAnalisando: {file_name}")
        
        # a) Contar importadores
        importers_count = count_importers(file_path)
        print(f"  Importadores: {importers_count}")
        
        # b) Verificar equivalente em services/
        equivalent_svc = find_equivalent_service(file_name)
        if equivalent_svc:
            print(f"  Equivalente em services/: {equivalent_svc}")
        
        # c) Classificar
        classification_info = classify_file(file_name, importers_count, equivalent_svc)
        
        audit_results.append({
            "name": file_name,
            "importers_count": importers_count,
            "classification": classification_info["classification"],
            "equivalent_svc": equivalent_svc,
            "action_suggested": classification_info["action_suggested"]
        })
    
    # Gerar estatísticas
    stats = {
        "total_files": len(audit_results),
        "by_classification": {},
        "by_action": {}
    }
    
    for result in audit_results:
        cls = result["classification"]
        action = result["action_suggested"]
        
        stats["by_classification"][cls] = stats["by_classification"].get(cls, 0) + 1
        stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
    
    # Salvar relatório
    report = {
        "metadata": {
            "ticket_id": "NC-DS-117",
            "audit_date": "2026-04-20",
            "core_directory": str(CORE_DIR),
            "total_files_analyzed": len(audit_results)
        },
        "statistics": stats,
        "files": audit_results
    }
    
    # Garantir que o diretório de saída existe
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("RESUMO DA AUDITORIA:")
    print("=" * 60)
    
    print(f"\nTotal de arquivos: {stats['total_files']}")
    
    print("\nClassificação:")
    for cls, count in sorted(stats["by_classification"].items()):
        print(f"  {cls}: {count}")
    
    print("\nAções sugeridas:")
    for action, count in sorted(stats["by_action"].items()):
        print(f"  {action}: {count}")
    
    print(f"\nRelatório salvo em: {OUTPUT_FILE}")
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Auditoria interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro durante auditoria: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)