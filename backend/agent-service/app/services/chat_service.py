"""
Chat Service
============

Service for AI chat functionality.
"""

import json
import uuid
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from tara_shared.config import settings
from tara_shared.database.redis import get_cache_service
from tara_shared.utils import get_logger

logger = get_logger(__name__)

# In-memory fallback for chat history when Redis is unavailable
_chat_history_store: Dict[str, List[Dict[str, Any]]] = {}


class ChatService:
    """Service for AI chat operations."""

    SYSTEM_PROMPT = """你是一个专业的汽车网络安全分析助手，专注于威胁分析与风险评估(TARA)。
你的职责包括：
1. 帮助用户理解汽车网络安全概念
2. 协助进行威胁识别和STRIDE分析
3. 指导攻击路径分析和风险评估
4. 提供符合ISO/SAE 21434标准的建议

请用专业但易懂的方式回答问题。如果用户问的问题与汽车网络安全无关，你也可以友好地回答，但会提示这不是你的专业领域。"""

    def __init__(self):
        self.cache = get_cache_service()

    async def chat(
        self,
        messages: List[Dict[str, str]],
        project_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Send chat messages and get response."""
        # Prepare messages with system prompt
        full_messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add project context if provided
        if project_id:
            project_context = await self._get_project_context(project_id)
            if project_context:
                full_messages.append(
                    {
                        "role": "system",
                        "content": f"当前项目上下文：\n{project_context}",
                    }
                )

        # Add extra context if provided
        if context:
            context_str = self._format_context(context)
            if context_str:
                full_messages.append(
                    {
                        "role": "system",
                        "content": f"额外上下文信息：\n{context_str}",
                    }
                )

        # Add user messages
        full_messages.extend(messages)

        # Save user message to history
        if messages:
            await self._save_message(
                project_id=project_id,
                role="user",
                content=messages[-1].get("content", ""),
            )

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
                assistant_response = result["choices"][0]["message"]["content"]

                # Save assistant response to history
                await self._save_message(
                    project_id=project_id,
                    role="assistant",
                    content=assistant_response,
                )

                return assistant_response

        except httpx.ConnectError:
            logger.warning("AI service not available, using fallback response")
            return self._get_fallback_response(messages)
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            return self._get_fallback_response(messages)

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        project_id: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response."""
        full_messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if project_id:
            context = await self._get_project_context(project_id)
            if context:
                full_messages.append(
                    {
                        "role": "system",
                        "content": f"当前项目上下文：\n{context}",
                    }
                )

        full_messages.extend(messages)

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
                                chunk = json.loads(data)
                                content = (
                                    chunk.get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if content:
                                    yield content
                            except Exception:
                                continue

        except httpx.ConnectError:
            logger.warning("AI service not available for streaming")
            yield self._get_fallback_response(messages)
        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            yield "抱歉，AI服务暂时不可用，请稍后再试。"

    async def get_history(
        self, project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get chat history for a project."""
        history_key = self._get_history_key(project_id)

        # Try to get from Redis cache
        if self.cache and self.cache.is_available():
            try:
                cached = self.cache.get(history_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"Failed to get history from cache: {e}")

        # Fallback to in-memory store
        return _chat_history_store.get(history_key, [])

    async def clear_history(self, project_id: Optional[int] = None) -> None:
        """Clear chat history for a project."""
        history_key = self._get_history_key(project_id)

        # Clear from Redis cache
        if self.cache and self.cache.is_available():
            try:
                self.cache.delete(history_key)
            except Exception as e:
                logger.warning(f"Failed to clear history from cache: {e}")

        # Clear from in-memory store
        if history_key in _chat_history_store:
            del _chat_history_store[history_key]

    async def _save_message(
        self,
        project_id: Optional[int],
        role: str,
        content: str,
    ) -> None:
        """Save a message to history."""
        history_key = self._get_history_key(project_id)

        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        # Get existing history
        history = await self.get_history(project_id)
        history.append(message)

        # Keep only last 50 messages
        if len(history) > 50:
            history = history[-50:]

        # Try to save to Redis cache
        if self.cache and self.cache.is_available():
            try:
                self.cache.set(
                    history_key, json.dumps(history), expire=86400
                )  # 24 hours
            except Exception as e:
                logger.warning(f"Failed to save history to cache: {e}")

        # Also save to in-memory store
        _chat_history_store[history_key] = history

    def _get_history_key(self, project_id: Optional[int]) -> str:
        """Get the cache key for chat history."""
        if project_id:
            return f"chat_history:project:{project_id}"
        return "chat_history:global"

    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary to string."""
        if not context:
            return ""

        parts = []
        if "action" in context:
            parts.append(f"操作类型: {context['action']}")
        if "asset_id" in context:
            parts.append(f"资产ID: {context['asset_id']}")
        if "threat_id" in context:
            parts.append(f"威胁ID: {context['threat_id']}")

        return "\n".join(parts) if parts else ""

    def _get_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Get a fallback response when AI service is unavailable."""
        if not messages:
            return "您好！我是TARA AI助手，请问有什么可以帮您的？"

        user_message = messages[-1].get("content", "").lower()

        # Simple keyword-based responses
        if "stride" in user_message or "威胁" in user_message:
            return """STRIDE是一种威胁建模方法，包括六类威胁：

1. **S - Spoofing (欺骗)**: 身份伪造，冒充合法用户或系统
2. **T - Tampering (篡改)**: 恶意修改数据或代码
3. **R - Repudiation (否认)**: 否认已执行的操作
4. **I - Information Disclosure (信息泄露)**: 未授权访问敏感信息
5. **D - Denial of Service (拒绝服务)**: 使系统或服务不可用
6. **E - Elevation of Privilege (权限提升)**: 获取未授权的权限

对于汽车网络安全，每种威胁都需要根据具体资产和攻击面进行分析。"""

        elif "cal" in user_message or "风险" in user_message or "等级" in user_message:
            return """CAL (Cybersecurity Assurance Level) 是ISO 21434标准中的网络安全保障等级：

- **CAL 1**: 基础安全保障 - 适用于低风险场景
- **CAL 2**: 标准安全保障 - 系统化的安全开发流程
- **CAL 3**: 高级安全保障 - 严格的安全测试和审计
- **CAL 4**: 最高安全保障 - 形式化验证和独立审计

CAL等级由风险评估结果决定，考虑影响(Impact)和可行性(Feasibility)。"""

        elif "iso" in user_message or "21434" in user_message or "标准" in user_message:
            return """ISO/SAE 21434是汽车网络安全工程标准，主要内容包括：

1. **组织网络安全管理**: 建立网络安全文化和治理
2. **项目依赖的网络安全管理**: 管理供应链安全
3. **分布式网络安全活动**: 跨组织协作
4. **持续的网络安全活动**: 监控、响应和更新
5. **概念阶段**: 定义网络安全目标
6. **产品开发阶段**: TARA分析和安全设计
7. **生产和运维**: 确保生产环境安全

该标准强调全生命周期的网络安全管理。"""

        elif "攻击" in user_message or "路径" in user_message:
            return """攻击路径分析是评估攻击可行性的重要方法，需要考虑：

1. **攻击潜力参数**:
   - 专业知识 (Expertise)
   - 所需时间 (Elapsed Time)
   - 所需设备 (Equipment)
   - 目标知识 (Knowledge of Target)
   - 攻击窗口 (Window of Opportunity)

2. **可行性评级**:
   - 攻击潜力 0-9: 高可行性
   - 攻击潜力 10-17: 中可行性
   - 攻击潜力 18-24: 低可行性
   - 攻击潜力 25+: 极低可行性

建议结合具体资产和威胁场景进行详细分析。"""

        else:
            return """您好！我是TARA AI助手，专注于汽车网络安全分析。

我可以帮助您：
- 🔍 **威胁识别**: 使用STRIDE方法分析潜在威胁
- 📊 **风险评估**: 计算CAL等级和风险值
- 🛡️ **安全措施**: 推荐符合ISO 21434的控制措施
- 🔗 **攻击路径**: 分析攻击可行性和潜力

请问您需要什么帮助？"""

    async def _get_project_context(self, project_id: int) -> Optional[str]:
        """Get project context for chat."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://project-service:8001/api/v1/projects/{project_id}",
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    return f"""项目: {data.get('name', 'Unknown')}
车型: {data.get('vehicle_type', 'Unknown')} {data.get('vehicle_model', '')}
标准: {data.get('standard', 'ISO/SAE 21434')}
范围: {data.get('scope', 'N/A')}"""
        except Exception as e:
            logger.debug(f"Failed to get project context: {e}")

        return None
