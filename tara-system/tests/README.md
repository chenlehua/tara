# TARA System 测试

本目录包含系统级测试，包括端到端测试、性能测试和安全测试。

## 目录结构

```
tests/
├── e2e/                    # 端到端测试
│   ├── conftest.py         # 测试配置
│   ├── test_full_workflow.py   # 完整工作流测试
│   └── test_user_scenarios.py  # 用户场景测试
├── performance/            # 性能测试
│   ├── locustfile.py       # Locust 负载测试
│   └── benchmark.py        # 基准测试
└── security/               # 安全测试
    ├── test_auth.py        # 认证安全测试
    └── test_injection.py   # 注入攻击测试
```

## 运行测试

### 端到端测试
```bash
# 需要先启动所有服务
pytest tests/e2e/ -v
```

### 性能测试
```bash
# 使用 Locust
cd tests/performance
locust -f locustfile.py --host=http://localhost:8001

# 或使用 benchmark
python benchmark.py
```

### 安全测试
```bash
pytest tests/security/ -v
```

## 测试环境要求

- 所有微服务运行中
- 数据库已初始化
- 测试数据已准备

## 测试覆盖率

```bash
pytest --cov=backend --cov-report=html tests/
```
