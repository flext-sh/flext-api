<!-- Generated from docs/guides/testing.md for flext-api. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-api - FLEXT Testing Guide

<!-- TOC START -->
- [Overview](#overview)
- [Test Structure](#test-structure)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [Test Fixtures](#test-fixtures)
- [Best Practices](#best-practices)
  - [1. Test Naming](#1-test-naming)
  - [2. Test Organization](#2-test-organization)
  - [3. Assertion Quality](#3-assertion-quality)
  - [4. Test Independence](#4-test-independence)
- [Continuous Integration](#continuous-integration)
- [Troubleshooting](#troubleshooting)
  - [Import Errors](#import-errors)
  - [Test Timeout](#test-timeout)
  - [Coverage Issues](#coverage-issues)
- [Resources](#resources)
<!-- TOC END -->

This guide covers testing strategies, best practices, and executable examples for
`flext-api` using the current FLEXT HTTP facade and railway result patterns.

## Overview

FLEXT projects share a unified testing contract: tests exercise the public facade
(`FlextApi`, `FlextApiClient`, `m.Api.HttpRequest`, `p.Result`) and never depend
on internal implementation details. The examples below run without network access
by using small `FakeApi` subclasses that simulate the real client behavior.

## Test Structure

FLEXT packages use a hierarchical test structure:

```text
tests/
├── unit/           # Fast, isolated tests of models and utilities
├── integration/    # Tests that cross package boundaries
├── e2e/           # End-to-end workflow tests
├── fixtures/      # Test data and builders
└── conftest.py    # Shared pytest configuration
```

## Unit Tests

Test model validation and the public API facade in isolation:

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, c, m, p, r


class FakeApi(FlextApi):
    """In-memory API facade for unit tests."""

    def get(
        self, url: str, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"endpoint": url, "method": "GET"},
                headers={"Content-Type": "application/json"},
            )
        )


def test_get_users_returns_success():
    api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/users")

    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert response.body["endpoint"] == "/users"


def test_http_request_model_validation():
    request = m.Api.HttpRequest(
        method=c.Api.Method.GET,
        url="https://example.com/users",
        headers={"Accept": "application/json"},
    )

    assert request.method == "GET"
    assert request.content_type == "application/json"


test_get_users_returns_success()
test_http_request_model_validation()```
## Integration Tests

Integration tests exercise the real `FlextApiClient.request` pipeline with a
known, safe endpoint such as `httpbin.org` and always handle failures gracefully:

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings


def test_real_http_get():
    api = FlextApi(
        settings=FlextApiSettings(base_url="https://httpbin.org", timeout=5.0)
    )
    result = api.get("/get")

    if result.failure:
        print(f"Network unavailable: {result.error}")
    else:
        response = result.unwrap()
        assert response.status_code == 200
        assert response.success
        assert "url" in response.body


test_real_http_get()```
## Test Fixtures

Avoid pytest decorators in markdown examples by showing plain factory functions
that tests can call directly:

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


def make_api(status_code: int = 200, body: dict | None = None) -> FlextApi:
    """Factory for a fake API facade."""

    class FakeApi(FlextApi):
        def get(
            self, url, headers=None, request_kwargs=None
        ) -> p.Result[m.Api.HttpResponse]:
            return r[m.Api.HttpResponse].ok(
                m.Api.create_response(
                    status_code=status_code,
                    body=body if body is not None else {"endpoint": url},
                    headers={"Content-Type": "application/json"},
                )
            )

    return FakeApi(settings=FlextApiSettings(base_url="https://example.com"))


def test_user_list_with_factory():
    api = make_api(body={"users": [{"id": 1, "name": "Alice"}]})
    result = api.get("/users")

    assert result.success
    assert result.unwrap().body["users"][0]["name"] == "Alice"


test_user_list_with_factory()```
## Best Practices

### 1. Test Naming

```python
from __future__ import annotations


# ✅ GOOD - Descriptive test names
def test_parse_valid_http_request_returns_success():
    """Test that a valid HTTP request model validates successfully."""
    pass


# ❌ BAD - Vague test names
def test_parse():
    pass


test_parse_valid_http_request_returns_success()```
### 2. Test Organization

```python
from __future__ import annotations


class TestHttpRequestModel:
    """Test HTTP request model validation."""

    def test_valid_get_request(self):
        pass

    def test_invalid_method_raises(self):
        pass

    def test_url_is_required(self):
        pass


TestHttpRequestModel().test_valid_get_request()```
### 3. Assertion Quality

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class FakeApi(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"dn": "cn=test,dc=example,dc=com", "attributes": {"cn": "test"}},
                headers={"Content-Type": "application/json"},
            )
        )


# ✅ GOOD - Specific assertions
def test_api_result():
    api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/test")

    assert result.success
    response = result.unwrap()
    assert response.status_code == 200
    assert response.body["dn"] == "cn=test,dc=example,dc=com"
    assert "cn" in response.body["attributes"]


# ❌ BAD - Vague assertions
def test_api_result_vague():
    api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/test")
    assert result  # Too vague


test_api_result()
test_api_result_vague()```
### 4. Test Independence

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class FakeApi(FlextApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"url": url},
                headers={"Content-Type": "application/json"},
            )
        )


# ✅ GOOD - Independent tests create their own facade instances
def test_get_users():
    api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/users")
    assert result.success


def test_get_projects():
    api = FakeApi(settings=FlextApiSettings(base_url="https://example.com"))
    result = api.get("/projects")
    assert result.success


test_get_users()
test_get_projects()


# ❌ BAD - Shared mutable state between tests
class BadSuite:
    api = FlextApi(settings=FlextApiSettings(base_url="https://example.com"))```
## Continuous Integration

Run the test suite through the FLEXT workspace dispatcher:

```bash
# Run all tests for flext-api
make test PROJECT=flext-api

# Run the markdown documentation examples
uv run pytest --markdown-docs -q```
## Troubleshooting

### Import Errors

```bash
# Ensure the workspace environment is bootstrapped
make boot
uv run pytest --markdown-docs docs/guides/testing.md -q
```

### Test Timeout

```bash
# Increase the per-test timeout during debugging
uv run pytest --markdown-docs -q --timeout=60
```

### Coverage Issues

```bash
# Check coverage configuration for the project
uv run pytest --cov=src/flext_api --cov-report=term-missing
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- FLEXT Quality Standards
- Test Examples in `tests/`
- CI/CD Configuration in `.github/workflows/`
