FROM python:3.11-slim

WORKDIR /app

# Copy dependency files first for better caching
COPY requirements.txt ./

# Install system dependencies, Python packages, then remove build deps
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

# Copy application code
COPY src/warmit/ ./warmit/
COPY scripts/ ./scripts/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "warmit.main:app", "--host", "0.0.0.0", "--port", "8000"]
