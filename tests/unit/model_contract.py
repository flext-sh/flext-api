"""Shared model contract tests for flext-api HTTP request/response models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_api import c, m, t, u


class TestsFlextApiModelContract:
    """Shared model contract tests for sync and async client test suites."""

    # ---- HttpRequest model contract -------------------------------------

    @staticmethod
    def test_http_request_applies_documented_defaults() -> None:
        """A minimal request defaults to GET with empty headers and body."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        tm.that(request.method, eq="GET")
        tm.that(request.url, eq="https://example.com")
        tm.that(dict(request.headers), eq={})
        tm.that(request.body, eq={})

    @staticmethod
    def test_http_request_preserves_supplied_method() -> None:
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
    @staticmethod
    def test_http_request_content_type_derives_from_headers(
        headers: t.StrMapping,
        expected: str,
    ) -> None:
        """content_type computed field reflects headers, defaulting to JSON."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "headers": headers,
        })
        tm.that(request.content_type, eq=expected)

    @staticmethod
    def test_http_request_rejects_empty_url() -> None:
        """An empty URL fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({"url": ""})

    @staticmethod
    def test_http_request_rejects_unknown_method() -> None:
        """A method outside the allowed pattern fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({
                "url": "https://example.com",
                "method": "FETCH",
            })

    @staticmethod
    def test_http_request_roundtrips_through_model_dump() -> None:
        """model_dump preserves the observable request fields."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "method": "POST",
        })
        dumped = request.model_dump()
        tm.that(dumped["url"], eq="https://example.com")
        tm.that(dumped["method"], eq="POST")

    @staticmethod
    def test_http_request_defaults_sni_hostname_to_none() -> None:
        """A request without an explicit SNI hostname exposes None."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        tm.that(request.sni_hostname, none=True)

    @staticmethod
    def test_http_request_preserves_sni_hostname_for_ip_targets() -> None:
        """An IP-targeted request keeps the SNI hostname for TLS verification."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://185.199.108.153/path",
            "headers": {"Host": "www.encode.io"},
            "sni_hostname": "www.encode.io",
        })
        tm.that(request.sni_hostname, eq="www.encode.io")
        tm.that(request.model_dump(round_trip=True)["sni_hostname"], eq="www.encode.io")

    # ---- HttpResponse model contract ------------------------------------

    @staticmethod
    def test_http_response_accepts_valid_payload() -> None:
        """A 200 response exposes its status code and body verbatim."""
        response = m.Api.HttpResponse.model_validate({
            "status_code": 200,
            "body": {"result": "ok"},
        })
        tm.that(response.status_code, eq=200)
        tm.that(response.body, eq={"result": "ok"})

    @pytest.mark.parametrize("status_code", [0, 99, 600, 999])
    @staticmethod
    def test_http_response_rejects_out_of_range_status(status_code: int) -> None:
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
    @staticmethod
    def test_http_response_classification_computed_fields(
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

    @staticmethod
    def test_create_response_builds_equivalent_model() -> None:
        """create_response yields the same state as direct validation."""
        built = m.Api.create_response(status_code=200, body={"a": 1})
        tm.that(built.status_code, eq=200)
        tm.that(built.body, eq={"a": 1})
        tm.that(built.success, eq=True)

    # ---- Serializer contract --------------------------------------------

    @staticmethod
    def test_packb_returns_non_empty_bytes() -> None:
        """Packb serializes a mapping into non-empty bytes."""
        payload: t.StrMapping = {"key": "value"}
        packed = u.Api.packb(payload)
        tm.that(packed, is_=bytes, length_gt=0)

    @pytest.mark.parametrize(
        "original",
        [{"hello": "world", "count": 42}, {"nested": {"a": [1, 2, 3]}}, {}],
    )
    @staticmethod
    def test_packb_unpackb_is_lossless_roundtrip(original: t.JsonMapping) -> None:
        """Packing then unpacking reproduces the original payload."""
        result = u.Api.unpackb(u.Api.packb(original))
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)
