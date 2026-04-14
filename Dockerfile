# Debug-friendly Dockerfile for Render
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

# Debug: test imports before switching user
RUN python -c "from app.main import app; print('App import OK')" 2>&1 || echo "APP IMPORT FAILED"

USER appuser

# Render detects this port
EXPOSE 8000

# Start with PORT env var (Render sets this)
# Use entrypoint script for debugging
ENTRYPOINT ["sh", "-c", "python -c 'from app.core.config import get_settings; s=get_settings(); print(f\"Settings loaded: ENV={s.APP_ENV}, URL={s.SUPABASE_URL[:30]}...\")' 2>&1 && exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]