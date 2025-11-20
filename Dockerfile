FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    openssl \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r nix && useradd -r -g nix nix

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY nix-system/ /app/nix-system/
COPY requirements.txt /app/

# Create necessary directories
RUN mkdir -p /var/log/nix/audit \
    /var/log/nix/security \
    /var/log/nix/application \
    /app/data

# Set permissions
RUN chown -R nix:nix /app /var/log/nix

# Switch to non-root user
USER nix

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "nix_system.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
