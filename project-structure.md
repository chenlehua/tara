# 智能TARA分析系统 - MVP代码目录结构

```
tara-system/
├── README.md                           # 项目说明文档
├── LICENSE                             # 许可证
├── .gitignore                          # Git忽略配置
├── .env.example                        # 环境变量示例
├── Makefile                            # 常用命令封装
│
├── docs/                               # 📚 项目文档
│   ├── architecture/                   # 架构文档
│   │   ├── overview.md                 # 架构概述
│   │   ├── mvp-architecture.md         # MVP架构设计
│   │   └── diagrams/                   # 架构图
│   │       ├── system-architecture.mermaid
│   │       ├── workflow.mermaid
│   │       └── data-model.mermaid
│   ├── api/                            # API文档
│   │   └── openapi.yaml                # OpenAPI规范
│   ├── deployment/                     # 部署文档
│   │   ├── docker-deploy.md
│   │   └── k8s-deploy.md
│   └── user-guide/                     # 用户手册
│       └── user-manual.md
│
├── deploy/                             # 🚀 部署配置
│   ├── docker/                         # Docker部署
│   │   ├── docker-compose.yml          # 主编排文件
│   │   ├── docker-compose.gpu.yml      # GPU服务编排
│   │   ├── docker-compose.dev.yml      # 开发环境
│   │   └── dockerfiles/                # Dockerfile集合
│   │       ├── frontend.Dockerfile
│   │       ├── backend.Dockerfile
│   │       └── agent.Dockerfile
│   ├── kubernetes/                     # K8s部署
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── ingress.yaml
│   │   ├── services/                   # 服务部署
│   │   │   ├── frontend.yaml
│   │   │   ├── project-service.yaml
│   │   │   ├── document-service.yaml
│   │   │   ├── asset-service.yaml
│   │   │   ├── threat-risk-service.yaml
│   │   │   ├── diagram-service.yaml
│   │   │   ├── report-service.yaml
│   │   │   └── agent-service.yaml
│   │   ├── data/                       # 数据层部署
│   │   │   ├── mysql.yaml
│   │   │   ├── redis.yaml
│   │   │   ├── neo4j.yaml
│   │   │   ├── milvus.yaml
│   │   │   ├── elasticsearch.yaml
│   │   │   └── minio.yaml
│   │   └── models/                     # AI模型部署
│   │       ├── vllm-qwen3-vl.yaml
│   │       ├── vllm-qwen3.yaml
│   │       ├── ocrflux.yaml
│   │       └── embedding.yaml
│   ├── nginx/                          # Nginx配置
│   │   ├── nginx.conf
│   │   └── conf.d/
│   │       └── tara.conf
│   └── scripts/                        # 部署脚本
│       ├── init-db.sh                  # 数据库初始化
│       ├── start.sh                    # 启动脚本
│       └── backup.sh                   # 备份脚本
│
├── frontend/                           # 🖥️ 前端项目 (Vue3)
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── vite.config.ts                  # Vite配置
│   ├── tsconfig.json                   # TypeScript配置
│   ├── tailwind.config.js              # TailwindCSS配置
│   ├── .eslintrc.cjs                   # ESLint配置
│   ├── .prettierrc                     # Prettier配置
│   ├── index.html
│   ├── public/                         # 静态资源
│   │   ├── favicon.ico
│   │   └── logo.svg
│   └── src/
│       ├── main.ts                     # 入口文件
│       ├── App.vue                     # 根组件
│       ├── env.d.ts                    # 类型声明
│       │
│       ├── api/                        # API接口
│       │   ├── index.ts                # API统一导出
│       │   ├── request.ts              # Axios封装
│       │   ├── project.ts              # 项目管理API
│       │   ├── document.ts             # 文档解析API
│       │   ├── asset.ts                # 资产管理API
│       │   ├── threat-risk.ts          # 威胁风险API
│       │   ├── diagram.ts              # 图表API
│       │   ├── report.ts               # 报告API
│       │   └── agent.ts                # 智能体API
│       │
│       ├── views/                      # 页面视图
│       │   ├── project/                # 项目管理
│       │   │   ├── ProjectList.vue     # 项目列表
│       │   │   ├── ProjectDetail.vue   # 项目详情
│       │   │   └── ProjectCreate.vue   # 创建项目
│       │   ├── document/               # 文档解析
│       │   │   ├── DocumentList.vue    # 文档列表
│       │   │   ├── DocumentUpload.vue  # 文档上传
│       │   │   └── DocumentPreview.vue # 文档预览
│       │   ├── asset/                  # 资产管理
│       │   │   ├── AssetList.vue       # 资产列表
│       │   │   ├── AssetDetail.vue     # 资产详情
│       │   │   ├── AssetGraph.vue      # 资产图谱
│       │   │   └── DamageScenario.vue  # 损害场景
│       │   ├── threat-risk/            # 威胁风险分析
│       │   │   ├── ThreatList.vue      # 威胁列表
│       │   │   ├── ThreatAnalysis.vue  # 威胁分析
│       │   │   ├── AttackPath.vue      # 攻击路径
│       │   │   ├── AttackTree.vue      # 攻击树
│       │   │   ├── RiskAssessment.vue  # 风险评估
│       │   │   └── RiskMatrix.vue      # 风险矩阵
│       │   ├── diagram/                # 图表中心
│       │   │   ├── DiagramList.vue     # 图表列表
│       │   │   └── DiagramEditor.vue   # 图表编辑
│       │   ├── report/                 # 报告中心
│       │   │   ├── ReportList.vue      # 报告列表
│       │   │   ├── ReportGenerate.vue  # 生成报告
│       │   │   └── ReportPreview.vue   # 报告预览
│       │   └── common/                 # 通用页面
│       │       ├── Dashboard.vue       # 工作台
│       │       └── NotFound.vue        # 404页面
│       │
│       ├── components/                 # 公共组件
│       │   ├── common/                 # 通用组件
│       │   │   ├── PageHeader.vue
│       │   │   ├── SearchBar.vue
│       │   │   ├── DataTable.vue
│       │   │   ├── ConfirmDialog.vue
│       │   │   └── LoadingSpinner.vue
│       │   ├── graph/                  # 图谱组件
│       │   │   ├── KnowledgeGraph.vue  # 知识图谱 (D3.js)
│       │   │   ├── AttackTreeView.vue  # 攻击树 (GoJS)
│       │   │   └── DFDEditor.vue       # 数据流图
│       │   ├── chart/                  # 图表组件
│       │   │   ├── RiskMatrixChart.vue # 风险矩阵
│       │   │   ├── StatisticsChart.vue # 统计图表
│       │   │   └── TrendChart.vue      # 趋势图
│       │   ├── ai/                     # AI相关组件
│       │   │   ├── AIChatPanel.vue     # AI对话面板
│       │   │   ├── AIAnalysisCard.vue  # AI分析卡片
│       │   │   └── StreamingText.vue   # 流式文本
│       │   └── document/               # 文档组件
│       │       ├── DocViewer.vue       # 文档查看器
│       │       ├── PdfPreview.vue      # PDF预览
│       │       └── FileUploader.vue    # 文件上传
│       │
│       ├── layouts/                    # 布局组件
│       │   ├── MainLayout.vue          # 主布局
│       │   ├── Sidebar.vue             # 侧边栏
│       │   └── Header.vue              # 顶部导航
│       │
│       ├── router/                     # 路由配置
│       │   └── index.ts
│       │
│       ├── stores/                     # Pinia状态管理
│       │   ├── index.ts
│       │   ├── project.ts              # 项目状态
│       │   ├── document.ts             # 文档状态
│       │   ├── asset.ts                # 资产状态
│       │   ├── threat-risk.ts          # 威胁风险状态
│       │   └── app.ts                  # 应用全局状态
│       │
│       ├── composables/                # 组合式函数
│       │   ├── useRequest.ts           # 请求Hook
│       │   ├── useTable.ts             # 表格Hook
│       │   ├── useWebSocket.ts         # WebSocket Hook
│       │   └── useAIChat.ts            # AI对话Hook
│       │
│       ├── types/                      # TypeScript类型
│       │   ├── index.ts
│       │   ├── project.ts
│       │   ├── document.ts
│       │   ├── asset.ts
│       │   ├── threat-risk.ts
│       │   ├── diagram.ts
│       │   └── report.ts
│       │
│       ├── utils/                      # 工具函数
│       │   ├── index.ts
│       │   ├── format.ts               # 格式化
│       │   ├── validate.ts             # 校验
│       │   ├── storage.ts              # 存储
│       │   └── constants.ts            # 常量
│       │
│       └── styles/                     # 样式文件
│           ├── index.css               # 全局样式
│           ├── variables.css           # CSS变量
│           └── element-plus.css        # Element Plus定制
│
├── backend/                            # ⚙️ 后端服务
│   ├── shared/                         # 🔧 共享模块
│   │   ├── pyproject.toml
│   │   └── tara_shared/
│   │       ├── __init__.py
│   │       ├── config/                 # 配置管理
│   │       │   ├── __init__.py
│   │       │   └── settings.py         # 配置类
│   │       ├── database/               # 数据库连接
│   │       │   ├── __init__.py
│   │       │   ├── mysql.py            # MySQL连接
│   │       │   ├── redis.py            # Redis连接
│   │       │   ├── neo4j.py            # Neo4j连接
│   │       │   ├── milvus.py           # Milvus连接
│   │       │   ├── elasticsearch.py    # ES连接
│   │       │   └── minio.py            # MinIO连接
│   │       ├── models/                 # 共享数据模型
│   │       │   ├── __init__.py
│   │       │   ├── base.py             # 基础模型
│   │       │   ├── project.py          # 项目模型
│   │       │   ├── document.py         # 文档模型
│   │       │   ├── asset.py            # 资产模型
│   │       │   ├── threat_risk.py      # 威胁风险模型
│   │       │   └── report.py           # 报告模型
│   │       ├── schemas/                # Pydantic模式
│   │       │   ├── __init__.py
│   │       │   ├── base.py
│   │       │   ├── project.py
│   │       │   ├── document.py
│   │       │   ├── asset.py
│   │       │   ├── threat_risk.py
│   │       │   └── report.py
│   │       ├── utils/                  # 工具函数
│   │       │   ├── __init__.py
│   │       │   ├── logger.py           # 日志
│   │       │   ├── exceptions.py       # 异常
│   │       │   ├── response.py         # 响应封装
│   │       │   └── helpers.py          # 辅助函数
│   │       └── constants/              # 常量定义
│   │           ├── __init__.py
│   │           ├── enums.py            # 枚举
│   │           └── tara.py             # TARA相关常量
│   │
│   ├── project-service/                # 📁 项目管理服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py                 # FastAPI入口
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   └── v1/
│   │       │       ├── __init__.py
│   │       │       ├── router.py       # 路由注册
│   │       │       └── endpoints/
│   │       │           ├── __init__.py
│   │       │           └── project.py  # 项目接口
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   └── project_service.py  # 项目业务逻辑
│   │       ├── repositories/
│   │       │   ├── __init__.py
│   │       │   └── project_repo.py     # 项目数据访问
│   │       └── config.py               # 服务配置
│   │
│   ├── document-service/               # 📄 文档解析服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── router.py
│   │       │       └── endpoints/
│   │       │           └── document.py
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── document_service.py # 文档管理
│   │       │   ├── ocr_service.py      # OCR服务
│   │       │   ├── parser_service.py   # 解析服务
│   │       │   └── extractor_service.py # 内容提取
│   │       ├── repositories/
│   │       │   └── document_repo.py
│   │       ├── parsers/                # 文档解析器
│   │       │   ├── __init__.py
│   │       │   ├── base_parser.py
│   │       │   ├── pdf_parser.py
│   │       │   ├── word_parser.py
│   │       │   ├── excel_parser.py
│   │       │   └── dbc_parser.py       # DBC文件解析
│   │       └── config.py
│   │
│   ├── asset-service/                  # 🔍 资产识别服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── router.py
│   │       │       └── endpoints/
│   │       │           ├── asset.py
│   │       │           └── damage_scenario.py
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── asset_service.py    # 资产管理
│   │       │   ├── discovery_service.py # 资产发现
│   │       │   ├── graph_service.py    # 图谱服务
│   │       │   └── damage_service.py   # 损害场景
│   │       ├── repositories/
│   │       │   ├── asset_repo.py
│   │       │   └── neo4j_repo.py       # Neo4j操作
│   │       └── config.py
│   │
│   ├── threat-risk-service/            # ⚠️ 威胁风险分析服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── router.py
│   │       │       └── endpoints/
│   │       │           ├── threat.py   # 威胁接口
│   │       │           ├── attack_path.py # 攻击路径
│   │       │           └── risk.py     # 风险评估
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── threat_service.py   # 威胁分析
│   │       │   ├── stride_service.py   # STRIDE分析
│   │       │   ├── attack_path_service.py # 攻击路径
│   │       │   ├── risk_service.py     # 风险评估
│   │       │   └── treatment_service.py # 处置建议
│   │       ├── repositories/
│   │       │   ├── threat_repo.py
│   │       │   └── risk_repo.py
│   │       ├── engines/                # 分析引擎
│   │       │   ├── __init__.py
│   │       │   ├── stride_engine.py    # STRIDE引擎
│   │       │   ├── attack_potential.py # 攻击可行性
│   │       │   └── risk_calculator.py  # 风险计算
│   │       └── config.py
│   │
│   ├── diagram-service/                # 📊 图表生成服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── router.py
│   │       │       └── endpoints/
│   │       │           └── diagram.py
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── diagram_service.py
│   │       │   ├── attack_tree_service.py  # 攻击树
│   │       │   ├── dfd_service.py      # 数据流图
│   │       │   ├── risk_matrix_service.py # 风险矩阵
│   │       │   └── export_service.py   # 导出服务
│   │       ├── generators/             # 图表生成器
│   │       │   ├── __init__.py
│   │       │   ├── base_generator.py
│   │       │   ├── attack_tree_gen.py
│   │       │   ├── dfd_generator.py
│   │       │   └── matrix_generator.py
│   │       └── config.py
│   │
│   ├── report-service/                 # 📑 报告中心服务
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── router.py
│   │       │       └── endpoints/
│   │       │           ├── report.py
│   │       │           └── template.py
│   │       ├── services/
│   │       │   ├── __init__.py
│   │       │   ├── report_service.py   # 报告管理
│   │       │   ├── generator_service.py # 报告生成
│   │       │   ├── template_service.py # 模板管理
│   │       │   └── export_service.py   # 导出服务
│   │       ├── repositories/
│   │       │   └── report_repo.py
│   │       ├── templates/              # 报告模板
│   │       │   ├── iso21434/           # ISO 21434模板
│   │       │   │   ├── tara_report.docx
│   │       │   │   └── tara_report.html
│   │       │   └── custom/             # 自定义模板
│   │       └── config.py
│   │
│   └── agent-service/                  # 🤖 智能体服务
│       ├── pyproject.toml
│       ├── Dockerfile
│       └── app/
│           ├── __init__.py
│           ├── main.py
│           ├── api/
│           │   └── v1/
│           │       ├── router.py
│           │       └── endpoints/
│           │           ├── agent.py    # Agent接口
│           │           └── chat.py     # 对话接口
│           ├── services/
│           │   ├── __init__.py
│           │   ├── orchestrator.py     # Agent编排器
│           │   ├── chat_service.py     # 对话服务
│           │   └── task_service.py     # 任务管理
│           ├── agents/                 # Agent实现
│           │   ├── __init__.py
│           │   ├── base_agent.py       # 基础Agent
│           │   ├── document_agent.py   # 文档理解Agent
│           │   ├── asset_agent.py      # 资产挖掘Agent
│           │   ├── threat_risk_agent.py # 威胁风险Agent
│           │   └── report_agent.py     # 报告撰写Agent
│           ├── mcp/                    # MCP服务
│           │   ├── __init__.py
│           │   ├── server.py           # MCP Server基类
│           │   ├── knowledge_server.py # 知识图谱Server
│           │   ├── database_server.py  # 数据库Server
│           │   ├── document_server.py  # 文档Server
│           │   ├── inference_server.py # 推理Server
│           │   └── report_server.py    # 报告Server
│           ├── llm/                    # LLM客户端
│           │   ├── __init__.py
│           │   ├── client.py           # vLLM客户端
│           │   ├── qwen3_vl.py         # Qwen3-VL调用
│           │   ├── qwen3.py            # Qwen3调用
│           │   └── embedding.py        # Embedding调用
│           ├── prompts/                # Prompt模板
│           │   ├── __init__.py
│           │   ├── document_prompts.py
│           │   ├── asset_prompts.py
│           │   ├── threat_prompts.py
│           │   └── report_prompts.py
│           └── config.py
│
├── ai-models/                          # 🧠 AI模型配置
│   ├── README.md
│   ├── configs/                        # 模型配置
│   │   ├── qwen3-vl-8b.yaml
│   │   ├── qwen3.yaml
│   │   ├── ocrflux.yaml
│   │   └── embedding.yaml
│   ├── scripts/                        # 模型脚本
│   │   ├── download_models.sh          # 模型下载
│   │   ├── start_vllm.sh               # 启动vLLM
│   │   └── benchmark.py                # 性能测试
│   └── prompts/                        # 系统Prompt
│       ├── system_prompts/
│       │   ├── document_understanding.txt
│       │   ├── asset_discovery.txt
│       │   ├── threat_analysis.txt
│       │   └── report_writing.txt
│       └── few_shot_examples/          # Few-shot示例
│           ├── asset_examples.json
│           └── threat_examples.json
│
├── knowledge-base/                     # 📚 知识库
│   ├── README.md
│   ├── threat_library/                 # 威胁库
│   │   ├── stride_threats.json         # STRIDE威胁
│   │   ├── automotive_threats.json     # 汽车领域威胁
│   │   └── cwe_mapping.json            # CWE映射
│   ├── control_library/                # 控制措施库
│   │   ├── security_controls.json
│   │   └── iso21434_controls.json
│   ├── asset_templates/                # 资产模板
│   │   ├── ecu_template.json
│   │   ├── gateway_template.json
│   │   └── tbox_template.json
│   └── neo4j_import/                   # Neo4j导入脚本
│       ├── import_threats.cypher
│       └── import_controls.cypher
│
├── database/                           # 💾 数据库脚本
│   ├── mysql/
│   │   ├── init/                       # 初始化脚本
│   │   │   ├── 01_create_database.sql
│   │   │   ├── 02_create_tables.sql
│   │   │   └── 03_init_data.sql
│   │   └── migrations/                 # 迁移脚本
│   │       └── versions/
│   ├── neo4j/
│   │   ├── init/
│   │   │   ├── 01_constraints.cypher
│   │   │   └── 02_init_graph.cypher
│   │   └── queries/                    # 常用查询
│   │       └── asset_queries.cypher
│   ├── elasticsearch/
│   │   └── mappings/                   # 索引映射
│   │       ├── documents.json
│   │       └── threats.json
│   └── milvus/
│       └── collections/                # Collection定义
│           ├── doc_embeddings.json
│           └── threat_embeddings.json
│
├── scripts/                            # 🔧 开发脚本
│   ├── dev/
│   │   ├── setup.sh                    # 环境搭建
│   │   ├── start-dev.sh                # 启动开发环境
│   │   └── seed-data.py                # 测试数据填充
│   ├── test/
│   │   ├── run-tests.sh                # 运行测试
│   │   └── coverage.sh                 # 覆盖率报告
│   └── tools/
│       ├── generate-api-client.sh      # 生成API客户端
│       └── db-migrate.sh               # 数据库迁移
│
└── tests/                              # 🧪 测试目录
    ├── frontend/                       # 前端测试
    │   ├── unit/
    │   └── e2e/
    ├── backend/                        # 后端测试
    │   ├── unit/
    │   │   ├── test_project_service.py
    │   │   ├── test_document_service.py
    │   │   ├── test_asset_service.py
    │   │   ├── test_threat_risk_service.py
    │   │   ├── test_diagram_service.py
    │   │   └── test_report_service.py
    │   └── integration/
    │       └── test_tara_workflow.py   # 完整流程测试
    ├── agent/                          # Agent测试
    │   ├── test_orchestrator.py
    │   └── test_agents.py
    └── fixtures/                       # 测试数据
        ├── sample_documents/
        ├── sample_assets.json
        └── sample_threats.json
```

---

## 目录说明

### 核心目录

| 目录 | 说明 |
|------|------|
| `frontend/` | Vue3前端项目，包含6个核心功能模块页面 |
| `backend/` | 7个FastAPI微服务 + 共享模块 |
| `backend/agent-service/` | 智能体服务，包含4个Agent和5个MCP Server |
| `ai-models/` | AI模型配置和Prompt模板 |
| `knowledge-base/` | 威胁库、控制措施库等知识数据 |
| `deploy/` | Docker和Kubernetes部署配置 |
| `database/` | 数据库初始化和迁移脚本 |

### 后端服务

| 服务 | 端口 | 说明 |
|------|------|------|
| `project-service` | 8001 | 项目管理 |
| `document-service` | 8002 | 文档解析 |
| `asset-service` | 8003 | 资产识别 |
| `threat-risk-service` | 8004 | 威胁风险分析 |
| `diagram-service` | 8005 | 图表生成 |
| `report-service` | 8006 | 报告中心 |
| `agent-service` | 8007 | 智能体服务 |

### 前端页面

| 模块 | 页面 |
|------|------|
| 项目管理 | 列表、详情、创建 |
| 文档解析 | 列表、上传、预览 |
| 资产管理 | 列表、详情、图谱、损害场景 |
| 威胁风险 | 威胁列表、分析、攻击路径、攻击树、风险评估、风险矩阵 |
| 图表中心 | 列表、编辑 |
| 报告中心 | 列表、生成、预览 |
