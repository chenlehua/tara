FROM python:3.11-slim

ARG SERVICE_NAME=project-service

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module first
COPY backend/shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Copy the specific service
COPY backend/${SERVICE_NAME} /app/service
RUN pip install --no-cache-dir -e /app/service

WORKDIR /app/service

# Extract port from service name
# project=8001, document=8002, asset=8003, threat-risk=8004, diagram=8005, report=8006, agent=8007
EXPOSE 8001 8002 8003 8004 8005 8006 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
