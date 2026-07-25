"""Functional smoke tests for flext-api core types and models.

Validates that key facades, constants, models, and serializers
actually work — not just that they exist.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApi,
    FlextApiSettings,
)
from flext_api._utilities.client import FlextApiClient
from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u


class TestsFlextApiSmoke:
    """Validate constants are usable at runtime."""

    def test_method_enum_values(self) -> None:
        """HTTP methods resolve to correct string values."""
        assert c.Api.Method.GET == "GET"
        assert c.Api.Method.POST == "POST"
        assert c.Api.Method.DELETE == "DELETE"

    def test_status_enum_values(self) -> None:
        """Status enum contains expected states."""
        assert c.Api.Status.SUCCESS.value == "success"
        assert c.Api.Status.FAILED.value == "failed"

    def test_content_type_enum_values(self) -> None:
        """Content type enum maps to MIME types."""
        assert c.Api.ContentType.JSON.value == "application/json"
        assert c.Api.ContentType.XML.value == "application/xml"

    def test_safe_methods_are_frozenset(self) -> None:
        """SAFE_METHODS is immutable and contains expected values."""
        assert "GET" in c.Api.SAFE_METHODS
        assert "POST" not in c.Api.SAFE_METHODS

    def test_terminal_statuses(self) -> None:
        """Terminal statuses include failure states."""
        assert "completed" in c.Api.TERMINAL_STATUSES
        assert "failed" in c.Api.TERMINAL_STATUSES
        assert "pending" not in c.Api.TERMINAL_STATUSES

    def test_http_status_bounds(self) -> None:
        """HTTP status code boundaries are defined correctly."""
        assert c.Api.HTTP_STATUS_MIN == 100
        assert c.Api.HTTP_STATUS_MAX == 599
        assert c.Api.HTTP_SUCCESS_MIN == 200
        assert c.Api.HTTP_SUCCESS_MAX == 300

    def test_http_request_defaults(self) -> None:
        """HttpRequest fills defaults for method, headers, body."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        assert request.method == "GET"
        assert request.url == "https://example.com"
        assert dict(request.headers) == {}

    def test_http_request_custom_method(self) -> None:
        """HttpRequest accepts valid custom method."""
        request = m.Api.HttpRequest.model_validate({
            "url": "https://example.com",
            "method": "POST",
        })
        assert request.method == "POST"

    def test_http_request_rejects_empty_url(self) -> None:
        """HttpRequest rejects empty URL."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({"url": ""})

    def test_http_response_success(self) -> None:
        """HttpResponse accepts valid status code and body."""
        response = m.Api.HttpResponse.model_validate({
            "status_code": 200,
            "body": {"result": "ok"},
        })
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

    def test_http_response_rejects_invalid_status(self) -> None:
        """HttpResponse rejects status codes outside 100-599."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpResponse.model_validate({"status_code": 999})

    def test_packb_produces_bytes(self) -> None:
        """Packb returns non-empty bytes for valid input."""
        payload: t.JsonMapping = {"key": "value"}
        packed = u.packb(payload)
        assert packed, "packb should return non-empty bytes"
        assert len(packed) > 0

    def test_packb_unpackb_roundtrip(self) -> None:
        """Pack then unpack returns original data."""
        original: t.JsonMapping = {"hello": "world", "count": 42}
        packed = u.packb(original)
        result = u.unpackb(packed)
        assert result.success is True
        assert result.value == original

    def test_api_client_uses_keyword_settings(self) -> None:
        """FlextApiClient accepts a settings model through the public settings input."""
        settings = FlextApiSettings(base_url="https://service.example", timeout=9.5)
        client = FlextApiClient(settings=settings)
        assert client.base_url == "https://service.example"
        assert abs(client.timeout - 9.5) < 1e-9

    def test_api_facade_uses_keyword_settings(self) -> None:
        """FlextApi accepts a settings model through the public settings input."""
        settings = FlextApiSettings(base_url="https://api.example", timeout=4.0)
        api = FlextApi(settings=settings)
        result = api.execute()
        assert result.success is True
        assert result.value is True
        assert api.settings.base_url == "https://api.example"
        assert abs(api.settings.timeout - 4.0) < 1e-9

    def test_package_imports_main_facade(self) -> None:
        assert FlextApi.__name__ == "FlextApi"
