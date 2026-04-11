"""Functional smoke tests for flext-api core types and models.

Validates that key facades, constants, models, and serializers
actually work — not just that they exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm
from pydantic import ValidationError

from flext_api import (
    FlextApi,
    FlextApiConstants,
    FlextApiModels,
    FlextApiUtilitiesSerializers,
    c,
    m,
    t,
)


class TestConstants:
    """Validate constants are usable at runtime."""

    def test_method_enum_values(self) -> None:
        """HTTP methods resolve to correct string values."""
        tm.that(c.Api.Method.GET, eq="GET")
        tm.that(c.Api.Method.POST, eq="POST")
        tm.that(c.Api.Method.DELETE, eq="DELETE")

    def test_status_enum_values(self) -> None:
        """Status enum contains expected states."""
        tm.that(c.Api.Status.SUCCESS, eq="success")
        tm.that(c.Api.Status.FAILED, eq="failed")

    def test_content_type_enum_values(self) -> None:
        """Content type enum maps to MIME types."""
        tm.that(c.Api.ContentType.JSON, eq="application/json")
        tm.that(c.Api.ContentType.XML, eq="application/xml")

    def test_safe_methods_are_frozenset(self) -> None:
        """SAFE_METHODS is immutable and contains expected values."""
        tm.that("GET" in c.Api.SAFE_METHODS, eq=True)
        tm.that("POST" in c.Api.SAFE_METHODS, eq=False)

    def test_terminal_statuses(self) -> None:
        """Terminal statuses include failure states."""
        tm.that("completed" in c.Api.TERMINAL_STATUSES, eq=True)
        tm.that("failed" in c.Api.TERMINAL_STATUSES, eq=True)
        tm.that("pending" in c.Api.TERMINAL_STATUSES, eq=False)

    def test_http_status_bounds(self) -> None:
        """HTTP status code boundaries are defined correctly."""
        tm.that(c.Api.HTTP_STATUS_MIN, eq=100)
        tm.that(c.Api.HTTP_STATUS_MAX, eq=599)
        tm.that(c.Api.HTTP_SUCCESS_MIN, eq=200)
        tm.that(c.Api.HTTP_SUCCESS_MAX, eq=300)


class TestModels:
    """Validate Pydantic models accept/reject data correctly."""

    def test_http_request_defaults(self) -> None:
        """HttpRequest fills defaults for method, headers, body."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        tm.that(request.method, eq="GET")
        tm.that(request.url, eq="https://example.com")
        tm.that(dict(request.headers), eq={})

    def test_http_request_custom_method(self) -> None:
        """HttpRequest accepts valid custom method."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "method": "POST",
        })
        tm.that(request.method, eq="POST")

    def test_http_request_rejects_empty_url(self) -> None:
        """HttpRequest rejects empty URL."""
        with pytest.raises(ValidationError):
            m.Api.HttpRequest.model_validate({"url": ""})

    def test_http_response_success(self) -> None:
        """HttpResponse accepts valid status code and body."""
        response = m.Api.HttpResponse.model_validate({
            "status_code": 200,
            "body": {"result": "ok"},
        })
        tm.that(response.status_code, eq=200)
        tm.that(response.body, eq={"result": "ok"})

    def test_http_response_rejects_invalid_status(self) -> None:
        """HttpResponse rejects status codes outside 100-599."""
        with pytest.raises(ValidationError):
            m.Api.HttpResponse.model_validate({"status_code": 999})


class TestSerializers:
    """Validate serializer round-trip works."""

    def test_packb_produces_bytes(self) -> None:
        """Packb returns non-empty bytes for valid input."""
        payload: t.StrMapping = {"key": "value"}
        packed = FlextApiUtilitiesSerializers.packb(payload)
        assert packed, "packb should return non-empty bytes"
        tm.that(len(packed) > 0, eq=True)

    def test_packb_unpackb_roundtrip(self) -> None:
        """Pack then unpack returns original data."""
        original: t.HeaderMapping = {"hello": "world", "count": 42}
        packed = FlextApiUtilitiesSerializers.packb(original)
        result = FlextApiUtilitiesSerializers.unpackb(packed)
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=original)


class TestFacadeInheritance:
    """Validate MRO chain is intact."""

    def test_constants_inherits_web(self) -> None:
        """FlextApiConstants extends FlextWebConstants via MRO."""
        tm.that(issubclass(FlextApiConstants, FlextApiConstants.__mro__[1]), eq=True)

    def test_models_has_api_namespace(self) -> None:
        """FlextApiModels exposes Api inner class."""
        tm.that(
            issubclass(
                FlextApiModels.Api.HttpRequest.__mro__[0],
                FlextApiModels.Api.HttpRequest,
            ),
            eq=True,
        )


def test_package_imports_main_facade() -> None:
    """Package root exports the main API facade."""
    tm.that(FlextApi.__name__, eq="FlextApi")
