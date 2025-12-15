FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Copy service code
COPY asset-service /app/service
RUN pip install --no-cache-dir -e /app/service

WORKDIR /app/service

EXPOSE 8003

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
