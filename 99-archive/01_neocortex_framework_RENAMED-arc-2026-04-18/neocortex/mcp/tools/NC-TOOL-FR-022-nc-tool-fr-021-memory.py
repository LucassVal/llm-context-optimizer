from __future__ import annotations

"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "021", "memory"]
hash: "auto-generated"
---"""
#!/usr/bin/env python3
"""
NC-TOOL-FR-021-memory.py
FR-021  MCP Tool: neocortex_memory

Tool unificada para gesto de memria modular (lobes, cortex, manifestos, busca).
Absorve: NC-TOOL-FR-001-cortex.py, NC-TOOL-FR-009-lobes.py, NC-TOOL-FR-014-search.py,
         NC-TOOL-FR-013-manifest.py (lgica em manifest_service), NC-TOOL-FR-007-init.py (parcial)

Aes disponveis:
  lobe.list_active       lista lobes disponveis e status (ativo/inativo)
  lobe.get_content       retorna contedo de lobe especfico
  lobe.activate          ativa lobe pelo nome
  lobe.deactivate        desativa lobe
  lobe.search            busca texto dentro de lobes (FTS suportado)
  lobe.list_all          lista todos os lobes com metadados
  lobe.get_checkpoint_tree  extrai rvore de checkpoints de um lobe

  cortex.get_full        contedo completo do cortex com metadados
  cortex.get_section     retorna seo especfica do cortex
  cortex.get_aliases     retorna todos os aliases definidos
  cortex.get_workflows   retorna workflows definidos no cortex
  cortex.validate_alias  valida se alias est correto

  manifest.generate      gera manifesto para lobe ou cortex
  manifest.update        atualiza metadados de manifesto existente
  manifest.query         filtra manifestos por tags/domain/entities
  manifest.list          lista todos os manifestos
  manifest.generate_all  gera manifestos para todos os lobes

  search.advanced        busca avanada com filtros (mdulo, status, tags)
"""


import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Servios singleton
def _get_cortex_service():
    try:
        from ...core.cortex_service import get_cortex_service

        return get_cortex_service()
    except ImportError as e:
        logger.error(f"Erro ao importar cortex_service: {e}")
        raise


def _get_lobe_service():
    try:
        from ...core import get_lobe_service

        return get_lobe_service()
    except ImportError as e:
        logger.error(f"Erro ao importar lobe_service: {e}")
        raise


def _get_manifest_service():
    try:
        from ...core.manifest_service import get_manifest_service

        return get_manifest_service()
    except ImportError as e:
        logger.error(f"Erro ao importar manifest_service: {e}")
        raise


def register_tool(mcp) -> None:
    """Registra neocortex_memory no servidor MCP."""

    @mcp.tool(name="neocortex_memory")
    def neocortex_memory(
        action: str,
        lobe_name: str = "",
        section: str = "",
        alias: str = "",
        query: str = "",
        module: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
        target: str = "",
        manifest_id: str = "",
        metadata: str = "",
        search_term: Optional[str] = None,
        manifest_type: Optional[str] = None,
        tags_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Gesto unificada de memria modular: lobes, cortex, manifestos, busca.

        Aes disponveis (prefixo lobe., cortex., manifest., search.):

        Lobe:
          lobe.list_active       lista lobes ativos/inativos
          lobe.get_content       contedo de lobe especfico (lobe_name obrigatrio)
          lobe.activate          ativa lobe (lobe_name obrigatrio)
          lobe.deactivate        desativa lobe (lobe_name obrigatrio)
          lobe.search            busca texto em lobes (query obrigatrio)
          lobe.list_all          lista todos os lobes com metadados
          lobe.get_checkpoint_tree  rvore de checkpoints de um lobe (lobe_name)

        Cortex:
          cortex.get_full        contedo completo do cortex
          cortex.get_section     retorna seo especfica (section obrigatrio)
          cortex.get_aliases     lista todos os aliases definidos
          cortex.get_workflows   lista workflows definidos
          cortex.validate_alias  valida um alias (alias obrigatrio)

        Manifest:
          manifest.generate      gera manifesto para target (cortex ou lobe)
          manifest.update        atualiza manifesto (manifest_id obrigatrio, metadata JSON opcional)
          manifest.query         filtra manifestos (search_term, manifest_type, tags_filter, limit)
          manifest.list          lista todos os manifestos
          manifest.generate_all  gera manifestos para todos os lobes e cortex

        Search:
          search.advanced        busca avanada com filtros (query, module, status, tags, limit)
        """
        #  lobe.list_active
        if action == "lobe.list_active":
            lobe_service = _get_lobe_service()
            all_lobes_result = lobe_service.list_lobes()
            active_lobes_result = lobe_service.get_active_lobes()
            return {
                "success": True,
                "action": action,
                "all_lobes": all_lobes_result.get("lobes", []),
                "active_lobes": active_lobes_result.get("active_lobes", []),
                "active_lobes_details": active_lobes_result.get("lobe_details", []),
                "total_lobes": all_lobes_result.get("total", 0),
                "total_active": active_lobes_result.get("total_active", 0),
            }

        #  lobe.list_all
        elif action == "lobe.list_all":
            lobe_service = _get_lobe_service()
            result = lobe_service.list_lobes()
            return {**result, "action": action}

        #  lobe.get_content
        elif action == "lobe.get_content":
            if not lobe_name:
                return {"success": False, "error": "lobe_name  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.get_lobe(lobe_name)
            return {**result, "action": action}

        #  lobe.activate
        elif action == "lobe.activate":
            if not lobe_name:
                return {"success": False, "error": "lobe_name  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.activate_lobe(lobe_name)
            return {**result, "action": action}

        #  lobe.deactivate
        elif action == "lobe.deactivate":
            if not lobe_name:
                return {"success": False, "error": "lobe_name  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.deactivate_lobe(lobe_name)
            return {**result, "action": action}

        #  lobe.search
        elif action == "lobe.search":
            if not query:
                return {"success": False, "error": "query  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.search_lobes(query, case_sensitive=False)
            return {**result, "action": action}

        #  lobe.get_checkpoint_tree
        elif action == "lobe.get_checkpoint_tree":
            if not lobe_name:
                return {"success": False, "error": "lobe_name  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.get_checkpoint_tree(lobe_name)
            return {**result, "action": action}

        #  cortex.get_full
        elif action == "cortex.get_full":
            cortex_service = _get_cortex_service()
            result = cortex_service.get_full_cortex()
            return {
                "success": True,
                "action": action,
                "content": result["content"],
                "metadata": result["metadata"],
                "aliases": result["aliases"],
                "workflows": result["workflows"],
            }

        #  cortex.get_section
        elif action == "cortex.get_section":
            if not section:
                return {"success": False, "error": "section  obrigatrio"}
            cortex_service = _get_cortex_service()
            result = cortex_service.get_cortex_section(section)
            if result.get("found"):
                return {
                    "success": True,
                    "action": action,
                    "section": result["section"],
                    "content": result["content"],
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Section no encontrada"),
                }

        #  cortex.get_aliases
        elif action == "cortex.get_aliases":
            cortex_service = _get_cortex_service()
            aliases = cortex_service.get_aliases()
            alias_list = [{"symbol": k, "path": v} for k, v in aliases.items()]
            return {"success": True, "action": action, "aliases": alias_list}

        #  cortex.get_workflows
        elif action == "cortex.get_workflows":
            cortex_service = _get_cortex_service()
            workflows = cortex_service.get_workflows()
            return {
                "success": True,
                "action": action,
                "workflows": workflows,
                "count": len(workflows),
            }

        #  cortex.validate_alias
        elif action == "cortex.validate_alias":
            if not alias:
                return {"success": False, "error": "alias  obrigatrio"}
            cortex_service = _get_cortex_service()
            result = cortex_service.validate_alias(alias)
            if result["valid"]:
                return {
                    "success": True,
                    "action": action,
                    "valid": True,
                    "exists": result["exists"],
                    "alias": result.get("alias"),
                    "value": result.get("value"),
                }
            else:
                return {
                    "success": False,
                    "valid": False,
                    "error": result.get("error", "Alias no encontrado"),
                }

        #  manifest.generate
        elif action == "manifest.generate":
            if not target:
                return {
                    "success": False,
                    "error": "target  obrigatrio (cortex ou lobe name)",
                }
            manifest_service = _get_manifest_service()
            result = manifest_service.generate_manifest(target)
            return {**result, "action": action}

        #  manifest.update
        elif action == "manifest.update":
            if not manifest_id:
                return {"success": False, "error": "manifest_id  obrigatrio"}
            metadata_dict = {}
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    return {"success": False, "error": "metadata deve ser JSON vlido"}
            manifest_service = _get_manifest_service()
            result = manifest_service.update_manifest(manifest_id, metadata_dict)
            return {**result, "action": action}

        #  manifest.query
        elif action == "manifest.query":
            manifest_service = _get_manifest_service()
            result = manifest_service.query_manifests(
                search_term=search_term,
                manifest_type=manifest_type,
                tags=tags_filter,
                limit=limit,
            )
            return {**result, "action": action}

        #  manifest.list
        elif action == "manifest.list":
            manifest_service = _get_manifest_service()
            result = manifest_service.list_all_manifests()
            return {**result, "action": action}

        #  manifest.generate_all
        elif action == "manifest.generate_all":
            manifest_service = _get_manifest_service()
            result = manifest_service.generate_all_manifests()
            return {**result, "action": action}

        #  search.advanced
        elif action == "search.advanced":
            if not query:
                return {"success": False, "error": "query  obrigatrio"}
            lobe_service = _get_lobe_service()
            result = lobe_service.search_lobes_advanced(
                query=query,
                module=module,
                status=status,
                tags=tags,
                limit=limit,
            )
            return {**result, "action": action}

        #  ao desconhecida
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "lobe.list_active",
                    "lobe.list_all",
                    "lobe.get_content",
                    "lobe.activate",
                    "lobe.deactivate",
                    "lobe.search",
                    "lobe.get_checkpoint_tree",
                    "cortex.get_full",
                    "cortex.get_section",
                    "cortex.get_aliases",
                    "cortex.get_workflows",
                    "cortex.validate_alias",
                    "manifest.generate",
                    "manifest.update",
                    "manifest.query",
                    "manifest.list",
                    "manifest.generate_all",
                    "search.advanced",
                ],
            }

    return neocortex_memory
