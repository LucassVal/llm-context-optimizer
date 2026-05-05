#!/usr/bin/env python3
"""
NC-SCR-FR-070-genealogy-builder.py
Genealogy Builder - Constri grafo de relaes (imports, ferramentas MCP, referncias SSOT) usando networkx.

Autor: Agente Genealogista
Data: 2026-04-14
"""

import os
import re
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any
import networkx as nx

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("GenealogyBuilder")

# Diretrio raiz do projeto (assumindo que o script est na raiz)
PROJECT_ROOT = Path(__file__).parent.resolve()

# Diretrios a ignorar
IGNORE_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "lobes",
    "DIR-BAK-FR-001-backup-main",
    "DIR-ARC-FR-001-archive-main",
    "data",
    "vector_db",
    "01_neocortex_framework_RENAMED",  # ignorar mirror renomeado, focar no original
}

# Extenses de arquivo a processar
EXTENSIONS = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".mdc"}

# Padres de regex
# 1. Imports Python - captura mdulo base aps 'import' ou 'from'
# Exemplos: import json, from neocortex.core import get_ledger_store, from neocortex.NC-CORE-FR-001-config import get_config
IMPORT_REGEX = re.compile(
    r"^\s*(?:import\s+([\w\.\-]+)(?:\s*,\s*[\w\.\-]+)*|from\s+([\w\.\-]+)\s+import)",
    re.MULTILINE,
)

# 2. Referncias a ferramentas MCP (padres comuns)
MCP_TOOL_PATTERN = re.compile(r"\bneocortex_[a-z_]+\b")  # funes neocortex_*
MCP_NC_TOOL_PATTERN = re.compile(r"NC-TOOL-FR-\d{3}[a-z\-]*")  # NC-TOOL-FR-XXX
MCP_SERVER_PATTERN = re.compile(r"\bMCP\b", re.IGNORECASE)

# 3. Menes a arquivos SSOT (padro NC-XXX-FR-XXX)
SSOT_PATTERN = re.compile(r"NC-[A-Z]+-FR-\d{3}(?:[a-zA-Z0-9\-]*)?")
# Tambm mences como @BOOT, @SSOT
SSOT_REF_PATTERN = re.compile(r"@(BOOT|SSOT|NC-[A-Z]+-FR-\d{3})")


def extract_python_imports(content: str) -> List[str]:
    """Extrai mdulos importados de cdigo Python."""
    imports = []
    for match in IMPORT_REGEX.finditer(content):
        # group 1: import module(s) (pode ser mltiplos separados por vrgula)
        # group 2: from module
        import_module = match.group(1)
        from_module = match.group(2)
        if from_module:
            imports.append(from_module)
        elif import_module:
            # Pode ser algo como "import os, sys, json"
            modules = [m.strip() for m in import_module.split(",")]
            imports.extend(modules)
    # Remover duplicatas e retornar
    return list(set(imports))


def extract_mcp_references(content: str) -> List[str]:
    """Extrai referncias a ferramentas MCP."""
    refs = []
    # Procura por padres de nome de ferramenta
    for match in MCP_TOOL_PATTERN.finditer(content):
        refs.append(match.group(0))
    for match in MCP_NC_TOOL_PATTERN.finditer(content):
        refs.append(match.group(0))
    # Se houver meno explcita a MCP (case-insensitive)
    if MCP_SERVER_PATTERN.search(content):
        refs.append("MCP")
    return list(set(refs))  # remover duplicatas


def extract_ssot_mentions(content: str) -> List[str]:
    """Extrai menes a arquivos SSOT."""
    mentions = []
    for match in SSOT_PATTERN.finditer(content):
        mentions.append(match.group(0))
    for match in SSOT_REF_PATTERN.finditer(content):
        mentions.append(match.group(0))
    return list(set(mentions))


def scan_file(file_path: Path) -> Dict[str, Any]:
    """Extrai relaes de um arquivo."""
    rel_path = file_path.relative_to(PROJECT_ROOT)
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Erro ao ler {rel_path}: {e}")
        return {}

    result = {
        "file": str(rel_path).replace("\\", "/"),
        "imports": [],
        "mcp_references": [],
        "ssot_mentions": [],
    }

    # Extrair conforme extenso
    if file_path.suffix == ".py":
        result["imports"] = extract_python_imports(content)

    # Para todos os arquivos, extrair referncias MCP e SSOT
    result["mcp_references"] = extract_mcp_references(content)
    result["ssot_mentions"] = extract_ssot_mentions(content)

    return result


def build_genealogy_graph(scan_results: List[Dict[str, Any]]) -> nx.DiGraph:
    """Constri um grafo direcionado com base nos resultados do scan."""
    G = nx.DiGraph()

    # Adicionar ns (arquivos)
    for res in scan_results:
        file_node = res["file"]
        G.add_node(file_node, type="file")

        # Adicionar arestas para imports (apenas Python)
        for imp in res["imports"]:
            # Tentar mapear import para arquivo local (simplificado)
            # Por enquanto, adicionar como n de import
            import_node = f"import:{imp}"
            G.add_node(import_node, type="import")
            G.add_edge(file_node, import_node, relation="imports")

        # Adicionar arestas para referncias MCP
        for mcp_ref in res["mcp_references"]:
            mcp_node = f"mcp:{mcp_ref}"
            G.add_node(mcp_node, type="mcp_reference")
            G.add_edge(file_node, mcp_node, relation="references_mcp")

        # Adicionar arestas para menes SSOT
        for ssot in res["ssot_mentions"]:
            ssot_node = f"ssot:{ssot}"
            G.add_node(ssot_node, type="ssot_mention")
            G.add_edge(file_node, ssot_node, relation="mentions_ssot")

    return G


def graph_to_json(G: nx.DiGraph) -> Dict[str, Any]:
    """Converte o grafo networkx para um formato JSON serializvel."""
    nodes = []
    for node, attr in G.nodes(data=True):
        nodes.append({"id": node, **attr})

    edges = []
    for u, v, attr in G.edges(data=True):
        edges.append({"source": u, "target": v, **attr})

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "generated_at": str(datetime.datetime.now().isoformat()),
        },
    }


def main():
    logger.info("Iniciando Genealogy Builder (NC-SCR-FR-070)...")
    logger.info(f"Raiz do projeto: {PROJECT_ROOT}")

    scan_results = []

    # Percorrer diretrios
    for dirpath, dirnames, filenames in os.walk(PROJECT_ROOT):
        # Filtrar diretrios ignorados
        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix not in EXTENSIONS:
                continue
            if name.startswith("."):
                continue
            # Ignorar arquivos dentro de diretrios ignorados (aps filtro)
            rel_path = path.relative_to(PROJECT_ROOT)
            if any(ignored in str(rel_path) for ignored in IGNORE_DIRS):
                continue

            logger.debug(f"Processando {rel_path}")
            result = scan_file(path)
            if result:
                scan_results.append(result)

    logger.info(f"Scan concludo. {len(scan_results)} arquivos processados.")

    # Construir grafo
    logger.info("Construindo grafo de relaes...")
    G = build_genealogy_graph(scan_results)

    # Exportar para JSON

    graph_data = graph_to_json(G)
    output_path = PROJECT_ROOT / "genealogy_graph.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(graph_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Grafo salvo em {output_path}")
    logger.info(f"Total de ns: {graph_data['metadata']['total_nodes']}")
    logger.info(f"Total de arestas: {graph_data['metadata']['total_edges']}")

    # Estatsticas simples
    file_nodes = [n for n in G.nodes() if G.nodes[n].get("type") == "file"]
    import_nodes = [n for n in G.nodes() if G.nodes[n].get("type") == "import"]
    mcp_nodes = [n for n in G.nodes() if G.nodes[n].get("type") == "mcp_reference"]
    ssot_nodes = [n for n in G.nodes() if G.nodes[n].get("type") == "ssot_mention"]

    logger.info("--- Estatsticas ---")
    logger.info(f"Arquivos: {len(file_nodes)}")
    logger.info(f"Imports: {len(import_nodes)}")
    logger.info(f"Referncias MCP: {len(mcp_nodes)}")
    logger.info(f"Menes SSOT: {len(ssot_nodes)}")

    # Tambm salvar um resumo em formato de texto
    summary_path = PROJECT_ROOT / "genealogy_summary.txt"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("Resumo do Grafo Genealgico\n")
        f.write("===========================\n")
        f.write(f"Arquivos processados: {len(file_nodes)}\n")
        f.write(f"Total de ns: {len(G.nodes())}\n")
        f.write(f"Total de arestas: {len(G.edges())}\n")
        f.write("\nTop 10 arquivos com mais conexes (grau de sada):\n")
        out_degree = {node: G.out_degree(node) for node in file_nodes}
        sorted_files = sorted(out_degree.items(), key=lambda x: x[1], reverse=True)[:10]
        for file, deg in sorted_files:
            f.write(f"  {file}: {deg} conexes\n")

    logger.info(f"Resumo salvo em {summary_path}")
    logger.info("Genealogy Builder concludo.")


if __name__ == "__main__":
    main()
