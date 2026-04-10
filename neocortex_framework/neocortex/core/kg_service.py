#!/usr/bin/env python3
"""
Knowledge Graph Service - Business logic for knowledge graph operations.

This service encapsulates business logic for knowledge graph operations,
using repository interfaces for storage abstraction.
"""

import json
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class KGService:
    """Service for knowledge graph business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize KG service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def _ensure_kg_structure(self, ledger: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure knowledge graph structure exists in memory_cortex."""
        memory_cortex = ledger.get("memory_cortex", {})
        if "knowledge_graph" not in memory_cortex:
            memory_cortex["knowledge_graph"] = {
                "entities": {},
                "relations": [],
                "entity_types": [
                    "lobe",
                    "cortex",
                    "file",
                    "directory",
                    "command",
                    "pattern",
                    "concept",
                ],
            }
            ledger["memory_cortex"] = memory_cortex
        return ledger

    def add_entity(self, entity: str, entity_type: str = "concept") -> Dict[str, Any]:
        """
        Add an entity to the knowledge graph.

        Args:
            entity: Entity ID
            entity_type: Type of entity (default: "concept")

        Returns:
            Operation result dictionary
        """
        if not entity:
            return {"success": False, "error": "entity is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})

        # Check if entity already exists
        if entity in entities:
            return {
                "success": True,
                "entity": entity,
                "message": f"Entity '{entity}' already exists in KG",
                "existing": True,
            }

        # Create new entity
        new_entity = {
            "id": entity,
            "type": entity_type,
            "created_at": "auto_generated",
            "last_accessed": "auto_generated",
            "relations_count": 0,
            "metadata": {},
        }

        entities[entity] = new_entity
        kg["entities"] = entities
        ledger["memory_cortex"]["knowledge_graph"] = kg

        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "entity": new_entity,
            "message": f"Entity '{entity}' added to KG",
        }

    def add_relation(
        self, source: str, relation: str, target: str, metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Add a relation between entities.

        Args:
            source: Source entity ID
            relation: Relation type
            target: Target entity ID
            metadata: Optional relation metadata

        Returns:
            Operation result dictionary
        """
        if not source or not relation or not target:
            return {
                "success": False,
                "error": "source, relation and target are required",
            }

        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})
        relations = kg.get("relations", [])

        # Check if entities exist
        if source not in entities:
            return {
                "success": False,
                "error": f"Source entity not found: {source}",
            }
        if target not in entities:
            return {
                "success": False,
                "error": f"Target entity not found: {target}",
            }

        # Create new relation
        new_relation = {
            "source": source,
            "relation": relation,
            "target": target,
            "created_at": "auto_generated",
            "metadata": metadata or {},
        }

        # Add to relations list
        relations.append(new_relation)

        # Update relation counts in entities
        entities[source]["relations_count"] = (
            entities[source].get("relations_count", 0) + 1
        )
        entities[target]["relations_count"] = (
            entities[target].get("relations_count", 0) + 1
        )

        kg["relations"] = relations
        kg["entities"] = entities
        ledger["memory_cortex"]["knowledge_graph"] = kg

        self.repository.write_ledger(ledger)

        return {
            "success": True,
            "relation": new_relation,
            "message": f"Relation '{source} {relation} {target}' added to KG",
        }

    def query_relations(self, entity: str) -> Dict[str, Any]:
        """
        Query all relations involving an entity.

        Args:
            entity: Entity ID to query

        Returns:
            Dictionary with relations information
        """
        if not entity:
            return {"success": False, "error": "entity is required"}

        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})
        relations = kg.get("relations", [])

        if entity not in entities:
            return {"success": False, "error": f"Entity not found: {entity}"}

        # Find all relations involving the entity
        entity_relations = []
        for rel in relations:
            if rel["source"] == entity or rel["target"] == entity:
                entity_relations.append(rel)

        # Classify by direction
        outgoing = [r for r in entity_relations if r["source"] == entity]
        incoming = [r for r in entity_relations if r["target"] == entity]

        return {
            "success": True,
            "entity": entity,
            "entity_info": entities[entity],
            "outgoing_relations": outgoing,
            "incoming_relations": incoming,
            "total_relations": len(entity_relations),
        }

    def find_similar(self, entity: str = "") -> Dict[str, Any]:
        """
        Find entities similar to a given entity.

        Args:
            entity: Entity ID to find similar entities for.
                   If empty, returns most connected entities.

        Returns:
            Dictionary with similar entities
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})
        relations = kg.get("relations", [])

        if not entity:
            # Return most connected entities
            sorted_entities = sorted(
                entities.items(),
                key=lambda x: x[1].get("relations_count", 0),
                reverse=True,
            )
            top_entities = [{"id": e[0], **e[1]} for e in sorted_entities[:5]]

            return {
                "success": True,
                "similar_to": "none (most connected entities)",
                "results": top_entities,
                "count": len(top_entities),
            }

        if entity not in entities:
            return {"success": False, "error": f"Entity not found: {entity}"}

        # Find entities related (first degree)
        related_entities = set()
        for rel in relations:
            if rel["source"] == entity:
                related_entities.add(rel["target"])
            elif rel["target"] == entity:
                related_entities.add(rel["source"])

        # Convert to list with information
        similar = []
        for ent_id in related_entities:
            if ent_id in entities:
                similar.append({"id": ent_id, **entities[ent_id]})

        return {
            "success": True,
            "similar_to": entity,
            "results": similar,
            "count": len(similar),
        }

    def visualize(self) -> Dict[str, Any]:
        """
        Generate visualization of the knowledge graph.

        Returns:
            Dictionary with DOT format content and statistics
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})
        relations = kg.get("relations", [])

        # Generate DOT representation
        dot_lines = ["digraph NeoCortexKG {"]
        dot_lines.append("  rankdir=LR;")
        dot_lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")

        # Add nodes (entities)
        for ent_id, ent_data in entities.items():
            label = f"{ent_id}\\n({ent_data.get('type', 'concept')})"
            dot_lines.append(f'  "{ent_id}" [label="{label}"];')

        # Add edges (relations)
        for rel in relations:
            dot_lines.append(
                f'  "{rel["source"]}" -> "{rel["target"]}" [label="{rel["relation"]}"];'
            )

        dot_lines.append("}")
        dot_content = "\n".join(dot_lines)

        # Calculate statistics
        most_connected = max(
            [(e, d.get("relations_count", 0)) for e, d in entities.items()],
            key=lambda x: x[1],
            default=("none", 0),
        )[0]

        return {
            "success": True,
            "format": "dot",
            "dot_content": dot_content,
            "stats": {
                "total_entities": len(entities),
                "total_relations": len(relations),
                "most_connected": most_connected,
            },
            "message": "KG graph exported in DOT format. Use Graphviz to visualize.",
        }

    def get_stats(self) -> Dict[str, Any]:
        """
        Get knowledge graph statistics.

        Returns:
            Dictionary with KG statistics
        """
        ledger = self.repository.read_ledger()
        ledger = self._ensure_kg_structure(ledger)

        kg = ledger["memory_cortex"]["knowledge_graph"]
        entities = kg.get("entities", {})
        relations = kg.get("relations", [])

        # Calculate entity type distribution
        type_distribution = {}
        for ent_data in entities.values():
            ent_type = ent_data.get("type", "unknown")
            type_distribution[ent_type] = type_distribution.get(ent_type, 0) + 1

        # Calculate relation type distribution
        relation_distribution = {}
        for rel in relations:
            rel_type = rel.get("relation", "unknown")
            relation_distribution[rel_type] = relation_distribution.get(rel_type, 0) + 1

        return {
            "success": True,
            "total_entities": len(entities),
            "total_relations": len(relations),
            "entity_type_distribution": type_distribution,
            "relation_type_distribution": relation_distribution,
            "avg_relations_per_entity": len(relations) / len(entities)
            if entities
            else 0,
        }


# Singleton instance for convenience
_default_kg_service = None


def get_kg_service(repository: Optional[LedgerRepository] = None) -> KGService:
    """
    Get KG service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        KGService instance
    """
    global _default_kg_service

    if repository is not None:
        return KGService(repository)

    if _default_kg_service is None:
        _default_kg_service = KGService()

    return _default_kg_service
