# Testing Plan & Strategy

## Overview

This document describes the current testing strategy for `flext_api`. The public API surface is intentionally small and testable:

- `FlextApiSettings` for configuration.
- `FlextApiClient` for the low-level HTTP client.
- `FlextApi` for the high-level HTTP facade (`get`, `post`, `put`, `patch`, `delete`, `request`).
- `m.Api.HttpRequest` and `m.Api.HttpResponse` for typed request/response values.
- `p.Result` and `r.ok` / `r.fail` for railway-style error handling.

Tests should validate the real contract: every `FlextApi` method returns `p.Result[m.Api.HttpResponse]`, successes are inspected via `result.unwrap()`, and failures are inspected via `result.error`.

## Test Structure

```text
tests/
├── unit/           # Fast, isolated tests of helpers and models
├── integration/    # Multi-component tests with a fake or real HTTP layer
├── e2e/            # Full workflow tests against a real service
└── conftest.py     # Shared pytest fixtures and configuration
```

The examples below use plain functions and deterministic `FakeApi` subclasses. They run as standalone scripts and can also be collected by pytest.

## Unit Tests

Unit tests exercise one behavior at a time. A `FakeApi` subclass replaces the real HTTP backend so the tests run without network access.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users") and str(request.method) == "GET":
            body = [{"id": 1, "name": "Alice"}]
        elif request.url.endswith("/users/404"):
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body={"error": "not found"},
                    request_id="unit-1",
                )
            )
        else:
            body = {"ok": True}
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=body,
                request_id="unit-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = FakeApi(settings=settings)


def test_get_users_returns_success() -> None:
    result = api.get("/users")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert isinstance(response.body, list)


def test_not_found_is_classified() -> None:
    result = api.get("/users/404")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 404
    assert response.client_error


test_get_users_returns_success()
test_not_found_is_classified()
```

Model validation can also be tested in isolation.

```python
from __future__ import annotations
from flext_api import c, m, p, r, t, u


def test_request_model_requires_valid_url() -> None:
    request = m.Api.HttpRequest(method="GET", url="https://api.example.com/users")
    assert request.method == c.Api.Method.GET
    assert request.url == "https://api.example.com/users"


def test_response_model_classifies_errors() -> None:
    response = m.Api.HttpResponse(
        status_code=500,
        headers={"Content-Type": "application/json"},
        body={"error": "server error"},
        request_id="unit-2",
    )
    assert response.server_error
    assert not response.success


test_request_model_requires_valid_url()
test_response_model_classifies_errors()
```

## Integration Tests

Integration tests exercise a sequence of API calls and transformations. Use a stateful `FakeApi` subclass to simulate the backend and assert the combined outcome.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class WorkflowApi(FlextApi):
    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        super().__init__(settings=settings)
        object.__setattr__(self, "_orders", {})

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        orders: dict[int, dict] = getattr(self, "_orders")
        if request.url.endswith("/orders") and str(request.method) == "POST":
            body = request.body if isinstance(request.body, dict) else {}
            order_id = len(orders) + 1
            orders[order_id] = {"id": order_id, **body}
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=201,
                    headers={"Content-Type": "application/json"},
                    body=orders[order_id],
                    request_id="int-1",
                )
            )
        if request.url.endswith("/orders") and str(request.method) == "GET":
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                    body=list(orders.values()),
                    request_id="int-1",
                )
            )
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="int-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = WorkflowApi(settings=settings)


def test_create_and_list_orders() -> None:
    create_result = api.post("/orders", data={"item": "book", "quantity": 2})
    assert create_result.success
    created = create_result.unwrap()
    assert created.status_code == 201
    body = created.body
    assert isinstance(body, dict)
    assert body.get("item") == "book"

    list_result = api.get("/orders")
    assert list_result.success
    orders = list_result.unwrap().body
    assert isinstance(orders, list)
    assert len(orders) == 1


test_create_and_list_orders()
```

## Running Tests

Use the root `make` commands as the canonical test runner.

```bash
# Run all tests in the flext-api project
make test PROJECT=flext-api

# Run the markdown examples
uv run pytest --markdown-docs docs/testing.md guides/http-client.md guides/testing.md -q
```

## Test Data and Helpers

Keep tests clean by extracting reusable helper functions. These can be used in standalone scripts or in pytest-collected test files.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c, m, p, r, t, u


def make_settings(base_url: str = "https://api.example.com", timeout: float = 5.0) -> FlextApiSettings:
    return FlextApiSettings(base_url=base_url, timeout=timeout)


def make_api(settings: FlextApiSettings | None = None) -> FlextApi:
    return FlextApi(settings=settings if settings is not None else make_settings())


def make_client(settings: FlextApiSettings | None = None) -> FlextApiClient:
    return FlextApiClient(settings=settings if settings is not None else make_settings())


settings = make_settings()
assert settings.Api.base_url == "https://api.example.com"
assert settings.Api.timeout == 5.0

client = make_client(settings)
assert client.base_url == "https://api.example.com"

api = make_api(settings)
assert isinstance(api, FlextApi)
```

## Mocking External APIs

Do not use `unittest.mock` in executable examples. Use a small `FakeApi` subclass to return deterministic responses and test the real `FlextApi` contract.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"id": 1, "name": "Test User"},
                request_id="mock-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = FakeApi(settings=settings)


def test_with_fake_api() -> None:
    result = api.get("/users/1")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert response.body.get("name") == "Test User"


test_with_fake_api()
```

## Success Metrics

- **Test Pass Rate**: 100% of collected tests.
- **Coverage**: follow the thresholds in `pyproject.toml`.
- **Determinism**: network-dependent tests should use `FakeApi` or be clearly marked as integration/e2e tests against a known environment.
- **Maintainability**: tests validate the real `FlextApi` contract and avoid vague assertions.

## Risk Mitigation

- **Flaky Tests**: Use `FakeApi` subclasses for deterministic unit and integration tests.
- **External Service Dependencies**: Keep real network tests in `tests/e2e/` and run them only in controlled environments.
- **Coverage Gaps**: Test success paths, error status codes, model validation, and request/response serialization.

---

**Next Priority**: Keep the markdown examples in `docs/testing.md` and `guides/testing.md` aligned with the current `FlextApi` contract as the library evolves.
