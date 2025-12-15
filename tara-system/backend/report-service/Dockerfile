FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Copy shared module
COPY shared /app/shared
RUN pip install --no-cache-dir -e /app/shared

# Copy service code
COPY report-service /app/service
RUN pip install --no-cache-dir -e /app/service

WORKDIR /app/service

EXPOSE 8006

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006"]
