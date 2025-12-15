# 开发环境搭建

本文档指导如何搭建 TARA System 的开发环境。

## 前置要求

### 软件要求

- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 24+
- **Docker Compose**: 2.0+
- **Git**: 2.0+

### 硬件要求 (开发环境)

- CPU: 4+ 核心
- 内存: 16 GB+
- 存储: 50 GB+
- GPU: 可选 (用于本地运行 AI 模型)

## 环境搭建

### 1. 克隆代码

```bash
git clone https://github.com/your-org/tara-system.git
cd tara-system
```

### 2. 安装开发依赖

```bash
# 运行开发环境安装脚本
./scripts/setup/install-dev.sh
```

或手动安装：

```bash
# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate

# 配置 pip 使用国内镜像源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com

# 安装 Python 依赖
pip install -e backend/shared
pip install -e backend/project-service
pip install -e backend/document-service
pip install -e backend/asset-service
pip install -e backend/threat-risk-service
pip install -e backend/diagram-service
pip install -e backend/report-service
pip install -e backend/agent-service

# 安装开发工具
pip install pytest pytest-cov pytest-asyncio black isort mypy ruff

# 安装 pnpm 并配置淘宝镜像源
npm install -g pnpm --registry https://registry.npmmirror.com
pnpm config set registry https://registry.npmmirror.com

# 安装前端依赖
cd frontend && pnpm install && cd ..
```

### 镜像源配置

#### pip (阿里云)
```bash
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
```

#### pnpm/npm (淘宝)
```bash
pnpm config set registry https://registry.npmmirror.com
```

#### Docker (国内镜像)
编辑 `/etc/docker/daemon.json`:
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```
然后重启 Docker:
```bash
sudo systemctl restart docker
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量。

### 4. 启动基础设施

```bash
# 使用 Docker Compose 启动数据库等
make docker-up-infra

# 等待服务就绪
sleep 30

# 初始化数据库
make db-init
```

### 5. 启动开发服务器

```bash
# 终端 1: 启动后端服务
make backend-dev

# 终端 2: 启动前端开发服务器
make frontend-dev
```

访问 http://localhost:3000 查看应用。

## IDE 配置

### VS Code

推荐安装以下扩展：

- Python
- Pylance
- Vue - Official (Volar)
- ESLint
- Prettier
- Tailwind CSS IntelliSense

项目已包含 VS Code 配置文件：
- `.vscode/settings.json`: 编辑器设置
- `.vscode/launch.json`: 调试配置

### PyCharm

1. 打开项目目录
2. 配置 Python 解释器为 `venv`
3. 标记 `backend/shared` 为 Sources Root
4. 配置 pytest 为测试运行器

## 代码规范

### Python

- 格式化: Black
- 导入排序: isort
- 类型检查: mypy
- 代码检查: ruff

```bash
# 格式化代码
black backend/
isort backend/

# 类型检查
mypy backend/

# 代码检查
ruff check backend/
```

### TypeScript/Vue

- 格式化: Prettier
- 代码检查: ESLint

```bash
cd frontend

# 格式化
npm run format

# 代码检查
npm run lint
```

## 测试

### 运行所有测试

```bash
make test
```

### 运行特定服务测试

```bash
# 单元测试
pytest backend/project-service/tests/unit -v

# 集成测试
pytest backend/project-service/tests/integration -v
```

### 测试覆盖率

```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## 调试

### 后端调试 (VS Code)

1. 打开 Run and Debug 面板
2. 选择要调试的服务配置
3. 设置断点
4. 按 F5 启动调试

### 前端调试

1. 在 Chrome 中打开开发者工具
2. 使用 Vue DevTools 扩展
3. 在 Sources 面板设置断点

## 数据库管理

### 查看数据库

```bash
# MySQL
docker exec -it tara-mysql mysql -u tara -p tara_db

# Redis
docker exec -it tara-redis redis-cli

# Neo4j
# 访问 http://localhost:7474
```

### 数据库迁移

```bash
# 创建迁移
python scripts/migration/migrate.py create add_new_column

# 执行迁移
python scripts/migration/migrate.py upgrade

# 回滚迁移
python scripts/migration/migrate.py downgrade
```

## 常见问题

### 端口冲突

如果端口被占用，修改 `.env` 中的端口配置：

```env
MYSQL_PORT=3307
REDIS_PORT=6380
```

### 数据库连接失败

确保 Docker 容器正在运行：

```bash
docker ps | grep tara
```

### 内存不足

减少同时运行的服务数量，或增加 Docker 内存限制。

### AI 模型加载失败

确保有足够的 GPU 内存，或使用 CPU 模式：

```env
USE_GPU=false
```

## 下一步

- [贡献指南](contributing.md)
- [测试指南](testing.md)
- [部署指南](deployment.md)
