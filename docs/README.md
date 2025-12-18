# TARA System 文档

本目录包含 TARA 系统的完整文档。

## 文档结构

```
docs/
├── api/                    # API 文档
│   ├── openapi.yaml        # OpenAPI 规范
│   └── examples/           # API 调用示例
├── architecture/           # 架构文档
│   ├── system-overview.md  # 系统概览
│   ├── data-model.md       # 数据模型
│   └── ai-agents.md        # AI Agent 架构
├── user-guide/             # 用户指南
│   ├── getting-started.md  # 快速开始
│   ├── project-management.md # 项目管理
│   ├── tara-workflow.md    # TARA 工作流
│   └── report-generation.md # 报告生成
└── development/            # 开发文档
    ├── setup.md            # 开发环境搭建
    ├── contributing.md     # 贡献指南
    ├── testing.md          # 测试指南
    └── deployment.md       # 部署指南
```

## 快速链接

- [API 文档](api/openapi.yaml)
- [系统架构](architecture/system-overview.md)
- [用户指南](user-guide/getting-started.md)
- [开发指南](development/setup.md)

## 在线文档

启动文档服务器：
```bash
make docs
```

访问 http://localhost:8080 查看文档。
