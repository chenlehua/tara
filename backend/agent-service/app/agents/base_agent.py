"""
Base Agent
==========

Base class for all TARA agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import httpx
from app.common.config import settings
from app.common.utils import get_logger


class BaseAgent(ABC):
    """Base class for TARA agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(name)

    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the agent's main task."""
        pass

    async def call_llm(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Call the LLM for text generation."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.qwen3_url}/chat/completions",
                    json={
                        "model": "qwen3",
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    timeout=120.0,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise

    async def call_vl_model(
        self,
        prompt: str,
        image_data: bytes = None,
        image_url: str = None,
    ) -> str:
        """Call the vision-language model."""
        messages = [{"role": "user", "content": prompt}]

        if image_data:
            import base64

            image_b64 = base64.b64encode(image_data).decode()
            messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                },
            ]
        elif image_url:
            messages[0]["content"] = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.qwen3_vl_url}/chat/completions",
                    json={
                        "model": "qwen3-vl",
                        "messages": messages,
                        "max_tokens": 2000,
                    },
                    timeout=120.0,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            self.logger.error(f"VL model call failed: {e}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.embedding_url}/embeddings",
                    json={
                        "model": "qwen3-embedding",
                        "input": texts,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()
                return [item["embedding"] for item in result["data"]]
        except Exception as e:
            self.logger.error(f"Embedding call failed: {e}")
            raise
