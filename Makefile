# FLEXT-API Makefile - Enterprise API Gateway
# ============================================

.PHONY: help install test clean lint format build docs dev server security api-test load-test

# Default target
help: ## Show this help message
	@echo "🌐 FLEXT-API - Enterprise API Gateway"
	@echo "====================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Installation & Setup
install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies for flext-api gateway..."
	poetry install --all-extras

install-dev: ## Install with dev dependencies
	@echo "🛠️  Installing dev dependencies..."
	poetry install --all-extras --group dev --group test --group security

# Server Management
server: ## Run development server with auto-reload
	@echo "🚀 Starting flext-api development server..."
	poetry run uvicorn flext_api.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

server-prod: ## Run production server
	@echo "🏭 Starting flext-api production server..."
	poetry run gunicorn flext_api.main:app -w 4 -k uvicorn.workers.UvicornWorker --host 0.0.0.0 --port 8000

server-docker: ## Run in Docker container
	@echo "🐳 Building and running flext-api in Docker..."
	docker build -t flext-api .
	docker run -p 8000:8000 flext-api

# Testing
test: ## Run API tests
	@echo "🧪 Running API tests..."
	poetry run pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	poetry run pytest tests/ --cov=src/flext_api --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-fail-under=95

api-test: ## Test API endpoints
	@echo "🔍 Testing API endpoints..."
	poetry run python -m pytest tests/integration/ -v -k "endpoint"

load-test: ## Run load tests
	@echo "⚡ Running load tests..."
	@if [ -f tests/load/locustfile.py ]; then \
		poetry run locust -f tests/load/locustfile.py --host=http://localhost:8000; \
	else \
		echo "Load tests not configured"; \
	fi

# Code Quality - Maximum Strictness
lint: ## Run all linters with maximum strictness
	@echo "🔍 Running maximum strictness linting for API..."
	poetry run ruff check . --output-format=verbose
	@echo "✅ Ruff linting complete"

format: ## Format code with strict standards
	@echo "🎨 Formatting API code..."
	poetry run black .
	poetry run ruff check --fix .
	@echo "✅ Code formatting complete"

type-check: ## Run strict type checking
	@echo "🎯 Running strict MyPy type checking..."
	poetry run mypy src/flext_api --strict --show-error-codes
	@echo "✅ Type checking complete"

security: ## Run security analysis
	@echo "🔒 Running security analysis for API..."
	poetry run bandit -r src/ -f json -o reports/security.json || true
	poetry run bandit -r src/ -f txt
	@echo "✅ Security analysis complete"

pre-commit: ## Run pre-commit hooks
	@echo "🎣 Running pre-commit hooks..."
	poetry run pre-commit run --all-files
	@echo "✅ Pre-commit checks complete"

check: lint type-check security test ## Run all quality checks
	@echo "✅ All quality checks complete for flext-api!"

# Build & Distribution
build: ## Build the package with Poetry
	@echo "🔨 Building flext-api package..."
	poetry build
	@echo "📦 Package built successfully"

build-docker: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t flext-api:latest .
	@echo "🏗️  Docker image built successfully"

# API Documentation
docs: ## Generate API documentation
	@echo "📚 Generating API documentation..."
	poetry run python -c "
import json
from flext_api.main import app
with open('docs/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
print('OpenAPI spec generated at docs/openapi.json')
"

docs-serve: ## Serve API documentation
	@echo "📖 Serving API documentation..."
	@echo "API docs available at: http://localhost:8000/docs"
	@echo "ReDoc available at: http://localhost:8000/redoc"

# Development Workflow
dev-setup: install-dev ## Complete development setup
	@echo "🎯 Setting up development environment for flext-api..."
	poetry run pre-commit install
	mkdir -p reports logs
	@echo "✅ Development setup complete!"

dev: server ## Alias for development server

# Health & Monitoring
health: ## Check API health
	@echo "💓 Checking API health..."
	@curl -f http://localhost:8000/health || echo "API not running"

metrics: ## View API metrics
	@echo "📊 Fetching API metrics..."
	@curl -s http://localhost:8000/metrics || echo "Metrics not available"

# Database & Dependencies
migrate: ## Run database migrations
	@echo "🗃️  Running database migrations..."
	poetry run alembic upgrade head

reset-db: ## Reset database
	@echo "🔄 Resetting database..."
	poetry run alembic downgrade base
	poetry run alembic upgrade head

# Cleanup
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf reports/ logs/ .coverage htmlcov/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true

# Environment variables
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export FLEXT_API_DEV := true
export UVICORN_LOG_LEVEL := debug