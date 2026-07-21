# Private project handlers for flext-api.
# Strict extension: only `_custom_<verb>_<what>` handlers and `(pre|post)-<verb>[-<what>]`
# hooks. Public targets, toolchain vars, .DEFAULT_GOAL, includes, and help are
# invalid (base.mk owns those). Each handler maps to `make <verb> WHAT=<what>`.
.PHONY: _custom_run_dev _custom_run_openapi
_custom_run_dev: ## make run WHAT=dev — start dev server (uvicorn, reload)
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run uvicorn flext_api:app --reload --host 0.0.0.0 --port 8000
_custom_run_openapi: ## make run WHAT=openapi — print OpenAPI schema
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run python -c "from flext_api import app; import json; print(json.dumps(app.openapi(), indent=2))"
