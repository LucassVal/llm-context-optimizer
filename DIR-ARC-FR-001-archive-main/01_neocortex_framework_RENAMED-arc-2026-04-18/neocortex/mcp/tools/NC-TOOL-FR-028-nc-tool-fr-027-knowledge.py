from __future__ import annotations
"""---
domain: "orchestration"
layer: "core"
type: "service"
tags: ["tool", "027", "knowledge"]
hash: "auto-generated"
---"""
"""
NC-TOOL-FR-027-knowledge.py
FR-027  MCP Tool: neocortex_knowledge

Gesto de conhecimento e indexao do NeoCortex.
Aes disponveis:
  knowledge.search           busca semntica nos lobes indexados (FTS5)
  knowledge.get_documents    recupera documentos por URI/nome do ndice
  knowledge.project_manifest  retorna estrutura compacta do projeto para bootstrap IA
  knowledge.get_boot_context  string compacta para incio de sesso (substitui leitura manual)
  knowledge.update_index     fora re-indexao de lobes aps mudanas
"""


import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _config():
    try:
        from neocortex.NC-CORE-FR-001-config import get_config

        return get_config()
    except Exception:
        return None


def _get_search_engine():
    try:
        from neocortex.infra import get_search_engine

        return get_search_engine()
    except Exception:
        return None


def _get_lobe_service():
    try:
        from neocortex.core import get_lobe_service

        return get_lobe_service()
    except Exception:
        return None


def _get_lobe_index():
    try:
        from neocortex.infra import get_lobe_index

        return get_lobe_index()
    except Exception:
        return None


def _get_manifest_service():
    try:
        from neocortex.core import get_manifest_service

        return get_manifest_service()
    except Exception:
        return None


def register_tool(mcp) -> None:
    """Registra neocortex_knowledge no servidor MCP."""

    @mcp.tool(name="neocortex_knowledge")
    def neocortex_knowledge(
        action: str,
        query: str = "",
        uri: str = "",
        limit: int = 10,
        format: str = "compact",
    ) -> Dict[str, Any]:
        """
        Gesto de conhecimento e indexao do NeoCortex.

        Aes disponveis:
          knowledge.search           busca semntica nos lobes indexados (FTS5)
          knowledge.get_documents    recupera documentos por URI/nome do ndice
          knowledge.project_manifest  retorna estrutura compacta do projeto para bootstrap IA
          knowledge.get_boot_context  string compacta para incio de sesso (substitui leitura manual)
          knowledge.update_index     fora re-indexao de lobes aps mudanas

        Args:
            action:   Ao desejada
            query:    Consulta para search
            uri:      URI do documento para get_documents
            limit:    Limite de resultados para search (default: 10)
            format:   Formato para project_manifest (compact/detailed)
        """

        #  knowledge.search 
        if action == "knowledge.search":
            if not query:
                return {
                    "success": False,
                    "error": "Fornea 'query' para knowledge.search.",
                }
            search_engine = _get_search_engine()
            if search_engine is None:
                return {"success": False, "error": "SearchEngine no disponvel."}
            try:
                results = search_engine.search(query, limit=limit)
                return {
                    "success": True,
                    "action": action,
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  knowledge.get_documents 
        elif action == "knowledge.get_documents":
            if not uri:
                return {
                    "success": False,
                    "error": "Fornea 'uri' para knowledge.get_documents.",
                }
            lobe_index = _get_lobe_index()
            if lobe_index is None:
                return {"success": False, "error": "LobeIndex no disponvel."}
            try:
                documents = lobe_index.get_documents_by_uri(uri)
                return {
                    "success": True,
                    "action": action,
                    "uri": uri,
                    "documents": documents,
                    "count": len(documents),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  knowledge.project_manifest 
        elif action == "knowledge.project_manifest":
            manifest_service = _get_manifest_service()
            if manifest_service is None:
                # Fallback para leitura direta do arquivo gerado
                try:
                    cfg = _config()
                    if cfg:
                        base = Path(cfg.base_path)
                        manifest_file = base / "NC-MAN-FR-001-project-manifest.md"
                        if manifest_file.exists():
                            content = manifest_file.read_text(
                                encoding="utf-8", errors="replace"
                            )
                            return {
                                "success": True,
                                "action": action,
                                "format": format,
                                "manifest": content[:5000]
                                if format == "compact"
                                else content,
                                "source": "file",
                                "timestamp": datetime.now().isoformat(),
                            }
                    return {
                        "success": False,
                        "error": "Arquivo de manifesto no encontrado.",
                    }
                except Exception as e:
                    return {"success": False, "error": str(e)}
            try:
                if format == "compact":
                    manifest = manifest_service.get_compact_manifest()
                else:
                    manifest = manifest_service.get_detailed_manifest()
                return {
                    "success": True,
                    "action": action,
                    "format": format,
                    "manifest": manifest,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  knowledge.get_boot_context 
        elif action == "knowledge.get_boot_context":
            # Gera contexto compacto para incio de sesso
            try:
                cfg = _config()
                base_path = Path(cfg.base_path) if cfg else Path(".")
                boot_context = f"""# NeoCortex Boot Context [2026-04-12]
                
## Estrutura do Projeto
- Framework: {base_path.name}
- Tools MCP: ~25 ferramentas NC-TOOL-FR-*
- Lobos ativos: NC-LBE-FR-ARCHITECTURE-001, SECURITY-001, etc.

## Tickets Ativos (Fase 3)
- FR-021 neocortex_memory (pendente)
- FR-022 neocortex_session (pendente)
- FR-023 neocortex_orchestration (pendente)
- FR-024 neocortex_governance (pendente)
- FR-025 neocortex_system ( DONE)
- FR-026 neocortex_intelligence ( DONE)
- FR-027 neocortex_knowledge (este)

## Comandos teis
- Use neocortex_search para buscar em lobes
- Use neocortex_system para diagnstico
- Use neocortex_intelligence para planejamento

## Regras de Nomenclatura
- Prefixo NC- obrigatrio
- Use logger em vez de print()
- Use get_config() para paths

Gerado automaticamente por neocortex_knowledge.get_boot_context"""
                return {
                    "success": True,
                    "action": action,
                    "boot_context": boot_context,
                    "length": len(boot_context),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  knowledge.update_index 
        elif action == "knowledge.update_index":
            lobe_service = _get_lobe_service()
            if lobe_service is None:
                return {"success": False, "error": "LobeService no disponvel."}
            try:
                # Fora reindexao de todos os lobes
                result = lobe_service.reindex_all()
                return {
                    "success": True,
                    "action": action,
                    "reindexed_lobes": result.get("reindexed", []),
                    "count": result.get("count", 0),
                    "message": "Reindexao forada concluda.",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  ao desconhecida 
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "knowledge.search",
                    "knowledge.get_documents",
                    "knowledge.project_manifest",
                    "knowledge.get_boot_context",
                    "knowledge.update_index",
                ],
            }
