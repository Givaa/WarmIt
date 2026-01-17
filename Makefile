.PHONY: help install test test-cov lint format type-check start stop restart clean build deploy

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "WarmIt - Email Warming Tool"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
install: ## Install dependencies with Poetry
	poetry install --with dev

install-prod: ## Install production dependencies only
	poetry install --only main

# Testing
test: ## Run tests
	poetry run pytest tests/ -v

test-cov: ## Run tests with coverage
	poetry run pytest tests/ -v --cov=warmit --cov-report=html --cov-report=term-missing

test-unit: ## Run only unit tests
	poetry run pytest tests/unit/ -v

test-integration: ## Run only integration tests
	poetry run pytest tests/integration/ -v

test-watch: ## Run tests in watch mode
	poetry run ptw tests/ -- -v

# Code Quality
lint: ## Run linter (Ruff)
	poetry run ruff check src/

lint-fix: ## Run linter and fix issues
	poetry run ruff check --fix src/

format: ## Format code with Ruff
	poetry run ruff format src/

format-check: ## Check code formatting
	poetry run ruff format --check src/

type-check: ## Run type checker (mypy)
	poetry run mypy src/warmit --ignore-missing-imports

quality: lint format-check type-check ## Run all quality checks

# Docker Operations
start: ## Start all services
	./warmit.sh start

stop: ## Stop all services
	./warmit.sh stop

restart: ## Restart all services
	./warmit.sh restart

logs: ## View logs
	docker compose -f docker/docker-compose.prod.yml logs -f

logs-api: ## View API logs
	docker logs -f warmit-api

logs-worker: ## View worker logs
	docker logs -f warmit-worker

logs-dashboard: ## View dashboard logs
	docker logs -f warmit-dashboard

status: ## Show service status
	docker compose -f docker/docker-compose.prod.yml ps

# Database
db-migrate: ## Run database migrations
	poetry run alembic upgrade head

db-rollback: ## Rollback last migration
	poetry run alembic downgrade -1

db-shell: ## Open database shell
	docker exec -it warmit-db psql -U warmit -d warmit

# Cleanup
clean: ## Clean up build artifacts and caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -f .coverage
	rm -f coverage.xml

clean-docker: ## Remove all Docker containers and volumes
	./warmit.sh down

# Build
build: ## Build Docker images
	docker compose -f docker/docker-compose.prod.yml build

build-no-cache: ## Build Docker images without cache
	docker compose -f docker/docker-compose.prod.yml build --no-cache

# Deployment
deploy: build ## Build and deploy
	docker compose -f docker/docker-compose.prod.yml up -d

health: ## Check system health
	curl http://localhost:8000/health/detailed | jq

# Development helpers
shell: ## Open Python shell with project context
	poetry run python

dashboard: ## Open dashboard in browser (macOS/Linux/Windows)
	@command -v open >/dev/null 2>&1 && open http://localhost:8501 || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8501 || \
	command -v start >/dev/null 2>&1 && start http://localhost:8501 || \
	echo "Please open http://localhost:8501 in your browser"

api-docs: ## Open API documentation (macOS/Linux/Windows)
	@command -v open >/dev/null 2>&1 && open http://localhost:8000/docs || \
	command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:8000/docs || \
	command -v start >/dev/null 2>&1 && start http://localhost:8000/docs || \
	echo "Please open http://localhost:8000/docs in your browser"

# Pre-commit
pre-commit-install: ## Install pre-commit hooks
	poetry run pre-commit install

pre-commit-run: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

# Documentation
docs-serve: ## Serve documentation locally
	@echo "Documentation is in docs/ directory"
	@echo "Main: docs/README.md"
	@echo "Developer: docs/developer/README.md"

# Security
security-check: ## Run security checks
	poetry run safety check || true
	poetry run bandit -r src/ || true

# All checks before commit
check-all: quality test ## Run all checks (lint, format, type-check, tests)

# Initialize project
init: install pre-commit-install ## Initialize project for development
	@echo "✅ Project initialized!"
	@echo "Run 'make start' to start services"
