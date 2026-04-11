#!/usr/bin/env python3
"""
LLMBackendFactory - Factory for creating LLM backends from configuration.

Supports dynamic backend creation and configuration.
"""

import logging
from typing import Dict, Any, List, Optional, Type
from .backend import LLMBackend, LLMProvider, FallbackChain
from .ollama_backend import OllamaBackend
from .deepseek_backend import DeepSeekBackend
from .openai_backend import OpenAIBackend

logger = logging.getLogger(__name__)


# Registry of backend classes by provider
_BACKEND_REGISTRY = {
    LLMProvider.OLLAMA: OllamaBackend,
    LLMProvider.DEEPSEEK: DeepSeekBackend,
    LLMProvider.OPENAI: OpenAIBackend,
}


class LLMBackendFactory:
    """
    Factory for creating and managing LLM backends.

    Supports singleton instances and configuration-based creation.
    """

    _instances = {}  # Cache of backend instances by config hash

    @classmethod
    def create_backend(cls, provider: str, config: Dict[str, Any]) -> LLMBackend:
        """
        Create a backend instance for the given provider.

        Args:
            provider: Provider name (ollama, deepseek, openai)
            config: Backend-specific configuration

        Returns:
            LLMBackend instance

        Raises:
            ValueError: If provider is not supported
        """
        # Normalize provider name
        provider = provider.lower().strip()

        # Map to enum
        provider_enum = None
        for p in LLMProvider:
            if p.value == provider:
                provider_enum = p
                break

        if provider_enum is None:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported: {[p.value for p in LLMProvider]}"
            )

        # Ensure provider is in config
        config = config.copy()
        config["provider"] = provider_enum.value

        # Create instance key for caching
        # Exclude unhashable keys (lists, dicts) from hash
        unhashable_keys = {"fallback_chain", "agent_backends"}
        config_for_hash = {k: v for k, v in config.items() if k not in unhashable_keys}
        instance_key = f"{provider}:{hash(frozenset(config_for_hash.items()))}"

        if instance_key in cls._instances:
            logger.debug(f"Reusing cached backend instance: {instance_key}")
            return cls._instances[instance_key]

        # Get backend class
        backend_class = _BACKEND_REGISTRY.get(provider_enum)
        if backend_class is None:
            raise ValueError(f"No backend implementation for provider: {provider}")

        # Create instance
        logger.info(
            f"Creating {provider} backend with config keys: {list(config.keys())}"
        )
        instance = backend_class(config)

        # Cache instance
        cls._instances[instance_key] = instance

        return instance

    @classmethod
    def create_from_config(cls, llm_config: Dict[str, Any]) -> LLMBackend:
        """
        Create backend from NeoCortex LLM configuration.

        Expected config structure:
        {
            "provider": "ollama",
            "model": "llama2",
            "api_key": "sk-...",  # For cloud providers
            "base_url": "...",    # Optional
            ...  # Other provider-specific options
        }

        Args:
            llm_config: LLM configuration dictionary

        Returns:
            LLMBackend instance
        """
        provider = llm_config.get("provider", "ollama")
        return cls.create_backend(provider, llm_config)

    @classmethod
    def create_fallback_chain(cls, chain_config: List[Dict[str, Any]]) -> FallbackChain:
        """
        Create a fallback chain from a list of backend configurations.

        Args:
            chain_config: List of backend configurations in priority order

        Returns:
            FallbackChain instance
        """
        backends = []
        for backend_config in chain_config:
            try:
                backend = cls.create_from_config(backend_config)
                backends.append(backend)
            except Exception as e:
                logger.warning(
                    f"Failed to create backend from config {backend_config}: {e}"
                )

        if not backends:
            raise ValueError("No backends could be created from chain config")

        logger.info(
            f"Created fallback chain with {len(backends)} backends: "
            f"{[b.provider.value for b in backends]}"
        )

        return FallbackChain(backends)

    @classmethod
    def create_hybrid_chain(
        cls,
        local_config: Optional[Dict[str, Any]] = None,
        cloud_config: Optional[Dict[str, Any]] = None,
    ) -> FallbackChain:
        """
        Create a hybrid chain with local fallback to cloud.

        Args:
            local_config: Configuration for local backend (default: Ollama)
            cloud_config: Configuration for cloud backend (default: DeepSeek)

        Returns:
            FallbackChain with local first, then cloud
        """
        # Default local config
        if local_config is None:
            local_config = {
                "provider": "ollama",
                "model": "llama2",
                "base_url": "http://localhost:11434",
            }

        # Default cloud config
        if cloud_config is None:
            cloud_config = {
                "provider": "deepseek",
                "model": "deepseek-chat",
                "api_key": "",  # Should be set via environment variable
            }

        return cls.create_fallback_chain([local_config, cloud_config])

    @classmethod
    def cleanup(cls):
        """Clean up all backend instances."""
        for key, instance in list(cls._instances.items()):
            try:
                if hasattr(instance, "close"):
                    # Try to close async session if possible
                    import asyncio

                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.create_task(instance.close())
                        else:
                            loop.run_until_complete(instance.close())
                    except Exception:
                        pass
            except Exception as e:
                logger.warning(f"Error cleaning up backend {key}: {e}")

        cls._instances.clear()
        logger.info("Cleaned up all LLM backend instances")

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """Get list of available provider names."""
        return [p.value for p in _BACKEND_REGISTRY.keys()]

    @classmethod
    def get_backend_stats(cls) -> Dict[str, Any]:
        """Get statistics about created backends."""
        stats = {
            "total_instances": len(cls._instances),
            "instances_by_provider": {},
            "instance_keys": list(cls._instances.keys()),
        }

        for key, instance in cls._instances.items():
            provider = instance.provider.value
            stats["instances_by_provider"][provider] = (
                stats["instances_by_provider"].get(provider, 0) + 1
            )

        return stats
