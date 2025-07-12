# FLEXT-API Makefile - Enterprise FastAPI Gateway
# Uses FLEXT standardized patterns and flext-core integration

# Project Configuration
PROJECT_NAME := flext-api
PYTHON_VERSION := 3.13
POETRY := poetry
PYTHON := $(POETRY) run python
PYTEST := $(POETRY) run pytest
RUFF := $(POETRY) run ruff
MYPY := $(POETRY) run mypy

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

## Help
help: ## Show this help message
	@echo "$(BLUE)FLEXT-API Makefile$(RESET)"
	@echo "Enterprise FastAPI Gateway Service"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

## Development
install: ## Install all dependencies
	@echo "$(BLUE)📦 Installing dependencies for $(PROJECT_NAME)...$(RESET)"
	@$(POETRY) install
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)📦 Installing development dependencies...$(RESET)"
	@$(POETRY) install --with dev
	@echo "$(GREEN)✅ Development dependencies installed$(RESET)"

update: ## Update dependencies
	@echo "$(BLUE)🔄 Updating dependencies...$(RESET)"
	@$(POETRY) update
	@echo "$(GREEN)✅ Dependencies updated$(RESET)"

## Code Quality
lint: ## Run linting
	@echo "$(BLUE)🔍 Running linting for $(PROJECT_NAME)...$(RESET)"
	@$(RUFF) check src/ tests/ || true
	@echo "$(GREEN)✅ Linting complete$(RESET)"

lint-fix: ## Fix linting issues
	@echo "$(BLUE)🔧 Fixing linting issues...$(RESET)"
	@$(RUFF) check --fix src/ tests/ || true
	@$(RUFF) format src/ tests/ || true
	@echo "$(GREEN)✅ Linting issues fixed$(RESET)"

format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	@$(RUFF) format src/ tests/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

type-check: ## Run type checking
	@echo "$(BLUE)🔍 Running type checking...$(RESET)"
	@$(MYPY) src/flext_api/ || true
	@echo "$(GREEN)✅ Type checking complete$(RESET)"

check: lint type-check ## Run all code quality checks

## Testing
test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests for $(PROJECT_NAME)...$(RESET)"
	@$(PYTEST) -v
	@echo "$(GREEN)✅ All tests passed$(RESET)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	@$(PYTEST) tests/unit/ -v -m "not integration"
	@echo "$(GREEN)✅ Unit tests passed$(RESET)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	@$(PYTEST) tests/integration/ -v -m "integration"
	@echo "$(GREEN)✅ Integration tests passed$(RESET)"

test-cov: ## Run tests with coverage
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	@$(PYTEST) --cov=flext_api --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Tests with coverage complete$(RESET)"

## API Operations
api-config: ## Show current API configuration
	@echo "$(BLUE)⚙️ Showing FLEXT API configuration...$(RESET)"
	@$(PYTHON) -m flext_api.cli config

api-test: ## Test API system
	@echo "$(BLUE)🧪 Testing FLEXT API system...$(RESET)"
	@$(PYTHON) -m flext_api.cli test

api-serve: ## Start API server (development)
	@echo "$(BLUE)🚀 Starting FLEXT API server (development)...$(RESET)"
	@$(PYTHON) -m flext_api.cli serve --reload

api-serve-prod: ## Start API server (production)
	@echo "$(BLUE)🚀 Starting FLEXT API server (production)...$(RESET)"
	@$(PYTHON) -m flext_api.cli serve --workers 4

api-health: ## Check API health
	@echo "$(BLUE)🏥 Checking FLEXT API health...$(RESET)"
	@$(PYTHON) -m flext_api.cli health

api-docs: ## Open API documentation
	@echo "$(BLUE)📚 Opening API documentation...$(RESET)"
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	@echo "OpenAPI Schema: http://localhost:8000/openapi.json"

## Docker Operations
docker-build: ## Build Docker image
	@echo "$(BLUE)🐳 Building Docker image for $(PROJECT_NAME)...$(RESET)"
	@docker build -t flext-api:latest .
	@echo "$(GREEN)✅ Docker image built$(RESET)"

docker-run: ## Run Docker container
	@echo "$(BLUE)🐳 Running Docker container...$(RESET)"
	@docker run -p 8000:8000 --env-file .env flext-api:latest

docker-compose: ## Run with docker-compose
	@echo "$(BLUE)🐳 Starting services with docker-compose...$(RESET)"
	@docker-compose up -d

## Build and Distribution
build: ## Build the package
	@echo "$(BLUE)🏗️ Building $(PROJECT_NAME)...$(RESET)"
	@$(POETRY) build
	@echo "$(GREEN)✅ Package built$(RESET)"

clean: ## Clean build artifacts
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	@rm -rf dist/ build/ *.egg-info/
	@rm -rf .coverage htmlcov/ .pytest_cache/
	@rm -rf .mypy_cache/ .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Build artifacts cleaned$(RESET)"

## Development Utilities
shell: ## Start Python shell with project context
	@echo "$(BLUE)🐍 Starting Python shell...$(RESET)"
	@$(POETRY) shell

env: ## Show environment information
	@echo "$(BLUE)🌍 Environment Information:$(RESET)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)"
	@echo "Poetry: $(shell $(POETRY) --version)"
	@echo "Virtual Environment: $(shell $(POETRY) env info --path)"

## Security
security: ## Run security checks
	@echo "$(BLUE)🔒 Running security checks...$(RESET)"
	@$(POETRY) run bandit -r src/ || true
	@echo "$(GREEN)✅ Security checks complete$(RESET)"

## Version Management
version: ## Show current version
	@echo "$(BLUE)📋 Current version:$(RESET)"
	@$(POETRY) version

bump-patch: ## Bump patch version
	@echo "$(BLUE)📈 Bumping patch version...$(RESET)"
	@$(POETRY) version patch
	@echo "$(GREEN)✅ Patch version bumped$(RESET)"

bump-minor: ## Bump minor version
	@echo "$(BLUE)📈 Bumping minor version...$(RESET)"
	@$(POETRY) version minor
	@echo "$(GREEN)✅ Minor version bumped$(RESET)"

bump-major: ## Bump major version
	@echo "$(BLUE)📈 Bumping major version...$(RESET)"
	@$(POETRY) version major
	@echo "$(GREEN)✅ Major version bumped$(RESET)"

## Load Testing
load-test: ## Run load tests (requires locust)
	@echo "$(BLUE)⚡ Running load tests...$(RESET)"
	@$(POETRY) run locust -f tests/load/locustfile.py --host=http://localhost:8000

## Quick Development Workflow
dev: install lint-fix test ## Full development workflow (install, fix, test)
	@echo "$(GREEN)✅ Development workflow complete$(RESET)"

ci: check test ## Continuous integration workflow
	@echo "$(GREEN)✅ CI workflow complete$(RESET)"

## Information
info: ## Show project information
	@echo "$(BLUE)📊 Project Information:$(RESET)"
	@echo "Name: $(PROJECT_NAME)"
	@echo "Description: FLEXT API - Enterprise FastAPI Gateway"
	@echo "Python: $(PYTHON_VERSION)"
	@echo "Poetry: $(shell $(POETRY) --version)"
	@echo ""
	@echo "$(GREEN)📁 Project Structure:$(RESET)"
	@echo "├── src/flext_api/          # Source code"
	@echo "├── tests/                  # Test files"
	@echo "├── pyproject.toml         # Project configuration"
	@echo "├── Makefile               # This file"
	@echo "└── README.md              # Documentation"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(RESET)"
	@echo "1. make install            # Install dependencies"
	@echo "2. make api-test           # Test the system"
	@echo "3. make api-serve          # Start development server"
	@echo "4. make dev                # Full development workflow"
	@echo ""
	@echo "$(GREEN)🌐 API Endpoints:$(RESET)"
	@echo "• http://localhost:8000/docs     - Swagger UI"
	@echo "• http://localhost:8000/redoc    - ReDoc"
	@echo "• http://localhost:8000/health   - Health check"
	@echo ""
	@echo "Documentation available in README.md"

.PHONY: help install install-dev update lint lint-fix format type-check check test test-unit test-integration test-cov api-config api-test api-serve api-serve-prod api-health api-docs docker-build docker-run docker-compose build clean shell env security version bump-patch bump-minor bump-major load-test dev ci info
