#!/usr/bin/env python3
"""
OpenAIBackend - OpenAI-compatible LLM backend.

Supports OpenAI API and compatible providers (OpenRouter, etc.)
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
import aiohttp
from .backend import LLMBackend, LLMRequest, LLMResponse, LLMProvider

logger = logging.getLogger(__name__)


class OpenAIBackend(LLMBackend):
    """
    OpenAI-compatible backend for cloud LLM inference.

    Supports OpenAI API and compatible providers.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize OpenAI backend.

        Args:
            config: Must include 'api_key' and optionally 'base_url'
                    (default: https://api.openai.com/v1).
        """
        self.api_key = config.get("api_key", "")
        if not self.api_key:
            logger.warning("OpenAI API key not provided in config")

        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.session: Optional[aiohttp.ClientSession] = None
        super().__init__(config)

    def _initialize(self) -> None:
        """
        Initialize OpenAI backend.

        Note: Actual API validation happens on first request.
        """
        if self.api_key:
            self.is_available = True
            logger.info(
                "OpenAI backend initialized (availability will be tested on first request)"
            )
        else:
            self.is_available = False
            logger.warning("OpenAI backend disabled - no API key")

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            self.session = aiohttp.ClientSession(
                headers=headers, timeout=aiohttp.ClientTimeout(total=300)
            )
        return self.session

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate completion using OpenAI API.

        Args:
            request: LLMRequest with prompt and parameters.

        Returns:
            LLMResponse with generated content.
        """
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured")

        session = await self._ensure_session()

        # Prepare messages
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": False,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        start_time = asyncio.get_event_loop().time()

        try:
            async with session.post(
                f"{self.base_url}/chat/completions", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"OpenAI API error {response.status}: {error_text}"
                    )

                result = await response.json()

                completion_time = (
                    asyncio.get_event_loop().time() - start_time
                ) * 1000  # to milliseconds

                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)

                return LLMResponse(
                    content=content,
                    model=self.model,
                    provider=LLMProvider.OPENAI,
                    tokens_used=tokens_used,
                    completion_time_ms=completion_time,
                    metadata={
                        "openai_response": result,
                        "finish_reason": result["choices"][0].get("finish_reason"),
                        "id": result.get("id"),
                    },
                )

        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream completion tokens from OpenAI.

        Args:
            request: LLMRequest with stream=True.

        Yields:
            Token strings as they become available.
        """
        if not self.api_key:
            raise RuntimeError("OpenAI API key not configured")

        session = await self._ensure_session()

        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        try:
            async with session.post(
                f"{self.base_url}/chat/completions", json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"OpenAI API error {response.status}: {error_text}"
                    )

                async for line in response.content:
                    if line:
                        line = line.strip()
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    token = delta.get("content", "")
                                    if token:
                                        yield token
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            raise

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for OpenAI models.

        Uses approximation: ~4 characters per token.
        """
        return len(text) // 4

    def get_available_models(self) -> List[str]:
        """
        Get available OpenAI models.

        Note: This would require API call to list models.
        For now, return common OpenAI models.
        """
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini",
        ]

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
