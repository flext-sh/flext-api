# Storage API Reference

This page documents the storage/cache story for `flext-api`.

> **Current status:** `flext-api` does not expose a storage, cache, or file
> abstraction API. File-like payloads are transported as request/response bodies
> through the public `FlextApi` facade and `m.Api.HttpRequest` /
> `m.Api.HttpResponse` models.

## Modeling File Payloads with HTTP Models

```python
from __future__ import annotations

from flext_api import FlextApi, FlextApiSettings, c, m, p, r


class FileUploadApi(FlextApi):
    """Example facade that POSTs a file payload as the request body."""

    def upload_document(
        self, filename: str, content: bytes
    ) -> p.Result[m.Api.HttpResponse]:
        return self.post(
            "/documents",
            data={"filename": filename, "content": content.decode("utf-8")},
            headers={"Content-Type": "application/json"},
        )


# In-memory override so the example runs without network access.
class FakeFileUploadApi(FileUploadApi):
    def post(
        self, url, data=None, headers=None, request_kwargs=None
    ) -> p.Result[m.Api.HttpResponse]:
        return r[m.Api.HttpResponse].ok(
            m.Api.create_response(
                status_code=201,
                body={"id": 1, "filename": data["filename"]},
                headers={"Content-Type": "application/json"},
            )
        )


api = FakeFileUploadApi(settings=FlextApiSettings(base_url="https://example.com"))
result = api.upload_document("report.txt", b"Hello, FLEXT!")
assert result.success
body = result.unwrap().body
assert body["filename"] == "report.txt"
assert body["id"] == 1
```

## What Is Not Implemented

The following storage concepts are **not** part of the current public API and
are therefore not documented as executable examples:

- `FlextApiStorage`, `FlextApiCache`, `MultiBackendStorage`
- `FlextFileProcessor`, `FileUploadMiddleware`
- `UploadFile`, `ImageResizer`, `ImageOptimizer`, `VirusScanner`
- File lifecycle helpers such as TTL, clear, or size operations

If a future release adds a storage abstraction, this page will be updated with
real, runnable examples.
