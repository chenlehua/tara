FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library first
COPY backend/shared /app/shared
RUN pip install -e /app/shared

# Copy service files
COPY backend/knowledge-service /app/service
WORKDIR /app/service

# Install dependencies
RUN pip install -e .

# Run the application
EXPOSE 8007
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
