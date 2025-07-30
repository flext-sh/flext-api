# FLEXT-API Makefile
PROJECT_NAME := flext-api
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests

# Quality standards
MIN_COVERAGE := 90

# FastAPI Configuration
API_HOST := 0.0.0.0
API_PORT := 8000

# Help
help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Installation
install: ## Install dependencies
	$(POETRY) install

install-dev: ## Install dev dependencies
	$(POETRY) install --with dev,test,docs

setup: install-dev ## Complete project setup
	$(POETRY) run pre-commit install

# Quality gates
validate: lint type-check security test ## Run all quality gates

check: lint type-check ## Quick health check

lint: ## Run linting
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR)

format: ## Format code
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

type-check: ## Run type checking
	PYTHONPATH=src $(POETRY) run mypy $(SRC_DIR) --strict

security: ## Run security scanning
	$(POETRY) run bandit -r $(SRC_DIR) -c pyproject.toml
	$(POETRY) run pip-audit

fix: ## Auto-fix issues
	$(POETRY) run ruff check $(SRC_DIR) $(TESTS_DIR) --fix
	$(POETRY) run ruff format $(SRC_DIR) $(TESTS_DIR)

# Testing
test: ## Run tests with coverage
	PYTHONPATH=src $(POETRY) run pytest

test-unit: ## Run unit tests
	PYTHONPATH=src $(POETRY) run pytest -m unit -n auto --dist=loadfile --tb=short

test-integration: ## Run integration tests
	PYTHONPATH=src $(POETRY) run pytest -m integration --timeout=600 -v

test-api: ## Run API endpoint tests
	PYTHONPATH=src $(POETRY) run pytest -m api -v

test-fast: ## Run tests without coverage
	PYTHONPATH=src $(POETRY) run pytest --no-cov -q

coverage-html: ## Generate HTML coverage report
	PYTHONPATH=src $(POETRY) run pytest --cov-report=html --no-cov-on-fail

# FastAPI Development
dev: ## Start development server
	$(POETRY) run uvicorn flext_api.main:app --reload --host $(API_HOST) --port $(API_PORT)

serve: dev ## Alias for dev

api-docs: ## Generate OpenAPI documentation
	$(POETRY) run python -c "import json; from flext_api.main import app; f = open('openapi.json', 'w'); json.dump(app.openapi(), f, indent=2); f.close(); print('OpenAPI schema exported to openapi.json')"

# Build
build: ## Build package
	$(POETRY) build

build-clean: clean build ## Clean and build

# Documentation
docs: ## Build documentation
	$(POETRY) run mkdocs build

docs-serve: ## Serve documentation
	$(POETRY) run mkdocs serve

# Dependencies
deps-update: ## Update dependencies
	$(POETRY) update

deps-show: ## Show dependency tree
	$(POETRY) show --tree

deps-audit: ## Audit dependencies
	$(POETRY) run pip-audit

# Development
shell: ## Open Python shell
	$(POETRY) run python

pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# Maintenance
clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/ openapi.json
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

clean-all: clean ## Deep clean including venv
	rm -rf .venv/

reset: clean-all setup ## Reset project

# Diagnostics
diagnose: ## Project diagnostics
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@echo "FastAPI: $$($(POETRY) run python -c 'import fastapi; print(fastapi.__version__)')"
	@$(POETRY) env info

doctor: diagnose check ## Health check

# Aliases
t: test
l: lint
f: format
tc: type-check
c: clean
i: install
v: validate
d: dev
s: serve

.DEFAULT_GOAL := help
.PHONY: help install install-dev setup validate check lint format type-check security fix test test-unit test-integration test-api test-fast coverage-html dev serve api-docs build build-clean docs docs-serve deps-update deps-show deps-audit shell pre-commit clean clean-all reset diagnose doctor t l f tc c i v d s