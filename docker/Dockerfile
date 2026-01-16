FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Poetry
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install Python packages using Poetry
# --no-root: don't install the project itself yet
# --only main: only install main dependencies, not dev
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && rm -rf /root/.cache

# Copy application code
COPY src/warmit/ ./warmit/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "warmit.main:app", "--host", "0.0.0.0", "--port", "8000"]
