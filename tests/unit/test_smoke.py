"""Behavioral tests for the flext-api public contract.

Exercises observable behavior of the public facades, models, serializers,
and result-returning operations — never implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_api import FlextApi, FlextApiClient, FlextApiSettings
from flext_tests import tm
from tests import c, m, u

if TYPE_CHECKING:
    from tests import t


class TestsFlextApiSmoke:
    """Behavioral contract of the flext-api public surface."""

    # ---- Constants contract ---------------------------------------------

    @pytest.mark.parametrize(
        ("method", "expected"),
        [
            (c.Api.Method.GET, "GET"),
            (c.Api.Method.POST, "POST"),
            (c.Api.Method.PUT, "PUT"),
            (c.Api.Method.DELETE, "DELETE"),
            (c.Api.Method.PATCH, "PATCH"),
        ],
    )
    def test_http_method_enum_resolves_to_wire_string(
        self, method: c.Api.Method, expected: str
    ) -> None:
        """Each HTTP method compares equal to its wire string value."""
        tm.that(method, eq=expected)

    @pytest.mark.parametrize(
        ("status", "expected"),
        [(c.Api.Status.SUCCESS, "success"), (c.Api.Status.FAILED, "failed")],
    )
    def test_status_enum_value(self, status: c.Api.Status, expected: str) -> None:
        """Status enum members expose the documented string values."""
        tm.that(status.value, eq=expected)

    @pytest.mark.parametrize(
        ("content_type", "expected"),
        [
            (c.Api.ContentType.JSON, "application/json"),
            (c.Api.ContentType.XML, "application/xml"),
        ],
    )
    def test_content_type_maps_to_mime(
        self, content_type: c.Api.ContentType, expected: str
    ) -> None:
        """ContentType members map to their MIME type strings."""
        tm.that(content_type.value, eq=expected)

    def test_safe_methods_membership_contract(self) -> None:
        """SAFE_METHODS classifies GET as safe and POST as unsafe."""
        tm.that(c.Api.SAFE_METHODS, has="GET")
        tm.that(c.Api.SAFE_METHODS, lacks="POST")

    def test_safe_methods_is_immutable(self) -> None:
        """SAFE_METHODS is a frozenset and rejects mutation."""
        tm.that(c.Api.SAFE_METHODS, is_=frozenset)

    def test_terminal_statuses_membership_contract(self) -> None:
        """Terminal statuses include completion/failure but not pending."""
        tm.that(c.Api.TERMINAL_STATUSES, has="completed")
        tm.that(c.Api.TERMINAL_STATUSES, has="failed")
        tm.that(c.Api.TERMINAL_STATUSES, lacks="pending")

    def test_http_status_bounds_are_ordered(self) -> None:
        """HTTP status boundaries form a valid, ordered range."""
        tm.that(c.Api.HTTP_STATUS_MIN, eq=100)
        tm.that(c.Api.HTTP_STATUS_MAX, eq=599)
        tm.that(c.Api.HTTP_STATUS_MIN, lt=c.Api.HTTP_SUCCESS_MIN)
        tm.that(c.Api.HTTP_SUCCESS_MIN, lt=c.Api.HTTP_SUCCESS_MAX)
        tm.that(c.Api.HTTP_SUCCESS_MAX, lte=c.Api.HTTP_STATUS_MAX)

    # ---- HttpRequest model contract -------------------------------------

    def test_http_request_applies_documented_defaults(self) -> None:
        """A minimal request defaults to GET with empty headers and body."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        tm.that(request.method, eq="GET")
        tm.that(request.url, eq="https://example.com")
        tm.that(dict(request.headers), eq={})
        tm.that(request.body, eq={})

    def test_http_request_preserves_supplied_method(self) -> None:
        """A supplied method survives validation unchanged."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "method": "POST",
        })
        tm.that(request.method, eq="POST")

    @pytest.mark.parametrize(
        ("headers", "expected"),
        [
            ({}, "application/json"),
            ({"Content-Type": "application/xml"}, "application/xml"),
            ({"content-type": "text/plain"}, "text/plain"),
        ],
    )
    def test_http_request_content_type_derives_from_headers(
        self, headers: dict[str, str], expected: str
    ) -> None:
        """content_type computed field reflects headers, defaulting to JSON."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "headers": headers,
        })
        tm.that(request.content_type, eq=expected)

    def test_http_request_rejects_empty_url(self) -> None:
        """An empty URL fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({"url": ""})

    def test_http_request_rejects_unknown_method(self) -> None:
        """A method outside the allowed pattern fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({
                "url": "https://example.com",
                "method": "FETCH",
            })

    def test_http_request_roundtrips_through_model_dump(self) -> None:
        """model_dump preserves the observable request fields."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "method": "POST",
        })
        dumped = request.model_dump()
        tm.that(dumped["url"], eq="https://example.com")
        tm.that(dumped["method"], eq="POST")

    def test_http_request_defaults_sni_hostname_to_none(self) -> None:
        """A request without an explicit SNI hostname exposes None."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        tm.that(request.sni_hostname, none=True)

    def test_http_request_preserves_sni_hostname_for_ip_targets(self) -> None:
        """An IP-targeted request keeps the SNI hostname for TLS verification."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://185.199.108.153/path",
            "headers": {"Host": "www.encode.io"},
            "sni_hostname": "www.encode.io",
        })
        tm.that(request.sni_hostname, eq="www.encode.io")
        tm.that(request.model_dump(round_trip=True)["sni_hostname"], eq="www.encode.io")

    # ---- HttpResponse model contract ------------------------------------

    def test_http_response_accepts_valid_payload(self) -> None:
        """A 200 response exposes its status code and body verbatim."""
        response = m.Api.HttpResponse.model_validate({
            "status_code": 200,
            "body": {"result": "ok"},
        })
        tm.that(response.status_code, eq=200)
        tm.that(response.body, eq={"result": "ok"})

    @pytest.mark.parametrize("status_code", [0, 99, 600, 999])
    def test_http_response_rejects_out_of_range_status(self, status_code: int) -> None:
        """Status codes outside 100-599 fail validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpResponse.model_validate({"status_code": status_code})

    @pytest.mark.parametrize(
        ("status_code", "success", "redirect", "client_error", "server_error"),
        [
            (200, True, False, False, False),
            (204, True, False, False, False),
            (301, False, True, False, False),
            (404, False, False, True, False),
            (500, False, False, False, True),
        ],
    )
    def test_http_response_classification_computed_fields(
        self,
        *,
        status_code: int,
        success: bool,
        redirect: bool,
        client_error: bool,
        server_error: bool,
    ) -> None:
        """Computed classification fields agree with the status code class."""
        response = m.Api.HttpResponse.model_validate({"status_code": status_code})
        tm.that(response.success, eq=success)
        tm.that(response.redirect, eq=redirect)
        tm.that(response.client_error, eq=client_error)
        tm.that(response.server_error, eq=server_error)
        tm.that(response.error, eq=client_error or server_error)

    def test_create_response_builds_equivalent_model(self) -> None:
        """create_response yields the same state as direct validation."""
        built = m.Api.create_response(status_code=200, body={"a": 1})
        tm.that(built.status_code, eq=200)
        tm.that(built.body, eq={"a": 1})
        tm.that(built.success, eq=True)

    # ---- Serializer contract --------------------------------------------

    def test_packb_returns_non_empty_bytes(self) -> None:
        """Packb serializes a mapping into non-empty bytes."""
        payload: t.JsonMapping = {"key": "value"}
        packed = u.Api.packb(payload)
        tm.that(packed, is_=bytes, length_gt=0)

    @pytest.mark.parametrize(
        "original", [{"hello": "world", "count": 42}, {"nested": {"a": [1, 2, 3]}}, {}]
    )
    def test_packb_unpackb_is_lossless_roundtrip(self, original: t.JsonMapping) -> None:
        """Packing then unpacking reproduces the original payload."""
        result = u.Api.unpackb(u.Api.packb(original))
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)

    # ---- Client / facade contract ---------------------------------------

    def test_client_exposes_settings_through_public_properties(self) -> None:
        """The client surfaces its configured base_url and timeout."""
        settings = FlextApiSettings(base_url="https://service.example", timeout=9.5)
        client = FlextApiClient(settings=settings)
        tm.that(client.base_url, eq="https://service.example")
        tm.that(client.timeout, eq=pytest.approx(9.5))

    def test_client_execute_reports_success(self) -> None:
        """A configured client executes its lifecycle successfully."""
        client = FlextApiClient(
            settings=FlextApiSettings(base_url="https://service.example")
        )
        result = client.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    def test_facade_execute_reports_success_and_retains_settings(self) -> None:
        """The facade executes successfully and preserves its settings."""
        settings = FlextApiSettings(base_url="https://api.example", timeout=4.0)
        api = FlextApi(settings=settings)
        result = api.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)
        tm.that(api.settings.Api.base_url, eq="https://api.example")
        tm.that(api.settings.Api.timeout, eq=pytest.approx(4.0))

    def test_facade_default_settings_provide_base_url(self) -> None:
        """A facade built without settings still exposes a usable base_url."""
        api = FlextApi()
        tm.that(api.settings.Api.base_url, is_=str)
        tm.that(api.execute().success, eq=True)
