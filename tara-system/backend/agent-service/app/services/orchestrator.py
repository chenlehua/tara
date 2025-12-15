"""
Agent Orchestrator
==================

Orchestrates multiple agents for TARA analysis workflow.
"""

from typing import Any, Dict, List, Optional
import uuid
from datetime import datetime

from tara_shared.utils import get_logger

from ..agents.document_agent import DocumentAgent
from ..agents.asset_agent import AssetAgent
from ..agents.threat_risk_agent import ThreatRiskAgent
from ..agents.report_agent import ReportAgent

logger = get_logger(__name__)


class TaskManager:
    """Simple in-memory task manager."""
    
    _tasks: Dict[str, Dict[str, Any]] = {}
    
    @classmethod
    def create_task(cls, task_id: str, task_type: str, **kwargs) -> str:
        cls._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "status": "pending",
            "progress": 0,
            "message": None,
            "result": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **kwargs,
        }
        return task_id
    
    @classmethod
    def update_task(cls, task_id: str, **kwargs) -> None:
        if task_id in cls._tasks:
            cls._tasks[task_id].update(kwargs)
            cls._tasks[task_id]["updated_at"] = datetime.now().isoformat()
    
    @classmethod
    def get_task(cls, task_id: str) -> Optional[Dict[str, Any]]:
        return cls._tasks.get(task_id)
    
    @classmethod
    def delete_task(cls, task_id: str) -> bool:
        if task_id in cls._tasks:
            del cls._tasks[task_id]
            return True
        return False


class AgentOrchestrator:
    """Orchestrator for AI agents in TARA workflow."""

    def __init__(self):
        self.document_agent = DocumentAgent()
        self.asset_agent = AssetAgent()
        self.threat_risk_agent = ThreatRiskAgent()
        self.report_agent = ReportAgent()

    def create_task(
        self,
        task_type: str,
        project_id: int,
        document_ids: List[int] = None,
        options: Dict[str, Any] = None,
    ) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        TaskManager.create_task(
            task_id=task_id,
            task_type=task_type,
            project_id=project_id,
            document_ids=document_ids or [],
            options=options or {},
        )
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        return TaskManager.get_task(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a task."""
        task = TaskManager.get_task(task_id)
        if task and task["status"] in ["pending", "running"]:
            TaskManager.update_task(task_id, status="cancelled")
            return True
        return False

    def list_agents(self) -> List[Dict[str, Any]]:
        """List available agents."""
        return [
            {
                "name": "DocumentAgent",
                "description": "文档理解Agent - 负责文档OCR、版面分析和内容提取",
                "capabilities": ["ocr", "layout_analysis", "content_extraction"],
            },
            {
                "name": "AssetAgent",
                "description": "资产挖掘Agent - 负责资产实体抽取、分类和关系识别",
                "capabilities": ["entity_extraction", "asset_classification", "relation_discovery"],
            },
            {
                "name": "ThreatRiskAgent",
                "description": "威胁风险Agent - 负责STRIDE分析、攻击路径构建和风险评估",
                "capabilities": ["stride_analysis", "attack_path", "risk_assessment"],
            },
            {
                "name": "ReportAgent",
                "description": "报告撰写Agent - 负责内容撰写、图表生成和报告导出",
                "capabilities": ["content_writing", "chart_generation", "report_export"],
            },
        ]

    async def run_full_analysis(
        self,
        task_id: str,
        project_id: int,
        document_ids: List[int],
        options: Dict[str, Any] = None,
    ) -> None:
        """Run full TARA analysis workflow."""
        logger.info(f"Starting full analysis for task {task_id}")
        
        TaskManager.update_task(task_id, status="running", progress=0, message="开始分析")
        
        try:
            # Phase 1: Document Understanding (0-25%)
            TaskManager.update_task(task_id, progress=5, message="文档解析中...")
            doc_results = await self.document_agent.process_documents(document_ids)
            TaskManager.update_task(task_id, progress=25, message="文档解析完成")
            
            # Phase 2: Asset Discovery (25-50%)
            TaskManager.update_task(task_id, progress=30, message="资产识别中...")
            asset_results = await self.asset_agent.discover_assets(
                project_id=project_id,
                document_content=doc_results.get("content", ""),
            )
            TaskManager.update_task(task_id, progress=50, message="资产识别完成")
            
            # Phase 3: Threat Analysis (50-75%)
            TaskManager.update_task(task_id, progress=55, message="威胁分析中...")
            threat_results = await self.threat_risk_agent.analyze_threats(
                project_id=project_id,
                assets=asset_results.get("assets", []),
            )
            TaskManager.update_task(task_id, progress=75, message="威胁分析完成")
            
            # Phase 4: Report Generation (75-100%)
            TaskManager.update_task(task_id, progress=80, message="报告生成中...")
            report_results = await self.report_agent.generate_report(
                project_id=project_id,
            )
            TaskManager.update_task(task_id, progress=100, message="分析完成")
            
            # Complete
            TaskManager.update_task(
                task_id,
                status="completed",
                result={
                    "documents_processed": len(document_ids),
                    "assets_discovered": len(asset_results.get("assets", [])),
                    "threats_identified": len(threat_results.get("threats", [])),
                    "report_id": report_results.get("report_id"),
                },
            )
            
            logger.info(f"Full analysis completed for task {task_id}")
            
        except Exception as e:
            logger.error(f"Analysis failed for task {task_id}: {e}")
            TaskManager.update_task(
                task_id,
                status="failed",
                message=f"分析失败: {str(e)}",
            )
