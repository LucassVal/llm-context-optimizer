#!/usr/bin/env python3
"""
Config Service - Business logic for system configuration.

This service encapsulates business logic for system configuration,
using repository interfaces for storage abstraction.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from ..repositories import LedgerRepository


class ConfigService:
    """Service for system configuration business logic."""

    def __init__(self, repository: Optional[LedgerRepository] = None):
        """
        Initialize config service.

        Args:
            repository: Ledger repository implementation (filesystem, hub, etc.)
                       If None, uses default FileSystemLedgerRepository.
        """
        if repository is None:
            from ..repositories import FileSystemLedgerRepository

            self.repository = FileSystemLedgerRepository()
        else:
            self.repository = repository

    def get_system_config(self) -> Dict[str, Any]:
        """
        Get full system configuration from ledger.

        Returns:
            Dictionary with system configuration
        """
        ledger = self.repository.read_ledger()

        # Extract configuration sections
        agent_session = ledger.get("agent_session", {})
        system_constraints = ledger.get("system_constraints", {})
        memory_cortex = ledger.get("memory_cortex", {})
        hierarchical_validation = ledger.get("hierarchical_validation", {})

        config = {
            "agent_session": agent_session,
            "system_constraints": system_constraints,
            "memory_cortex": {
                "has_memory_cortex": bool(memory_cortex),
                "active_lobes": memory_cortex.get("active_lobes", []),
                "has_synapses": "synapses" in memory_cortex,
            },
            "hierarchical_validation": {
                "has_validation": bool(hierarchical_validation),
                "has_regression_buffer": "regression_buffer" in hierarchical_validation,
            },
            "ledger_metadata": {
                "neocortex_version": ledger.get("neocortex_version", "unknown"),
                "system_type": ledger.get("system_type", "unknown"),
                "architecture": ledger.get("architecture", "unknown"),
                "last_modified": ledger.get("last_modified", "unknown"),
            },
        }

        return {
            "success": True,
            "config": config,
            "summary": {
                "model": agent_session.get("model_id", "unknown"),
                "mode": agent_session.get("mode", "single_agent"),
                "platform": agent_session.get("platform", "unknown"),
                "max_context_depth": system_constraints.get(
                    "max_context_depth", "unknown"
                ),
                "hot_context_limit": system_constraints.get(
                    "hot_context_limit", "unknown"
                ),
            },
        }

    def set_model(self, model_id: str) -> Dict[str, Any]:
        """
        Set LLM model in agent session.

        Args:
            model_id: Model ID (e.g., "deepseek-reasoner", "gpt-4")

        Returns:
            Dictionary with operation result
        """
        if not model_id:
            return {"success": False, "error": "model_id is required"}

        ledger = self.repository.read_ledger()

        # Ensure agent_session structure exists
        if "agent_session" not in ledger:
            ledger["agent_session"] = {}

        agent_session = ledger["agent_session"]
        previous_model = agent_session.get("model_id", "unknown")

        # Update model
        agent_session["model_id"] = model_id
        agent_session["model_changed_at"] = datetime.now().isoformat()
        agent_session["previous_model"] = previous_model

        ledger["agent_session"] = agent_session

        # Add to timeline
        if "session_timeline" not in ledger:
            ledger["session_timeline"] = []

        timeline = ledger["session_timeline"]
        timeline.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "model_changed",
                "previous_model": previous_model,
                "new_model": model_id,
                "description": f"Model changed from {previous_model} to {model_id}",
            }
        )
        ledger["session_timeline"] = timeline

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "model_set": model_id,
                "previous_model": previous_model,
                "message": f"Model set to: {model_id}",
                "timestamp": datetime.now().isoformat(),
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def list_available_models(self) -> Dict[str, Any]:
        """
        List available LLM models.

        Returns:
            Dictionary with available models and metadata
        """
        # Define available models with metadata
        models = [
            {
                "id": "deepseek-reasoner",
                "name": "DeepSeek Reasoner",
                "provider": "DeepSeek",
                "context_window": 128000,
                "capabilities": ["reasoning", "code", "planning"],
                "recommended": True,
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "context_window": 128000,
                "capabilities": ["general", "code", "creativity"],
                "recommended": False,
            },
            {
                "id": "claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "context_window": 200000,
                "capabilities": ["reasoning", "writing", "analysis"],
                "recommended": True,
            },
            {
                "id": "llama-3.1",
                "name": "Llama 3.1",
                "provider": "Meta",
                "context_window": 128000,
                "capabilities": ["general", "code", "multilingual"],
                "recommended": False,
            },
            {
                "id": "qwen2.5",
                "name": "Qwen 2.5",
                "provider": "Alibaba",
                "context_window": 128000,
                "capabilities": ["general", "code", "math"],
                "recommended": False,
            },
        ]

        # Get current model from ledger
        ledger = self.repository.read_ledger()
        current_model = ledger.get("agent_session", {}).get("model_id", "unknown")

        # Add current flag
        for model in models:
            model["current"] = model["id"] == current_model

        return {
            "success": True,
            "models": models,
            "total_models": len(models),
            "current_model": current_model,
            "recommended_models": [m for m in models if m["recommended"]],
        }

    def update_system_constraint(
        self, constraint_key: str, value: Any
    ) -> Dict[str, Any]:
        """
        Update a system constraint.

        Args:
            constraint_key: Constraint key (e.g., "max_context_depth")
            value: New value

        Returns:
            Dictionary with operation result
        """
        if not constraint_key:
            return {"success": False, "error": "constraint_key is required"}

        # Validate value based on constraint key
        if constraint_key in ["max_context_depth", "hot_context_limit"]:
            if not isinstance(value, int) or value <= 0:
                return {
                    "success": False,
                    "error": f"{constraint_key} must be a positive integer",
                }

        ledger = self.repository.read_ledger()

        # Ensure system_constraints structure exists
        if "system_constraints" not in ledger:
            ledger["system_constraints"] = {}

        system_constraints = ledger["system_constraints"]
        previous_value = system_constraints.get(constraint_key, "not_set")

        # Update constraint
        system_constraints[constraint_key] = value
        system_constraints["last_modified"] = datetime.now().isoformat()

        ledger["system_constraints"] = system_constraints

        # Add to timeline
        if "session_timeline" not in ledger:
            ledger["session_timeline"] = []

        timeline = ledger["session_timeline"]
        timeline.append(
            {
                "timestamp": datetime.now().isoformat(),
                "event": "constraint_updated",
                "constraint": constraint_key,
                "previous_value": previous_value,
                "new_value": value,
                "description": f"System constraint '{constraint_key}' updated from {previous_value} to {value}",
            }
        )
        ledger["session_timeline"] = timeline

        # Write back to ledger
        success = self.repository.write_ledger(ledger)

        if success:
            return {
                "success": True,
                "constraint": constraint_key,
                "previous_value": previous_value,
                "new_value": value,
                "message": f"Constraint '{constraint_key}' updated successfully",
            }
        else:
            return {"success": False, "error": "Failed to write to ledger"}

    def get_constraint_summary(self) -> Dict[str, Any]:
        """
        Get summary of all system constraints.

        Returns:
            Dictionary with constraints summary
        """
        ledger = self.repository.read_ledger()
        system_constraints = ledger.get("system_constraints", {})

        # Calculate constraint utilization (simplified)
        constraints = []
        for key, value in system_constraints.items():
            constraint = {
                "key": key,
                "value": value,
                "type": type(value).__name__,
                "description": self._get_constraint_description(key),
            }
            constraints.append(constraint)

        return {
            "success": True,
            "constraints": constraints,
            "total_constraints": len(constraints),
            "last_modified": system_constraints.get("last_modified", "unknown"),
            "has_constraints": bool(system_constraints),
        }

    def _get_constraint_description(self, constraint_key: str) -> str:
        """Get description for a constraint key."""
        descriptions = {
            "max_context_depth": "Maximum depth of context nesting",
            "hot_context_limit": "Maximum number of hot context entries",
            "token_budget": "Maximum token budget per interaction",
            "compaction_threshold": "Threshold for triggering compaction",
            "regression_buffer_size": "Maximum size of regression buffer",
        }
        return descriptions.get(constraint_key, "No description available")


# Singleton instance for convenience
_default_config_service = None


def get_config_service(repository: Optional[LedgerRepository] = None) -> ConfigService:
    """
    Get config service instance (singleton pattern).

    Args:
        repository: Optional repository implementation

    Returns:
        ConfigService instance
    """
    global _default_config_service

    if repository is not None:
        return ConfigService(repository)

    if _default_config_service is None:
        _default_config_service = ConfigService()

    return _default_config_service
