#!/bin/bash

# Development startup script - runs all services

set -e

echo "🔥 Starting WarmIt Development Environment"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run scripts/setup.sh first"
    exit 1
fi

# Check if Redis is running
if ! pgrep -x redis-server > /dev/null; then
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi
echo "✅ Redis running"

# Create logs directory
mkdir -p logs

echo ""
echo "Starting services..."
echo "---"

# Start Celery worker in background
echo "Starting Celery worker..."
poetry run celery -A warmit.tasks worker --loglevel=info > logs/celery-worker.log 2>&1 &
CELERY_WORKER_PID=$!
echo "✅ Celery worker (PID: $CELERY_WORKER_PID)"

# Start Celery beat in background
echo "Starting Celery beat..."
poetry run celery -A warmit.tasks beat --loglevel=info > logs/celery-beat.log 2>&1 &
CELERY_BEAT_PID=$!
echo "✅ Celery beat (PID: $CELERY_BEAT_PID)"

# Wait a bit for Celery to start
sleep 2

echo ""
echo "🚀 All background services started!"
echo ""
echo "Starting API server..."
echo "Visit http://localhost:8000/docs for API documentation"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C to cleanup
cleanup() {
    echo ""
    echo "Stopping services..."
    kill $CELERY_WORKER_PID 2>/dev/null || true
    kill $CELERY_BEAT_PID 2>/dev/null || true
    echo "✅ Services stopped"
    exit 0
}

trap cleanup INT TERM

# Start API server (foreground)
poetry run uvicorn warmit.main:app --reload --host 0.0.0.0 --port 8000
