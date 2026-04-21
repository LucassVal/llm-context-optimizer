"""
NC-TOOL-FR-028-export.py
FR-028  MCP Tool: neocortex_export

Exportao de dados do sistema NeoCortex em mltiplos formatos.
Absorve: NC-TOOL-FR-006-export.py (arquivar aps ativao)

Aes disponveis:
  to_markdown         estado completo em Markdown
  to_json             estado completo em JSON (pretty ou minificado)
  to_graph            grafo de dependncias (mermaid, dot, json)
  export_lobes        todos os lobes exportados em Markdown
  export_ssot         snapshot SSOT (NC-NAM-FR-001 + @ROADMAP) para backup
  export_docker_compose  gera docker-compose.yml com 7 servios/portas
  export_readme       gera README.md a partir do manifesto NC-MAN-FR-001
  export_obsidian     exporta lobes em formato Obsidian vault
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def _export_svc():
    try:
        from neocortex.core import get_export_service
        return get_export_service()
    except Exception as e:
        logger.warning(f"[export_tool] ExportService indisponvel: {e}")
        return None


def _config():
    try:
        from neocortex.config import get_config
        return get_config()
    except Exception:
        return None


DOCKER_COMPOSE_TEMPLATE = """\
# NeoCortex Docker Compose  gerado em {date}
# SAND-001: Instncia dev isolada na porta 8766
version: "3.9"

services:
  neocortex-mcp:
    build: .
    ports: ["8765:8765"]
    environment:
      - NEOCORTEX_ENV=production
      - PYTHONUTF8=1
    volumes:
      - ./01_neocortex_framework:/app
      - neocortex_data:/app/.neocortex

  neocortex-dev:
    build: .
    ports: ["8766:8766"]
    environment:
      - NEOCORTEX_ENV=development
      - PYTHONUTF8=1
    volumes:
      - ./01_neocortex_framework:/app
      - neocortex_dev_data:/app/.neocortex_dev

  neocortex-a2a-gateway:
    image: nginx:alpine
    ports: ["8767:80"]
    profiles: ["a2a"]

  neocortex-courier:
    image: ollama/ollama:latest
    ports: ["8768:11434"]
    profiles: ["workers"]

  neocortex-engineer:
    image: ollama/ollama:latest
    ports: ["8769:11434"]
    profiles: ["workers"]

  neocortex-web:
    build:
      context: .
      dockerfile: Dockerfile.web
    ports: ["8770:8000"]
    profiles: ["web"]

volumes:
  neocortex_data:
  neocortex_dev_data:
"""

README_TEMPLATE = """\
# NeoCortex MCP Framework

> Autonomous AI orchestration framework with multi-agent support, token economy, and governance.

## Quick Start

```bash
pip install neocortex-mcp
neocortex-server
```

Or clone and run locally:
```bash
git clone https://github.com/your-org/neocortex-mcp.git
cd neocortex-mcp
python -m neocortex.mcp.server
```

## Architecture

- **T0**: Orchestrator (DeepSeek-chat / Claude)
- **T1**: Sub-agents (DeepSeek-chat, cheap tasks)
- **T2**: Courier (Qwen 1.5B local, bulk work)
- **T3**: Engineer (Qwen 3B local, code)

## Tools ({tool_count} available)

{tool_list}

## Ports

| Port | Service |
|------|---------|
| 8765 | MCP Server (main) |
| 8766 | Dev instance |
| 8767 | A2A Gateway |
| 8768 | Courier agent |
| 8769 | Engineer agent |
| 8770 | Web panel |

## License

MIT  White-label ready. Fork and customize.
"""


def register_tool(mcp) -> None:
    """Registra neocortex_export no servidor MCP."""

    @mcp.tool(name="neocortex_export")
    def neocortex_export(
        action: str,
        format: str = "markdown",
        output_path: str = "",
    ) -> Dict[str, Any]:
        """
        Exportao de dados do NeoCortex em mltiplos formatos.

        Aes disponveis:
          to_markdown         estado completo em Markdown
          to_json             estado completo em JSON (pretty | minified)
          to_graph            grafo de dependncias (mermaid | dot | json)
          export_lobes        todos os lobes exportados em Markdown
          export_ssot         snapshot dos arquivos SSOT para backup
          export_docker_compose  gera docker-compose.yml com 7 servios
          export_readme       gera README.md a partir do manifesto
          export_obsidian     exporta lobes em formato Obsidian vault

        Args:
            action:      Ao desejada
            format:      Formato de sada (varia por ao)
            output_path: Caminho de sada (opcional  se vazio, retorna inline)
        """
        svc = _export_svc()
        cfg = _config()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        #  to_markdown 
        if action == "to_markdown":
            if svc is None:
                return {"success": False, "error": "ExportService indisponvel."}
            result = svc.export_to_markdown(include_lobes=True, include_timeline=True)
            return result

        #  to_json 
        elif action == "to_json":
            if svc is None:
                return {"success": False, "error": "ExportService indisponvel."}
            pretty = format.lower() == "pretty"
            result = svc.export_to_json(pretty=pretty)
            return result

        #  to_graph 
        elif action == "to_graph":
            if svc is None:
                return {"success": False, "error": "ExportService indisponvel."}
            result = svc.export_to_graph(graph_type=format or "mermaid")
            return result

        #  export_lobes 
        elif action == "export_lobes":
            if svc is None:
                return {"success": False, "error": "ExportService indisponvel."}
            result = svc.export_lobes_to_markdown()
            return result

        #  export_ssot 
        elif action == "export_ssot":
            ssot_files = []
            if cfg:
                try:
                    base = Path(cfg.base_path)
                    docs_dir = base / "DIR-DOC-FR-001-docs-main"
                    ssot_files = [
                        {"file": f.name, "size_bytes": f.stat().st_size, "path": str(f)}
                        for f in docs_dir.glob("NC-*.md") if f.is_file()
                    ] + [
                        {"file": f.name, "size_bytes": f.stat().st_size, "path": str(f)}
                        for f in docs_dir.glob("NC-*.yaml") if f.is_file()
                    ]
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {
                "success": True,
                "action": action,
                "timestamp": ts,
                "ssot_files": sorted(ssot_files, key=lambda x: x["file"]),
                "count": len(ssot_files),
            }

        #  export_docker_compose 
        elif action == "export_docker_compose":
            content = DOCKER_COMPOSE_TEMPLATE.format(date=ts)
            if output_path:
                try:
                    Path(output_path).write_text(content, encoding="utf-8")
                    return {"success": True, "action": action, "written_to": output_path, "bytes": len(content)}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": True, "action": action, "content": content, "bytes": len(content)}

        #  export_readme 
        elif action == "export_readme":
            tools_dir = Path(__file__).parent
            tool_files = sorted(tools_dir.glob("NC-TOOL-FR-*.py"))
            tool_list = "\n".join(f"- `{f.stem.split('-')[-1]}`" for f in tool_files)
            content = README_TEMPLATE.format(
                tool_count=len(tool_files),
                tool_list=tool_list if tool_list else "- (run server to enumerate)",
            )
            if output_path:
                try:
                    Path(output_path).write_text(content, encoding="utf-8")
                    return {"success": True, "action": action, "written_to": output_path}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": True, "action": action, "content": content, "chars": len(content)}

        #  export_obsidian 
        elif action == "export_obsidian":
            if svc is None:
                return {"success": False, "error": "ExportService indisponvel."}
            try:
                result = svc.export_lobes_to_markdown()
                # Obsidian vault format: adiciona frontmatter YAML a cada lobe
                obsidian_notes = []
                for lobe_name, content in result.get("lobes", {}).items():
                    note = f"---\ntags: [neocortex, lobe]\ncreated: {ts}\n---\n\n{content}"
                    obsidian_notes.append({"lobe": lobe_name, "content": note})
                return {
                    "success": True,
                    "action": action,
                    "notes_count": len(obsidian_notes),
                    "notes": obsidian_notes,
                    "tip": "Copie cada 'content' para um arquivo .md no seu Obsidian vault.",
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        #  ao desconhecida 
        else:
            return {
                "success": False,
                "error": f"Ao desconhecida: '{action}'.",
                "available": [
                    "to_markdown", "to_json", "to_graph",
                    "export_lobes", "export_ssot",
                    "export_docker_compose", "export_readme", "export_obsidian",
                ],
            }
