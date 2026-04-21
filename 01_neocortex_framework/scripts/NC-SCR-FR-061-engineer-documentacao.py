#!/usr/bin/env python3
"""---
_genealogy:
  injected_at: '2026-04-16T00:24:01.739026'
  injected_by: NC-SCR-FR-075-genealogy-injector.py
  version: '1.0'
topology: neocortex-other
level: 0
parent_ssot: NC-NAM-FR-001-naming-convention
related_ssot:
  - NC-SCR-FR-061-engineer-documentacao
  - NC-NAM-FR-001
  - NC-SCR-FR-061
tags:
  - neocortex-other
  - level-0
  - nc-prefix
  - python
---"""

"""---
domain: "governance"
layer: "infra"
type: "SCR"
tags: ["engineer", "documentation", "project-map", "compliance", "nc-ds-055"]
hash: "auto-generated"
---

NC-SCR-FR-061-engineer-documentacao.py
Agente Engineer: Atualiza mapa do projeto e verifica conformidade com SSOT.
Autor: T0 (NeoCortex)
Data: 2026-04-14
Status: Fase 1/3 - Gerao de mapa estrutural
"""

import io
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# Configurar encoding UTF-8 para stdout/stderr no Windows
if sys.platform == "win32":
    # Substituir sys.stdout e sys.stderr com wrappers UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Configuraes
PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = PROJECT_ROOT / "01_neocortex_framework" / "DIR-DOC-FR-001-docs-main"
PROJECT_MAP_FILE = DOCS_DIR / "PROJECT_MAP.md"
NAMING_CONVENTION = DOCS_DIR / "NC-NAM-FR-001-naming-convention.md"

# Diretrios cannicos esperados (baseados em NC-NAM-FR-001)
CANONICAL_DIR_PREFIXES = [
    "DIR-DOC-FR-",
    "DIR-ARC-FR-",
    "DIR-BOOT-FR-",
    "DIR-DS-",
    "DIR-RES-",
    "DIR-TMP-FR-",
    "DIR-CFG-FR-",
    "DIR-TEST-FR-",
    "DIR-MCP-FR-",
    "DIR-CORE-FR-",
    "DIR-PRF-FR-",
    "DIR-BAK-FR-",
]

# Zonas de quarentena (dvida tcnica reconhecida)
QUARANTINE_DIRS = ["neocortex/core", "neocortex/infra", "neocortex/mcp/tools"]

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def generate_directory_tree(
    root_path: Path, exclude_dirs: Optional[Set[str]] = None
) -> List[str]:
    """
    Gera representao em rvore de diretrios.
    Retorna lista de strings formatadas.
    """
    if exclude_dirs is None:
        exclude_dirs = {".git", "__pycache__", ".ruff_cache", ".neocortex", ".kilocode"}

    tree_lines = []

    def walk(dir_path: Path, prefix: str = ""):
        try:
            # Obter itens ordenados (diretrios primeiro)
            items = sorted(
                dir_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())
            )

            for i, item in enumerate(items):
                is_last = i == len(items) - 1

                # Pular diretrios excludos
                if item.name in exclude_dirs:
                    continue

                # Determinar prefixos grficos
                connector = " " if is_last else " "

                # Adicionar linha
                tree_lines.append(f"{prefix}{connector}{item.name}")

                # Se for diretrio, recurso
                if item.is_dir():
                    extension = "    " if is_last else "   "
                    walk(item, prefix + extension)

        except PermissionError:
            logger.warning(f"Permisso negada para acessar: {dir_path}")
        except Exception as e:
            logger.error(f"Erro ao caminhar em {dir_path}: {e}")

    # Linha inicial
    tree_lines.append(f"{root_path.name}/")

    # Gerar rvore
    walk(root_path)

    return tree_lines


def check_directory_compliance(dir_path: Path) -> str:
    """
    Verifica conformidade do diretrio com NC-NAM-FR-001.
    Retorna emoji de status.
    """
    dir_name = dir_path.name

    # Verificar se  diretrio cannico
    for prefix in CANONICAL_DIR_PREFIXES:
        if dir_name.startswith(prefix):
            return " Conforme"

    # Verificar se est em zona de quarentena
    rel_path = str(dir_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    for quarantine in QUARANTINE_DIRS:
        if quarantine in rel_path:
            return " Quarentena"

    # Outros diretrios (anlise adicional)
    if dir_name.startswith("DIR-"):
        return "  Prefixo DIR- mas no cannico"

    return " No-Conforme"


def check_file_compliance(file_path: Path) -> str:
    """
    Verifica conformidade do arquivo com NC-NAM-FR-001.
    Retorna emoji de status.
    """
    file_name = file_path.name

    # Verificar prefixo NC-
    if file_name.startswith("NC-"):
        return " Conforme"

    # Verificar se est em zona de quarentena
    rel_path = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    for quarantine in QUARANTINE_DIRS:
        if quarantine in rel_path:
            return " Quarentena"

    # Arquivos permitidos sem prefixo NC-
    ALLOWED_NON_NC = [
        "README.md",
        "pyproject.toml",
        "requirements.txt",
        "start_neocortex_mcp.bat",
        "start_neocortex_mcp.ps1",
        "start_neocortex_dev.bat",
        "NeoCortex_HUD.bat",
        ".gitignore",
        ".pre-commit-config.yaml",
    ]

    if file_name in ALLOWED_NON_NC:
        return " Conforme (exceo)"

    return " No-Conforme"


def analyze_structure(root_path: Path) -> Dict:
    """
    Analisa toda a estrutura do projeto e coleta estatsticas.
    """
    stats = {
        "total_dirs": 0,
        "total_files": 0,
        "conforme_dirs": 0,
        "conforme_files": 0,
        "quarantine_dirs": 0,
        "quarantine_files": 0,
        "non_conforme_dirs": 0,
        "non_conforme_files": 0,
        "directory_compliance": [],
        "file_compliance": [],
    }

    # Analisar diretrios
    for dir_path in root_path.rglob("*"):
        if dir_path.is_dir():
            stats["total_dirs"] += 1
            status = check_directory_compliance(dir_path)

            entry = {"path": str(dir_path.relative_to(root_path)), "status": status}
            stats["directory_compliance"].append(entry)

            # Contar por categoria
            if "" in status:
                stats["conforme_dirs"] += 1
            elif "" in status:
                stats["quarantine_dirs"] += 1
            elif "" in status:
                stats["non_conforme_dirs"] += 1

    # Analisar arquivos
    for file_path in root_path.rglob("*"):
        if file_path.is_file():
            stats["total_files"] += 1
            status = check_file_compliance(file_path)

            entry = {"path": str(file_path.relative_to(root_path)), "status": status}
            stats["file_compliance"].append(entry)

            # Contar por categoria
            if "" in status:
                stats["conforme_files"] += 1
            elif "" in status:
                stats["quarantine_files"] += 1
            elif "" in status:
                stats["non_conforme_files"] += 1

    return stats


def generate_project_map(stats: Dict, tree_lines: List[str]) -> str:
    """
    Gera contedo do PROJECT_MAP.md com formatao completa.
    """
    timestamp = "2026-04-14"

    content = f"""# PROJECT_MAP.md - Mapa Estrutural do Projeto NeoCortex

**Gerado:** {timestamp} | **Agente:** Engineer (NC-SCR-FR-061)  
**Base:** NC-NAM-FR-001-naming-convention.md

##  Estatsticas de Conformidade

| Categoria | Diretrios | Arquivos | Total |
|-----------|------------|----------|-------|
|  Conforme | {stats["conforme_dirs"]} | {stats["conforme_files"]} | {stats["conforme_dirs"] + stats["conforme_files"]} |
|  Quarentena | {stats["quarantine_dirs"]} | {stats["quarantine_files"]} | {stats["quarantine_dirs"] + stats["quarantine_files"]} |
|  No-Conforme | {stats["non_conforme_dirs"]} | {stats["non_conforme_files"]} | {stats["non_conforme_dirs"] + stats["non_conforme_files"]} |
| **Total** | **{stats["total_dirs"]}** | **{stats["total_files"]}** | **{stats["total_dirs"] + stats["total_files"]}** |

##  rvore de Diretrios (TURBOQUANT_V42/)

```
{"\\n".join(tree_lines)}
```

##  Legenda de Status

| Emoji | Significado | Ao Recomendada |
|-------|-------------|------------------|
|  Conforme | Segue padro NC-NAM-FR-001 | Nenhuma ao necessria |
|  Quarentena | Dvida tcnica reconhecida (core/, infra/, mcp/tools/) | Aguardar saneamento pelo Courier |
|  No-Conforme | Viola padro SSOT | Requer correo ou arquivamento |
|   Prefixo DIR- mas no cannico | Usa prefixo DIR- mas no est na lista cannica | Verificar necessidade de adicionar ao SSOT |
|  Conforme (exceo) | Arquivo permitido sem prefixo NC- (README.md, etc.) | Nenhuma ao necessria |

##  Diretrios Cannicos Esperados

Os seguintes prefixos de diretrio so considerados **cannicos** conforme NC-NAM-FR-001:

```
{"\\n".join([f"- {prefix}*" for prefix in CANONICAL_DIR_PREFIXES])}
```

##  Zonas de Quarentena (Dvida Tcnica)

Os seguintes diretrios contm arquivos legados que esto em processo de saneamento:

```
{"\\n".join([f"- {quarantine}" for quarantine in QUARANTINE_DIRS])}
```

##  Recomendaes para o Agente Courier

1. **Arquivos em Quarentena:** {stats["quarantine_files"]} arquivos aguardam renomeao cannica.
2. **Diretrios No-Conformes:** {stats["non_conforme_dirs"]} diretrios requerem reviso.
3. **Arquivos No-Conformes:** {stats["non_conforme_files"]} arquivos violam padro SSOT.

##  Atualizao do SSOT

Se novos diretrios cannicos forem identificados durante a auditoria, editar:
`01_neocortex_framework/DIR-DOC-FR-001-docs-main/NC-NAM-FR-001-naming-convention.md`

---

*Mapa gerado automaticamente por NC-SCR-FR-061-engineer-documentacao.py*  
*Prxima execuo: Ao adicionar novos diretrios ou modificar estrutura*
"""

    return content


def update_naming_convention(new_dirs: List[str]) -> None:
    """
    Atualiza NC-NAM-FR-001 com novos diretrios cannicos identificados.
    """
    if not new_dirs:
        logger.info("Nenhum novo diretrio cannico identificado.")
        return

    try:
        content = NAMING_CONVENTION.read_text(encoding="utf-8")

        # Encontrar seo de diretrios cannicos
        # (Implementao simplificada - em produo seria mais robusta)
        logger.info(f"Novos diretrios cannicos identificados: {new_dirs}")
        logger.warning("Atualizao manual do NC-NAM-FR-001 necessria.")

        # Salvar sugestes em arquivo separado
        suggestions_file = DOCS_DIR / "suggested_dir_updates.txt"
        suggestions = "\\n".join([f"- {dir_path}" for dir_path in new_dirs])
        suggestions_file.write_text(
            f"Diretrios sugeridos para adio ao NC-NAM-FR-001:\\n{suggestions}",
            encoding="utf-8",
        )

        logger.info(f"Sugestes salvas em {suggestions_file}")

    except Exception as e:
        logger.error(f"Erro ao tentar atualizar NC-NAM-FR-001: {e}")


def main() -> None:
    """
    Fluxo principal do Agente Engineer.
    """
    logger.info("=== INCIO: Agente Engineer - Mapa do Projeto ===")

    # 1. Gerar rvore de diretrios
    logger.info("Gerando rvore de diretrios...")
    tree_lines = generate_directory_tree(PROJECT_ROOT)

    # 2. Analisar estrutura e conformidade
    logger.info("Analisando conformidade com NC-NAM-FR-001...")
    stats = analyze_structure(PROJECT_ROOT)

    # 3. Identificar novos diretrios cannicos
    new_canonical_dirs = []
    for entry in stats["directory_compliance"]:
        if "" in entry["status"] and entry["path"].startswith("DIR-"):
            new_canonical_dirs.append(entry["path"])

    # 4. Atualizar SSOT se necessrio
    if new_canonical_dirs:
        update_naming_convention(new_canonical_dirs)

    # 5. Gerar PROJECT_MAP.md
    logger.info("Gerando PROJECT_MAP.md...")
    map_content = generate_project_map(stats, tree_lines)

    PROJECT_MAP_FILE.write_text(map_content, encoding="utf-8")
    logger.info(f"Mapa do projeto salvo em {PROJECT_MAP_FILE}")

    # 6. Relatrio final
    logger.info("=== RELATRIO FINAL ===")
    logger.info(f"Diretrios totais: {stats['total_dirs']}")
    logger.info(f"Arquivos totais: {stats['total_files']}")
    logger.info(
        f"Conformidade diretrios: {stats['conforme_dirs']} , {stats['quarantine_dirs']} , {stats['non_conforme_dirs']} "
    )
    logger.info(
        f"Conformidade arquivos: {stats['conforme_files']} , {stats['quarantine_files']} , {stats['non_conforme_files']} "
    )

    if new_canonical_dirs:
        logger.info(
            f"Novos diretrios cannicos identificados: {len(new_canonical_dirs)}"
        )

    logger.info(f"Mapa gerado: {PROJECT_MAP_FILE}")
    logger.info("=== FIM: Agente Engineer concludo ===")

    # 7. Instrues para prximo agente
    print("\n" + "=" * 60)
    print("INSTRUCOES PARA PROXIMO AGENTE (Tester/Courier):")
    print("=" * 60)
    print("1. Revisar o mapa do projeto em:")
    print(f"   {PROJECT_MAP_FILE}")
    print("2. Priorizar saneamento de arquivos [NAO-CONFORME].")
    print("3. Usar zonas [QUARENTENA] como referencia para renomeacao.")
    print("4. Validar novos diretorios canonicos sugeridos.")
    print("5. Executar auditoria periodica para manter conformidade.")
    print("=" * 60)


if __name__ == "__main__":
    main()
