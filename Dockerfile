# Minimal Dockerfile for Render — no cleanup, maximum compatibility
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY src/backend/requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY src/backend/ ./

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Render detects this port
EXPOSE 8000

# Start with PORT env var (Render sets this)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}