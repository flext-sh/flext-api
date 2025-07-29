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
	@$(POETRY) run bandit -r $(SRC_DIR) -c pyproject.toml
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
# TESTING - Optimized with pytest plugins
# =============================================================================

.PHONY: test
test: ## Run all tests with optimized coverage
	@echo "🧪 Running optimized test suite..."
	@PYTHONPATH=src $(POETRY) run pytest

.PHONY: test-unit
test-unit: ## Run unit tests only (fast with parallel execution)
	@echo "⚡ Running unit tests in parallel..."
	@PYTHONPATH=src $(POETRY) run pytest -m unit -n auto --dist=loadfile --tb=short

.PHONY: test-unit-fast
test-unit-fast: ## Run unit tests without coverage (fastest)
	@echo "🚀 Running unit tests (no coverage)..."
	@PYTHONPATH=src $(POETRY) run pytest -m unit --no-cov -q

.PHONY: test-integration
test-integration: ## Run integration tests with timeout protection
	@echo "🔗 Running integration tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m integration --timeout=600 -v

.PHONY: test-e2e
test-e2e: ## Run end-to-end tests
	@echo "🎯 Running E2E tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m e2e --timeout=600 -v

.PHONY: test-api
test-api: ## Run API endpoint tests
	@echo "🌐 Running API endpoint tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m api -v

.PHONY: test-client
test-client: ## Run HTTP client tests
	@echo "📡 Running HTTP client tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m client -v

.PHONY: test-builder
test-builder: ## Run builder pattern tests
	@echo "🏗️ Running builder pattern tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m builder -v

.PHONY: test-core
test-core: ## Run core functionality tests
	@echo "🔧 Running core functionality tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m core -v

.PHONY: test-smoke
test-smoke: ## Run smoke tests for CI
	@echo "💨 Running smoke tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m smoke -x --tb=no -q

.PHONY: test-parallel
test-parallel: ## Run all tests in parallel (maximum speed)
	@echo "⚡ Running tests in parallel..."
	@PYTHONPATH=src $(POETRY) run pytest -n auto --dist=loadfile

.PHONY: test-random
test-random: ## Run tests in random order to detect dependencies
	@echo "🎲 Running tests in random order..."
	@PYTHONPATH=src $(POETRY) run pytest --randomly-seed=12345

.PHONY: test-failed
test-failed: ## Re-run only failed tests from last execution
	@echo "🔄 Re-running failed tests..."
	@PYTHONPATH=src $(POETRY) run pytest --lf -v

.PHONY: test-debug
test-debug: ## Run tests with enhanced debugging
	@echo "🐛 Running tests with debug info..."
	@PYTHONPATH=src $(POETRY) run pytest -v --tb=long --log-cli --log-cli-level=DEBUG

.PHONY: test-benchmark
test-benchmark: ## Run performance benchmarks
	@echo "📊 Running performance benchmarks..."
	@PYTHONPATH=src $(POETRY) run pytest -m benchmark --benchmark-only --benchmark-sort=mean

.PHONY: test-dead-fixtures
test-dead-fixtures: ## Find unused test fixtures
	@echo "🕵️ Finding dead fixtures..."
	@PYTHONPATH=src $(POETRY) run pytest --dead-fixtures

.PHONY: test-collect
test-collect: ## Show test collection without running
	@echo "📋 Collecting tests..."
	@PYTHONPATH=src $(POETRY) run pytest --collect-only -q

.PHONY: coverage
coverage: ## Generate comprehensive coverage report
	@echo "📊 Generating coverage report..."
	@PYTHONPATH=src $(POETRY) run pytest --cov-report=html --cov-report=xml --cov-report=term-missing

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	@echo "📊 Generating HTML coverage report..."
	@PYTHONPATH=src $(POETRY) run pytest --cov-report=html --no-cov-on-fail
	@echo "📊 Coverage report: htmlcov/index.html"

.PHONY: coverage-xml
coverage-xml: ## Generate XML coverage report for CI
	@echo "📊 Generating XML coverage report..."
	@PYTHONPATH=src $(POETRY) run pytest --cov-report=xml

.PHONY: test-profile
test-profile: ## Profile test execution for optimization
	@echo "⏱️ Profiling test execution..."
	@PYTHONPATH=src $(POETRY) run pytest --durations=10 -v

.PHONY: test-security
test-security: ## Run security-related tests
	@echo "🔒 Running security tests..."
	@PYTHONPATH=src $(POETRY) run pytest -m security -v

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