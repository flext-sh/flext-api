# Schemas API Reference

This page documents the schema/model story for `flext-api`.

> **Current status:** `flext-api` does not expose OpenAPI/JSON Schema generation
> utilities or request/response schema builders beyond the public Pydantic models
> under `m.Api`. Applications should use `m.Api.HttpRequest` and
> `m.Api.HttpResponse` as the canonical HTTP schema types.

## Public HTTP Models

```python
from __future__ import annotations

from flext_api import c, m

request = m.Api.HttpRequest(
    method=c.Api.Method.POST,
    url="https://api.example.com/users",
    headers={"Content-Type": "application/json"},
    body={"name": "Alice", "email": "alice@example.com"},
)

json_data = request.model_dump_json(exclude={"content_type"})
deserialized = m.Api.HttpRequest.model_validate_json(json_data)
assert deserialized.method == "POST"

response = m.Api.create_response(
    status_code=201,
    headers={"Content-Type": "application/json"},
    body={"id": 1, "name": "Alice"},
)
assert response.success
assert response.status_code == 201
```

## What Is Not Implemented

The following schema concepts are **not** part of the current public API and
are therefore not documented as executable examples:

- `OpenApiSchema`, `OpenApiConfig`, `create_fastapi_app`
- `AsyncApiSchema`, `JsonSchema`, `JsonSchemaValidator`
- `SchemaValidationError`, `JsonSchemaExtension`
- FastAPI-specific `response_model` integration

If a future release adds schema generation helpers, this page will be updated
with real, runnable examples.
