#!/usr/bin/env python3
"""
Export Service - Business logic for data export operations.

This service encapsulates business logic for exporting data,
using repository interfaces for storage abstraction.
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository, CortexRepository, LobeRepository


class ExportService:
    """Service for data export business logic."""

    def __init__(
        self,
        ledger_repository: Optional[LedgerRepository] = None,
        cortex_repository: Optional[CortexRepository] = None,
        lobe_repository: Optional[LobeRepository] = None,
    ):
        """
        Initialize export service.

        Args:
            ledger_repository: Ledger repository implementation
            cortex_repository: Cortex repository implementation
            lobe_repository: Lobe repository implementation
        """
        if ledger_repository is None:
            from ..infra.ledger_store import LedgerStore

            self.ledger_repository = LedgerStore()
        else:
            self.ledger_repository = ledger_repository

        if cortex_repository is None:
            from ..repositories import FileSystemCortexRepository

            self.cortex_repository = FileSystemCortexRepository()
        else:
            self.cortex_repository = cortex_repository

        if lobe_repository is None:
            from ..repositories import FileSystemLobeRepository

            self.lobe_repository = FileSystemLobeRepository()
        else:
            self.lobe_repository = lobe_repository

    def export_to_markdown(
        self, include_lobes: bool = True, include_timeline: bool = True
    ) -> Dict[str, Any]:
        """
        Export system state to markdown format.

        Args:
            include_lobes: Whether to include lobe information
            include_timeline: Whether to include timeline events

        Returns:
            Dictionary with markdown export
        """
        ledger = self.ledger_repository.read_ledger()
        cortex_content = self.cortex_repository.read_cortex()

        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract project identity
        project_identity = ledger.get("project_identity", {})
        project_name = project_identity.get("name", "Unknown Project")

        # Extract session metrics
        session_metrics = ledger.get("session_metrics", {})
        total_interactions = session_metrics.get("total_interactions", 0)
        files_created = session_metrics.get("files_created", 0)
        problems_solved = session_metrics.get("problems_solved", 0)

        # Extract memory cortex
        memory_cortex = ledger.get("memory_cortex", {})
        active_lobes = memory_cortex.get("active_lobes", [])

        # Build markdown content
        markdown_lines = [
            f"# NeoCortex Export - {project_name}",
            f"",
            f"**Export Date:** {current_time}",
            f"**NeoCortex Version:** {ledger.get('neocortex_version', 'Unknown')}",
            f"",
            f"## Project Overview",
            f"- **System Type:** {ledger.get('system_type', 'Unknown')}",
            f"- **Architecture:** {ledger.get('architecture', 'Unknown')}",
            f"",
            f"## Session Metrics",
            f"- **Total Interactions:** {total_interactions}",
            f"- **Files Created:** {files_created}",
            f"- **Problems Solved:** {problems_solved}",
            f"",
            f"## System Constraints",
        ]

        # Add system constraints
        system_constraints = ledger.get("system_constraints", {})
        for key, value in system_constraints.items():
            if key != "last_modified":
                markdown_lines.append(f"- **{key}:** {value}")

        if include_lobes and active_lobes:
            markdown_lines.extend(
                [
                    f"",
                    f"## Active Lobes",
                ]
            )
            for lobe in active_lobes:
                markdown_lines.append(f"- {lobe}")

        if include_timeline:
            timeline = ledger.get("session_timeline", [])
            if timeline:
                markdown_lines.extend(
                    [
                        f"",
                        f"## Recent Timeline Events",
                    ]
                )
                # Show last 10 events
                for event in timeline[-10:]:
                    timestamp = event.get("timestamp", "Unknown time")
                    event_type = event.get("event", "Unknown event")
                    description = event.get("description", "")
                    markdown_lines.append(
                        f"- **{timestamp}** - {event_type}: {description}"
                    )

        # Add cortex summary
        if cortex_content:
            cortex_lines = cortex_content.split("\n")
            cortex_size = len(cortex_content)
            cortex_line_count = len(cortex_lines)

            markdown_lines.extend(
                [
                    f"",
                    f"## Cortex Summary",
                    f"- **Size:** {cortex_size} characters",
                    f"- **Lines:** {cortex_line_count}",
                    f"- **Has Aliases:** {'$' in cortex_content}",
                    f"- **Has Commands:** {'!' in cortex_content}",
                ]
            )

        # Add action queue summary
        action_queue = ledger.get("action_queue", {})
        if action_queue:
            pending = len(action_queue.get("pending", []))
            in_progress = len(action_queue.get("in_progress", []))
            completed = len(action_queue.get("completed", []))

            markdown_lines.extend(
                [
                    f"",
                    f"## Action Queue Summary",
                    f"- **Pending:** {pending} tasks",
                    f"- **In Progress:** {in_progress} tasks",
                    f"- **Completed:** {completed} tasks",
                ]
            )

        markdown_content = "\n".join(markdown_lines)

        return {
            "success": True,
            "format": "markdown",
            "content": markdown_content,
            "metadata": {
                "export_time": current_time,
                "project_name": project_name,
                "total_interactions": total_interactions,
                "active_lobes_count": len(active_lobes),
                "timeline_events_count": len(ledger.get("session_timeline", [])),
                "content_size": len(markdown_content),
            },
        }

    def export_to_json(self, pretty: bool = True) -> Dict[str, Any]:
        """
        Export system state to JSON format.

        Args:
            pretty: Whether to format JSON with indentation

        Returns:
            Dictionary with JSON export
        """
        ledger = self.ledger_repository.read_ledger()

        # Add export metadata
        export_data = {
            "export": {
                "timestamp": datetime.now().isoformat(),
                "format": "json",
                "version": "1.0",
            },
            "ledger": ledger,
            "summary": {
                "project_name": ledger.get("project_identity", {}).get(
                    "name", "Unknown"
                ),
                "neocortex_version": ledger.get("neocortex_version", "Unknown"),
                "system_type": ledger.get("system_type", "Unknown"),
                "session_metrics": ledger.get("session_metrics", {}),
                "active_lobes": ledger.get("memory_cortex", {}).get("active_lobes", []),
                "timeline_events": len(ledger.get("session_timeline", [])),
            },
        }

        # Convert to JSON
        if pretty:
            json_content = json.dumps(
                export_data, indent=2, ensure_ascii=False, default=str
            )
        else:
            json_content = json.dumps(export_data, ensure_ascii=False, default=str)

        return {
            "success": True,
            "format": "json",
            "content": json_content,
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "data_size_bytes": len(json_content),
                "pretty_print": pretty,
            },
        }

    def export_to_graph(self, graph_type: str = "dependency") -> Dict[str, Any]:
        """
        Export to graph format (e.g., for visualization).

        Args:
            graph_type: Type of graph ("dependency", "timeline", "knowledge")

        Returns:
            Dictionary with graph export
        """
        ledger = self.ledger_repository.read_ledger()
        cortex_content = self.cortex_repository.read_cortex()

        # Build graph based on type
        if graph_type == "dependency":
            graph = self._build_dependency_graph(ledger, cortex_content)
        elif graph_type == "timeline":
            graph = self._build_timeline_graph(ledger)
        elif graph_type == "knowledge":
            graph = self._build_knowledge_graph(ledger, cortex_content)
        else:
            return {
                "success": False,
                "error": f"Unknown graph type: {graph_type}. Available: dependency, timeline, knowledge",
            }

        return {
            "success": True,
            "format": "graph",
            "graph_type": graph_type,
            "content": graph,
            "metadata": {
                "export_time": datetime.now().isoformat(),
                "nodes_count": len(graph.get("nodes", [])),
                "edges_count": len(graph.get("edges", [])),
                "graph_type": graph_type,
            },
        }

    def export_lobes_to_markdown(
        self, lobe_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Export specific lobes to markdown format.

        Args:
            lobe_names: List of lobe names to export (None = all)

        Returns:
            Dictionary with lobe export
        """
        if lobe_names is None:
            lobe_names = self.lobe_repository.list_lobes()

        exported_lobes = []
        failed_lobes = []

        for lobe_name in lobe_names:
            content = self.lobe_repository.read_lobe(lobe_name)
            if content:
                exported_lobes.append(
                    {
                        "name": lobe_name,
                        "content": content,
                        "size_chars": len(content),
                        "lines": content.count("\n") + 1,
                    }
                )
            else:
                failed_lobes.append(lobe_name)

        # Build combined markdown
        markdown_lines = [
            f"# Lobe Export",
            f"**Export Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Lobes:** {len(exported_lobes)}",
            f"",
        ]

        for lobe_data in exported_lobes:
            markdown_lines.extend(
                [
                    f"---",
                    f"## {lobe_data['name']}",
                    f"**Size:** {lobe_data['size_chars']} chars, {lobe_data['lines']} lines",
                    f"",
                    lobe_data["content"],
                    f"",
                ]
            )

        markdown_content = "\n".join(markdown_lines)

        return {
            "success": True,
            "format": "markdown",
            "content": markdown_content,
            "lobes_exported": len(exported_lobes),
            "lobes_failed": len(failed_lobes),
            "failed_lobe_names": failed_lobes,
            "total_size_chars": len(markdown_content),
        }

    def _build_dependency_graph(
        self, ledger: Dict[str, Any], cortex_content: str
    ) -> Dict[str, Any]:
        """Build dependency graph from system state."""
        nodes = []
        edges = []

        # Add project node
        project_name = ledger.get("project_identity", {}).get("name", "Project")
        nodes.append(
            {"id": "project", "label": project_name, "type": "project", "size": 50}
        )

        # Add lobe nodes
        active_lobes = ledger.get("memory_cortex", {}).get("active_lobes", [])
        for i, lobe in enumerate(active_lobes):
            nodes.append({"id": f"lobe_{i}", "label": lobe, "type": "lobe", "size": 30})
            edges.append(
                {
                    "source": "project",
                    "target": f"lobe_{i}",
                    "type": "contains",
                    "label": "contains",
                }
            )

        # Add checkpoint nodes
        memory_cortex = ledger.get("memory_cortex", {})
        global_index = memory_cortex.get("global_checkpoint_index", {})
        checkpoints = global_index.get("checkpoints", [])

        for i, checkpoint in enumerate(checkpoints):
            nodes.append(
                {
                    "id": f"checkpoint_{i}",
                    "label": checkpoint,
                    "type": "checkpoint",
                    "size": 20,
                }
            )
            # Connect to first lobe (simplified)
            if active_lobes:
                edges.append(
                    {
                        "source": f"lobe_{0}",
                        "target": f"checkpoint_{i}",
                        "type": "has_checkpoint",
                        "label": "has",
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "lobe_count": len(active_lobes),
                "checkpoint_count": len(checkpoints),
            },
        }

    def _build_timeline_graph(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Build timeline graph from session timeline."""
        nodes = []
        edges = []

        timeline = ledger.get("session_timeline", [])

        for i, event in enumerate(timeline):
            event_id = f"event_{i}"
            nodes.append(
                {
                    "id": event_id,
                    "label": event.get("event", f"Event {i}"),
                    "type": "event",
                    "timestamp": event.get("timestamp", ""),
                    "description": event.get("description", ""),
                    "size": 15,
                }
            )

            # Connect to previous event
            if i > 0:
                edges.append(
                    {
                        "source": f"event_{i - 1}",
                        "target": event_id,
                        "type": "follows",
                        "label": "follows",
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_events": len(timeline),
                "time_range": f"{timeline[0].get('timestamp')} to {timeline[-1].get('timestamp')}"
                if timeline
                else "No events",
            },
        }

    def _build_knowledge_graph(
        self, ledger: Dict[str, Any], cortex_content: str
    ) -> Dict[str, Any]:
        """Build knowledge graph from cortex content."""
        nodes = []
        edges = []

        # Extract concepts from cortex (simplified)
        if cortex_content:
            # Look for patterns in cortex
            lines = cortex_content.split("\n")

            # Add cortex node
            nodes.append(
                {
                    "id": "cortex",
                    "label": "Central Cortex",
                    "type": "cortex",
                    "size": 40,
                }
            )

            # Extract aliases (simplified)
            import re

            alias_pattern = r"\$(\w+)"
            aliases = re.findall(alias_pattern, cortex_content)

            for i, alias in enumerate(set(aliases)):
                nodes.append(
                    {
                        "id": f"alias_{i}",
                        "label": f"${alias}",
                        "type": "alias",
                        "size": 20,
                    }
                )
                edges.append(
                    {
                        "source": "cortex",
                        "target": f"alias_{i}",
                        "type": "defines",
                        "label": "defines",
                    }
                )

            # Extract commands
            command_pattern = r"!(\w+)"
            commands = re.findall(command_pattern, cortex_content)

            for i, command in enumerate(set(commands)):
                nodes.append(
                    {
                        "id": f"command_{i}",
                        "label": f"!{command}",
                        "type": "command",
                        "size": 20,
                    }
                )
                edges.append(
                    {
                        "source": "cortex",
                        "target": f"command_{i}",
                        "type": "defines",
                        "label": "defines",
                    }
                )

        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_concepts": len(nodes),
                "aliases_found": len([n for n in nodes if n["type"] == "alias"]),
                "commands_found": len([n for n in nodes if n["type"] == "command"]),
            },
        }


# Singleton instance for convenience
_default_export_service = None


def get_export_service(
    ledger_repository: Optional[LedgerRepository] = None,
    cortex_repository: Optional[CortexRepository] = None,
    lobe_repository: Optional[LobeRepository] = None,
) -> ExportService:
    """
    Get export service instance (singleton pattern).

    Args:
        ledger_repository: Optional ledger repository implementation
        cortex_repository: Optional cortex repository implementation
        lobe_repository: Optional lobe repository implementation

    Returns:
        ExportService instance
    """
    global _default_export_service

    if (
        ledger_repository is not None
        or cortex_repository is not None
        or lobe_repository is not None
    ):
        return ExportService(ledger_repository, cortex_repository, lobe_repository)

    if _default_export_service is None:
        _default_export_service = ExportService()

    return _default_export_service
