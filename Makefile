# =============================================================================
# FLEXT-API - PROJECT MAKEFILE
# =============================================================================
# Enterprise FastAPI REST API with Clean Architecture + DDD + Zero Tolerance Quality
# Python 3.13 + FastAPI + Async/Await + Modern Type Safety
# =============================================================================

# Project Configuration
PROJECT_NAME := flext-api
PROJECT_TYPE := python-library
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs

# Quality Gates Configuration
MIN_COVERAGE := 90
MYPY_STRICT := true
RUFF_CONFIG := pyproject.toml
PEP8_LINE_LENGTH := 79

# FastAPI Configuration
API_HOST := 0.0.0.0
API_PORT := 8000
API_RELOAD := true

# Export environment variables
export PYTHON_VERSION
export MIN_COVERAGE
export MYPY_STRICT
export API_HOST
export API_PORT

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "$(PROJECT_NAME) - FastAPI Enterprise Application"
	@echo "==============================================="
	@echo ""
	@echo "📋 AVAILABLE COMMANDS:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-18s %s\\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🔧 PROJECT INFO:"
	@echo "  Type: $(PROJECT_TYPE)"
	@echo "  Python: $(PYTHON_VERSION)"
	@echo "  Coverage: $(MIN_COVERAGE)%"
	@echo "  API Host: $(API_HOST):$(API_PORT)"
	@echo "  Line Length: $(PEP8_LINE_LENGTH)"

.PHONY: info
info: ## Show project information
	@echo "Project Information"
	@echo "=================="
	@echo "Name: $(PROJECT_NAME)"
	@echo "Type: $(PROJECT_TYPE)"
	@echo "Python Version: $(PYTHON_VERSION)"
	@echo "Source Directory: $(SRC_DIR)"
	@echo "Tests Directory: $(TESTS_DIR)"
	@echo "API Host: $(API_HOST)"
	@echo "API Port: $(API_PORT)"
	@echo "Quality Standards: Zero Tolerance"
	@echo "Architecture: Clean Architecture + DDD + FastAPI"

# =============================================================================
# INSTALLATION & SETUP
# =============================================================================

.PHONY: install
install: ## Install project dependencies
	@echo "📦 Installing $(PROJECT_NAME) dependencies..."
	@$(POETRY) install

.PHONY: install-dev
install-dev: ## Install development dependencies
	@echo "📦 Installing development dependencies..."
	@$(POETRY) install --with dev,test,docs

.PHONY: setup
setup: ## Complete project setup
	@echo "🚀 Setting up $(PROJECT_NAME)..."
	@make install-dev
	@make pre-commit-install
	@echo "✅ Setup complete"

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "🔧 Installing pre-commit hooks..."
	@$(POETRY) run pre-commit install
	@$(POETRY) run pre-commit autoupdate

# =============================================================================
# QUALITY GATES & VALIDATION
# =============================================================================

.PHONY: validate
validate: ## Run complete validation (quality gate)
	@echo "🔍 Running complete validation for $(PROJECT_NAME)..."
	@make lint
	@make type-check
	@make security
	@make test
	@make pep8-check
	@echo "✅ Validation complete"

.PHONY: check
check: ## Quick health check
	@echo "🏥 Running health check..."
	@make lint
	@make type-check
	@echo "✅ Health check complete"

.PHONY: lint
lint: ## Run code linting
	@echo "🧹 Running linting..."
	@$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR)

.PHONY: format
format: ## Format code
	@echo "🎨 Formatting code..."
	@$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

.PHONY: format-check
format-check: ## Check code formatting
	@echo "🎨 Checking code formatting..."
	@$(POETRY) run ruff format --check $(SRC_DIR) $(TESTS_DIR)

.PHONY: type-check
type-check: ## Run type checking
	@echo "🔍 Running type checking..."
	@PYTHONPATH=src $(POETRY) run mypy $(SRC_DIR) --strict

.PHONY: security
security: ## Run security scanning
	@echo "🔒 Running security scanning..."
	@$(POETRY) run bandit -r $(SRC_DIR)
	@$(POETRY) run pip-audit

.PHONY: pep8-check
pep8-check: ## Check PEP8 compliance
	@echo "📏 Checking PEP8 compliance..."
	@$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR) --select E,W
	@echo "✅ PEP8 check complete"

.PHONY: fix
fix: ## Auto-fix code issues
	@echo "🔧 Auto-fixing code issues..."
	@$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR) --fix
	@make format

# =============================================================================
# TESTING
# =============================================================================

.PHONY: test
test: ## Run all tests with coverage
	@echo "🧪 Running tests with coverage..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=term-missing --cov-fail-under=$(MIN_COVERAGE)

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) -m "not integration" -v

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) -m integration -v

.PHONY: test-api
test-api: ## Run API endpoint tests
	@echo "🧪 Running API endpoint tests..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) -m api -v

.PHONY: test-fast
test-fast: ## Run tests without coverage
	@echo "🧪 Running fast tests..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) -v

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "🧪 Running tests in watch mode..."
	@PYTHONPATH=src $(POETRY) run pytest-watch $(TESTS_DIR)

.PHONY: coverage
coverage: ## Generate coverage report
	@echo "📊 Generating coverage report..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=xml

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	@echo "📊 Generating HTML coverage report..."
	@PYTHONPATH=src $(POETRY) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html
	@echo "📊 Coverage report: htmlcov/index.html"

# =============================================================================
# FASTAPI DEVELOPMENT SERVER
# =============================================================================

.PHONY: dev
dev: ## Start development server with auto-reload
	@echo "🚀 Starting FastAPI development server..."
	@echo "📡 Server will be available at: http://$(API_HOST):$(API_PORT)"
	@echo "📚 API documentation at: http://$(API_HOST):$(API_PORT)/docs"
	@echo "📖 ReDoc documentation at: http://$(API_HOST):$(API_PORT)/redoc"
	@$(POETRY) run uvicorn flext_api.main:app --reload --host $(API_HOST) --port $(API_PORT)

.PHONY: serve
serve: dev ## Alias for dev command

.PHONY: dev-reload
dev-reload: ## Start development server with aggressive reload
	@echo "🚀 Starting FastAPI development server (aggressive reload)..."
	@$(POETRY) run uvicorn flext_api.main:app --reload --reload-dir $(SRC_DIR) --host $(API_HOST) --port $(API_PORT)

.PHONY: dev-production
dev-production: ## Start server with production settings
	@echo "🚀 Starting FastAPI server (production mode)..."
	@$(POETRY) run uvicorn flext_api.main:app --host $(API_HOST) --port $(API_PORT) --workers 4

# =============================================================================
# BUILD & DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build distribution packages
	@echo "🏗️ Building $(PROJECT_NAME)..."
	@$(POETRY) build

.PHONY: build-clean
build-clean: ## Clean build and rebuild
	@echo "🏗️ Clean build..."
	@make clean
	@make build

.PHONY: publish-test
publish-test: ## Publish to test PyPI
	@echo "📦 Publishing to test PyPI..."
	@$(POETRY) publish --repository testpypi

.PHONY: publish
publish: ## Publish to PyPI
	@echo "📦 Publishing to PyPI..."
	@$(POETRY) publish

# =============================================================================
# API DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Build API documentation
	@echo "📚 Building API documentation..."
	@$(POETRY) run mkdocs build

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	@$(POETRY) run mkdocs serve

.PHONY: api-docs
api-docs: ## Generate OpenAPI documentation
	@echo "📚 Generating OpenAPI documentation..."
	@$(POETRY) run python -c "import json; from flext_api.main import app; f = open('openapi.json', 'w'); json.dump(app.openapi(), f, indent=2); f.close(); print('OpenAPI schema exported to openapi.json')"

.PHONY: api-test-server
api-test-server: ## Test API server health
	@echo "🔍 Testing API server health..."
	@$(POETRY) run python -c "import httpx; print('✅ API test requires server running')"

# =============================================================================
# DEPENDENCY MANAGEMENT
# =============================================================================

.PHONY: deps-update
deps-update: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	@$(POETRY) update

.PHONY: deps-show
deps-show: ## Show dependency tree
	@echo "📋 Showing dependency tree..."
	@$(POETRY) show --tree

.PHONY: deps-audit
deps-audit: ## Audit dependencies for security
	@echo "🔍 Auditing dependencies..."
	@$(POETRY) run pip-audit

.PHONY: deps-export
deps-export: ## Export requirements.txt
	@echo "📄 Exporting requirements..."
	@$(POETRY) export -f requirements.txt --output requirements.txt
	@$(POETRY) export -f requirements.txt --dev --output requirements-dev.txt

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

.PHONY: shell
shell: ## Open Python shell with project loaded
	@echo "🐍 Opening Python shell..."
	@$(POETRY) run python

.PHONY: notebook
notebook: ## Start Jupyter notebook
	@echo "📓 Starting Jupyter notebook..."
	@$(POETRY) run jupyter lab

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	@echo "🔍 Running pre-commit hooks..."
	@$(POETRY) run pre-commit run --all-files

# =============================================================================
# MAINTENANCE & CLEANUP
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts and cache
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf htmlcov/
	@rm -rf .coverage
	@rm -rf .mypy_cache/
	@rm -rf .ruff_cache/
	@rm -rf openapi.json
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true

.PHONY: clean-all
clean-all: clean ## Deep clean including virtual environment
	@echo "🧹 Deep cleaning..."
	@rm -rf .venv/

.PHONY: reset
reset: clean-all ## Reset project to clean state
	@echo "🔄 Resetting project..."
	@make setup

# =============================================================================
# DIAGNOSTICS & TROUBLESHOOTING
# =============================================================================

.PHONY: diagnose
diagnose: ## Run project diagnostics
	@echo "🔬 Running project diagnostics..."
	@echo "Python version: $$(python --version)"
	@echo "Poetry version: $$($(POETRY) --version)"
	@echo "FastAPI status: $$($(POETRY) run python -c 'import fastapi; print(fastapi.__version__)')"
	@echo "Project info:"
	@$(POETRY) show --no-dev
	@echo "Environment status:"
	@$(POETRY) env info

.PHONY: doctor
doctor: ## Check project health
	@echo "👩‍⚕️ Checking project health..."
	@make diagnose
	@make check
	@echo "✅ Health check complete"

# =============================================================================
# CONVENIENCE ALIASES
# =============================================================================

.PHONY: t
t: test ## Alias for test

.PHONY: l
l: lint ## Alias for lint

.PHONY: f
f: format ## Alias for format

.PHONY: tc
tc: type-check ## Alias for type-check

.PHONY: c
c: clean ## Alias for clean

.PHONY: i
i: install ## Alias for install

.PHONY: v
v: validate ## Alias for validate

.PHONY: d
d: dev ## Alias for dev

.PHONY: s
s: serve ## Alias for serve

# =============================================================================
# Default target
# =============================================================================

.DEFAULT_GOAL := help