FROM python:3.11-slim

ARG SERVICE_NAME=project-service

WORKDIR /app

# === 1. 彻底清理所有现有 APT 源 ===
RUN rm -f /etc/apt/sources.list && \
    rm -rf /etc/apt/sources.list.d/*

# === 2. 使用 trixie（Debian 13）的阿里云源 ===
RUN echo "deb https://mirrors.aliyun.com/debian/ trixie main non-free non-free-firmware contrib" > /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian/ trixie-updates main non-free non-free-firmware contrib" >> /etc/apt/sources.list && \
    echo "deb https://mirrors.aliyun.com/debian-security/ trixie-security main non-free non-free-firmware contrib" >> /etc/apt/sources.list

# === 3. 配置 pip 使用阿里云镜像 ===
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

# === 4. 安装系统依赖 ===
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# === 5. 复制并安装具体服务（每个服务包含自己的common模块） ===
COPY backend/${SERVICE_NAME} /app/service
RUN pip install --no-cache-dir -e /app/service

WORKDIR /app/service

# 端口映射: project=8001, document=8002, asset=8003, threat-risk=8004, diagram=8005, report=8006, agent=8007, knowledge=8008
EXPOSE 8001 8002 8003 8004 8005 8006 8007 8008

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# 启动应用
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
