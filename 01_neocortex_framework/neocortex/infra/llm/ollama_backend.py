#!/usr/bin/env python3
"""
OllamaBackend - Local Ollama LLM backend.

Supports running local models via Ollama API.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import aiohttp
from .backend import LLMBackend, LLMRequest, LLMResponse, LLMProvider

logger = logging.getLogger(__name__)


class OllamaBackend(LLMBackend):
    """
    Ollama backend for local LLM inference.

    Requires Ollama to be installed and running locally.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Ollama backend.

        Args:
            config: Must include 'base_url' (default: http://localhost:11434)
                    and 'model' (default: llama2).
        """
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.session: Optional[aiohttp.ClientSession] = None
        super().__init__(config)

    def _initialize(self) -> None:
        """Initialize Ollama connection."""
        try:
            # Test connection synchronously for simplicity
            import urllib.request
            import urllib.error

            test_url = f"{self.base_url}/api/tags"
            req = urllib.request.Request(test_url, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=5) as response:
                    if response.status == 200:
                        self.is_available = True
                        logger.info(f"Ollama backend connected at {self.base_url}")
                    else:
                        logger.warning(f"Ollama returned status {response.status}")
            except urllib.error.URLError as e:
                logger.warning(f"Ollama not available at {self.base_url}: {e}")
                self.is_available = False
        except Exception as e:
            logger.warning(f"Failed to initialize Ollama backend: {e}")
            self.is_available = False

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=300)
            )
        return self.session

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using Ollama API.

        Args:
            request: LLMRequest with prompt and parameters.

        Returns:
            LLMResponse with generated content.
        """
        session = await self._ensure_session()

        # Prepare Ollama API payload
        payload = {
            "model": self.model,
            "prompt": request.prompt,
            "stream": False,
            "options": {
                "temperature": request.temperature,
            },
        }

        if request.system_prompt:
            payload["system"] = request.system_prompt

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        start_time = asyncio.get_event_loop().time()

        try:
            async with session.post(
                f"{self.base_url}/api/generate", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"Ollama API error {response.status}: {error_text}"
                    )

                result = await response.json()

                completion_time = (
                    asyncio.get_event_loop().time() - start_time
                ) * 1000  # to milliseconds

                return LLMResponse(
                    content=result.get("response", ""),
                    model=self.model,
                    provider=LLMProvider.OLLAMA,
                    tokens_used=result.get("total_duration", 0),
                    completion_time_ms=completion_time,
                    metadata={
                        "ollama_response": result,
                        "eval_count": result.get("eval_count", 0),
                        "eval_duration": result.get("eval_duration", 0),
                    },
                )

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens from Ollama.

        Args:
            request: LLMRequest with stream=True.

        Yields:
            Token strings as they become available.
        """
        session = await self._ensure_session()

        payload = {
            "model": self.model,
            "prompt": request.prompt,
            "stream": True,
            "options": {
                "temperature": request.temperature,
            },
        }

        if request.system_prompt:
            payload["system"] = request.system_prompt

        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        try:
            async with session.post(
                f"{self.base_url}/api/generate", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"Ollama API error {response.status}: {error_text}"
                    )

                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            token = data.get("response", "")
                            if token:
                                yield token
                        except json.JSONDecodeError:
                            continue

        except Exception as e:
            logger.error(f"Ollama streaming failed: {e}")
            raise

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for Ollama models.

        Very rough estimation: ~4 characters per token for Llama models.
        """
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """
        Get available Ollama models.

        Note: This requires a synchronous HTTP request.
        """
        try:
            import urllib.request
            import json as json_module

            response = urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=5)
            data = json_module.load(response)
            models = [model["name"] for model in data.get("models", [])]
            return models
        except Exception as e:
            logger.warning(f"Failed to fetch Ollama models: {e}")
            return [self.model]  # At least return the configured model

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def __del__(self):
        """Ensure session is closed on deletion."""
        if self.session and not self.session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule session closure
                    asyncio.create_task(self.session.close())
                else:
                    loop.run_until_complete(self.session.close())
            except Exception:
                pass  # Best effort cleanup
