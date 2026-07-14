"""Public-facade basic-usage example for flext-api.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_api import FlextApi, c, m, p, r, s, settings, t, u


class FlextApiExamplesBasicUsage(s[t.JsonMapping]):
    """Minimal guided tour of flext-api through public aliases and facades."""

    @staticmethod
    def _emit(message: object) -> None:
        """Render example output through the canonical CLI facade."""
        u.Cli.formatters_print(str(message))

    def build_request(self) -> p.Result[m.Api.HttpRequest]:
        """Build a validated HTTP request through the public utility facade."""
        timeout_result = u.Api.RequestUtils.coerce_positive_timeout(
            str(settings.Api.timeout),
        )
        if timeout_result.failure:
            timeout_failure: p.Result[m.Api.HttpRequest] = r[m.Api.HttpRequest].fail(
                timeout_result.error or "failed to normalize timeout",
            )
            return timeout_failure

        payload_result = u.Api.RequestUtils.build_request_payload(
            method=c.Api.Method.GET,
            url=f"{settings.Api.base_url.rstrip('/')}/resources",
            headers={"accept": c.Api.ContentType.JSON.value},
            request_kwargs={"params": {"page": 1, "active": True}},
            timeout=timeout_result.value,
        )
        if payload_result.failure:
            payload_failure: p.Result[m.Api.HttpRequest] = r[m.Api.HttpRequest].fail(
                payload_result.error or "failed to build request payload",
            )
            return payload_failure

        request_result: p.Result[m.Api.HttpRequest] = u.parse_model(
            payload_result.value.root,
            m.Api.HttpRequest,
        )
        return request_result

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
        response_result: p.Result[m.Api.HttpResponse] = r[m.Api.HttpResponse].ok(
            m.Api.HttpResponse.model_validate(response_payload),
        )
        return response_result

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Run the public basic-usage flow through typed examples aliases."""
        self._emit("FLEXT API - Basic Usage")
        self._emit("=======================")

        self._emit("\n1. Setup via s/base.py")
        runtime_snapshot: t.JsonMapping = {
            "base_url": settings.Api.base_url,
            "timeout": settings.Api.timeout,
            "max_retries": settings.Api.max_retries,
            "verify_ssl": settings.Api.verify_ssl,
        }
        self._emit(runtime_snapshot)

        api = FlextApi()
        execute_result = api.execute(example="basic-usage")
        if execute_result.failure:
            execute_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].fail(
                execute_result.error or "flext-api execute failed",
            )
            return execute_failure
        self._emit(f"Facade ready: base_url={api.settings.Api.base_url}")

        self._emit("\n2. Request normalization via u.Api.RequestUtils")
        request_result = self.build_request()
        if request_result.failure:
            request_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].fail(
                request_result.error or "failed to build request",
            )
            return request_failure
        request = request_result.value
        self._emit(f"Request ok: {request.method} {request.url}")

        self._emit("\n3. Pydantic 2 models via m.Api")
        response_result = self.build_response(request)
        if response_result.failure:
            response_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].fail(
                response_result.error or "failed to build response",
            )
            return response_failure
        response = response_result.value
        self._emit(
            f"Response ok: status={response.status_code}, success={response.success}",
        )

        self._emit("\n4. Storage models + railway result ergonomics")
        entry_value: t.JsonValue = t.Api.API_JSON_VALUE_ADAPTER.validate_python(
            response.body or {},
        )
        namespace = type(self).__name__.lower()
        ttl = int(settings.Api.timeout)
        # NOTE (multi-agent): avoid shadowing the module-level ``settings``
        # singleton (ADR-005 namespaced settings); use a distinct local name.
        storage_settings = m.Api.Storage.Settings(
            namespace=namespace,
            default_ttl=ttl,
        )
        entry = m.Api.Storage.Metadata.model_validate({
            "value": entry_value,
            "timestamp": u.generate_iso_timestamp(),
            "ttl": storage_settings.default_ttl,
        })
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
            namespace=storage_settings.namespace,
        )
        self._emit(f"Storage entry: {state.entries['latest-response'].value}")
        self._emit(f"Stats: {stats.model_dump(mode='python')}")
        self._emit(
            "Result contract: "
            f"ok.success={r[str].ok('ready').success}, "
            f"fail.failure={r[str].fail('example failure').failure}",
        )

        summary: t.JsonMapping = {
            "base_url": api.settings.Api.base_url,
            "request_method": str(request.method),
            "response_status": response.status_code,
            "storage_entries": len(state.entries),
            "result_contract": "public-r",
        }
        self._emit("\nExamples completed")
        summary_result: p.Result[t.JsonMapping] = r[t.JsonMapping].ok(summary)
        return summary_result

    @classmethod
    def main(cls) -> None:
        """Run the example and render failures through the public result contract."""
        result = cls().execute()
        if result.success:
            return
        cls._emit(f"Example failed: {result.error or 'unexpected failure'}")


def main() -> None:
    """Main entry point for the basic usage example."""
    FlextApiExamplesBasicUsage.main()


if __name__ == "__main__":
    main()
