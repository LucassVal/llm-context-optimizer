# @UBL @UBL @SCR-FR | LEXICO: #SCRIPTS
#!/usr/bin/env python3


import io
import sys

# Fix encoding for Windows (UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.701690'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-SCR-FR-022
related_ssot:
  - NC-SCR-FR-022-coverage-auditor
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
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

# Add neocortex to path for symbolic compressor import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "neocortex"))

# Try to import SymbolicCompressor
try:
    from neocortex.core.file_utils import get_lobes_path
    from neocortex.infra.symbolic_compressor import SymbolicCompressor

    SYMBOLIC_COMPRESSOR_AVAILABLE = True
    SYMBOLIC_COMPRESSOR_ERROR = None
except ImportError as e:
    SymbolicCompressor = None
    SYMBOLIC_COMPRESSOR_AVAILABLE = False
    SYMBOLIC_COMPRESSOR_ERROR = str(e)

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
    get_lobes_path(),
]

# Extenses de arquivo a considerar
SCAN_EXTENSIONS = {".py", ".md", ".yaml", ".yml", ".json", ".mdc"}


def load_symbolic_terms() -> set[str]:
    """Carrega os termos do mapa simblico."""
    with open(SYMBOLIC_MAP_PATH, "r", encoding="utf-8") as f:
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
            if any(
                part in ["__pycache__", ".git", ".venv", "node_modules"]
                for part in Path(root).parts
            ):
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

    result = {"path": rel_path, "status": "unknown", "matched_terms": []}

    # Verificar nome do arquivo
    filename_matches = [term for term in terms if term in filepath.name]

    # Tentar ler contedo
    try:
        content = filepath.read_text(encoding="utf-8", errors="strict")
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
            "coverage_percent": (len(recrutados) / len(results) * 100)
            if results
            else 0,
        },
        "desertores": [r["path"] for r in desertores],
        "inimigos": [{"path": r["path"], "error": r.get("error")} for r in inimigos],
        "details": results,
    }

    with open(COVERAGE_REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_content = f"""# Relatrio de Cobertura da KGS

**Data:** 2026-04-14
**Total de Arquivos Vlidos Analisados:** {report["summary"]["total_files"]}
**Recrutados (Indexados - Presentes na Teia):** {report["summary"]["recrutados"]} ({report["summary"]["coverage_percent"]:.1f}%)
**Desertores (Orfos Mudos - Ponto Cego):** {report["summary"]["desertores"]}
**Inimigos (Corrompidos/Erros):** {report["summary"]["inimigos"]}

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
    with open(COVERAGE_REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)


def load_symbolic_compressor():
    """Carrega o SymbolicCompressor usando importlib se a importao padro falhar."""
    global SymbolicCompressor, SYMBOLIC_COMPRESSOR_AVAILABLE, SYMBOLIC_COMPRESSOR_ERROR

    if SYMBOLIC_COMPRESSOR_AVAILABLE and SymbolicCompressor is not None:
        return SymbolicCompressor

    # Tentar importao direta via importlib
    try:
        import importlib.util

        compressor_path = (
            Path(__file__).resolve().parent.parent
            / "neocortex"
            / "infra"
            / "symbolic_compressor.py"
        )
        spec = importlib.util.spec_from_file_location(
            "symbolic_compressor", compressor_path
        )
        if spec is None:
            raise ImportError(f"No foi possvel criar spec para {compressor_path}")
        if spec.loader is None:
            raise ImportError(f"Loader no disponvel para {compressor_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SymbolicCompressor = module.SymbolicCompressor
        SYMBOLIC_COMPRESSOR_AVAILABLE = True
        SYMBOLIC_COMPRESSOR_ERROR = None
        return SymbolicCompressor
    except Exception as e:
        SYMBOLIC_COMPRESSOR_AVAILABLE = False
        SYMBOLIC_COMPRESSOR_ERROR = str(e)
        return None


def test_compression_on_files(results: list[dict], sample_count: int = 5):
    """Testa compresso simblica em arquivos recrutados."""
    # Tentar carregar o compressor
    compressor_class = load_symbolic_compressor()
    if compressor_class is None:
        print(
            f"   [!] No foi possvel carregar SymbolicCompressor: {SYMBOLIC_COMPRESSOR_ERROR}"
        )
        return None

    compressor = compressor_class()
    if not compressor.get_symbol_mapping():
        print(
            "   [!] Mapa simblico vazio. Execute NC-SCR-FR-021-lexicon-extractor.py primeiro."
        )
        return None

    # Filtrar arquivos recrutados que tm termos mapeados
    recrutados = [
        r for r in results if "RECRUTADO" in r["status"] and r.get("matched_terms")
    ]
    if not recrutados:
        print("   [!] Nenhum arquivo recrutado com termos mapeados.")
        return None

    # Pegar amostra
    sample = recrutados[:sample_count]
    compression_results = []

    print(f"\n Testando compresso simblica em {len(sample)} arquivos...")

    for item in sample:
        filepath = (
            Path(item["path"])
            if Path(item["path"]).exists()
            else PROJECT_ROOT / item["path"]
        )
        if not filepath.exists():
            continue

        try:
            content = filepath.read_text(encoding="utf-8")
            encoded, stats = compressor.encode_with_stats(content, aggressive=False)

            compression_results.append(
                {
                    "file": item["path"],
                    "matched_terms": item["matched_terms"],
                    "stats": stats,
                }
            )

            print(f"    {filepath.name}:")
            print(f"      Termos mapeados: {len(item['matched_terms'])}")
            print(
                f"      Reduo tokens: {stats['tokens_reduction_pct']:.1f}% ({stats['tokens_saved']} tokens)"
            )
            print(
                f"      Reduo chars: {stats['chars_reduction_pct']:.1f}% ({stats['chars_saved']} chars)"
            )

        except Exception as e:
            print(f"   [!] Erro ao processar {filepath.name}: {e}")

    if compression_results:
        # Calcular mdias
        avg_token_reduction = sum(
            r["stats"]["tokens_reduction_pct"] for r in compression_results
        ) / len(compression_results)
        avg_char_reduction = sum(
            r["stats"]["chars_reduction_pct"] for r in compression_results
        ) / len(compression_results)
        total_tokens_saved = sum(
            r["stats"]["tokens_saved"] for r in compression_results
        )

        print("\n RESUMO COMPRESSO:")
        print(f"   Mdia reduo tokens: {avg_token_reduction:.1f}%")
        print(f"   Mdia reduo chars: {avg_char_reduction:.1f}%")
        print(f"   Tokens salvos totais: {total_tokens_saved}")

        # Salvar relatrio de compresso
        compression_report_path = DOCS_DIR / "compression_report.json"
        report = {
            "timestamp": "2026-04-14",
            "sample_size": len(compression_results),
            "avg_token_reduction_pct": avg_token_reduction,
            "avg_char_reduction_pct": avg_char_reduction,
            "total_tokens_saved": total_tokens_saved,
            "details": compression_results,
        }

        with open(compression_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"    Relatrio salvo em: {compression_report_path}")

        return report

    return None


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
    print(f"    Domnio Teia KGS:   {recrutados / len(results) * 100:.1f}%")

    # Testar compresso simblica
    test_compression_on_files(results, sample_count=3)


if __name__ == "__main__":
    main()
