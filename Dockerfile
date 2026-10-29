# ==========================================
# Multi-Stage Production Dockerfile for ML Web App
# ML DevOps Lab - LAB-ISE 2
# Student: Abhi Trambadiya | PRN: 2324000344
# ==========================================

# Stage 1: Build & Dependencies
FROM python:3.11-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Final Minimal Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code and model artifacts
COPY app.py .
COPY templates/ templates/
COPY models/ models/

# Document service port
EXPOSE 5000

# Healthcheck probe
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; exit(0 if urllib.request.urlopen('http://127.0.0.1:5000/health').getcode() == 200 else 1)"

# Start production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "app:app"]

