# 报告多版本管理设计方案

## 1. 概述

本文档描述了TARA报告系统中报告与项目关联以及多版本管理的详细设计方案。

### 1.1 设计目标

1. **项目-报告关联**: 清晰的项目与报告层级关系
2. **版本管理**: 支持同一报告的多版本管理
3. **版本追踪**: 记录每个版本的变更历史
4. **版本对比**: 支持不同版本间的差异对比
5. **版本回滚**: 支持回滚到历史版本
6. **基线管理**: 支持设置报告基线版本

---

## 2. 数据模型设计

### 2.1 实体关系图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Entity Relationship                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐       1:N        ┌──────────────┐       1:N        ┌──────────────────┐
│   Project    │─────────────────>│    Report    │─────────────────>│  ReportVersion   │
│              │                  │              │                  │                  │
│ id           │                  │ id           │                  │ id               │
│ name         │                  │ project_id   │──────┐           │ report_id        │
│ description  │                  │ name         │      │           │ version_number   │
│ status       │                  │ report_type  │      │           │ major_version    │
│ ...          │                  │ template     │      │           │ minor_version    │
└──────────────┘                  │ current_     │      │           │ content          │
       │                          │   version_id │──────┼──────────>│ statistics       │
       │                          │ baseline_    │      │           │ snapshot_data    │
       │                          │   version_id │──────┼──────────>│ change_summary   │
       │                          │ ...          │      │           │ created_by       │
       │                          └──────────────┘      │           │ created_at       │
       │                                 │              │           │ is_baseline      │
       │                                 │              │           │ status           │
       │                                 │              │           └──────────────────┘
       │                                 │                                    │
       │                                 │              1:N                   │
       │                                 │                                    ▼
       │                                 │              ┌──────────────────────────────┐
       │                                 └─────────────>│     ReportVersionChange      │
       │                                                │                              │
       ▼                                                │ id                           │
┌──────────────┐                                        │ version_id                   │
│    Asset     │                                        │ change_type                  │
│              │                                        │ entity_type                  │
│ id           │                                        │ entity_id                    │
│ project_id   │                                        │ field_name                   │
│ name         │                                        │ old_value                    │
│ ...          │                                        │ new_value                    │
└──────────────┘                                        │ created_at                   │
       │                                                └──────────────────────────────┘
       │
       ▼
┌──────────────┐
│  ThreatRisk  │
│              │
│ id           │
│ project_id   │
│ asset_id     │
│ ...          │
└──────────────┘
```

### 2.2 数据库表设计

#### 2.2.1 Report 表 (增强版)

```sql
CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    
    -- 基本信息
    name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) DEFAULT 'tara',
    description TEXT,
    template VARCHAR(50),
    
    -- 版本管理
    current_version_id INT,           -- 当前版本ID
    baseline_version_id INT,          -- 基线版本ID
    latest_version_number VARCHAR(20), -- 最新版本号 (如 "2.3")
    version_count INT DEFAULT 0,       -- 版本总数
    
    -- 状态
    status INT DEFAULT 0,
    progress INT DEFAULT 0,
    error_message TEXT,
    
    -- 元数据
    author VARCHAR(100),
    reviewer VARCHAR(100),
    review_status INT DEFAULT 0,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (current_version_id) REFERENCES report_versions(id) ON DELETE SET NULL,
    FOREIGN KEY (baseline_version_id) REFERENCES report_versions(id) ON DELETE SET NULL,
    
    INDEX idx_project_id (project_id),
    INDEX idx_status (status)
);
```

#### 2.2.2 ReportVersion 表 (新增)

```sql
CREATE TABLE report_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    report_id INT NOT NULL,
    
    -- 版本标识
    version_number VARCHAR(20) NOT NULL,  -- 完整版本号 "1.0", "1.1", "2.0"
    major_version INT NOT NULL DEFAULT 1,  -- 主版本号
    minor_version INT NOT NULL DEFAULT 0,  -- 次版本号
    
    -- 版本内容 (完整快照)
    content JSON,                -- 报告内容快照
    statistics JSON,             -- 统计数据快照
    sections JSON,               -- 章节列表快照
    snapshot_data JSON,          -- 完整数据快照 (包含资产、威胁、措施)
    
    -- 版本元数据
    change_summary TEXT,         -- 变更摘要
    change_reason VARCHAR(200),  -- 变更原因
    created_by VARCHAR(100),     -- 创建人
    approved_by VARCHAR(100),    -- 审批人
    approved_at DATETIME,        -- 审批时间
    
    -- 版本状态
    status VARCHAR(20) DEFAULT 'draft',  -- draft, review, approved, deprecated
    is_baseline BOOLEAN DEFAULT FALSE,    -- 是否为基线版本
    is_current BOOLEAN DEFAULT FALSE,     -- 是否为当前版本
    
    -- 文件信息
    file_paths JSON,             -- 各格式文件路径 {pdf: "", docx: "", xlsx: ""}
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    
    INDEX idx_report_id (report_id),
    INDEX idx_version (report_id, version_number),
    INDEX idx_is_current (report_id, is_current),
    UNIQUE KEY uk_report_version (report_id, version_number)
);
```

#### 2.2.3 ReportVersionChange 表 (新增 - 变更追踪)

```sql
CREATE TABLE report_version_changes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version_id INT NOT NULL,
    
    -- 变更类型
    change_type VARCHAR(20) NOT NULL,  -- add, modify, delete
    entity_type VARCHAR(50) NOT NULL,  -- asset, threat, measure, project_info
    entity_id INT,                      -- 实体ID
    entity_name VARCHAR(200),           -- 实体名称 (便于显示)
    
    -- 变更详情
    field_name VARCHAR(100),            -- 变更字段
    old_value TEXT,                     -- 旧值 (JSON格式)
    new_value TEXT,                     -- 新值 (JSON格式)
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (version_id) REFERENCES report_versions(id) ON DELETE CASCADE,
    
    INDEX idx_version_id (version_id),
    INDEX idx_entity (entity_type, entity_id)
);
```

### 2.3 Pydantic Schemas

```python
# schemas/report_version.py

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReportVersionBase(BaseModel):
    """报告版本基础Schema"""
    version_number: str = Field(..., description="版本号")
    change_summary: Optional[str] = Field(default=None, description="变更摘要")
    change_reason: Optional[str] = Field(default=None, description="变更原因")


class ReportVersionCreate(ReportVersionBase):
    """创建报告版本"""
    report_id: int = Field(..., description="报告ID")
    is_major: bool = Field(default=False, description="是否为主版本升级")


class ReportVersionResponse(ReportVersionBase):
    """报告版本响应"""
    id: int
    report_id: int
    major_version: int
    minor_version: int
    content: Optional[Dict[str, Any]] = None
    statistics: Optional[Dict[str, Any]] = None
    snapshot_data: Optional[Dict[str, Any]] = None
    status: str
    is_baseline: bool
    is_current: bool
    created_by: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ReportVersionListResponse(BaseModel):
    """版本列表响应"""
    versions: List[ReportVersionResponse]
    total: int
    current_version: Optional[str] = None
    baseline_version: Optional[str] = None


class VersionCompareRequest(BaseModel):
    """版本对比请求"""
    version_a: str = Field(..., description="版本A")
    version_b: str = Field(..., description="版本B")


class VersionCompareResponse(BaseModel):
    """版本对比响应"""
    version_a: str
    version_b: str
    changes: List[Dict[str, Any]]
    summary: Dict[str, int]  # {added: 5, modified: 3, deleted: 1}


class VersionChangeRecord(BaseModel):
    """版本变更记录"""
    change_type: str  # add, modify, delete
    entity_type: str  # asset, threat, measure
    entity_id: Optional[int] = None
    entity_name: str
    field_name: Optional[str] = None
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    created_at: datetime
```

---

## 3. 版本管理服务设计

### 3.1 ReportVersionService

```python
# services/report_version_service.py

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from deepdiff import DeepDiff  # 用于比较版本差异

from app.common.models import Report, ReportVersion, ReportVersionChange
from app.common.utils import get_logger

logger = get_logger(__name__)


class ReportVersionService:
    """报告版本管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_version(
        self,
        report_id: int,
        is_major: bool = False,
        change_summary: str = None,
        change_reason: str = None,
        created_by: str = None,
    ) -> ReportVersion:
        """
        创建新版本
        
        Args:
            report_id: 报告ID
            is_major: 是否为主版本升级 (1.x -> 2.0)
            change_summary: 变更摘要
            change_reason: 变更原因
            created_by: 创建人
        
        Returns:
            新创建的版本对象
        """
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # 计算新版本号
        latest_version = self._get_latest_version(report_id)
        if latest_version:
            if is_major:
                major = latest_version.major_version + 1
                minor = 0
            else:
                major = latest_version.major_version
                minor = latest_version.minor_version + 1
        else:
            major, minor = 1, 0
        
        version_number = f"{major}.{minor}"
        
        # 创建快照数据
        snapshot_data = self._create_snapshot(report)
        
        # 计算变更记录
        changes = []
        if latest_version:
            changes = self._calculate_changes(
                latest_version.snapshot_data or {},
                snapshot_data
            )
        
        # 创建新版本
        new_version = ReportVersion(
            report_id=report_id,
            version_number=version_number,
            major_version=major,
            minor_version=minor,
            content=report.content,
            statistics=report.statistics,
            sections=report.sections,
            snapshot_data=snapshot_data,
            change_summary=change_summary or self._generate_change_summary(changes),
            change_reason=change_reason,
            created_by=created_by,
            status='draft',
            is_current=True,
        )
        
        # 取消旧版本的 is_current 标记
        self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_current == True
        ).update({'is_current': False})
        
        self.db.add(new_version)
        self.db.commit()
        self.db.refresh(new_version)
        
        # 保存变更记录
        for change in changes:
            change_record = ReportVersionChange(
                version_id=new_version.id,
                **change
            )
            self.db.add(change_record)
        
        # 更新报告的当前版本引用
        report.current_version_id = new_version.id
        report.latest_version_number = version_number
        report.version_count = (report.version_count or 0) + 1
        self.db.commit()
        
        logger.info(f"Created version {version_number} for report {report_id}")
        return new_version
    
    def get_version(self, report_id: int, version_number: str) -> Optional[ReportVersion]:
        """获取指定版本"""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.version_number == version_number
        ).first()
    
    def list_versions(
        self,
        report_id: int,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ReportVersion], int]:
        """列出报告的所有版本"""
        query = self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id
        ).order_by(ReportVersion.created_at.desc())
        
        total = query.count()
        versions = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return versions, total
    
    def compare_versions(
        self,
        report_id: int,
        version_a: str,
        version_b: str,
    ) -> Dict:
        """
        对比两个版本的差异
        
        Returns:
            {
                "version_a": "1.0",
                "version_b": "1.1",
                "changes": [...],
                "summary": {"added": 5, "modified": 3, "deleted": 1}
            }
        """
        v_a = self.get_version(report_id, version_a)
        v_b = self.get_version(report_id, version_b)
        
        if not v_a or not v_b:
            raise ValueError("Version not found")
        
        diff = DeepDiff(
            v_a.snapshot_data or {},
            v_b.snapshot_data or {},
            ignore_order=True
        )
        
        changes = self._parse_diff(diff)
        summary = {
            "added": len([c for c in changes if c['change_type'] == 'add']),
            "modified": len([c for c in changes if c['change_type'] == 'modify']),
            "deleted": len([c for c in changes if c['change_type'] == 'delete']),
        }
        
        return {
            "version_a": version_a,
            "version_b": version_b,
            "changes": changes,
            "summary": summary,
        }
    
    def rollback_to_version(
        self,
        report_id: int,
        version_number: str,
        created_by: str = None,
    ) -> ReportVersion:
        """
        回滚到指定版本
        
        创建一个新版本，内容复制自目标版本
        """
        target_version = self.get_version(report_id, version_number)
        if not target_version:
            raise ValueError(f"Version {version_number} not found")
        
        report = self.db.query(Report).filter(Report.id == report_id).first()
        
        # 恢复报告内容
        report.content = target_version.content
        report.statistics = target_version.statistics
        report.sections = target_version.sections
        
        self.db.commit()
        
        # 创建新版本记录回滚操作
        new_version = self.create_version(
            report_id=report_id,
            is_major=False,
            change_summary=f"回滚到版本 {version_number}",
            change_reason=f"Rollback from version {version_number}",
            created_by=created_by,
        )
        
        return new_version
    
    def set_baseline(self, report_id: int, version_number: str) -> ReportVersion:
        """设置基线版本"""
        version = self.get_version(report_id, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")
        
        # 取消旧的基线标记
        self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id,
            ReportVersion.is_baseline == True
        ).update({'is_baseline': False})
        
        # 设置新基线
        version.is_baseline = True
        version.status = 'approved'
        
        # 更新报告的基线版本引用
        report = self.db.query(Report).filter(Report.id == report_id).first()
        report.baseline_version_id = version.id
        
        self.db.commit()
        self.db.refresh(version)
        
        return version
    
    def approve_version(
        self,
        report_id: int,
        version_number: str,
        approved_by: str,
    ) -> ReportVersion:
        """审批版本"""
        version = self.get_version(report_id, version_number)
        if not version:
            raise ValueError(f"Version {version_number} not found")
        
        version.status = 'approved'
        version.approved_by = approved_by
        version.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(version)
        
        return version
    
    # ==================== Private Methods ====================
    
    def _get_latest_version(self, report_id: int) -> Optional[ReportVersion]:
        """获取最新版本"""
        return self.db.query(ReportVersion).filter(
            ReportVersion.report_id == report_id
        ).order_by(
            ReportVersion.major_version.desc(),
            ReportVersion.minor_version.desc()
        ).first()
    
    def _create_snapshot(self, report: Report) -> Dict:
        """创建报告的完整数据快照"""
        from app.common.models import Asset, ThreatRisk, ControlMeasure
        
        # 获取关联数据
        assets = self.db.query(Asset).filter(
            Asset.project_id == report.project_id
        ).all()
        
        threats = self.db.query(ThreatRisk).filter(
            ThreatRisk.project_id == report.project_id
        ).all()
        
        measures = self.db.query(ControlMeasure).join(
            ThreatRisk, ControlMeasure.threat_risk_id == ThreatRisk.id
        ).filter(
            ThreatRisk.project_id == report.project_id
        ).all()
        
        return {
            "project": {
                "id": report.project_id,
                "name": report.project.name if report.project else None,
            },
            "report": {
                "id": report.id,
                "name": report.name,
                "template": report.template,
            },
            "assets": [
                {"id": a.id, "name": a.name, "asset_type": a.asset_type}
                for a in assets
            ],
            "threats": [
                {"id": t.id, "threat_name": t.threat_name, "risk_level": t.risk_level}
                for t in threats
            ],
            "measures": [
                {"id": m.id, "name": m.name, "control_type": m.control_type}
                for m in measures
            ],
            "statistics": report.statistics,
            "captured_at": datetime.now().isoformat(),
        }
    
    def _calculate_changes(
        self,
        old_snapshot: Dict,
        new_snapshot: Dict,
    ) -> List[Dict]:
        """计算两个快照之间的变更"""
        changes = []
        
        # 比较资产变更
        old_assets = {a['id']: a for a in old_snapshot.get('assets', [])}
        new_assets = {a['id']: a for a in new_snapshot.get('assets', [])}
        
        for aid, asset in new_assets.items():
            if aid not in old_assets:
                changes.append({
                    'change_type': 'add',
                    'entity_type': 'asset',
                    'entity_id': aid,
                    'entity_name': asset.get('name'),
                    'new_value': str(asset),
                })
            elif asset != old_assets[aid]:
                changes.append({
                    'change_type': 'modify',
                    'entity_type': 'asset',
                    'entity_id': aid,
                    'entity_name': asset.get('name'),
                    'old_value': str(old_assets[aid]),
                    'new_value': str(asset),
                })
        
        for aid, asset in old_assets.items():
            if aid not in new_assets:
                changes.append({
                    'change_type': 'delete',
                    'entity_type': 'asset',
                    'entity_id': aid,
                    'entity_name': asset.get('name'),
                    'old_value': str(asset),
                })
        
        # 同样的逻辑应用于 threats 和 measures
        # ... (类似实现)
        
        return changes
    
    def _generate_change_summary(self, changes: List[Dict]) -> str:
        """生成变更摘要"""
        if not changes:
            return "初始版本"
        
        adds = len([c for c in changes if c['change_type'] == 'add'])
        mods = len([c for c in changes if c['change_type'] == 'modify'])
        dels = len([c for c in changes if c['change_type'] == 'delete'])
        
        parts = []
        if adds:
            parts.append(f"新增 {adds} 项")
        if mods:
            parts.append(f"修改 {mods} 项")
        if dels:
            parts.append(f"删除 {dels} 项")
        
        return "，".join(parts) if parts else "无变更"
    
    def _parse_diff(self, diff) -> List[Dict]:
        """解析 DeepDiff 结果为变更列表"""
        changes = []
        
        # 解析新增项
        for item in diff.get('dictionary_item_added', []):
            changes.append({
                'change_type': 'add',
                'path': str(item),
                'new_value': diff.get('values_changed', {}).get(item),
            })
        
        # 解析删除项
        for item in diff.get('dictionary_item_removed', []):
            changes.append({
                'change_type': 'delete',
                'path': str(item),
            })
        
        # 解析修改项
        for path, change in diff.get('values_changed', {}).items():
            changes.append({
                'change_type': 'modify',
                'path': str(path),
                'old_value': change.get('old_value'),
                'new_value': change.get('new_value'),
            })
        
        return changes
```

---

## 4. API 接口设计

### 4.1 版本管理 API

```
POST   /api/v1/reports/{report_id}/versions              # 创建新版本
GET    /api/v1/reports/{report_id}/versions              # 列出所有版本
GET    /api/v1/reports/{report_id}/versions/{version}    # 获取指定版本
GET    /api/v1/reports/{report_id}/versions/current      # 获取当前版本
GET    /api/v1/reports/{report_id}/versions/baseline     # 获取基线版本

POST   /api/v1/reports/{report_id}/versions/compare      # 对比版本
POST   /api/v1/reports/{report_id}/versions/{version}/rollback   # 回滚到版本
POST   /api/v1/reports/{report_id}/versions/{version}/baseline   # 设置为基线
POST   /api/v1/reports/{report_id}/versions/{version}/approve    # 审批版本
```

### 4.2 接口详细规范

#### 4.2.1 创建新版本

```http
POST /api/v1/reports/{report_id}/versions
Content-Type: application/json

Request:
{
  "is_major": false,
  "change_summary": "更新威胁分析结果",
  "change_reason": "根据安全团队评审意见修改"
}

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "id": 5,
    "report_id": 1,
    "version_number": "1.3",
    "major_version": 1,
    "minor_version": 3,
    "change_summary": "更新威胁分析结果",
    "status": "draft",
    "is_current": true,
    "is_baseline": false,
    "created_by": "张工程师",
    "created_at": "2024-12-16T15:30:00Z"
  }
}
```

#### 4.2.2 列出版本历史

```http
GET /api/v1/reports/{report_id}/versions?page=1&page_size=10

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "versions": [
      {
        "id": 5,
        "version_number": "1.3",
        "change_summary": "更新威胁分析结果",
        "status": "draft",
        "is_current": true,
        "is_baseline": false,
        "created_by": "张工程师",
        "created_at": "2024-12-16T15:30:00Z"
      },
      {
        "id": 4,
        "version_number": "1.2",
        "change_summary": "新增 3 个安全措施",
        "status": "approved",
        "is_current": false,
        "is_baseline": true,
        "created_by": "李工程师",
        "approved_by": "王总监",
        "approved_at": "2024-12-15T10:00:00Z",
        "created_at": "2024-12-14T09:00:00Z"
      }
    ],
    "total": 5,
    "current_version": "1.3",
    "baseline_version": "1.2"
  }
}
```

#### 4.2.3 版本对比

```http
POST /api/v1/reports/{report_id}/versions/compare
Content-Type: application/json

Request:
{
  "version_a": "1.1",
  "version_b": "1.3"
}

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "version_a": "1.1",
    "version_b": "1.3",
    "summary": {
      "added": 2,
      "modified": 5,
      "deleted": 1
    },
    "changes": [
      {
        "change_type": "add",
        "entity_type": "threat",
        "entity_name": "CAN消息重放攻击",
        "description": "新增威胁识别"
      },
      {
        "change_type": "modify",
        "entity_type": "asset",
        "entity_name": "IVI ECU",
        "field_name": "security_attrs",
        "old_value": {"confidentiality": false},
        "new_value": {"confidentiality": true},
        "description": "更新安全属性"
      },
      {
        "change_type": "delete",
        "entity_type": "measure",
        "entity_name": "临时措施1",
        "description": "删除临时控制措施"
      }
    ]
  }
}
```

---

## 5. 一键生成与版本管理集成

### 5.1 一键生成流程增强

```python
async def start_generation(
    self,
    task_id: str,
    files: List[UploadFile],
    template: str,
    prompt: str,
    project_name: str,
    project_id: Optional[int] = None,  # 新增: 支持关联到现有项目
    create_new_version: bool = True,   # 新增: 是否为现有报告创建新版本
    task_storage: dict,
) -> Dict[str, Any]:
    """
    初始化报告生成过程
    
    支持两种模式:
    1. 创建新项目 + 新报告 (project_id=None)
    2. 关联现有项目 + 创建新版本 (project_id=existing_id)
    """
    if project_id:
        # 模式2: 关联到现有项目
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # 获取或创建报告
        existing_report = self.db.query(Report).filter(
            Report.project_id == project_id,
            Report.report_type == "tara"
        ).first()
        
        if existing_report and create_new_version:
            # 为现有报告创建新版本
            report = existing_report
            # 版本将在生成完成后创建
        else:
            # 创建新报告
            report = Report(...)
    else:
        # 模式1: 创建新项目 + 新报告
        project = Project(...)
        report = Report(...)
    
    return {
        "project_id": project.id,
        "report_id": report.id,
        "is_new_project": project_id is None,
        "create_version": create_new_version and existing_report is not None,
    }
```

### 5.2 生成完成后创建版本

```python
async def _finalize_generation(
    self,
    report_id: int,
    report_data: Dict,
    create_version: bool = True,
) -> None:
    """生成完成后的处理"""
    
    # 保存报告内容
    await self._save_report_to_db_v2(report_id, report_data)
    
    # 创建版本记录
    if create_version:
        version_service = ReportVersionService(self.db)
        version_service.create_version(
            report_id=report_id,
            is_major=True,  # 一键生成通常是主版本
            change_summary="一键生成TARA分析报告",
            change_reason="自动生成",
            created_by="system",
        )
```

---

## 6. 前端设计

### 6.1 版本管理界面

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          报告详情 - IVI系统TARA分析                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 📊 当前版本: v1.3 (草稿)    🏷️ 基线版本: v1.2 (已审批)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 版本历史                                                [创建新版本]  │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │                                                                     │   │
│  │  ○ v1.3 (当前)                                     2024-12-16 15:30 │   │
│  │    └─ 更新威胁分析结果                                  张工程师    │   │
│  │    └─ [预览] [设为基线] [审批]                                      │   │
│  │                                                                     │   │
│  │  ● v1.2 (基线)                                     2024-12-15 10:00 │   │
│  │    └─ 新增 3 个安全措施                      ✓ 已审批 by 王总监     │   │
│  │    └─ [预览] [对比] [回滚到此版本]                                  │   │
│  │                                                                     │   │
│  │  ○ v1.1                                            2024-12-14 14:00 │   │
│  │    └─ 初始分析完成                                      李工程师    │   │
│  │    └─ [预览] [对比] [回滚到此版本]                                  │   │
│  │                                                                     │   │
│  │  ○ v1.0                                            2024-12-13 09:00 │   │
│  │    └─ 一键生成TARA分析报告                              system      │   │
│  │    └─ [预览] [对比] [回滚到此版本]                                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 版本对比                                                             │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  选择版本: [v1.1 ▼]  对比  [v1.3 ▼]        [开始对比]              │   │
│  │                                                                     │   │
│  │  变更摘要: 新增 2 项 | 修改 5 项 | 删除 1 项                        │   │
│  │                                                                     │   │
│  │  详细变更:                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ + [威胁] CAN消息重放攻击                                    │   │   │
│  │  │ ~ [资产] IVI ECU - 安全属性更新                            │   │   │
│  │  │ - [措施] 临时措施1                                         │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 项目关联选择

一键生成报告时的项目选择界面:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            一键生成TARA报告                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  项目关联方式:                                                              │
│                                                                             │
│  ○ 创建新项目                                                              │
│    └─ 项目名称: [________________]                                         │
│                                                                             │
│  ● 关联现有项目                                                            │
│    └─ 选择项目: [IVI系统TARA分析 ▼]                                       │
│    └─ ☑ 为现有报告创建新版本 (推荐)                                       │
│    └─ ☐ 创建新的独立报告                                                  │
│                                                                             │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                             │
│  上传文件:                                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  📎 拖拽文件至此或点击上传                                           │   │
│  │     支持: .xlsx, .csv, .json, .pdf, .png                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  已选文件:                                                                  │
│  • asset_list_v2.xlsx    (15KB)    [×]                                     │
│  • architecture.png      (245KB)   [×]                                     │
│                                                                             │
│                                            [取消]  [开始生成]              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. 实施路线图

### Phase 1: 基础版本管理 (1-2周)

1. 创建 `report_versions` 表
2. 实现 `ReportVersionService` 核心方法
3. 添加版本创建、列表、查看 API
4. 修改一键生成流程，自动创建初始版本

### Phase 2: 版本对比与回滚 (1周)

1. 实现版本对比算法
2. 添加版本回滚功能
3. 创建 `report_version_changes` 表
4. 实现变更追踪

### Phase 3: 基线管理与审批 (1周)

1. 实现基线版本设置
2. 添加版本审批流程
3. 添加版本状态管理

### Phase 4: 前端界面 (1-2周)

1. 版本历史列表组件
2. 版本对比可视化
3. 项目关联选择器
4. 一键生成流程增强

---

## 8. 总结

### 核心设计要点

1. **Report-Project 关联**: 通过 `project_id` 外键建立一对多关系
2. **版本存储**: 每个版本保存完整的快照数据，便于回滚和对比
3. **版本号规则**: 采用 `major.minor` 格式，支持主版本和次版本升级
4. **基线管理**: 支持设置基线版本作为对比基准
5. **变更追踪**: 记录每个版本的详细变更历史
6. **向后兼容**: 现有报告可以通过创建 v1.0 版本纳入版本管理

### 优势

- 完整的版本历史追踪
- 支持版本间差异对比
- 灵活的回滚机制
- 基线管理满足合规需求
- 与现有一键生成流程无缝集成
