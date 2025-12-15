# AI Agent 架构

## 概述

TARA System 使用 AI Agent 实现智能化的威胁分析与风险评估。Agent 采用 Model Context Protocol (MCP) 架构，支持工具调用和多轮对话。

## Agent 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Orchestrator                          │
│                     (任务编排与状态管理)                            │
└─────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │Document │   │ Asset   │   │ Threat  │   │ Report  │
    │ Agent   │   │ Agent   │   │ Agent   │   │ Agent   │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    MCP Server Layer                      │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
    │  │Knowledge │ │ Database │ │Inference │ │  Report  │   │
    │  │ Server   │ │  Server  │ │  Server  │ │  Server  │   │
    │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
    └─────────────────────────────────────────────────────────┘
                              │
                              ▼
    ┌─────────────────────────────────────────────────────────┐
    │                     AI Model Layer                       │
    │         Qwen3  │  Qwen3-VL  │  Embedding  │  OCR        │
    └─────────────────────────────────────────────────────────┘
```

## Agent 说明

### 1. Document Agent

**职责**: 文档解析与内容提取

**工具**:
- `parse_document`: 解析文档内容
- `extract_structure`: 提取文档结构
- `ocr_image`: OCR 识别图片文字
- `analyze_diagram`: 分析架构图

**工作流程**:
```
文档上传 → OCR/文本提取 → 结构分析 → 内容提取 → 实体识别
```

### 2. Asset Agent

**职责**: 资产发现与关系建模

**工具**:
- `discover_assets`: 从文档发现资产
- `classify_asset`: 资产分类
- `identify_relationships`: 识别资产关系
- `build_graph`: 构建资产图谱

**工作流程**:
```
内容分析 → 实体提取 → 资产分类 → 关系识别 → 图谱构建
```

### 3. Threat Agent

**职责**: 威胁分析与风险评估

**工具**:
- `stride_analysis`: STRIDE 威胁分析
- `analyze_attack_path`: 攻击路径分析
- `assess_feasibility`: 可行性评估
- `calculate_risk`: 风险计算
- `recommend_controls`: 控制措施推荐

**工作流程**:
```
资产分析 → STRIDE建模 → 攻击路径 → 可行性评估 → 风险计算 → 控制推荐
```

### 4. Report Agent

**职责**: 报告生成与导出

**工具**:
- `collect_data`: 收集报告数据
- `write_section`: 撰写报告章节
- `generate_chart`: 生成图表
- `export_report`: 导出报告文件

**工作流程**:
```
数据收集 → 内容撰写 → 图表生成 → 格式化 → 导出
```

## MCP Server

### Knowledge Server
提供威胁库、控制措施库、标准要求等知识检索服务。

```python
@server.tool()
async def search_threats(query: str, stride_type: str = None):
    """Search threat library."""
    ...

@server.tool()
async def get_controls(threat_type: str):
    """Get recommended controls for threat type."""
    ...
```

### Database Server
提供数据库 CRUD 操作接口。

```python
@server.tool()
async def get_project(project_id: int):
    """Get project details."""
    ...

@server.tool()
async def create_asset(data: dict):
    """Create new asset."""
    ...
```

### Inference Server
提供 AI 模型推理服务。

```python
@server.tool()
async def generate(prompt: str, max_tokens: int = 1024):
    """Generate text with LLM."""
    ...

@server.tool()
async def embed(text: str):
    """Get text embedding."""
    ...
```

## 工作流示例

### 完整 TARA 分析流程

```python
async def run_full_analysis(project_id: int):
    orchestrator = AgentOrchestrator()
    
    # Phase 1: Document Parsing
    documents = await document_agent.process_documents(project_id)
    
    # Phase 2: Asset Discovery
    assets = await asset_agent.discover_assets(documents)
    relationships = await asset_agent.identify_relationships(assets)
    
    # Phase 3: Threat Analysis
    for asset in assets:
        threats = await threat_agent.stride_analysis(asset)
        for threat in threats:
            paths = await threat_agent.analyze_attack_path(threat)
            await threat_agent.assess_feasibility(paths)
        await threat_agent.calculate_risk(threats)
    
    # Phase 4: Report Generation
    report = await report_agent.generate_report(project_id)
    
    return report
```

## 配置

### Agent 配置
```yaml
agents:
  document:
    model: qwen3-vl
    max_retries: 3
    timeout: 300
  
  asset:
    model: qwen3
    use_knowledge_base: true
  
  threat:
    model: qwen3
    use_stride_templates: true
  
  report:
    model: qwen3
    templates:
      - iso21434
      - simple
```

### 提示词模板
参见 `ai-models/prompts/` 目录下的提示词定义。

## 性能优化

1. **并行处理**: 对独立资产并行分析
2. **缓存**: 缓存 embedding 和中间结果
3. **批处理**: 批量处理同类请求
4. **流式输出**: 支持流式响应减少延迟
