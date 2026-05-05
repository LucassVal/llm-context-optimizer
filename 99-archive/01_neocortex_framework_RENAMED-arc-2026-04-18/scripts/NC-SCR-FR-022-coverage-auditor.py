#!/usr/bin/env python3
# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

"""---
domain: "orchestration"
layer: "infra"
type: "SCR"
tags: ["auditor", "coverage", "kgs", "nc-ds-050", "orphan"]
hash: "auto-generated"
---"""

"""
NC-SCR-FR-022-coverage-auditor.py
Audita a cobertura do mapa simblico sobre a materialidade dos arquivos.
Identifica Desertores (no indexados) e Inimigos (erros de leitura).
Autor: T0 (NeoCortex)
Data: 2026-04-14
"""

import json
import os
import sys
from pathlib import Path

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "DIR-DOC-FR-001-docs-main"
SYMBOLIC_MAP_PATH = DOCS_DIR / "symbolic_map.json"
COVERAGE_REPORT_JSON = DOCS_DIR / "coverage_report.json"
COVERAGE_REPORT_MD = DOCS_DIR / "coverage_report.md"

# Diretrios a serem vasculhados
SCAN_DIRS = [
    PROJECT_ROOT / "neocortex",
    PROJECT_ROOT / "DIR-DOC-FR-001-docs-main",
    PROJECT_ROOT / "DIR-PRF-FR-001-profiles-main",
    PROJECT_ROOT / "white_label",
    PROJECT_ROOT / "scripts",
    PROJECT_ROOT / "lobes",
    PROJECT_ROOT.parent / "02_memory_lobes" # Fallback if lobes is outside
]

# Extenses de arquivo a considerar
SCAN_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".mdc"}

def load_symbolic_terms() -> set[str]:
    """Carrega os termos do mapa simblico."""
    with open(SYMBOLIC_MAP_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data["encode"].keys())

def scan_files() -> list[Path]:
    """Retorna a lista de todos os arquivos a serem analisados."""
    files = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for root, _, filenames in os.walk(scan_dir):
            # Ignorar diretrios irrelevantes
            if any(part in ["__pycache__", ".git", ".venv", "node_modules"] for part in Path(root).parts):
                continue
            for filename in filenames:
                filepath = Path(root) / filename
                if filepath.suffix in SCAN_EXTENSIONS:
                    files.append(filepath)
    return files

def classify_file(filepath: Path, terms: set[str]) -> dict:
    """Classifica um arquivo como Recrutado, Desertor ou Inimigo."""
    try:
        rel_path = str(filepath.relative_to(PROJECT_ROOT))
    except ValueError:
        # If the file is outside PROJECT_ROOT (like 02_memory_lobes)
        rel_path = str(filepath.absolute())

    result = {
        "path": rel_path,
        "status": "unknown",
        "matched_terms": []
    }

    # Verificar nome do arquivo
    filename_matches = [term for term in terms if term in filepath.name]

    # Tentar ler contedo
    try:
        content = filepath.read_text(encoding='utf-8', errors='strict')
    except UnicodeDecodeError as e:
        result["status"] = "INIMIGO (Erro de Encoding UTF-8)"
        result["error"] = str(e)
        return result
    except Exception as e:
        result["status"] = "INIMIGO (Erro de Leitura)"
        result["error"] = str(e)
        return result

    # Verificar contedo
    content_matches = [term for term in terms if term in content]

    all_matches = list(set(filename_matches + content_matches))
    result["matched_terms"] = all_matches

    if all_matches:
        result["status"] = "RECRUTADO (Indexado)"
    else:
        result["status"] = "DESERTOR (No Indexado)"

    return result

def generate_report(results: list[dict]):
    """Gera relatrios JSON e Markdown."""
    recrutados = [r for r in results if "RECRUTADO" in r["status"]]
    desertores = [r for r in results if "DESERTOR" in r["status"]]
    inimigos = [r for r in results if "INIMIGO" in r["status"]]

    report = {
        "summary": {
            "total_files": len(results),
            "recrutados": len(recrutados),
            "desertores": len(desertores),
            "inimigos": len(inimigos),
            "coverage_percent": (len(recrutados) / len(results) * 100) if results else 0
        },
        "desertores": [r["path"] for r in desertores],
        "inimigos": [{"path": r["path"], "error": r.get("error")} for r in inimigos],
        "details": results
    }

    with open(COVERAGE_REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_content = f"""# Relatrio de Cobertura da KGS

**Data:** 2026-04-14
**Total de Arquivos Vlidos Analisados:** {report['summary']['total_files']}
**Recrutados (Indexados - Presentes na Teia):** {report['summary']['recrutados']} ({report['summary']['coverage_percent']:.1f}%)
**Desertores (Orfos Mudos - Ponto Cego):** {report['summary']['desertores']}
**Inimigos (Corrompidos/Erros):** {report['summary']['inimigos']}

##  Desertores (Matria Escura)
Estes arquivos no citam nem so citados por NENHUMA tag ou SSOT mestre.

"""
    for d in desertores[:20]:
        md_content += f"- `{d['path']}`\n"
    if len(desertores) > 20:
        md_content += f"\n... e mais {len(desertores) - 20} arquivos escondidos.\n"

    md_content += """
##  Inimigos (Erros)
Arquivos que o parser python reprovou de ler (encoding ou corrupo fatal).

"""
    for i in inimigos:
        md_content += f"- `{i['path']}`: {i.get('error', 'Erro desconhecido')}\n"

    md_content += """
---
*Relatrio gerado por NC-SCR-FR-022-coverage-auditor.py*
"""
    with open(COVERAGE_REPORT_MD, 'w', encoding='utf-8') as f:
        f.write(md_content)

def main():
    print(" NC-SCR-FR-022: Iniciando Central de Auditoria KGS...")
    terms = load_symbolic_terms()
    print(f"   [+] {len(terms)} SymTerms engatilhados.")

    files = scan_files()
    print(f"   [+] {len(files)} Arquivos vivos levantados.")

    results = []
    for filepath in files:
        results.append(classify_file(filepath, terms))

    generate_report(results)

    recrutados = sum(1 for r in results if "RECRUTADO" in r["status"])
    desertores = sum(1 for r in results if "DESERTOR" in r["status"])
    inimigos = sum(1 for r in results if "INIMIGO" in r["status"])

    print("\n RESUMO TTICO KGS:")
    print(f"    Recrutados na Teia: {recrutados}")
    print(f"    Desertores/Blind:   {desertores}")
    print(f"    Inimigos Syntax:    {inimigos}")
    print(f"    Domnio Teia KGS:   {recrutados/len(results)*100:.1f}%")

if __name__ == "__main__":
    main()
