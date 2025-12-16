"""
Chat Service
============

Service for AI chat functionality.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from tara_shared.config import settings
from tara_shared.utils import get_logger

logger = get_logger(__name__)


class ChatService:
    """Service for AI chat operations."""

    SYSTEM_PROMPT = """你是一个专业的汽车网络安全分析助手，专注于威胁分析与风险评估(TARA)。
你的职责包括：
1. 帮助用户理解汽车网络安全概念
2. 协助进行威胁识别和STRIDE分析
3. 指导攻击路径分析和风险评估
4. 提供符合ISO/SAE 21434标准的建议

请用专业但易懂的方式回答问题。"""

    async def chat(
        self,
        messages: List[Dict[str, str]],
        project_id: Optional[int] = None,
    ) -> str:
        """Send chat messages and get response."""
        # Prepare messages with system prompt
        full_messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ] + messages
        
        # Add project context if provided
        if project_id:
            context = await self._get_project_context(project_id)
            if context:
                full_messages.insert(1, {
                    "role": "system",
                    "content": f"当前项目上下文：\n{context}",
                })
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{settings.qwen3_url}/chat/completions",
                    json={
                        "model": "qwen3",
                        "messages": full_messages,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                    },
                    timeout=60.0,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            return "抱歉，AI服务暂时不可用，请稍后再试。"

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        project_id: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response."""
        full_messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ] + messages
        
        if project_id:
            context = await self._get_project_context(project_id)
            if context:
                full_messages.insert(1, {
                    "role": "system",
                    "content": f"当前项目上下文：\n{context}",
                })
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{settings.qwen3_url}/chat/completions",
                    json={
                        "model": "qwen3",
                        "messages": full_messages,
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "stream": True,
                    },
                    timeout=120.0,
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                chunk = json.loads(data)
                                content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                                if content:
                                    yield content
                            except Exception:
                                continue
                                
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield "抱歉，AI服务暂时不可用，请稍后再试。"

    async def _get_project_context(self, project_id: int) -> Optional[str]:
        """Get project context for chat."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8001/api/v1/projects/{project_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    return f"""项目: {data.get('name', 'Unknown')}
车型: {data.get('vehicle_type', 'Unknown')} {data.get('vehicle_model', '')}
标准: {data.get('standard', 'ISO/SAE 21434')}
范围: {data.get('scope', 'N/A')}"""
        except Exception as e:
            logger.error(f"Failed to get project context: {e}")
        
        return None
