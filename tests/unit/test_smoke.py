"""Behavioral tests for the flext-api public contract.

Exercises observable behavior of the public facades, models, serializers,
and result-returning operations — never implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_api import (
    FlextApi,
    FlextApiSettings,
)
from flext_api._utilities.client import FlextApiClient
from tests.constants import c
from tests.models import m
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


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
        assert method == expected

    @pytest.mark.parametrize(
        ("status", "expected"),
        [
            (c.Api.Status.SUCCESS, "success"),
            (c.Api.Status.FAILED, "failed"),
        ],
    )
    def test_status_enum_value(self, status: c.Api.Status, expected: str) -> None:
        """Status enum members expose the documented string values."""
        assert status.value == expected

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
        assert content_type.value == expected

    def test_safe_methods_membership_contract(self) -> None:
        """SAFE_METHODS classifies GET as safe and POST as unsafe."""
        assert "GET" in c.Api.SAFE_METHODS
        assert "POST" not in c.Api.SAFE_METHODS

    def test_safe_methods_is_immutable(self) -> None:
        """SAFE_METHODS is a frozenset and rejects mutation."""
        assert isinstance(c.Api.SAFE_METHODS, frozenset)

    def test_terminal_statuses_membership_contract(self) -> None:
        """Terminal statuses include completion/failure but not pending."""
        assert "completed" in c.Api.TERMINAL_STATUSES
        assert "failed" in c.Api.TERMINAL_STATUSES
        assert "pending" not in c.Api.TERMINAL_STATUSES

    def test_http_status_bounds_are_ordered(self) -> None:
        """HTTP status boundaries form a valid, ordered range."""
        assert c.Api.HTTP_STATUS_MIN == 100
        assert c.Api.HTTP_STATUS_MAX == 599
        assert c.Api.HTTP_STATUS_MIN < c.Api.HTTP_SUCCESS_MIN
        assert c.Api.HTTP_SUCCESS_MIN < c.Api.HTTP_SUCCESS_MAX <= c.Api.HTTP_STATUS_MAX

    # ---- HttpRequest model contract -------------------------------------

    def test_http_request_applies_documented_defaults(self) -> None:
        """A minimal request defaults to GET with empty headers and body."""
        request = m.Api.HttpRequest.model_validate({"url": "https://example.com"})
        assert request.method == "GET"
        assert request.url == "https://example.com"
        assert dict(request.headers) == {}
        assert request.body == {}

    def test_http_request_preserves_supplied_method(self) -> None:
        """A supplied method survives validation unchanged."""
        request = m.Api.HttpRequest.model_validate(
            {"url": "https://example.com", "method": "POST"}
        )
        assert request.method == "POST"

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
        request = m.Api.HttpRequest.model_validate(
            {"url": "https://example.com", "headers": headers}
        )
        assert request.content_type == expected

    def test_http_request_rejects_empty_url(self) -> None:
        """An empty URL fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate({"url": ""})

    def test_http_request_rejects_unknown_method(self) -> None:
        """A method outside the allowed pattern fails validation."""
        with pytest.raises(c.ValidationError):
            m.Api.HttpRequest.model_validate(
                {"url": "https://example.com", "method": "FETCH"}
            )

    def test_http_request_roundtrips_through_model_dump(self) -> None:
        """model_dump preserves the observable request fields."""
        request = m.Api.HttpRequest.model_validate(
            {"url": "https://example.com", "method": "POST"}
        )
        dumped = request.model_dump()
        assert dumped["url"] == "https://example.com"
        assert dumped["method"] == "POST"

    # ---- HttpResponse model contract ------------------------------------

    def test_http_response_accepts_valid_payload(self) -> None:
        """A 200 response exposes its status code and body verbatim."""
        response = m.Api.HttpResponse.model_validate(
            {"status_code": 200, "body": {"result": "ok"}}
        )
        assert response.status_code == 200
        assert response.body == {"result": "ok"}

    @pytest.mark.parametrize("status_code", [0, 99, 600, 999])
    def test_http_response_rejects_out_of_range_status(
        self, status_code: int
    ) -> None:
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
        status_code: int,
        success: bool,
        redirect: bool,
        client_error: bool,
        server_error: bool,
    ) -> None:
        """Computed classification fields agree with the status code class."""
        response = m.Api.HttpResponse.model_validate({"status_code": status_code})
        assert response.success is success
        assert response.redirect is redirect
        assert response.client_error is client_error
        assert response.server_error is server_error
        assert response.error is (client_error or server_error)

    def test_create_response_builds_equivalent_model(self) -> None:
        """create_response yields the same state as direct validation."""
        built = m.Api.create_response(status_code=200, body={"a": 1})
        assert built.status_code == 200
        assert built.body == {"a": 1}
        assert built.success is True

    # ---- Serializer contract --------------------------------------------

    def test_packb_returns_non_empty_bytes(self) -> None:
        """Packb serializes a mapping into non-empty bytes."""
        payload: t.JsonMapping = {"key": "value"}
        packed = u.Api.packb(payload)
        assert isinstance(packed, bytes)
        assert len(packed) > 0

    @pytest.mark.parametrize(
        "original",
        [
            {"hello": "world", "count": 42},
            {"nested": {"a": [1, 2, 3]}},
            {},
        ],
    )
    def test_packb_unpackb_is_lossless_roundtrip(
        self, original: t.JsonMapping
    ) -> None:
        """Packing then unpacking reproduces the original payload."""
        result = u.Api.unpackb(u.Api.packb(original))
        assert result.success is True
        assert result.value == original

    # ---- Client / facade contract ---------------------------------------

    def test_client_exposes_settings_through_public_properties(self) -> None:
        """The client surfaces its configured base_url and timeout."""
        settings = FlextApiSettings(base_url="https://service.example", timeout=9.5)
        client = FlextApiClient(settings=settings)
        assert client.base_url == "https://service.example"
        assert client.timeout == pytest.approx(9.5)

    def test_client_execute_reports_success(self) -> None:
        """A configured client executes its lifecycle successfully."""
        client = FlextApiClient(
            settings=FlextApiSettings(base_url="https://service.example")
        )
        result = client.execute()
        assert result.success is True
        assert result.value is True

    def test_facade_execute_reports_success_and_retains_settings(self) -> None:
        """The facade executes successfully and preserves its settings."""
        settings = FlextApiSettings(base_url="https://api.example", timeout=4.0)
        api = FlextApi(settings=settings)
        result = api.execute()
        assert result.success is True
        assert result.value is True
        assert api.settings.base_url == "https://api.example"
        assert api.settings.timeout == pytest.approx(4.0)

    def test_facade_default_settings_provide_base_url(self) -> None:
        """A facade built without settings still exposes a usable base_url."""
        api = FlextApi()
        assert isinstance(api.settings.base_url, str)
        assert api.execute().success is True
