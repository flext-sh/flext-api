"""Executable flext-api example using the final public contract.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from examples import c, m, r, t, u
from flext_api import FlextApi, FlextApiSettings, FlextApiStorage


def example_api_creation() -> None:
    """Create the facade with explicit settings and execute the service contract."""
    print("=== API Creation ===")
    settings = FlextApiSettings(
        base_url="https://service.internal",
        timeout=float(c.DEFAULT_TIMEOUT_SECONDS),
    )
    api = FlextApi(settings=settings)
    execute_result = api.execute()
    if execute_result.failure:
        print(f"❌ execute failed: {execute_result.error}")
        return
    print(f"✅ facade ready: base_url={api.settings.base_url}")


def example_models_validation() -> None:
    """Build request/response models through the canonical m alias."""
    print("\n=== Model Validation ===")
    request = m.Api.HttpRequest.model_validate({
        "method": c.Api.Method.POST,
        "url": "https://service.internal/resources",
        "headers": {"content-type": c.Api.ContentType.JSON.value},
        "body": {"name": "resource-1"},
    })
    response = m.Api.HttpResponse.model_validate({
        "status_code": c.Api.HTTP_SUCCESS_MIN + 1,
        "body": {"id": "r1", "name": "resource-1"},
        "request_id": "req-example-1",
    })
    print(f"✅ request ok: {request.method} {request.url}")
    print(f"✅ response ok: status={response.status_code}, success={response.success}")


def example_storage_usage() -> None:
    """Use the storage API with typed payloads and observable stats."""
    print("\n=== Storage Usage ===")
    storage = FlextApiStorage(
        settings=m.Api.Storage.Settings(namespace="examples", default_ttl=60),
    )
    payload: t.ContainerValueMapping = {
        "status_code": c.Api.HTTP_SUCCESS_MIN,
        "data": {"name": "cached-item"},
    }
    set_result = storage.set("item-1", payload)
    if set_result.failure:
        print(f"❌ storage.set failed: {set_result.error}")
        return
    get_result = storage.get("item-1")
    if get_result.failure:
        print(f"❌ storage.get failed: {get_result.error}")
        return
    print(f"✅ storage get: {get_result.value}")
    metrics_result = storage.metrics()
    if metrics_result.success:
        print(f"✅ storage metrics: {metrics_result.value}")


def example_utilities_usage() -> None:
    """Use utility helpers through the canonical u alias."""
    print("\n=== Utilities Usage ===")
    url_result = u.FlextWebValidator.validate_url("https://example.com/api/v1")
    if url_result.success:
        print(f"✅ URL ok: {url_result.value}")
    else:
        print(f"❌ URL invalid: {url_result.error}")
    response_result = u.ResponseBuilder.build_success_response(
        data={"users": [{"id": 1, "name": "John"}]},
        message="Users retrieved successfully",
    )
    if response_result.success:
        print(f"✅ response builder: {response_result.value}")
    else:
        print(f"❌ response builder failed: {response_result.error}")


def example_result_contract() -> None:
    """Show explicit handling of the railway-style result contract."""
    print("\n=== Result Contract ===")
    ok = r[str].ok("ready")
    fail = r[str].fail("example failure")
    print(f"✅ ok.success={ok.success}, value={ok.value}")
    print(f"✅ fail.failure={fail.failure}, error={fail.error}")


def main() -> None:
    """Run all executable examples for the final public contract."""
    print("FLEXT API - Basic Usage")
    print("======================")
    example_api_creation()
    example_models_validation()
    example_storage_usage()
    example_utilities_usage()
    example_result_contract()
    print("\n✅ examples completed")


if __name__ == "__main__":
    main()
