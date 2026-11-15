"""Public-facade basic-usage example for flext-api.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from examples import c, m, p, r, settings, t, u
from flext_api import FlextApi, FlextApiServiceBase


class FlextApiExamplesBasicUsage(FlextApiServiceBase[t.JsonMapping]):
    """Minimal guided tour of flext-api through public aliases and facades."""

    @staticmethod
    def _emit(message: t.JsonValue) -> None:
        """Render example output through the canonical CLI facade."""
        u.Cli.formatters_print(str(message))

    @staticmethod
    def build_request() -> p.Result[p.Api.HttpRequest]:
        """Build a validated HTTP request through the public utility facade.

        Returns:
            The resulting ``p.Result[p.Api.HttpRequest]``.

        """
        timeout_result = u.Api.RequestUtils.coerce_positive_timeout(
            str(settings.Api.timeout),
        )
        if timeout_result.failure:
            timeout_failure: p.Result[p.Api.HttpRequest] = r[
                m.Api.HttpRequest
            ].from_failure(timeout_result)
            return timeout_failure

        return u.Api.RequestUtils.build_request_payload(
            method=c.Api.Method.GET,
            url=f"{settings.Api.base_url.rstrip('/')}/resources",
            headers={"accept": c.Api.ContentType.JSON.value},
            request_kwargs={
                "params": {"page": 1, "active": True},
                "timeout": timeout_result.value,
            },
        )

    @staticmethod
    def build_response(request: p.Api.HttpRequest) -> p.Result[p.Api.HttpResponse]:
        """Build a response model without leaving the public API surface.

        Returns:
            The resulting ``p.Result[p.Api.HttpResponse]``.

        """
        response_payload: t.JsonMapping = {
            "status_code": c.Api.HTTP_SUCCESS_MIN,
            "body": {
                "method": str(request.method),
                "url": request.url,
                "headers": dict(request.headers),
            },
            c.ContextKey.REQUEST_ID: "example-request",
        }
        response_result: p.Result[p.Api.HttpResponse] = r[p.Api.HttpResponse].ok(
            m.Api.HttpResponse.model_validate(response_payload),
        )
        return response_result

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Run the public basic-usage flow through typed examples aliases.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        self._emit("FLEXT API - Basic Usage")
        self._emit("=======================")

        self._emit("\n1. Setup via s/base.py")
        runtime_snapshot: t.JsonValue = {
            "base_url": settings.Api.base_url,
            "timeout": settings.Api.timeout,
            "max_retries": settings.Api.max_retries,
            "verify_ssl": settings.Api.verify_ssl,
        }
        self._emit(runtime_snapshot)

        api = FlextApi()
        execute_result = api.execute(example="basic-usage")
        if execute_result.failure:
            execute_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].from_failure(
                execute_result,
            )
            return execute_failure
        self._emit(f"Facade ready: base_url={api.settings.Api.base_url}")

        self._emit("\n2. Request normalization via u.Api.RequestUtils")
        request_result = self.build_request()
        if request_result.failure:
            request_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].from_failure(
                request_result,
            )
            return request_failure
        request = request_result.value
        self._emit(f"Request ok: {request.method} {request.url}")

        self._emit("\n3. Pydantic 2 models via m.Api")
        response_result = self.build_response(request)
        if response_result.failure:
            response_failure: p.Result[t.JsonMapping] = r[t.JsonMapping].from_failure(
                response_result,
            )
            return response_failure
        response = response_result.value
        self._emit(
            f"Response ok: status={response.status_code}, success={response.success}",
        )

        self._emit("\n4. Storage models + railway result ergonomics")
        state = self._emit_storage_demo(response)
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

    @staticmethod
    def _emit_storage_demo(response: p.Api.HttpResponse) -> p.Api.StorageState:
        """Exercise storage models and railway result ergonomics for one response.

        Returns:
            The resulting ``m.Api.StorageState``.

        """
        entry_value: t.JsonValue = t.Api.API_JSON_VALUE_ADAPTER.validate_python(
            response.body or {},
        )
        namespace = FlextApiExamplesBasicUsage.__name__.lower()
        ttl = int(settings.Api.timeout)
        # NOTE (multi-agent): avoid shadowing the module-level ``settings``
        # singleton (ADR-005 namespaced settings); use a distinct local name.
        storage_settings = m.Api.StorageSettings(namespace=namespace, default_ttl=ttl)
        entry = m.Api.StorageMetadata(
            value=entry_value,
            timestamp=u.generate_iso_timestamp(),
            ttl=storage_settings.default_ttl,
        )
        state = m.Api.StorageState(
            entries={"latest-response": entry},
            operations_count=2,
            cache_hits=1,
            cache_misses=0,
        )
        stats = m.Api.StorageStats(
            total_operations=state.operations_count,
            cache_hits=state.cache_hits,
            cache_misses=state.cache_misses,
            storage_size=len(state.entries),
            memory_usage=len(repr(state.entries)),
            namespace=storage_settings.namespace,
        )
        FlextApiExamplesBasicUsage._emit(
            f"Storage entry: {state.entries['latest-response'].value}",
        )
        FlextApiExamplesBasicUsage._emit(f"Stats: {stats.model_dump(mode='python')}")
        return state

    @classmethod
    def main(cls) -> None:
        """Run the example and render failures through the public result contract."""
        result = cls().execute()
        if result.failure:
            cls._emit(f"Example failed: {result.error or 'unexpected failure'}")


if __name__ == "__main__":
    FlextApiExamplesBasicUsage.main()
