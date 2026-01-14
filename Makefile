.PHONY: help setup install dev test clean format lint dashboard docker-up docker-down

help:
	@echo "🔥 WarmIt - Email Warming Tool"
	@echo ""
	@echo "Production Commands:"
	@echo "  ./start.sh           - Start production (Docker)"
	@echo "  ./start.sh restart   - Restart all services"
	@echo "  ./start.sh stop      - Stop all services"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev             - Run dev server (all services)"
	@echo "  make api             - Run API server only"
	@echo "  make worker          - Run Celery worker only"
	@echo "  make beat            - Run Celery beat only"
	@echo "  make dashboard       - Run dashboard only"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up       - Start Docker services"
	@echo "  make docker-down     - Stop Docker services"
	@echo ""
	@echo "Development Tools:"
	@echo "  make test            - Run tests"
	@echo "  make format          - Format code"
	@echo "  make lint            - Lint code"
	@echo "  make clean           - Clean temp files"
	@echo "  make cli ARGS        - Run CLI tool"

setup:
	@chmod +x scripts/setup.sh
	@./scripts/setup.sh

install:
	poetry install

dev:
	@chmod +x scripts/run_dev.sh
	@./scripts/run_dev.sh

api:
	poetry run uvicorn warmit.main:app --reload --host 0.0.0.0 --port 8000

worker:
	poetry run celery -A warmit.tasks worker --loglevel=info

beat:
	poetry run celery -A warmit.tasks beat --loglevel=info

dashboard:
	poetry run streamlit run dashboard/app.py

docker-up:
	docker compose -f docker/docker-compose.prod.yml up -d

docker-down:
	docker compose -f docker/docker-compose.prod.yml down

test:
	poetry run pytest -v

format:
	poetry run black src/ tests/

lint:
	poetry run ruff check src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf dist/
	rm -rf build/
	rm -f *.db
	rm -f *.sqlite

cli:
	@poetry run python scripts/cli.py $(filter-out $@,$(MAKECMDGOALS))

# Catch-all target for cli arguments
%:
	@:
