#!/usr/bin/env python3
import json
import networkx as nx
from pathlib import Path


def load_graph(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    G = nx.DiGraph()
    for node in data["nodes"]:
        G.add_node(node["id"], **{k: v for k, v in node.items() if k != "id"})
    for edge in data["edges"]:
        G.add_edge(
            edge["source"],
            edge["target"],
            **{k: v for k, v in edge.items() if k not in ("source", "target")},
        )
    return G


def main():
    json_path = Path(__file__).parent / "genealogy_graph.json"
    G = load_graph(json_path)

    print(f"Ns: {G.number_of_nodes()}, Arestas: {G.number_of_edges()}")

    # Listar alguns arquivos
    file_nodes = [n for n, attr in G.nodes(data=True) if attr.get("type") == "file"]
    print(f"\nTotal arquivos: {len(file_nodes)}")

    # Escolher um arquivo conhecido (sub_server.py em mcp)
    target_file = None
    for f in file_nodes:
        if "sub_server.py" in f and "mcp" in f:
            target_file = f
            break
    if target_file:
        print(f"\nAnalisando {target_file}:")
        # arestas de sada
        out_edges = list(G.out_edges(target_file, data=True))
        print(f"  Conexes de sada: {len(out_edges)}")
        for u, v, d in out_edges[:10]:
            print(f"    -> {v} ({d.get('relation', '?')})")
        # arestas de entrada
        in_edges = list(G.in_edges(target_file, data=True))
        print(f"  Conexes de entrada: {len(in_edges)}")
        for u, v, d in in_edges[:10]:
            print(f"    <- {u} ({d.get('relation', '?')})")
    else:
        print("Arquivo NC-CORE-FR-027-sub-server.py no encontrado.")
        # listar alguns arquivos de mcp
        mcp_files = [f for f in file_nodes if "mcp" in f]
        print(f"Arquivos em mcp: {len(mcp_files)}")
        for f in mcp_files[:5]:
            print(f"  {f}")

    # Estatsticas por tipo de relao
    relations = {}
    for u, v, d in G.edges(data=True):
        rel = d.get("relation", "unknown")
        relations[rel] = relations.get(rel, 0) + 1
    print("\nRelaes:")
    for rel, count in sorted(relations.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rel}: {count}")


if __name__ == "__main__":
    main()
