#!/usr/bin/env python3
"""
NeoCortex Akl Tool

Ferramenta MCP para neocortex_akl.
"""

from typing import Dict, Any
from ...core import get_akl_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_akl no servidor MCP.
    """

    @mcp.tool(name="neocortex_akl")
    def tool_akl(
        action: str,
        target: str = "",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Adaptive Knowledge Lifecycle  gerencia relevancia do conhecimento.

        Actions:
        - assess_importance: Avalia importancia de regras com base no uso
        - decay_knowledge: Aplica decaimento a regras nao utilizadas
        - suggest_cleanup: Lista regras candidatas a arquivamento
        """
        service = get_akl_service()

        if action == "assess_importance":
            return service.assess_importance(target)
        elif action == "decay_knowledge":
            return service.decay_knowledge()
        elif action == "suggest_cleanup":
            # Use threshold from metadata if provided
            threshold = 20
            if metadata:
                try:
                    threshold = int(metadata)
                except ValueError:
                    pass
            return service.suggest_cleanup(threshold)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_akl

#!/usr/bin/env python3
"""
NeoCortex Consolidation Tool

Ferramenta MCP para neocortex_consolidation.
"""

import json
from typing import Dict, Any
from ...core import get_consolidation_service


def register_tool(mcp):
    """
    Registra a ferramenta neocortex_consolidation no servidor MCP.
    """

    @mcp.tool(name="neocortex_consolidation")
    def tool_consolidation(
        action: str,
        session_id: str = "",
        summary: str = "",
        target: str = "",
        metadata: str = "",
    ) -> Dict[str, Any]:
        """
        Consolidacao Semantica  transforma experiencia efemera em regras permanentes.

        Actions:
        - summarize_session: Resume uma sessao em regras concisas
        - merge_learnings: Combina aprendizados de multiplos agentes
        - promote_to_rule: Promove entrada do Regression Buffer a regra permanente
        """
        service = get_consolidation_service()

        if action == "summarize_session":
            metadata_dict = json.loads(metadata) if metadata else None
            return service.summarize_session(session_id, summary, metadata_dict)
        elif action == "merge_learnings":
            return service.merge_learnings()
        elif action == "promote_to_rule":
            return service.promote_to_rule(target)

        return {"success": False, "error": f"Acao desconhecida: {action}"}

    return tool_consolidation

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

#!/usr/bin/env python3
"""
NeoCortex Manifest Tool

MCP tool for neocortex_manifest using ManifestService.
"""

import json
from typing import Dict, Any
from ...core import get_manifest_service


def register_tool(mcp):
    """
    Register neocortex_manifest tool on MCP server.
    """

    @mcp.tool(name="neocortex_manifest")
    def tool_manifest(
        action: str, target: str = "", metadata: str = ""
    ) -> Dict[str, Any]:
        """
        Manifest management (lightweight indices for lobes/cortex).

        Actions:
        - generate: Generate manifest for a lobe or cortex
        - update: Update metadata of an existing manifest
        - query: Query manifests by tags, domain or entities
        - get: Get specific manifest
        - list: List all manifests
        - delete: Delete a manifest
        - generate_all: Generate manifests for all lobes and cortex
        """
        # Get manifest service
        manifest_service = get_manifest_service()

        if action == "generate":
            if not target:
                return {
                    "success": False,
                    "error": "target is required (cortex or lobe name)",
                }

            result = manifest_service.generate_manifest(target)
            return result

        elif action == "update":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            # Parse metadata JSON if provided
            metadata_dict = None
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    return {"success": False, "error": "metadata must be valid JSON"}

            result = manifest_service.update_manifest(target, metadata_dict)
            return result

        elif action == "query":
            # Parse metadata as search term or tags
            search_term = None
            tags = None

            if metadata:
                # Try to parse as JSON for tags
                try:
                    metadata_dict = json.loads(metadata)
                    if isinstance(metadata_dict, list):
                        tags = metadata_dict
                    elif isinstance(metadata_dict, dict) and "tags" in metadata_dict:
                        tags = metadata_dict["tags"]
                    elif isinstance(metadata_dict, dict) and "search" in metadata_dict:
                        search_term = metadata_dict["search"]
                    else:
                        search_term = str(metadata_dict)
                except json.JSONDecodeError:
                    # Use as search term
                    search_term = metadata

            result = manifest_service.query_manifests(
                search_term=search_term, tags=tags, limit=100
            )
            return result

        elif action == "get":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            result = manifest_service.get_manifest(target)
            return result

        elif action == "list":
            result = manifest_service.list_all_manifests()
            return result

        elif action == "delete":
            if not target:
                return {"success": False, "error": "target is required (manifest ID)"}

            result = manifest_service.delete_manifest(target)
            return result

        elif action == "generate_all":
            result = manifest_service.generate_all_manifests()
            return result

        return {"success": False, "error": f"Unknown action: {action}"}

    return tool_manifest

