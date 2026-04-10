#!/usr/bin/env python3
"""
NeoCortex Kg Tool

Ferramenta MCP para neocortex_kg.
"""

import json
from typing import Dict, Any
from ...core import get_kg_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_kg no servidor MCP.
    """

    @mcp.tool(name="neocortex_kg")
    def tool_kg(
        action: str,
        entity: str = "",
        relation: str = "",
        target: str = "",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Mini Knowledge Graph  grafo semantico local (evolucao do Compact Encoding).

        Actions:
        - add_entity: Adiciona uma entidade ao Mini-KG
        - add_relation: Adiciona uma relacao entre entidades
        - query_relations: Retorna todas as relacoes de uma entidade
        - find_similar: Encontra entidades/lobos com caracteristicas semelhantes
        - visualize: Exporta o grafo em formato DOT ou estrutura simplificada
        """
        service = get_kg_service()

        if action == "add_entity":
            entity_type = metadata if metadata else "concept"
            return service.add_entity(entity, entity_type)
        elif action == "add_relation":
            metadata_dict = json.loads(metadata) if metadata else None
            return service.add_relation(entity, relation, target, metadata_dict)
        elif action == "query_relations":
            return service.query_relations(entity)
        elif action == "find_similar":
            return service.find_similar(entity)
        elif action == "visualize":
            return service.visualize()

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_kg
