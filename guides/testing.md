<!-- Generated from docs/guides/testing.md for flext-api. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-api - Testing Guide

> Project profile: `flext-api`

<!-- TOC START -->
- [flext-api - Testing Guide](#flext-api---testing-guide)
  - [Overview](#overview)
  - [Test Structure](#test-structure)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [End-to-End Tests](#end-to-end-tests)
  - [Running Tests](#running-tests)
  - [Test Helpers](#test-helpers)
  - [Mocking External APIs](#mocking-external-apis)
  - [Performance Testing](#performance-testing)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
<!-- TOC END -->

This guide covers how to test code that uses `flext_api`. All Python examples use plain functions and real `flext_api` APIs, so they can be executed as standalone scripts as well as collected by pytest.

## Overview

`flext_api` exposes a small, deterministic public surface:

- `FlextApiSettings` for configuration.
- `FlextApiClient` for the low-level HTTP client.
- `FlextApi` for the high-level HTTP facade (`get`, `post`, `put`, `patch`, `delete`, `request`).
- `m.Api.HttpRequest` and `m.Api.HttpResponse` for typed request/response values.
- `p.Result` and `r.ok` / `r.fail` for railway-style error handling.

Tests should validate the real API contract: `FlextApi` methods return `p.Result[m.Api.HttpResponse]`, successes are inspected via `result.unwrap()`, and failures are inspected via `result.error`.

## Test Structure

A typical `flext-api` test layout looks like this:

```text
tests/
├── unit/           # Fast, isolated tests of helpers and models
├── integration/    # Multi-component tests with a fake or real HTTP layer
├── e2e/            # Full workflow tests (usually against a real service)
└── conftest.py     # Shared pytest fixtures and configuration
```

The examples below do not use `pytest` fixtures because `pytest-markdown-docs` runs each Python block as a standalone script. Instead, they use plain factory functions and deterministic `FakeApi` transports.

## Unit Tests

Unit tests exercise one piece of behavior in isolation. Here, a `FakeApi` subclass stands in for the real HTTP backend so the tests run without network access.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users") and str(request.method) == "GET":
            body = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        elif request.url.endswith("/users/404"):
            body = {"error": "not found"}
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=404,
                    headers={"Content-Type": "application/json"},
                    body=body,
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


def test_get_users_returns_list() -> None:
    result = api.get("/users")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert isinstance(response.body, list)
    assert len(response.body) == 2


def test_not_found_response_is_classified() -> None:
    result = api.get("/users/404")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 404
    assert response.client_error
    assert not response.success


test_get_users_returns_list()
test_not_found_response_is_classified()
```

You can also test model validation directly.

```python
from __future__ import annotations
from flext_api import c, m, p, r, t, u


def test_http_request_model_validates_url() -> None:
    request = m.Api.HttpRequest(
        method="GET",
        url="https://api.example.com/users",
        headers={"Accept": "application/json"},
    )
    assert request.method == c.Api.Method.GET
    assert request.url == "https://api.example.com/users"


def test_http_response_model_classifies_status() -> None:
    response = m.Api.HttpResponse(
        status_code=500,
        headers={"Content-Type": "application/json"},
        body={"error": "server error"},
        request_id="unit-2",
    )
    assert response.server_error
    assert response.error
    assert not response.success


test_http_request_model_validates_url()
test_http_response_model_classifies_status()
```

## Integration Tests

Integration tests exercise a sequence of API calls and transformations. Use a `FakeApi` subclass to simulate the backend and assert the combined outcome.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeStoreApi(FlextApi):
    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        super().__init__(settings=settings)
        object.__setattr__(self, "_users", {1: {"id": 1, "name": "Alice"}})

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        users: dict[int, dict] = getattr(self, "_users")
        if request.url.endswith("/users") and str(request.method) == "POST":
            body = request.body if isinstance(request.body, dict) else {}
            new_id = max(users.keys(), default=0) + 1
            users[new_id] = {"id": new_id, **body}
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=201,
                    headers={"Content-Type": "application/json"},
                    body=users[new_id],
                    request_id="int-1",
                )
            )
        if request.url.endswith("/users") and str(request.method) == "GET":
            return r[m.Api.HttpResponse].ok(
                m.Api.HttpResponse(
                    status_code=200,
                    headers={"Content-Type": "application/json"},
                    body=list(users.values()),
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


def create_user(api: FlextApi, name: str, email: str) -> p.Result[m.Api.HttpResponse]:
    return api.post("/users", data={"name": name, "email": email})


def list_users(api: FlextApi) -> p.Result[m.Api.HttpResponse]:
    return api.get("/users")


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
store_api = FakeStoreApi(settings=settings)


def test_create_user_and_list_users() -> None:
    create_result = create_user(store_api, "Bob", "bob@example.com")
    assert create_result.success
    created = create_result.unwrap()
    assert created.status_code == 201
    body = created.body
    assert isinstance(body, dict)
    assert body.get("name") == "Bob"

    list_result = list_users(store_api)
    assert list_result.success
    users = list_result.unwrap().body
    assert isinstance(users, list)
    assert len(users) == 2


test_create_user_and_list_users()
```

In real integration tests, point `FlextApiSettings` at a running service or use the global `settings` instance configured for the test environment.

## End-to-End Tests

End-to-end tests exercise the full request lifecycle, including URL construction and request/response model validation. The example uses a `FakeApi` transport to avoid external dependencies; in production, the same code would hit a real HTTP server.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class EchoApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={
                    "method": str(request.method),
                    "url": request.url,
                    "query_params": dict(request.query_params or {}),
                    "body": request.body,
                },
                request_id="e2e-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = EchoApi(settings=settings)


def test_end_to_end_request_flow() -> None:
    result = api.post(
        "/users",
        data={"name": "Alice", "email": "alice@example.com"},
        headers={"X-Request-ID": "req-42"},
        request_kwargs={"params": {"source": "onboarding"}},
    )
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    body = response.body
    assert isinstance(body, dict)
    assert body.get("method") == "POST"
    assert body.get("query_params") == {"source": "onboarding"}


test_end_to_end_request_flow()
```

## Running Tests

The project uses `make` as the canonical test runner.

```bash
# Run all tests for the workspace or a single project
make test
make test PROJECT=flext-api

# Run only the markdown-doc tests
uv run pytest --markdown-docs guides/http-client.md guides/testing.md docs/testing.md -q
```

When you are inside the `flext-api` project directory, you can also run pytest directly:

```bash
cd /home/marlonsc/flext/flext-api
uv run pytest -q
```

## Test Helpers

Keep tests clean by extracting reusable helpers instead of pytest fixtures. These helpers can be imported and used in standalone scripts or collected by pytest.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c, m, p, r, t, u


def make_api_settings(base_url: str = "https://api.example.com", timeout: float = 5.0) -> FlextApiSettings:
    return FlextApiSettings(base_url=base_url, timeout=timeout)


def make_api(settings: FlextApiSettings | None = None) -> FlextApi:
    return FlextApi(settings=settings if settings is not None else make_api_settings())


def make_client(settings: FlextApiSettings | None = None) -> FlextApiClient:
    return FlextApiClient(settings=settings if settings is not None else make_api_settings())


settings = make_api_settings()
assert settings.Api.base_url == "https://api.example.com"
assert settings.Api.timeout == 5.0

client = make_client(settings)
assert client.base_url == "https://api.example.com"
assert client.timeout == 5.0

api = make_api(settings)
assert isinstance(api, FlextApi)
```

## Mocking External APIs

Avoid `unittest.mock` in executable examples. Instead, create a small `FakeApi` subclass that returns deterministic responses. This pattern tests the real `FlextApi` contract without relying on network connectivity.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        if request.url.endswith("/users/1"):
            body = {"id": 1, "name": "Alice"}
        elif request.url.endswith("/users/1") and str(request.method) == "DELETE":
            body = {"deleted": True}
        else:
            body = {"ok": True}
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=body,
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
    body = response.body
    assert isinstance(body, dict)
    assert body.get("name") == "Alice"


test_with_fake_api()
```

## Performance Testing

Keep performance tests deterministic and local. Measure the latency of a few in-memory API calls with `time.perf_counter` rather than hitting the network.

```python
from __future__ import annotations
import time
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FastApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"ok": True},
                request_id="perf-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = FastApi(settings=settings)


def test_many_requests_are_fast() -> None:
    start = time.perf_counter()
    for _ in range(100):
        result = api.get("/data")
        assert result.success
    elapsed = time.perf_counter() - start
    print(f"100 requests in {elapsed:.4f}s")
    assert elapsed < 1.0


test_many_requests_are_fast()
```

## Best Practices

### 1. Test Naming

Use descriptive names that state the behavior under test.

```python
from __future__ import annotations

# Good

def test_get_users_returns_success_and_list():
    pass


def test_post_user_returns_created_status():
    pass


# Bad

def test_get():
    pass


def test_api():
    pass
```

### 2. Test Organization

Group related tests into plain classes or modules. Each example can be collected by pytest as a module-level function or a class method.

```python
from __future__ import annotations


class TestUserApi:
    def test_get_users(self) -> None:
        pass

    def test_create_user(self) -> None:
        pass

    def test_delete_user(self) -> None:
        pass
```

### 3. Assertion Quality

Prefer assertions against the real API contract instead of vague truthiness checks.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class FakeApi(FlextApi):
    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=[{"id": 1, "name": "Alice"}],
                request_id="assert-1",
            )
        )


settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
api = FakeApi(settings=settings)


def test_specific_assertions() -> None:
    result = api.get("/users")
    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    body = response.body
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0].get("name") == "Alice"


test_specific_assertions()
```

### 4. Test Independence

Create a fresh `FlextApi` or `FlextApiSettings` instance for each test so tests do not share mutable state.

```python
from __future__ import annotations
from flext_api import FlextApi, FlextApiSettings, c, m, p, r, t, u


class CounterApi(FlextApi):
    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        super().__init__(settings=settings)
        object.__setattr__(self, "_count", 0)

    def request(self, request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        count = getattr(self, "_count") + 1
        object.__setattr__(self, "_count", count)
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse(
                status_code=200,
                headers={"Content-Type": "application/json"},
                body={"count": count},
                request_id="indep-1",
            )
        )


def test_fresh_instance_per_test() -> None:
    settings = FlextApiSettings(base_url="https://api.example.com", timeout=5.0)
    api = CounterApi(settings=settings)
    result = api.get("/data")
    assert result.unwrap().body == {"count": 1}

    # A second fresh instance starts from zero
    api2 = CounterApi(settings=settings)
    result2 = api2.get("/data")
    assert result2.unwrap().body == {"count": 1}


test_fresh_instance_per_test()
```

## Troubleshooting

### Import Errors

Make sure the virtual environment is synced and use `uv run` or `make` to run tests:

```bash
make boot
make test PROJECT=flext-api
```

### Test Timeout

Increase the timeout in `FlextApiSettings` for slow tests, or mark them with `@pytest.mark.slow` in real pytest files and skip them with `pytest -m "not slow"`.

```python
from __future__ import annotations
from flext_api import FlextApiSettings

slow_settings = FlextApiSettings(base_url="https://api.example.com", timeout=60.0)
print(slow_settings.Api.timeout)
```

### Coverage Issues

Coverage thresholds are configured in `pyproject.toml` under `[tool.coverage.report]`. Run coverage through the canonical `make` target:

```bash
make test PROJECT=flext-api
```

### Network-Dependent Tests

If a test fails only when external services are unavailable, replace the real `FlextApiClient` with a deterministic `FakeApi` subclass, as shown in the [Mocking External APIs](#mocking-external-apis) section.

---

**Resources**

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [HTTP Client Guide](./http-client.md)
