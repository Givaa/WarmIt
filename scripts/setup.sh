#!/bin/bash

# WarmIt Setup Script

set -e

echo "🔥 WarmIt Setup"
echo "==============="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11 or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed"
    echo "Install it with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi
echo "✅ Poetry installed"

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "⚠️  Redis is not installed"
    echo "Install it with:"
    echo "  macOS: brew install redis"
    echo "  Ubuntu: sudo apt-get install redis-server"
    echo "  Other: https://redis.io/download"
    echo ""
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
poetry install

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys!"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo ""
echo "Initializing database..."
poetry run python -c "
import asyncio
from warmit.database import init_db
asyncio.run(init_db())
print('✅ Database initialized')
"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (OpenRouter or Groq)"
echo "2. Start Redis: redis-server"
echo "3. Start API server: poetry run uvicorn warmit.main:app --reload"
echo "4. Start Celery worker: poetry run celery -A warmit.tasks worker --loglevel=info"
echo "5. Start Celery beat: poetry run celery -A warmit.tasks beat --loglevel=info"
echo ""
echo "Visit http://localhost:8000/docs for API documentation"
