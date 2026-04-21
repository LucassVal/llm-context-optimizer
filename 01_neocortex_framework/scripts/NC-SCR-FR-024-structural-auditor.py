#!/usr/bin/env python3
# Fix encoding for Windows (UTF-8)
import sys

if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.712496'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001
related_ssot:
  - NC-SCR-FR-024-structural-auditor
  - NC-SCR-FR-024
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""
NC-SCR-FR-024-structural-auditor.py
Agente Infiltrado: Audita a conformidade estrutural dos arquivos com NC-NAM-FR-001.
Autor: T0 (NeoCortex)
Data: 2026-04-14
"""

import json
import re
from pathlib import Path

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "01_neocortex_framework"))
from neocortex.core.file_utils import get_lobes_path

DOCS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
COVERAGE_REPORT_JSON = DOCS_DIR / "coverage_report.json"
STRUCTURAL_AUDIT_MD = DOCS_DIR / "structural_audit_report.md"

# Tipos de arquivo permitidos (extrados de NC-NAM-FR-001)
ALLOWED_TYPES = {
    "TOOL",
    "SCR",
    "DOC",
    "TODO",
    "LBE",
    "CFG",
    "SEC",
    "SOP",
    "ARC",
    "BAK",
    "BOOT",
    "TST",
    "PROMPT",
    "APP",
    "NAM",
    "AUD",
    "LED",
    "CTX",
    "HK",
    "VAL",
    "WKR",
    "SVC",
    "UTL",
    "ADP",
    "REV",
}

# Mapeamento de TIPO para diretrio esperado
TYPE_TO_DIR = {
    "TOOL": "01_neocortex_framework/neocortex/mcp/tools",
    "SCR": "01_neocortex_framework/scripts",
    "DOC": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "LBE": "02_memory_lobes",
    "CFG": "01_neocortex_framework/DIR-CFG-FR-001-config-main",  # Or neocortex/core/config
    "SEC": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "SOP": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "BOOT": "01_neocortex_framework/DIR-BOOT-FR-001-bootup-main",
    "PROMPT": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "NAM": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "AUD": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
    "TODO": "01_neocortex_framework/DIR-DOC-FR-001-docs-main",
}


def load_recruited_files() -> list[Path]:
    """Carrega a lista de arquivos recrutados do relatrio de cobertura."""
    if not COVERAGE_REPORT_JSON.exists():
        print(f"Erro: {COVERAGE_REPORT_JSON} no encontrado.")
        return []

    with open(COVERAGE_REPORT_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    paths = []
    for item in data["details"]:
        if "RECRUTADO" in item.get("status", ""):
            # Reconstruct absolute paths
            p = Path(item["path"])
            if not p.is_absolute():
                p = PROJECT_ROOT / p
            paths.append(p)
    return paths


def check_naming_convention(filepath: Path) -> dict:
    """Verifica se o nome do arquivo segue NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext"""
    filename = filepath.name

    # Exceptions that are structural but valid
    if filename in [
        "__init__.py",
        "neocortex_config.yaml",
        "neocortex_config_dev.yaml",
        "README.md",
        "vector_engine.py",
        "logging_config.py",
    ]:
        return {"conforms": True, "tipo": "SYSTEM"}

    pattern = r"^NC-([A-Z]+)-([A-Z0-9]+)-(\d{3})-(.+)\.([a-z0-9]+)$"
    match = re.match(pattern, filename)

    if not match:
        return {
            "conforms": False,
            "error": "Nome no segue o padro NC-<TIPO>-<SIGLA>-<NUM>-<desc>.ext",
        }

    tipo, sigla, num, desc, ext = match.groups()

    if tipo not in ALLOWED_TYPES:
        return {
            "conforms": False,
            "error": f"Tipo '{tipo}' no est na lista de tipos permitidos: {list(ALLOWED_TYPES)[:5]}...",
        }

    return {
        "conforms": True,
        "tipo": tipo,
        "sigla": sigla,
        "num": num,
        "desc": desc,
        "ext": ext,
    }


def check_directory_conformance(filepath: Path, tipo: str) -> dict:
    """Verifica se o arquivo est no diretrio esperado para seu TIPO."""
    if tipo == "SYSTEM":
        return {"conforms": True}

    expected_dir = TYPE_TO_DIR.get(tipo)
    if not expected_dir:
        return {
            "conforms": True,
            "warning": f"Sem diretrio mapeado para tipo '{tipo}' na regra rgida.",
        }

    try:
        rel_path = filepath.relative_to(PROJECT_ROOT)
    except ValueError:
        return {"conforms": False, "error": "Arquivo fora da raiz do projeto"}

    # We use 'in' because subfolders might apply
    if expected_dir.replace("/", "\\") in str(rel_path) or expected_dir in str(
        rel_path.as_posix()
    ):
        return {"conforms": True}

    # Special exceptions due to refactoring
    if tipo == "CFG" and "neocortex/core/config" in str(rel_path.as_posix()):
        return {"conforms": True}
    if tipo == "LBE" and str(get_lobes_path().as_posix()) in str(filepath.as_posix()):
        return {"conforms": True}

    return {
        "conforms": False,
        "error": f"Arquivo em '{rel_path.parent}', mas deveria estar preferencialmente em '{expected_dir}'",
    }


def check_content_hints(filepath: Path, tipo: str) -> dict:
    """Verifica heursticas bsicas de contedo baseado no tipo."""
    if tipo == "SYSTEM":
        return {"conforms": True}

    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return {"conforms": False, "error": "No foi possvel ler o arquivo"}

    hints = []
    if tipo == "TOOL" and "def register_tool" not in content and "class" not in content:
        hints.append(
            "Arquivo TOOL parece no conter 'def register_tool' ou a lgica MCP T0"
        )
    if tipo == "SCR" and "def main" not in content and "if __name__" not in content:
        hints.append("Arquivo SCR pode no ter ponto de entrada")

    if hints:
        return {"conforms": True, "warnings": hints}
    return {"conforms": True}


def main():
    print(" NC-SCR-FR-024: Agente Infiltrado iniciando auditoria estrutural...")

    files = load_recruited_files()
    print(f"    {len(files)} arquivos a auditar.")
    if not files:
        return

    non_conforming = []
    warnings = []

    for filepath in files:
        try:
            rel_path = str(filepath.relative_to(PROJECT_ROOT))
        except ValueError:
            rel_path = str(filepath.absolute())

        result = {"path": rel_path}

        # 1. Verificar nomenclatura
        naming = check_naming_convention(filepath)
        if not naming["conforms"]:
            result["naming_error"] = naming["error"]
            non_conforming.append(result)
            continue

        result["tipo"] = naming["tipo"]

        # 2. Verificar diretrio
        dir_check = check_directory_conformance(filepath, naming["tipo"])
        if not dir_check["conforms"]:
            result["directory_error"] = dir_check["error"]
            non_conforming.append(result)
            continue

        # 3. Verificar contedo (heursticas)
        content_check = check_content_hints(filepath, naming["tipo"])
        if "warnings" in content_check:
            result["warnings"] = content_check["warnings"]
            warnings.append(result)

    # Gerar relatrio Markdown
    md_content = f"""# Relatrio de Auditoria Estrutural KGS

**Data:** 2026-04-14
**Total de Arquivos Auditados:** {len(files)}
**No-Conformidades (Violam SSOT/Padro):** {len(non_conforming)}
**Avisos Semnticos:** {len(warnings)}

##  No-Conformidades (Violaes Graves de Nomes/Paths)

"""
    if non_conforming:
        for item in non_conforming:
            md_content += f"### `{item['path']}`\n"
            if "naming_error" in item:
                md_content += f"- **Erro de Nomenclatura:** {item['naming_error']}\n"
            if "directory_error" in item:
                md_content += (
                    f"- **Erro de Diretrio / Fallback:** {item['directory_error']}\n"
                )
            md_content += "\n"
    else:
        md_content += (
            " Nenhuma no-conformidade encontrada. Arquitetura Diamante Pronta.\n\n"
        )

    md_content += "##  Avisos (Recomendaes Heursticas)\n\n"
    if warnings:
        for item in warnings:
            md_content += f"### `{item['path']}`\n"
            for w in item["warnings"]:
                md_content += f"- {w}\n"
            md_content += "\n"
    else:
        md_content += " Nenhum aviso em cdigo.\n\n"

    md_content += f"""
##  Resumo Final

| Indicador | Valor |
| :--- | :--- |
| Total de Arquivos Recrutados | {len(files)} |
| Conformes (100% Padro FR) | {len(files) - len(non_conforming)} |
| No-Conformidades | {len(non_conforming)} |
| Avisos | {len(warnings)} |

---
*Relatrio gerado por NC-SCR-FR-024-structural-auditor.py*
"""

    with open(STRUCTURAL_AUDIT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n RESULTADO DA INFILTRAO:")
    print(f"    No-Conformidades: {len(non_conforming)}")
    print(f"    Avisos: {len(warnings)}")
    print(f"    Relatrio salvo em: {STRUCTURAL_AUDIT_MD}")


if __name__ == "__main__":
    main()
