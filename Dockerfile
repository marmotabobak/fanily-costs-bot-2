FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Copy requirements.txt for caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy project files
COPY main.py .
COPY src/ ./src
COPY pyproject.toml .
COPY README.md .

CMD ["python", "main.py"]
