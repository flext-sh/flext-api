# flext-api - HTTP API Framework
PROJECT_NAME := flext-api
COV_DIR := flext_api
MIN_COVERAGE := 100

include ../base.mk

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: dev api-docs test-unit test-integration build shell

# FastAPI Configuration
API_HOST ?= 0.0.0.0
API_PORT ?= 8000

dev: ## Start development server
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run uvicorn flext_api:app --reload --host $(API_HOST) --port $(API_PORT)

api-docs: ## Generate OpenAPI documentation
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_api import app; import json; print(json.dumps(app.openapi(), indent=2))"

.DEFAULT_GOAL := help
