# FLEXT API - Production Docker Image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user
RUN groupadd -r flext && useradd -r -g flext flext

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Install the application
RUN pip install -e .

# Create directories and set permissions
RUN mkdir -p /app/logs \
    && chown -R flext:flext /app

# Switch to non-root user
USER flext

# Expose port
EXPOSE ${FlextConstants.Platform.FLEXT_API_PORT}

# Health check
HEALTHCHECK --interval=${FlextApiConstants.DEFAULT_TIMEOUT}s --timeout=${FlextApiConstants.TESTING_TIMEOUT}s --start-period=5s --retries=3 \
    CMD curl -f http://${FlextConstants.Platform.DEFAULT_HOST}:${FlextConstants.Platform.FLEXT_API_PORT}/health || exit 1

# Start the application
CMD ["uvicorn", "flext_api.app:app", "--host", "0.0.0.0", "--port", "${FlextConstants.Platform.FLEXT_API_PORT}"]