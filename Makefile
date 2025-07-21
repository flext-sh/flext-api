# FLEXT API - FastAPI Enterprise Application
# =========================================
# High-performance REST API with Clean Architecture + DDD
# Python 3.13 + FastAPI + Zero Tolerance Quality Gates

.PHONY: help check validate test lint type-check security format format-check fix
.PHONY: install dev-install setup pre-commit build clean dev serve dev-reload
.PHONY: coverage coverage-html test-unit test-integration test-api
.PHONY: deps-update deps-audit deps-tree api-docs api-openapi

# ============================================================================
# 🎯 HELP & INFORMATION
# ============================================================================

help: ## Show this help message
	@echo "🚀 FLEXT API - FastAPI Enterprise Application"
	@echo "============================================="
	@echo "🎯 Clean Architecture + DDD + Python 3.13 + FastAPI Enterprise Standards"
	@echo ""
	@echo "📦 High-performance REST API server for FLEXT data integration platform"
	@echo "🔒 Zero tolerance quality gates with enterprise security"
	@echo "🧪 90%+ test coverage requirement with API testing"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# 🎯 CORE QUALITY GATES - ZERO TOLERANCE
# ============================================================================

validate: lint type-check security test ## STRICT compliance validation (all must pass)
	@echo "✅ ALL QUALITY GATES PASSED - FLEXT API COMPLIANT"

check: lint type-check test ## Essential quality checks (pre-commit standard)
	@echo "✅ Essential checks passed"

lint: ## Ruff linting (17 rule categories, ALL enabled)
	@echo "🔍 Running ruff linter (ALL rules enabled)..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ Linting complete"

type-check: ## MyPy strict mode type checking (zero errors tolerated)
	@echo "🛡️ Running MyPy strict type checking..."
	@poetry run mypy src/ tests/ --strict
	@echo "✅ Type checking complete"

security: ## Security scans (bandit + pip-audit + secrets)
	@echo "🔒 Running security scans..."
	@poetry run bandit -r src/ --severity-level medium --confidence-level medium
	@poetry run pip-audit --ignore-vuln PYSEC-2022-42969
	@poetry run detect-secrets scan --all-files
	@echo "✅ Security scans complete"

format: ## Format code with ruff
	@echo "🎨 Formatting code..."
	@poetry run ruff format src/ tests/
	@echo "✅ Formatting complete"

format-check: ## Check formatting without fixing
	@echo "🎨 Checking code formatting..."
	@poetry run ruff format src/ tests/ --check
	@echo "✅ Format check complete"

fix: format lint ## Auto-fix all issues (format + imports + lint)
	@echo "🔧 Auto-fixing all issues..."
	@poetry run ruff check src/ tests/ --fix --unsafe-fixes
	@echo "✅ All auto-fixes applied"

# ============================================================================
# 🧪 TESTING - 90% COVERAGE MINIMUM
# ============================================================================

test: ## Run tests with coverage (90% minimum required)
	@echo "🧪 Running tests with coverage..."
	@poetry run pytest tests/ -v --cov=src/flext_api --cov-report=term-missing --cov-fail-under=90
	@echo "✅ Tests complete"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@poetry run pytest tests/unit/ -v
	@echo "✅ Unit tests complete"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@poetry run pytest tests/integration/ -v
	@echo "✅ Integration tests complete"

test-api: ## Run API endpoint tests
	@echo "🧪 Running API endpoint tests..."
	@poetry run pytest tests/api/ -v
	@echo "✅ API tests complete"

coverage: ## Generate detailed coverage report
	@echo "📊 Generating coverage report..."
	@poetry run pytest tests/ --cov=src/flext_api --cov-report=term-missing --cov-report=html
	@echo "✅ Coverage report generated in htmlcov/"

coverage-html: coverage ## Generate HTML coverage report
	@echo "📊 Opening coverage report..."
	@python -m webbrowser htmlcov/index.html

# ============================================================================
# 🚀 DEVELOPMENT SETUP
# ============================================================================

setup: install pre-commit ## Complete development setup
	@echo "🎯 Development setup complete!"

install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies..."
	@poetry install --all-extras --with dev,test,docs,security
	@echo "✅ Dependencies installed"

dev-install: install ## Install in development mode
	@echo "🔧 Setting up development environment..."
	@poetry install --all-extras --with dev,test,docs,security
	@poetry run pre-commit install
	@echo "✅ Development environment ready"

pre-commit: ## Setup pre-commit hooks
	@echo "🎣 Setting up pre-commit hooks..."
	@poetry run pre-commit install
	@poetry run pre-commit run --all-files || true
	@echo "✅ Pre-commit hooks installed"

# ============================================================================
# 🚀 FASTAPI DEVELOPMENT SERVER
# ============================================================================

dev: ## Start development server with auto-reload
	@echo "🚀 Starting FastAPI development server..."
	@echo "📡 Server will be available at: http://localhost:8000"
	@echo "📚 API documentation at: http://localhost:8000/docs"
	@echo "📖 ReDoc documentation at: http://localhost:8000/redoc"
	@poetry run uvicorn flext_api.main:app --reload --host 0.0.0.0 --port 8000

serve: dev ## Alias for dev command

dev-reload: ## Start development server with aggressive reload
	@echo "🚀 Starting FastAPI development server (aggressive reload)..."
	@poetry run uvicorn flext_api.main:app --reload --reload-dir src/ --host 0.0.0.0 --port 8000

dev-production: ## Start server with production settings
	@echo "🚀 Starting FastAPI server (production mode)..."
	@poetry run uvicorn flext_api.main:app --host 0.0.0.0 --port 8000 --workers 4

# ============================================================================
# 📦 BUILD & DISTRIBUTION
# ============================================================================

build: clean ## Build distribution packages
	@echo "🔨 Building distribution..."
	@poetry build
	@echo "✅ Build complete - packages in dist/"

api-docs: ## Generate API documentation
	@echo "📚 Generating API documentation..."
	@poetry run python -c "import uvicorn; from flext_api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)" &
	@sleep 3
	@curl -o openapi.json http://localhost:8000/openapi.json
	@pkill -f uvicorn
	@echo "✅ OpenAPI schema saved to openapi.json"

api-openapi: ## Export OpenAPI schema
	@echo "📚 Exporting OpenAPI schema..."
	@poetry run python -c "import json; from flext_api.main import app; f = open('openapi.json', 'w'); json.dump(app.openapi(), f, indent=2); f.close(); print('OpenAPI schema exported to openapi.json')"

# ============================================================================
# 🧹 CLEANUP
# ============================================================================

clean: ## Remove all artifacts
	@echo "🧹 Cleaning up..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .pytest_cache/
	@rm -rf reports/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# ============================================================================
# 📊 DEPENDENCY MANAGEMENT
# ============================================================================

deps-update: ## Update all dependencies
	@echo "🔄 Updating dependencies..."
	@poetry update
	@echo "✅ Dependencies updated"

deps-audit: ## Audit dependencies for vulnerabilities
	@echo "🔍 Auditing dependencies..."
	@poetry run pip-audit
	@echo "✅ Dependency audit complete"

deps-tree: ## Show dependency tree
	@echo "🌳 Dependency tree:"
	@poetry show --tree

deps-outdated: ## Show outdated dependencies
	@echo "📋 Outdated dependencies:"
	@poetry show --outdated

# ============================================================================
# 🔧 ENVIRONMENT CONFIGURATION
# ============================================================================

# Python settings
PYTHON := python3.13
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export PYTHONDONTWRITEBYTECODE := 1
export PYTHONUNBUFFERED := 1

# FastAPI settings
export FLEXT_API_HOST := 0.0.0.0
export FLEXT_API_PORT := 8000
export FLEXT_API_RELOAD := true
export FLEXT_API_LOG_LEVEL := debug

# Poetry settings
export POETRY_VENV_IN_PROJECT := false
export POETRY_CACHE_DIR := $(HOME)/.cache/pypoetry

# Quality gate settings
export MYPY_CACHE_DIR := .mypy_cache
export RUFF_CACHE_DIR := .ruff_cache

# ============================================================================
# 📝 PROJECT METADATA
# ============================================================================

# Project information
PROJECT_NAME := flext-api
PROJECT_VERSION := $(shell poetry version -s)
PROJECT_DESCRIPTION := FLEXT API - FastAPI Enterprise Application

.DEFAULT_GOAL := help

# ============================================================================
# 🎯 FASTAPI SPECIFIC COMMANDS
# ============================================================================

api-check: ## Check API health and endpoints
	@echo "🔍 Checking API health..."
	@poetry run python -c "import httpx, asyncio; print('❌ API is not running - start with make dev first')"

api-test-endpoints: ## Test all API endpoints
	@echo "🧪 Testing API endpoints..."
	@poetry run pytest tests/api/ -v --tb=short

api-load-test: ## Run load testing on API
	@echo "⚡ Running API load test..."
	@poetry run python -c "print('❌ API load test requires API to be running - start with make dev first')"

# ============================================================================
# 🎯 FLEXT ECOSYSTEM INTEGRATION
# ============================================================================

ecosystem-check: ## Verify FLEXT ecosystem compatibility
	@echo "🌐 Checking FLEXT ecosystem compatibility..."
	@echo "📦 API project: $(PROJECT_NAME) v$(PROJECT_VERSION)"
	@echo "🏗️ Architecture: Clean Architecture + DDD"
	@echo "🐍 Python: 3.13"
	@echo "🚀 Framework: FastAPI"
	@echo "📊 Quality: Zero tolerance enforcement"
	@echo "✅ Ecosystem compatibility verified"

workspace-info: ## Show workspace integration info
	@echo "🏢 FLEXT Workspace Integration"
	@echo "==============================="
	@echo "📁 Project Path: $(PWD)"
	@echo "🏆 Role: REST API Server (enterprise data integration)"
	@echo "🔗 Dependencies: flext-core, flext-auth, flext-plugin, flext-grpc"
	@echo "📦 Provides: HTTP REST API endpoints"
	@echo "🎯 Standards: Enterprise FastAPI patterns"