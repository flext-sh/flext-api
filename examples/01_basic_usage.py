"""Public-facade basic-usage example for flext-api.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from examples import c, m, p, r, s, t, u
from flext_api import FlextApi


class FlextApiExamplesBasicUsage(s[t.JsonMapping]):
    """Minimal guided tour of flext-api through public aliases and facades."""

    def build_request(self) -> p.Result[m.Api.HttpRequest]:
        """Build a validated HTTP request through the public utility facade."""
        timeout_result = u.Api.RequestUtils.coerce_positive_timeout(
            str(self.settings.timeout)
        )
        if timeout_result.failure:
            return r[m.Api.HttpRequest].fail(
                timeout_result.error or "failed to normalize timeout"
            )

        payload_result = u.Api.RequestUtils.build_request_payload(
            method=c.Api.Method.GET,
            url=f"{self.settings.base_url.rstrip('/')}/resources",
            headers={"accept": c.Api.ContentType.JSON.value},
            request_kwargs={"params": {"page": 1, "active": True}},
            timeout=timeout_result.value,
        )
        if payload_result.failure:
            return r[m.Api.HttpRequest].fail(
                payload_result.error or "failed to build request payload"
            )

        return u.parse_model(payload_result.value.root, m.Api.HttpRequest)

    @staticmethod
    def build_response(request: m.Api.HttpRequest) -> p.Result[m.Api.HttpResponse]:
        """Build a response model without leaving the public API surface."""
        response_payload: t.JsonMapping = {
            "status_code": c.Api.HTTP_SUCCESS_MIN,
            "body": {
                "method": str(request.method),
                "url": request.url,
                "headers": dict(request.headers),
            },
            "request_id": "example-request",
        }
        return r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse.model_validate(response_payload)
        )

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Run the public basic-usage flow through typed examples aliases."""
        print("FLEXT API - Basic Usage")
        print("=======================")

        print("\n1. Setup via s/base.py")
        runtime_snapshot: t.JsonMapping = {
            "base_url": self.settings.base_url,
            "timeout": self.settings.timeout,
            "max_retries": self.settings.max_retries,
            "verify_ssl": self.settings.verify_ssl,
        }
        print(runtime_snapshot)

        api = FlextApi()
        execute_result = api.execute(example="basic-usage")
        if execute_result.failure:
            return r[t.JsonMapping].fail(
                execute_result.error or "flext-api execute failed"
            )
        print(f"Facade ready: base_url={api.settings.base_url}")

        print("\n2. Request normalization via u.Api.RequestUtils")
        request_result = self.build_request()
        if request_result.failure:
            return r[t.JsonMapping].fail(
                request_result.error or "failed to build request"
            )
        request = request_result.value
        print(f"Request ok: {request.method} {request.url}")

        print("\n3. Pydantic 2 models via m.Api")
        response_result = self.build_response(request)
        if response_result.failure:
            return r[t.JsonMapping].fail(
                response_result.error or "failed to build response"
            )
        response = response_result.value
        print(f"Response ok: status={response.status_code}, success={response.success}")

        print("\n4. Storage models + railway result ergonomics")
        entry_value: t.JsonValue = t.Api.API_JSON_VALUE_ADAPTER.validate_python(
            response.body or {}
        )
        namespace = type(self).__name__.lower()
        ttl = int(self.settings.timeout)
        settings = m.Api.Storage.Settings(namespace=namespace, default_ttl=ttl)
        entry = m.Api.Storage.Metadata(
            value=entry_value,
            timestamp=u.generate_iso_timestamp(),
            ttl=settings.default_ttl,
        )
        state = m.Api.Storage.State(
            entries={"latest-response": entry},
            operations_count=2,
            cache_hits=1,
            cache_misses=0,
        )
        stats = m.Api.Storage.Stats(
            total_operations=state.operations_count,
            cache_hits=state.cache_hits,
            cache_misses=state.cache_misses,
            storage_size=len(state.entries),
            memory_usage=len(repr(state.entries)),
            namespace=settings.namespace,
        )
        print(f"Storage entry: {state.entries['latest-response'].value}")
        print(f"Stats: {stats.model_dump(mode='python')}")
        print(
            "Result contract: "
            f"ok.success={r[str].ok('ready').success}, "
            f"fail.failure={r[str].fail('example failure').failure}"
        )

        summary: t.JsonMapping = {
            "base_url": self.settings.base_url,
            "request_method": str(request.method),
            "response_status": response.status_code,
            "storage_entries": len(state.entries),
            "result_contract": "public-r",
        }
        print("\nExamples completed")
        return r[t.JsonMapping].ok(summary)

    @classmethod
    def main(cls) -> None:
        """Run the example and render failures through the public result contract."""
        result = cls().execute()
        if result.success:
            return
        print(f"Example failed: {result.error or 'unexpected failure'}")


def main() -> None:
    """Main entry point for the basic usage example."""
    FlextApiExamplesBasicUsage.main()


if __name__ == "__main__":
    main()
