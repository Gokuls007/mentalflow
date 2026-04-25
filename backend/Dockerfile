# ── Build stage ──
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (saves ~2GB vs CUDA version),
# then install the rest of the requirements
RUN pip install --no-cache-dir --prefix=/install \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Runtime stage ──
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/* && \
    # Create non-root user for security
    adduser --disabled-password --gecos '' appuser

COPY --from=builder /install /usr/local
COPY . .

# Create directories for models and data
RUN mkdir -p /models /app/data && chown -R appuser:appuser /app /models

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
