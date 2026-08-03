# Middleware API Reference

This page documents the current middleware story for `flext-api`.

> **Current status:** `flext-api` does not expose a dedicated middleware
> pipeline API. Cross-cutting concerns such as logging, authentication, and
> request/response transformation are handled through the public `FlextApi`
> facade, typed settings, and the `m.Api.HttpRequest` / `m.Api.HttpResponse`
> models.

## Wrapping the Public Facade

The idiomatic way to add behavior around HTTP calls is to subclass `FlextApi`
and override the verbs you care about. The example below adds request/response
logging without relying on any non-existent middleware API.

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, m, p, r


class LoggingApi(FlextApi):
    """Facade that logs every outgoing request and response metadata."""

    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        self.logger.info("request", url=url, method="GET")
        result = super().get(url, headers=headers, request_kwargs=request_kwargs)
        if result.success:
            response = result.unwrap()
            self.logger.info("response", url=url, status_code=response.status_code)
        else:
            self.logger.warning("request_failed", url=url, error=result.error)
        return result


# In-memory override so the example runs without network access.
class FakeLoggingApi(LoggingApi):
    def get(
        self, url, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=200,
                body={"endpoint": url, "method": "GET"},
                headers={"Content-Type": "application/json"},
            )
        )


api = FakeLoggingApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.get("/users")
assert result.success
assert result.unwrap().status_code == 200
```

## What Is Not Implemented

The following middleware concepts are **not** part of the current public API
and are therefore not documented as executable examples:

- `FlextApiMiddleware` base class
- `MiddlewarePipeline` chain
- `AuthenticationMiddleware`, `RequestMiddleware`, `ResponseMiddleware`,
  `ErrorHandlingMiddleware`, `PerformanceMonitoringMiddleware`
- Decorators such as `require_roles` or `require_permissions`
- FastAPI `app.add_middleware(...)` integration

If a future release adds a first-class middleware API, this page will be
updated with real, runnable examples.
