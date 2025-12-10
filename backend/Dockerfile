# Multi-stage build for optimized production image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for PyTorch and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .

# Install core Django packages first
RUN pip install --no-cache-dir \
    Django==3.2.23 \
    djangorestframework==3.12.4 \
    djangorestframework-simplejwt==4.8.0 \
    django-cors-headers==4.3.1

# Install MongoDB driver (skip djongo as it causes conflicts, use pymongo directly)
RUN pip install --no-cache-dir pymongo==3.11.4

# Install ML/AI packages
RUN pip install --no-cache-dir \
    torch==2.5.1 \
    torchvision==0.20.1 \
    Pillow==10.1.0 \
    numpy==1.26.2

# Install other utilities
RUN pip install --no-cache-dir \
    sqlparse==0.2.4 \
    requests==2.31.0 \
    python-decouple==3.8 \
    APScheduler==3.11.1 \
    sib-api-v3-sdk==7.6.0 \
    bing-image-downloader==1.1.2

# Copy application code
COPY . .

# Create directory for models if not exists
RUN mkdir -p analyzer/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/articles/', timeout=5)" || exit 1

# Run with gunicorn for production
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]