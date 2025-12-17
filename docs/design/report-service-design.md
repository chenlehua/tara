# 报告服务详细设计文档

## 1. 概述

报告服务（Report Service）是TARA Pro系统的核心服务之一，负责生成、管理和导出符合ISO/SAE 21434标准的TARA分析报告。该服务支持一键生成报告、多格式导出（PDF、Word、Excel）以及报告预览功能。

### 1.1 服务职责

- **报告生成**: 基于项目数据自动生成TARA分析报告
- **一键生成**: 从上传的文件（资产清单、架构图等）自动完成资产识别、威胁分析、风险评估和报告生成
- **多格式导出**: 支持PDF、Word（DOCX）、Excel（XLSX）格式导出
- **报告管理**: 创建、查询、删除报告记录
- **进度追踪**: 实时追踪报告生成进度

### 1.2 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | FastAPI |
| ORM | SQLAlchemy |
| PDF生成 | ReportLab |
| Word生成 | python-docx |
| Excel生成 | openpyxl |
| 文件存储 | MinIO (可选) |
| 任务队列 | FastAPI BackgroundTasks |

---

## 2. 模块交互关系

### 2.1 服务依赖图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend (Vue.js)                               │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │ ReportGenerator│    │ ReportList  │    │ ReportDetail │                 │
│   │    (一键生成) │    │  (报告列表)  │    │  (报告预览)  │                 │
│   └───────┬───────┘    └───────┬──────┘    └───────┬──────┘                 │
└───────────┼────────────────────┼───────────────────┼────────────────────────┘
            │                    │                   │
            ▼                    ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API Gateway (Nginx)                               │
│                     /api/v1/reports/* → report-service:8006                 │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Report Service (8006)                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         API Layer                                    │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐             │   │
│  │  │ /reports     │  │ /reports/    │  │ /reports/      │             │   │
│  │  │  (CRUD)      │  │  oneclick    │  │  {id}/download │             │   │
│  │  └──────────────┘  └──────────────┘  └────────────────┘             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       Service Layer                                  │   │
│  │  ┌──────────────────┐    ┌────────────────────────┐                 │   │
│  │  │  ReportService   │    │  OneClickGenerateService│                 │   │
│  │  │  - CRUD操作      │    │  - 文件解析             │                 │   │
│  │  │  - 数据收集      │    │  - 资产识别             │                 │   │
│  │  │  - 文件生成      │    │  - 威胁分析             │                 │   │
│  │  └──────────────────┘    │  - 风险评估             │                 │   │
│  │                          │  - 报告生成             │                 │   │
│  │                          └────────────────────────┘                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Generator Layer                                 │   │
│  │  ┌────────────┐    ┌────────────┐    ┌─────────────┐                │   │
│  │  │PDFGenerator│    │WordGenerator│    │ExcelGenerator│                │   │
│  │  └────────────┘    └────────────┘    └─────────────┘                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
            │                    │                   │
            ▼                    ▼                   ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Project Service │  │  Asset Service  │  │ Threat Service  │
│     (8001)       │  │     (8003)      │  │     (8004)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
            │                    │                   │
            └────────────────────┼───────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │    Shared Database      │
                    │       (MySQL)           │
                    └─────────────────────────┘
```

### 2.2 服务间通信

| 源服务 | 目标服务 | 通信方式 | 说明 |
|--------|----------|----------|------|
| Report Service | Database | 直接访问 | 通过SQLAlchemy ORM访问MySQL |
| Report Service | MinIO | HTTP | 文件存储和检索 |
| Report Service | Diagram Service | 可选HTTP | 获取图表（未来增强） |
| Frontend | Report Service | REST API | 通过Nginx反向代理 |

### 2.3 数据依赖关系

```
Report 依赖:
├── Project (项目信息)
│   ├── name, description
│   ├── vehicle_type, vehicle_model
│   └── standard, scope
├── Asset (资产数据)
│   ├── name, asset_type, category
│   ├── interfaces, security_attrs
│   └── criticality
├── ThreatRisk (威胁数据)
│   ├── threat_name, threat_type
│   ├── attack_vector, attack_path
│   ├── impact_level, risk_level
│   └── safety/financial/operational/privacy_impact
└── ControlMeasure (控制措施)
    ├── name, control_type
    ├── implementation, effectiveness
    └── iso21434_ref
```

---

## 3. 一键生成报告流程

### 3.1 流程概述

一键生成报告是报告服务的核心功能，允许用户上传文件后自动完成完整的TARA分析流程。

### 3.2 时序图

```
┌────────┐      ┌─────────┐      ┌──────────────┐      ┌─────────┐      ┌────────┐
│Frontend│      │  Nginx  │      │Report Service│      │ Database │      │ Storage│
└───┬────┘      └────┬────┘      └──────┬───────┘      └────┬────┘      └───┬────┘
    │                │                  │                   │               │
    │ POST /reports/oneclick            │                   │               │
    │ [files, template, prompt]         │                   │               │
    │───────────────────────────────────>                   │               │
    │                │                  │                   │               │
    │                │  Forward Request │                   │               │
    │                │─────────────────>│                   │               │
    │                │                  │                   │               │
    │                │                  │ start_generation()│               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │  Save Files       │               │
    │                │                  │──────────────────────────────────>│
    │                │                  │                   │               │
    │                │                  │ Create Project    │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Create Report     │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Return task_id    │               │
    │                │<─────────────────│                   │               │
    │                │                  │                   │               │
    │ Response: {task_id, report_id}    │                   │               │
    │<───────────────────────────────────                   │               │
    │                │                  │                   │               │
    │                │                  │ ═══════════════════════════════════
    │                │                  │ ║ Background Task (run_generation) ║
    │                │                  │ ═══════════════════════════════════
    │                │                  │                   │               │
    │                │                  │ Step 1: 解析文件  │               │
    │                │                  │ _parse_files()    │               │
    │                │                  │──────────────────────────────────>│
    │                │                  │                   │               │
    │                │                  │ Step 2: 识别资产  │               │
    │                │                  │ _identify_assets()│               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Save Assets       │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │ GET /oneclick/{task_id}/progress  │                   │               │
    │───────────────────────────────────>                   │               │
    │ Response: {progress: 30%}         │                   │               │
    │<───────────────────────────────────                   │               │
    │                │                  │                   │               │
    │                │                  │ Step 3: 威胁分析  │               │
    │                │                  │ _analyze_threats()│               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Save Threats      │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │ GET /oneclick/{task_id}/progress  │                   │               │
    │───────────────────────────────────>                   │               │
    │ Response: {progress: 50%}         │                   │               │
    │<───────────────────────────────────                   │               │
    │                │                  │                   │               │
    │                │                  │ Step 4: 风险评估  │               │
    │                │                  │ _assess_risks()   │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Save Measures     │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Step 5: 生成报告  │               │
    │                │                  │ _generate_report()│               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Save Report       │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │ GET /oneclick/{task_id}/progress  │                   │               │
    │───────────────────────────────────>                   │               │
    │ Response: {status: completed}     │                   │               │
    │<───────────────────────────────────                   │               │
    │                │                  │                   │               │
    │ GET /reports/{id}/download?format=pdf                 │               │
    │───────────────────────────────────>                   │               │
    │                │                  │ Get Report        │               │
    │                │                  │──────────────────>│               │
    │                │                  │                   │               │
    │                │                  │ Generate PDF      │               │
    │                │                  │────────────────>  │               │
    │ Response: PDF File                │                   │               │
    │<───────────────────────────────────                   │               │
    │                │                  │                   │               │
```

### 3.3 处理步骤详解

#### Step 1: 文件解析 (10%)
```python
async def _parse_files(file_paths: List[str]) -> Dict:
    # 支持的文件类型:
    # - JSON: 资产清单、威胁数据
    # - CSV: 资产清单
    # - Excel: 资产清单
    # - 图片: 架构图（用于存档）
```

#### Step 2: 资产识别 (30%)
```python
async def _identify_assets(parsed_data: Dict) -> List[Dict]:
    # 基于STRIDE模型识别资产类型
    # 生成安全属性（CIA-AAA）
    # 识别接口和连接关系
```

#### Step 3: 威胁分析 (50%)
```python
async def _analyze_threats(assets: List, template: str, prompt: str) -> List[Dict]:
    # 应用STRIDE威胁模型
    # 生成威胁场景
    # 计算攻击可行性
```

#### Step 4: 风险评估 (75%)
```python
async def _assess_risks(threats: List) -> Dict:
    # 计算影响等级（Safety, Financial, Operational, Privacy）
    # 评估风险等级（CAL-1 to CAL-4）
    # 生成控制措施建议
```

#### Step 5: 报告生成 (100%)
```python
async def _generate_report(...) -> Dict:
    # 汇总所有分析结果
    # 保存到数据库
    # 生成报告内容JSON
```

---

## 4. API接口规范

### 4.1 基础信息

| 属性 | 值 |
|------|-----|
| Base URL | `/api/v1/reports` |
| 认证方式 | Bearer Token |
| 响应格式 | JSON |
| 服务端口 | 8006 |

### 4.2 接口列表

#### 4.2.1 创建报告

```http
POST /api/v1/reports
Content-Type: application/json

Request:
{
  "project_id": 1,
  "name": "TARA分析报告",
  "report_type": "tara",
  "description": "描述信息",
  "template": "iso21434",
  "sections": ["scope", "assets", "threats", "risks", "controls"],
  "file_format": "pdf",
  "author": "张工程师"
}

Response:
{
  "success": true,
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "project_id": 1,
    "name": "TARA分析报告",
    "report_type": "tara",
    "status": 0,
    "progress": 0,
    "created_at": "2024-12-16T10:00:00Z",
    "updated_at": "2024-12-16T10:00:00Z"
  }
}
```

#### 4.2.2 获取报告列表

```http
GET /api/v1/reports?project_id=1&page=1&page_size=20&status=2

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "items": [
      {
        "id": 1,
        "project_id": 1,
        "name": "TARA分析报告",
        "status": 2,
        "progress": 100,
        "statistics": {
          "assets_count": 8,
          "threats_count": 10,
          "measures_count": 12,
          "high_risk_count": 4
        },
        "created_at": "2024-12-16T10:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

#### 4.2.3 获取报告详情

```http
GET /api/v1/reports/{report_id}

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "id": 1,
    "project_id": 1,
    "name": "TARA分析报告",
    "status": 2,
    "content": {
      "project": {...},
      "assets": [...],
      "threats": [...],
      "control_measures": [...],
      "risk_distribution": {...}
    },
    "statistics": {...}
  }
}
```

#### 4.2.4 删除报告

```http
DELETE /api/v1/reports/{report_id}

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "message": "Report deleted"
  }
}
```

#### 4.2.5 一键生成报告

```http
POST /api/v1/reports/oneclick
Content-Type: multipart/form-data

Request:
- files: File[] (资产清单、架构图等)
- template: string (full | threat | risk | measure)
- prompt: string (分析提示词)
- project_name: string (项目名称，可选)

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "task_id": "uuid-xxx-xxx",
    "report_id": 1,
    "project_id": 1,
    "status": "processing",
    "message": "报告生成已启动"
  }
}
```

#### 4.2.6 获取生成进度

```http
GET /api/v1/reports/oneclick/{task_id}/progress

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "task_id": "uuid-xxx-xxx",
    "status": "processing",  // processing | completed | failed
    "progress": 50,
    "current_step": "威胁分析",
    "steps": [
      {"label": "解析文件", "completed": true, "active": false},
      {"label": "识别资产", "completed": true, "active": false},
      {"label": "威胁分析", "completed": false, "active": true},
      {"label": "风险评估", "completed": false, "active": false},
      {"label": "生成报告", "completed": false, "active": false}
    ],
    "result": null,
    "error": null
  }
}
```

#### 4.2.7 下载报告

```http
GET /api/v1/reports/{report_id}/download?format=pdf

Parameters:
- format: pdf | docx | xlsx

Response:
- Content-Type: application/pdf (或对应MIME类型)
- Content-Disposition: attachment; filename="report.pdf"
- Body: 二进制文件内容
```

#### 4.2.8 报告预览

```http
GET /api/v1/reports/{report_id}/preview

Response:
{
  "success": true,
  "code": 200,
  "data": {
    "id": 1,
    "name": "TARA分析报告",
    "template": "iso21434",
    "status": 2,
    "statistics": {
      "assets_count": 8,
      "threats_count": 10,
      "measures_count": 12
    },
    "sections": [
      {"id": "assets", "title": "资产清单", "count": 8},
      {"id": "threats", "title": "威胁分析", "count": 10},
      {"id": "risks", "title": "风险评估", "count": 10}
    ],
    "content": {
      "project": {...},
      "assets": [...],
      "threats": [...],
      "control_measures": [...],
      "risk_distribution": {...}
    }
  }
}
```

### 4.3 状态码说明

| 状态码 | 含义 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 4.4 报告状态枚举

| 值 | 名称 | 说明 |
|----|------|------|
| 0 | PENDING | 待处理 |
| 1 | GENERATING | 生成中 |
| 2 | COMPLETED | 已完成 |
| 3 | FAILED | 失败 |

---

## 5. 存储设计

### 5.1 数据库模型

#### 5.1.1 Report表

```sql
CREATE TABLE reports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    project_id INT NOT NULL,
    name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) DEFAULT 'tara',
    description TEXT,
    template VARCHAR(50),
    
    -- 生成状态
    status INT DEFAULT 0,  -- 0:pending, 1:generating, 2:completed, 3:failed
    progress INT DEFAULT 0,  -- 0-100
    error_message TEXT,
    
    -- 文件信息
    file_path VARCHAR(500),
    file_format VARCHAR(20),
    file_size INT,
    
    -- 内容存储
    content JSON,  -- 报告内容
    sections JSON,  -- 章节列表
    
    -- 元数据
    version VARCHAR(20) DEFAULT '1.0',
    author VARCHAR(100),
    reviewer VARCHAR(100),
    review_status INT DEFAULT 0,
    
    -- 统计数据
    statistics JSON,
    
    -- 时间戳
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- 外键
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    
    -- 索引
    INDEX idx_project_id (project_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 5.1.2 content字段结构

```json
{
  "project": {
    "id": 1,
    "name": "项目名称",
    "description": "项目描述",
    "vehicle_type": "乘用车",
    "vehicle_model": "Model X",
    "standard": "ISO/SAE 21434"
  },
  "assets": [
    {
      "id": 1,
      "name": "资产名称",
      "asset_type": "ECU",
      "category": "内部实体",
      "interfaces": [{"type": "CAN", "connected_to": "Gateway"}],
      "security_attrs": {
        "authenticity": true,
        "integrity": true,
        "confidentiality": false,
        "availability": true
      },
      "criticality": "high"
    }
  ],
  "threats": [
    {
      "id": 1,
      "name": "威胁名称",
      "threat_type": "T",
      "category_name": "Tampering",
      "attack_vector": "Network",
      "attack_path": "WiFi -> IVI",
      "safety_impact": 2,
      "financial_impact": 3,
      "operational_impact": 3,
      "privacy_impact": 4,
      "risk_level": "CAL-3"
    }
  ],
  "control_measures": [
    {
      "id": 1,
      "name": "措施名称",
      "control_type": "prevention",
      "category": "加密",
      "implementation": "实施方案",
      "effectiveness": "high",
      "iso21434_ref": "RQ-09-01"
    }
  ],
  "risk_distribution": {
    "CAL-4": 2,
    "CAL-3": 4,
    "CAL-2": 3,
    "CAL-1": 1
  }
}
```

#### 5.1.3 statistics字段结构

```json
{
  "assets_count": 8,
  "threats_count": 10,
  "measures_count": 12,
  "high_risk_count": 6,
  "total_assets": 8,
  "total_threats": 10,
  "total_controls": 12,
  "critical_risks": 2,
  "high_risks": 4,
  "medium_risks": 3,
  "low_risks": 1
}
```

### 5.2 文件存储

#### 5.2.1 临时文件

- 路径: `/tmp/tara_uploads/{task_id}/`
- 用途: 存储上传的原始文件
- 生命周期: 任务完成后可清理

#### 5.2.2 MinIO对象存储（可选）

| Bucket | 用途 | 对象命名 |
|--------|------|----------|
| reports | 生成的报告文件 | `{report_id}/{filename}.{format}` |
| uploads | 上传的原始文件 | `{project_id}/{filename}` |
| diagrams | 生成的图表 | `{project_id}/{diagram_type}.png` |

### 5.3 缓存策略

#### 5.3.1 任务进度缓存

```python
# 内存缓存（当前实现）
_generation_tasks = {
    "task_id": {
        "status": "processing",
        "progress": 50,
        "current_step": "威胁分析",
        "steps": [...],
        "result": None,
        "error": None
    }
}

# Redis缓存（生产环境推荐）
# Key: tara:task:{task_id}
# TTL: 3600s
```

---

## 6. 报告生成器

### 6.1 PDF生成器 (PDFGenerator)

- **库**: ReportLab
- **中文支持**: 
  - 优先使用 STSong-Light CID字体
  - 备选系统TTF字体（WQY-ZenHei, Noto Sans CJK等）
- **章节结构**:
  1. 封面和项目信息
  2. 架构概述（项目边界、系统架构、软件架构）
  3. 资产识别
  4. 威胁分析
  5. 风险评估
  6. 控制措施

### 6.2 Word生成器 (WordGenerator)

- **库**: python-docx
- **样式**: 
  - 表格使用自定义样式（紫色表头，交替行颜色）
  - 支持多级标题
- **章节结构**: 与PDF保持一致

### 6.3 Excel生成器 (ExcelGenerator)

- **库**: openpyxl
- **工作表结构**:
  1. `1-相关定义`: 项目信息、边界图、架构图、参考标准
  2. `2-资产列表`: 资产识别和安全属性
  3. `3-数据流图`: 数据流分析和接口列表
  4. `4-攻击树图`: STRIDE分类的攻击树
  5. `5-TARA分析结果`: 完整的TARA分析表格

---

## 7. 部署配置

### 7.1 服务配置

```yaml
# docker-compose.yml
report-service:
  build:
    context: ./backend/report-service
    dockerfile: Dockerfile
  ports:
    - "8006:8006"
  environment:
    - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/tara
    - MINIO_ENDPOINT=minio:9000
    - MINIO_ACCESS_KEY=minioadmin
    - MINIO_SECRET_KEY=minioadmin
  depends_on:
    - mysql
    - minio
```

### 7.2 Nginx路由

```nginx
location /api/v1/reports {
    limit_req zone=api_limit burst=20 nodelay;
    set $report_upstream http://report-service:8006;
    proxy_pass $report_upstream;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 300;  # 长超时支持报告生成
}
```

---

## 8. 未来增强

### 8.1 计划功能

1. **AI增强分析**: 集成AI Agent进行更智能的威胁分析
2. **图表服务集成**: 调用Diagram Service生成可视化图表嵌入报告
3. **报告模板管理**: 支持自定义报告模板
4. **报告版本控制**: 支持报告修订历史
5. **协同审批**: 支持多人审批工作流
6. **批量导出**: 支持批量生成和导出报告

### 8.2 性能优化

1. **异步任务队列**: 使用Celery替代BackgroundTasks
2. **分布式缓存**: 使用Redis存储任务状态
3. **文件生成优化**: 增量生成和缓存
4. **数据库查询优化**: 预加载关联数据

---

## 附录

### A. 相关文档

- [系统架构文档](./architecture.md)
- [数据模型设计](./data-model.md)
- [API规范](../api/openapi.yaml)
- [部署指南](../development/deployment.md)

### B. 更新历史

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| 1.0 | 2024-12-16 | TARA Pro | 初始版本 |
