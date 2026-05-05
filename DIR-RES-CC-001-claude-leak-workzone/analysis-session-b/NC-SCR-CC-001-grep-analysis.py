#!/usr/bin/env python3
"""
NC-SCR-CC-001-grep-analysis.py
Script auxiliar para anlise de cdigo vazado.
Busca termos em free-code/ e official-claude-code/.
"""

import os
import re
import sys
from pathlib import Path

logger = None  # ser configurado se necessrio


def setup_logging():
    import logging

    global logger
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)


def find_files_with_terms(root_dir, extensions, terms):
    """
    Retorna dicionrio {termo: [caminhos]}.
    """
    root = Path(root_dir)
    if not root.exists():
        logger.error(f"Diretrio no encontrado: {root}")
        return {}

    # Coletar arquivos
    files = []
    for ext in extensions:
        files.extend(root.rglob(f"*{ext}"))

    logger.info(f"Analisando {len(files)} arquivos em {root}")

    results = {term: [] for term in terms}
    for file in files:
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for term in terms:
                if term.lower() in content.lower():
                    results[term].append(str(file))
        except Exception as e:
            logger.debug(f"Erro ao ler {file}: {e}")

    return results


def main():
    setup_logging()

    # Termos conforme metodologia do ticket
    terms_phase0 = [
        "KAIROS",
        "tick",
        "SendUserFile",
        "PushNotification",
        "SubscribePR",
        "BRIDGE_MODE",
        "VOICE_MODE",
        "AFK",
        "ULTRAPLAN",
        "__ULTRAPLAN_TELEPORT_LOCAL__",
        "advisor",
        "history_snipping",
        "DRM",
        "license",
        "telemetry",
        "obfuscat",
    ]

    extensions = [".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".yaml", ".yml", ".txt"]

    # Diretrios
    base = Path("C:/Users/Lucas Valrio/Desktop/CLAUDE_CODE_DISSECTION")
    free_code = base / "free-code"
    official = base / "official-claude-code"
    leaked = base / "leaked-claude-code"

    logger.info("=== GREP GLOBAL free-code ===")
    results_free = find_files_with_terms(free_code, extensions, terms_phase0)

    # Imprimir resumo
    for term, paths in results_free.items():
        if paths:
            logger.info(f"{term}: {len(paths)} arquivos")
            for p in paths[:5]:  # primeiros 5
                logger.info(f"  - {p}")
            if len(paths) > 5:
                logger.info(f"  ... e mais {len(paths) - 5}")

    # Salvar resultados em arquivo
    output_dir = Path(__file__).parent
    output_file = output_dir / "NC-ANA-CC-002-grep-results.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# NC-ANA-CC-002  Resultados GREP Global\n\n")
        f.write("Termos buscados:\n")
        for term in terms_phase0:
            f.write(f"- `{term}`\n")
        f.write("\n## Resultados por termo\n")
        for term, paths in results_free.items():
            if paths:
                f.write(f"\n### {term}\n")
                f.write(f"**Arquivos:** {len(paths)}\n")
                for p in paths[:20]:
                    f.write(f"- `{p}`\n")
                if len(paths) > 20:
                    f.write(f"- ... ({len(paths) - 20} mais)\n")
            else:
                f.write(f"\n### {term}\nNenhum arquivo encontrado.\n")

    logger.info(f"Resultados salvos em {output_file}")

    # FASE 3  Plugins
    logger.info("\n=== PLUGINS OFICIAIS ===")
    plugins_dir = official / "plugins"
    if plugins_dir.exists():
        plugins = [p for p in plugins_dir.iterdir() if p.is_dir()]
        logger.info(f"Plugins encontrados: {len(plugins)}")
        for plugin in plugins:
            readme = plugin / "README.md"
            if readme.exists():
                logger.info(f"  {plugin.name}: README presente")
            else:
                logger.info(f"  {plugin.name}: sem README")
    else:
        logger.warning(f"Diretrio de plugins no encontrado: {plugins_dir}")

    # FASE 5  Validao cruzada
    logger.info("\n=== VALIDAO CRUZADA leaked-claude-code ===")
    if leaked.exists():
        results_leaked = find_files_with_terms(
            leaked, extensions, ["KAIROS", "DRM", "ULTRAPLAN"]
        )
        for term, paths in results_leaked.items():
            if paths:
                logger.info(f"{term}: {len(paths)} arquivos em leaked")

    logger.info("\nAnlise concluda.")


if __name__ == "__main__":
    main()
