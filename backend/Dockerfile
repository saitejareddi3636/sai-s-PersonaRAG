FROM python:3.11-slim

WORKDIR /app

# Install system dependencies + Piper TTS binary (CPU, en_US voice baked below).
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG PIPER_RELEASE=2023.11.14-2
RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) PFILE="piper_linux_x86_64.tar.gz" ;; \
      arm64) PFILE="piper_linux_aarch64.tar.gz" ;; \
      *) echo "unsupported arch: $arch" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://github.com/rhasspy/piper/releases/download/${PIPER_RELEASE}/${PFILE}" -o /tmp/piper.tgz; \
    tar xzf /tmp/piper.tgz -C /tmp; \
    mv /tmp/piper/piper /usr/local/bin/piper; \
    chmod +x /usr/local/bin/piper; \
    rm -rf /tmp/piper /tmp/piper.tgz

# Small / fast English voice (~10MB) for Docker; override PIPER_MODEL_PATH in compose if needed.
RUN mkdir -p /app/piper-voice \
    && curl -fsSL -o /app/piper-voice/en_US-lessac-low.onnx \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx" \
    && curl -fsSL -o /app/piper-voice/en_US-lessac-low.onnx.json \
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json"

ENV PIPER_BINARY=/usr/local/bin/piper
ENV PIPER_MODEL_PATH=/app/piper-voice/en_US-lessac-low.onnx

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
