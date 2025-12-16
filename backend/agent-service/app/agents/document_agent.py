"""
Document Agent
==============

Agent for document understanding and content extraction.
"""

from typing import Any, Dict, List

from .base_agent import BaseAgent


class DocumentAgent(BaseAgent):
    """Agent for document processing."""

    SYSTEM_PROMPT = """你是一个专业的汽车技术文档分析专家。你的任务是：
1. 理解和分析汽车技术文档
2. 提取文档的结构和关键内容
3. 识别文档中的技术组件、接口和数据流
4. 总结文档的主要信息

请以结构化的方式输出分析结果。"""

    def __init__(self):
        super().__init__("DocumentAgent")

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute document processing."""
        document_ids = kwargs.get("document_ids", [])
        return await self.process_documents(document_ids)

    async def process_documents(
        self,
        document_ids: List[int],
    ) -> Dict[str, Any]:
        """Process multiple documents and extract content."""
        self.logger.info(f"Processing {len(document_ids)} documents")

        results = {
            "documents": [],
            "content": "",
            "summary": "",
            "entities": [],
        }

        # In production, this would:
        # 1. Fetch documents from document-service
        # 2. Use OCR for images
        # 3. Extract structured content
        # 4. Generate embeddings

        for doc_id in document_ids:
            results["documents"].append(
                {
                    "id": doc_id,
                    "status": "processed",
                }
            )

        return results

    async def extract_structure(self, content: str) -> Dict[str, Any]:
        """Extract document structure using LLM."""
        prompt = f"""分析以下文档内容，提取其结构：

{content[:5000]}

请以JSON格式输出：
{{
    "title": "文档标题",
    "sections": [
        {{"title": "章节标题", "content_summary": "内容摘要"}}
    ],
    "key_terms": ["关键术语1", "关键术语2"],
    "components_mentioned": ["组件1", "组件2"]
}}"""

        response = await self.call_llm(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
        )

        # Parse JSON response
        try:
            import json

            return json.loads(response)
        except Exception:
            return {"raw_response": response}

    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Analyze an image (diagram, architecture, etc.)."""
        prompt = """分析这张图片，描述其内容。如果是架构图或技术图表，请识别：
1. 图中的组件
2. 组件之间的连接/关系
3. 数据流向
请以结构化方式描述。"""

        response = await self.call_vl_model(
            prompt=prompt,
            image_data=image_data,
        )

        return {
            "description": response,
            "type": "technical_diagram",
        }
