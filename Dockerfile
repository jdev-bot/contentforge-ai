FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/backend/requirements.txt .
RUN pip install -r requirements.txt

COPY src/backend/ ./

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT