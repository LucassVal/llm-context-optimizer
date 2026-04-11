#!/usr/bin/env python3
"""
LLMBackend - Abstract base class for LLM backends.

Provides unified interface for local and cloud LLM providers.
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LOCAL = "local"


@dataclass
class LLMResponse:
    """Standardized LLM response."""

    content: str
    model: str
    provider: LLMProvider
    tokens_used: int = 0
    completion_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Standardized LLM request."""

    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMBackend(ABC):
    """
    Abstract base class for LLM backends.

    All backends must implement this interface to be compatible with
    the NeoCortex hybrid LLM system.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize backend with configuration.

        Args:
            config: Backend-specific configuration dictionary.
                   Must include at least 'provider' and 'model' keys.
        """
        self.config = config
        self.provider = LLMProvider(config.get("provider", "local"))
        self.model = config.get("model", "default")
        self.is_available = False
        self._initialize()

    @abstractmethod
    def _initialize(self) -> None:
        """
        Initialize backend connection and validate availability.

        Should set self.is_available based on successful initialization.
        """
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate a completion for the given request.

        Args:
            request: LLMRequest with prompt and parameters.

        Returns:
            LLMResponse with generated content and metadata.
        """
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens for the given request.

        Args:
            request: LLMRequest with stream=True.

        Yields:
            Token strings as they become available.
        """
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for the given text.

        Args:
            text: Input text to estimate.

        Returns:
            Estimated token count.
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this backend.

        Returns:
            List of model identifiers.
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check and return status.

        Returns:
            Dictionary with health status and metrics.
        """
        return {
            "provider": self.provider.value,
            "model": self.model,
            "available": self.is_available,
            "config_keys": list(self.config.keys()),
        }

    def __repr__(self) -> str:
        return f"LLMBackend(provider={self.provider.value}, model={self.model}, available={self.is_available})"


class FallbackChain:
    """
    Chain of LLM backends with fallback behavior.

    Tries backends in order until one succeeds.
    """

    def __init__(self, backends: List[LLMBackend]):
        """
        Initialize with ordered list of backends.

        Args:
            backends: List of LLMBackend instances in priority order.
        """
        self.backends = backends
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "fallback_used": 0,
            "errors": {},
        }

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using fallback chain.

        Args:
            request: LLMRequest with prompt and parameters.

        Returns:
            LLMResponse from first successful backend.

        Raises:
            RuntimeError: If all backends fail.
        """
        self.stats["total_requests"] += 1
        last_error = None

        for i, backend in enumerate(self.backends):
            if not backend.is_available:
                logger.debug(f"Backend {backend} not available, skipping")
                continue

            try:
                response = await backend.generate(request)
                self.stats["successful_requests"] += 1
                if i > 0:
                    self.stats["fallback_used"] += 1
                return response
            except Exception as e:
                last_error = e
                backend_name = f"{backend.provider.value}:{backend.model}"
                self.stats["errors"][backend_name] = (
                    self.stats["errors"].get(backend_name, 0) + 1
                )
                logger.warning(f"Backend {backend} failed: {e}")

        raise RuntimeError(f"All backends failed. Last error: {last_error}")

    def get_stats(self) -> Dict[str, Any]:
        """Get current chain statistics."""
        return self.stats.copy()
