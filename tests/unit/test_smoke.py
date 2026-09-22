"""Behavioral tests for the flext-api public contract.

Exercises observable behavior of the public facades, models, serializers,
and result-returning operations — never implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_api import FlextApi, FlextApiClient, FlextApiSettings, c

from .model_contract import TestsFlextApiModelContract


class TestsFlextApiSmoke(TestsFlextApiModelContract):
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

    # ---- Client / facade contract ---------------------------------------

    def test_client_exposes_settings_through_public_properties(self) -> None:
        """The client surfaces its configured base_url and timeout."""
        settings = FlextApiSettings(base_url="https://service.example", timeout=9.5)
        client = FlextApiClient(runtime_settings=settings)
        tm.that(client.base_url, eq="https://service.example")
        tm.that(client.timeout, eq=pytest.approx(9.5))

    def test_client_execute_reports_success(self) -> None:
        """A configured client executes its lifecycle successfully."""
        client = FlextApiClient(
            runtime_settings=FlextApiSettings(base_url="https://service.example")
        )
        result = client.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    def test_facade_execute_reports_success_and_retains_settings(self) -> None:
        """The facade executes successfully and preserves its settings."""
        settings = FlextApiSettings(base_url="https://api.example", timeout=4.0)
        api = FlextApi(runtime_settings=settings)
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


__all__: list[str] = ["TestsFlextApiSmoke"]
