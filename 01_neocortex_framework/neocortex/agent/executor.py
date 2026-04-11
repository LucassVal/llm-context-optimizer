#!/usr/bin/env python3
"""
AgentExecutor - Executes agent tasks using hybrid LLM backends.

Integrates with LLMBackendFactory to route tasks to appropriate backends
based on role, configuration, and override settings.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime

from ..config import get_config
from ..infra.llm.factory import LLMBackendFactory
from ..infra.llm.backend import LLMRequest, LLMResponse, FallbackChain
from ..infra.metrics_store import create_metrics_store

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Agent task definition."""

    task_id: str
    role: str
    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentExecutor:
    """
    Executes agent tasks using configured LLM backends.

    Features:
    - Role-based backend selection
    - Backend override support
    - Fallback chain for reliability
    - Metrics and logging
    """

    def __init__(self, config_provider=None, metrics_store=None):
        """
        Initialize AgentExecutor.

        Args:
            config_provider: Config provider instance (default: get_config())
            metrics_store: MetricsStore instance for recording metrics (default: create new)
        """
        self.config = config_provider or get_config()
        self.llm_factory = LLMBackendFactory

        # Initialize metrics store
        if metrics_store is None:
            self.metrics = create_metrics_store()
        else:
            self.metrics = metrics_store

        # Cache for backend instances
        self._backend_cache = {}
        self._fallback_chain_cache = None

        # Statistics
        self.stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "backend_usage": {},
            "fallback_usage": 0,
        }

    def _get_role_backend_config(self, role: str) -> Dict[str, Any]:
        """
        Get backend configuration for a specific role.

        Looks up configuration in this order:
        1. Role-specific backend config (llm.agent_backends.<role>)
        2. Default agent backend config (llm.agent_backends.default)
        3. Global LLM config (llm)

        Args:
            role: Agent role

        Returns:
            Backend configuration dictionary
        """
        # Try role-specific config
        role_key = f"llm.agent_backends.{role}"
        role_config = self.config.get(role_key)
        if role_config:
            logger.debug(f"Found role-specific config for {role}")
            return role_config

        # Try default agent config
        default_config = self.config.get("llm.agent_backends.default")
        if default_config:
            logger.debug(f"Using default agent config for {role}")
            return default_config

        # Fall back to global LLM config
        logger.debug(f"Using global LLM config for {role}")
        return self.config.llm_config

    def _get_backend_for_role(
        self, role: str, backend_override: Optional[str] = None
    ) -> Union[FallbackChain, Any]:
        """
        Get backend instance for role, with optional override.

        Args:
            role: Agent role
            backend_override: Optional override backend name (e.g., "ollama", "deepseek")

        Returns:
            LLMBackend or FallbackChain instance
        """
        # Check cache key
        cache_key = f"{role}:{backend_override}"
        if cache_key in self._backend_cache:
            return self._backend_cache[cache_key]

        # Determine backend config
        if backend_override:
            # Use override with global LLM config as base
            base_config = self.config.llm_config.copy()
            base_config["provider"] = backend_override
            config = base_config
            logger.info(
                f"Using backend override '{backend_override}' for role '{role}'"
            )
        else:
            # Get role-specific config
            config = self._get_role_backend_config(role)

        # Check if config is a list (fallback chain)
        if isinstance(config, list):
            # Create fallback chain
            backend = self.llm_factory.create_fallback_chain(config)
            logger.debug(
                f"Created fallback chain with {len(config)} backends for role '{role}'"
            )
        else:
            # Single backend
            backend = self.llm_factory.create_from_config(config)
            logger.debug(
                f"Created backend '{backend.provider.value}' for role '{role}'"
            )

        # Cache the backend
        self._backend_cache[cache_key] = backend
        return backend

    async def execute_async(
        self, task: AgentTask, backend_override: Optional[str] = None
    ) -> LLMResponse:
        """
        Execute agent task asynchronously.

        Args:
            task: AgentTask with prompt and parameters
            backend_override: Optional backend name override

        Returns:
            LLMResponse with generated content
        """
        self.stats["total_tasks"] += 1

        # Get backend for role
        backend = self._get_backend_for_role(task.role, backend_override)

        # Track backend usage
        backend_name = backend.__class__.__name__
        self.stats["backend_usage"][backend_name] = (
            self.stats["backend_usage"].get(backend_name, 0) + 1
        )

        # Prepare LLM request
        request = LLMRequest(
            prompt=task.prompt,
            system_prompt=task.system_prompt,
            model=task.model,
            temperature=task.temperature,
            max_tokens=task.max_tokens,
            metadata={
                "task_id": task.task_id,
                "role": task.role,
                **task.metadata,
            },
        )

        try:
            # Execute with backend
            response = await backend.generate(request)

            # Track fallback usage if applicable
            if (
                isinstance(backend, FallbackChain)
                and backend.stats.get("fallback_used", 0) > 0
            ):
                self.stats["fallback_usage"] += 1

            self.stats["successful_tasks"] += 1
            logger.info(
                f"Task {task.task_id} completed successfully with {backend_name}"
            )

            # Record agent activity
            try:
                self.metrics.record_agent_activity(
                    agent_id=task.role,
                    action="task_completed",
                    details={
                        "task_id": task.task_id,
                        "backend": backend_name,
                        "model": task.model or "default",
                    },
                )
            except Exception as metric_e:
                logger.warning(f"Failed to record agent activity: {metric_e}")

            # Record token usage if available in response
            try:
                if hasattr(response, "tokens_used") and response.tokens_used:
                    # Extract token counts - response.tokens_used might be a dict or int
                    if isinstance(response.tokens_used, dict):
                        total_tokens = response.tokens_used.get("total", 0)
                        output_tokens = response.tokens_used.get("output", 0)
                        cache_hit = response.tokens_used.get("cache_hit", 0)
                        cache_miss = response.tokens_used.get("cache_miss", 0)
                    else:
                        total_tokens = response.tokens_used
                        output_tokens = response.tokens_used  # approximation
                        cache_hit = 0
                        cache_miss = total_tokens

                    self.metrics.record_token_usage(
                        date=datetime.now(),
                        model=task.model or backend_name,
                        agent=task.role,
                        cache_hit=cache_hit,
                        cache_miss=cache_miss,
                        output_tokens=output_tokens,
                        total_tokens=total_tokens,
                    )
            except Exception as token_e:
                logger.debug(f"Could not record token usage: {token_e}")

            return response

        except Exception as e:
            self.stats["failed_tasks"] += 1
            logger.error(f"Task {task.task_id} failed: {e}")

            # Record failed task activity
            try:
                self.metrics.record_agent_activity(
                    agent_id=task.role,
                    action="task_failed",
                    details={
                        "task_id": task.task_id,
                        "backend": backend_name,
                        "error": str(e),
                    },
                )
            except Exception as metric_e:
                logger.warning(f"Failed to record failed task activity: {metric_e}")

            raise

    def execute(
        self, task: AgentTask, backend_override: Optional[str] = None
    ) -> LLMResponse:
        """
        Execute agent task synchronously (convenience wrapper).

        Note: This uses asyncio.run() and should not be called from async contexts.

        Args:
            task: AgentTask with prompt and parameters
            backend_override: Optional backend name override

        Returns:
            LLMResponse with generated content
        """
        import asyncio

        return asyncio.run(self.execute_async(task, backend_override))

    def get_available_backends(self) -> List[str]:
        """
        Get list of available backend providers.

        Returns:
            List of provider names
        """
        return self.llm_factory.get_available_providers()

    def set_role_backend(self, role: str, backend_config: Dict[str, Any]) -> None:
        """
        Set backend configuration for a specific role.

        Args:
            role: Agent role
            backend_config: Backend configuration dictionary
        """
        key = f"llm.agent_backends.{role}"
        self.config.set(key, backend_config)
        logger.info(f"Set backend config for role '{role}'")

        # Clear cache for this role
        keys_to_clear = [
            k for k in self._backend_cache.keys() if k.startswith(f"{role}:")
        ]
        for key in keys_to_clear:
            del self._backend_cache[key]

    def clear_cache(self) -> None:
        """Clear backend cache."""
        self._backend_cache.clear()
        logger.debug("Cleared backend cache")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get executor statistics.

        Returns:
            Dictionary with execution statistics
        """
        stats = self.stats.copy()
        stats["cache_size"] = len(self._backend_cache)
        stats["available_backends"] = self.get_available_backends()

        # Add backend health info
        stats["backend_health"] = {}
        for backend in self._backend_cache.values():
            if hasattr(backend, "health_check"):
                stats["backend_health"][backend.__class__.__name__] = (
                    backend.health_check()
                )

        return stats

    def record_agent_spawn(self, agent_id: str, role: str, backend: str) -> bool:
        """
        Record agent spawn event.

        Args:
            agent_id: Unique agent identifier
            role: Agent role (e.g., 'courier', 'engineer')
            backend: LLM backend used

        Returns:
            True if recorded successfully
        """
        try:
            return self.metrics.record_agent_activity(
                agent_id=agent_id,
                action="spawn",
                details={
                    "role": role,
                    "backend": backend,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to record agent spawn: {e}")
            return False

    def record_agent_stopped(self, agent_id: str, reason: str = "normal") -> bool:
        """
        Record agent stopped event.

        Args:
            agent_id: Unique agent identifier
            reason: Reason for stopping

        Returns:
            True if recorded successfully
        """
        try:
            return self.metrics.record_agent_activity(
                agent_id=agent_id,
                action="stopped",
                details={
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to record agent stopped: {e}")
            return False

    def record_token_usage(
        self,
        model: str,
        agent: str,
        cache_hit: int = 0,
        cache_miss: int = 0,
        output_tokens: int = 0,
        total_tokens: int = 0,
    ) -> bool:
        """
        Record token usage directly.

        Args:
            model: Model name
            agent: Agent identifier
            cache_hit: Number of cache hits
            cache_miss: Number of cache misses
            output_tokens: Output tokens generated
            total_tokens: Total tokens used

        Returns:
            True if recorded successfully
        """
        try:
            return self.metrics.record_token_usage(
                date=datetime.now(),
                model=model,
                agent=agent,
                cache_hit=cache_hit,
                cache_miss=cache_miss,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
        except Exception as e:
            logger.warning(f"Failed to record token usage: {e}")
            return False


# Singleton instance for convenience
_default_executor = None


def get_agent_executor(config_provider=None) -> AgentExecutor:
    """
    Get singleton AgentExecutor instance.

    Args:
        config_provider: Optional config provider

    Returns:
        AgentExecutor instance
    """
    global _default_executor

    if config_provider is not None:
        return AgentExecutor(config_provider)

    if _default_executor is None:
        _default_executor = AgentExecutor()

    return _default_executor
