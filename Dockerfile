# syntax=docker/dockerfile:1

FROM python:3.11-slim

# System deps for opencv/onnxruntime
RUN set -eux; \
    apt-get update; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
        ca-certificates \
        git \
    ; \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt ./
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy sources
COPY src ./src
COPY README.md ./

# Create non-root user
RUN useradd -ms /bin/bash appuser && chown -R appuser:appuser /app
USER appuser

# Default environment for Docker runtime (can be overridden by compose)
ENV PYTHONUNBUFFERED=1 \
    OUTPUT_FOLDER=/app/src/image_moderator/output \
    MODEL_PATH=/app/src/image_moderator/models/license-plate-finetune-v1l.onnx \
    SCHEDULER_INTERVAL_MINUTES=1

ENTRYPOINT ["python", "-m", "src.ad_moderator"]
