# Glow Claims API - Python Flask
# Multi-stage build for optimized image size

# === BUILD STAGE ===
FROM python:3.11-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# === RUNTIME STAGE ===
FROM python:3.11-slim

WORKDIR /app

# Security: Run as non-root user
RUN groupadd --system --gid 1001 glowgroup && \
    useradd --system --uid 1001 --gid glowgroup glowuser

# Copy dependencies from builder
COPY --from=builder /root/.local /home/glowuser/.local

# Copy application code
COPY --chown=glowuser:glowgroup src/ ./src/
COPY --chown=glowuser:glowgroup specs/ ./specs/
COPY --chown=glowuser:glowgroup scripts/ ./scripts/

# Switch to non-root user
USER glowuser

# Add local bin to PATH
ENV PATH=/home/glowuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/app.py

# Expose Flask port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the application
CMD ["python", "src/app.py"]
