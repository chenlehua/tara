# ============================================
# TARA System Makefile
# ============================================

.PHONY: help install dev build test clean docker-build docker-up docker-down

# 默认目标
.DEFAULT_GOAL := help

# 颜色定义
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

## ==================== 帮助 ====================
help: ## 显示帮助信息
	@echo ''
	@echo 'TARA System - 汽车智能威胁分析与风险评估系统'
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} { \
		if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "  ${YELLOW}%-20s${RESET} %s\n", $$1, $$2} \
	}' $(MAKEFILE_LIST)

## ==================== 环境设置 ====================
install: ## 安装所有依赖
	@echo "Installing dependencies..."
	cd frontend && pnpm install --registry https://registry.npmmirror.com
	cd backend/shared && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/project-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/document-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/asset-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/threat-risk-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/diagram-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/report-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .
	cd backend/agent-service && pip install -i https://mirrors.aliyun.com/pypi/simple/ -e .

setup-dev: ## 设置开发环境
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

## ==================== 开发 ====================
frontend-dev: ## 启动前端开发服务器
	cd frontend && pnpm install --registry https://registry.npmmirror.com && pnpm dev

backend-dev: ## 启动所有后端服务 (开发模式)
	@echo "Starting all backend services..."
	@trap 'kill 0' SIGINT; \
	cd backend/project-service && uvicorn app.main:app --reload --port 8001 & \
	cd backend/document-service && uvicorn app.main:app --reload --port 8002 & \
	cd backend/asset-service && uvicorn app.main:app --reload --port 8003 & \
	cd backend/threat-risk-service && uvicorn app.main:app --reload --port 8004 & \
	cd backend/diagram-service && uvicorn app.main:app --reload --port 8005 & \
	cd backend/report-service && uvicorn app.main:app --reload --port 8006 & \
	cd backend/agent-service && uvicorn app.main:app --reload --port 8007 & \
	wait

dev-project: ## 启动项目管理服务
	cd backend/project-service && uvicorn app.main:app --reload --port 8001

dev-document: ## 启动文档解析服务
	cd backend/document-service && uvicorn app.main:app --reload --port 8002

dev-asset: ## 启动资产识别服务
	cd backend/asset-service && uvicorn app.main:app --reload --port 8003

dev-threat-risk: ## 启动威胁风险分析服务
	cd backend/threat-risk-service && uvicorn app.main:app --reload --port 8004

dev-diagram: ## 启动图表生成服务
	cd backend/diagram-service && uvicorn app.main:app --reload --port 8005

dev-report: ## 启动报告中心服务
	cd backend/report-service && uvicorn app.main:app --reload --port 8006

dev-agent: ## 启动智能体服务
	cd backend/agent-service && uvicorn app.main:app --reload --port 8007

## ==================== 构建 ====================
build: build-frontend build-backend ## 构建所有

build-frontend: ## 构建前端
	cd frontend && pnpm install --registry https://registry.npmmirror.com && pnpm build

build-backend: ## 构建后端镜像
	docker compose -f deploy/docker/docker-compose.yml build

## ==================== Docker 操作 ====================
infra-up: ## 启动基础设施 (数据库等)
	docker compose -f deploy/docker/docker-compose.yml up -d mysql redis neo4j milvus elasticsearch minio

infra-down: ## 停止基础设施
	docker compose -f deploy/docker/docker-compose.yml down mysql redis neo4j milvus elasticsearch minio

backend-up: ## 启动后端服务 (Docker)
	docker compose -f deploy/docker/docker-compose.yml up -d project-service document-service asset-service threat-risk-service diagram-service report-service agent-service

backend-down: ## 停止后端服务
	docker compose -f deploy/docker/docker-compose.yml stop project-service document-service asset-service threat-risk-service diagram-service report-service agent-service

models-up: ## 启动AI模型服务 (需要GPU)
	docker compose -f deploy/docker/docker-compose.gpu.yml up -d

models-down: ## 停止AI模型服务
	docker compose -f deploy/docker/docker-compose.gpu.yml down

docker-up: ## 启动所有Docker服务
	docker compose -f deploy/docker/docker-compose.yml up -d

docker-down: ## 停止所有Docker服务
	docker compose -f deploy/docker/docker-compose.yml down

docker-logs: ## 查看Docker日志
	docker compose -f deploy/docker/docker-compose.yml logs -f

docker-ps: ## 查看Docker容器状态
	docker compose -f deploy/docker/docker-compose.yml ps

## ==================== 数据库 ====================
db-init: ## 初始化数据库 (通过Docker，先删除再重建)
	@echo "Initializing databases via Docker..."
	@echo "Waiting for MySQL to be ready..."
	@sleep 5
	@echo "Dropping existing database tara_db..."
	@echo "DROP DATABASE IF EXISTS tara_db;" | docker compose -f deploy/docker/docker-compose.yml exec -T mysql mysql -u root -proot_password
	@echo "Creating database and tables..."
	@cat database/mysql/init/01_create_database.sql | docker compose -f deploy/docker/docker-compose.yml exec -T mysql mysql -u root -proot_password
	@echo "Database initialized successfully!"

db-init-local: ## 初始化数据库 (本地MySQL，先删除再重建，需要输入密码)
	@echo "Initializing databases locally..."
	@echo "This will DROP and RECREATE the tara_db database!"
	mysql -h 127.0.0.1 -P 3306 -u root -p -e "DROP DATABASE IF EXISTS tara_db;"
	mysql -h 127.0.0.1 -P 3306 -u root -p < database/mysql/init/01_create_database.sql

db-init-tcp: ## 初始化数据库 (通过TCP连接Docker MySQL，先删除再重建)
	@echo "Initializing databases via TCP..."
	@echo "This will DROP and RECREATE the tara_db database!"
	mysql -h 127.0.0.1 -P 3306 -u root -proot_password -e "DROP DATABASE IF EXISTS tara_db;"
	mysql -h 127.0.0.1 -P 3306 -u root -proot_password < database/mysql/init/01_create_database.sql

db-migrate: ## 运行数据库迁移
	cd backend/shared && alembic upgrade head

db-rollback: ## 回滚数据库迁移
	cd backend/shared && alembic downgrade -1

db-seed: ## 填充测试数据
	python scripts/dev/seed-data.py

db-shell: ## 连接到MySQL (Docker)
	docker compose -f deploy/docker/docker-compose.yml exec mysql mysql -u tara -ptara_password tara_db

## ==================== 测试 ====================
# 安装共享模块（测试前必须安装）
install-shared: ## 安装共享模块
	pip install -i https://mirrors.aliyun.com/pypi/simple/ -e backend/shared/

test: install-shared ## 运行所有测试
	PYTHONPATH=backend/shared:backend/project-service:backend/document-service:backend/asset-service:backend/threat-risk-service:backend/diagram-service:backend/report-service:backend/agent-service \
		pytest backend/shared/tests/ -v

test-unit: install-shared ## 运行后端单元测试
	PYTHONPATH=backend/shared \
		pytest backend/shared/tests/unit/ -v

test-integration: install-shared ## 运行后端集成测试
	PYTHONPATH=backend/shared \
		pytest backend/shared/tests/integration/ -v

test-e2e: install-shared ## 运行端到端测试
	PYTHONPATH=backend/shared \
		pytest tests/e2e/ -v

test-security: install-shared ## 运行安全测试
	PYTHONPATH=backend/shared \
		pytest tests/security/ -v

test-frontend: ## 运行前端测试
	cd frontend && pnpm install --registry https://registry.npmmirror.com && pnpm test

coverage: install-shared ## 生成测试覆盖率报告
	PYTHONPATH=backend/shared \
		pytest backend/shared/tests/ --cov=backend/shared --cov-report=html
	@echo "Coverage report generated in htmlcov/"

## ==================== 代码质量 ====================
lint: lint-frontend lint-backend ## 运行所有lint检查

lint-frontend: ## 检查前端代码
	cd frontend && pnpm lint

lint-backend: ## 检查后端代码
	black --check backend/
	isort --check-only backend/
	flake8 backend/

format: format-frontend format-backend ## 格式化所有代码

format-frontend: ## 格式化前端代码
	cd frontend && pnpm format

format-backend: ## 格式化后端代码
	black backend/
	isort backend/

## ==================== 清理 ====================
clean: ## 清理构建产物
	rm -rf frontend/dist
	rm -rf backend/**/__pycache__
	rm -rf backend/**/*.egg-info
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-docker: ## 清理Docker资源
	docker compose -f deploy/docker/docker-compose.yml down -v --rmi local
	docker system prune -f

## ==================== 文档 ====================
docs: ## 生成API文档
	@echo "API docs available at http://localhost:800x/docs for each service"

docs-serve: ## 启动文档服务
	cd docs && mkdocs serve

## ==================== 工具 ====================
shell-mysql: ## 连接MySQL (Docker)
	docker compose -f deploy/docker/docker-compose.yml exec mysql mysql -u tara -ptara_password tara_db

shell-redis: ## 连接Redis (Docker)
	docker compose -f deploy/docker/docker-compose.yml exec redis redis-cli

shell-neo4j: ## 连接Neo4j (Docker)
	docker compose -f deploy/docker/docker-compose.yml exec neo4j cypher-shell -u neo4j -p neo4j_password

generate-api-client: ## 生成前端API客户端
	./scripts/tools/generate-api-client.sh

check-ports: ## 检查端口占用
	@echo "Checking service ports..."
	@for port in 3000 8001 8002 8003 8004 8005 8006 8007 3306 6379 7687 19530 9200 9000; do \
		if lsof -Pi :$$port -sTCP:LISTEN -t >/dev/null 2>&1; then \
			echo "Port $$port is in use"; \
		else \
			echo "Port $$port is available"; \
		fi \
	done
