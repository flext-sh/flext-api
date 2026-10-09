"""Behavioral tests for the flext-api public contract.

Exercises observable behavior of the public facades, models, serializers,
and result-returning operations — never implementation details. Settings are
consumed in the canonical strict form: the published ``settings`` singleton,
cloned (never rebuilt) when a test needs specific values.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_api import FlextApi, FlextApiClient, c, settings
from tests.unit.model_contract import TestsFlextApiModelContract


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
    @staticmethod
    def test_http_method_enum_resolves_to_wire_string(
        method: c.Api.Method,
        expected: str,
    ) -> None:
        """Each HTTP method compares equal to its wire string value."""
        tm.that(method, eq=expected)

    @pytest.mark.parametrize(
        ("status", "expected"),
        [(c.Api.Status.SUCCESS, "success"), (c.Api.Status.FAILED, "failed")],
    )
    @staticmethod
    def test_status_enum_value(status: c.Api.Status, expected: str) -> None:
        """Status enum members expose the documented string values."""
        tm.that(status.value, eq=expected)

    @pytest.mark.parametrize(
        ("content_type", "expected"),
        [
            (c.Api.ContentType.JSON, "application/json"),
            (c.Api.ContentType.XML, "application/xml"),
        ],
    )
    @staticmethod
    def test_content_type_maps_to_mime(
        content_type: c.Api.ContentType,
        expected: str,
    ) -> None:
        """ContentType members map to their MIME type strings."""
        tm.that(content_type.value, eq=expected)

    @staticmethod
    def test_safe_methods_membership_contract() -> None:
        """SAFE_METHODS classifies GET as safe and POST as unsafe."""
        tm.that(c.Api.SAFE_METHODS, has="GET")
        tm.that(c.Api.SAFE_METHODS, lacks="POST")

    @staticmethod
    def test_safe_methods_is_immutable() -> None:
        """SAFE_METHODS is a frozenset and rejects mutation."""
        tm.that(c.Api.SAFE_METHODS, is_=frozenset)

    @staticmethod
    def test_terminal_statuses_membership_contract() -> None:
        """Terminal statuses include completion/failure but not pending."""
        tm.that(c.Api.TERMINAL_STATUSES, has="completed")
        tm.that(c.Api.TERMINAL_STATUSES, has="failed")
        tm.that(c.Api.TERMINAL_STATUSES, lacks="pending")

    @staticmethod
    def test_http_status_bounds_are_ordered() -> None:
        """HTTP status boundaries form a valid, ordered range."""
        tm.that(c.Api.HTTP_STATUS_MIN, lt=c.Api.HTTP_SUCCESS_MIN)
        tm.that(c.Api.HTTP_SUCCESS_MIN, lt=c.Api.HTTP_SUCCESS_MAX)
        tm.that(c.Api.HTTP_SUCCESS_MAX, lte=c.Api.HTTP_STATUS_MAX)
        tm.that(c.Api.HTTP_STATUS_MIN, lt=c.Api.HTTP_STATUS_MAX)

    # ---- Client / facade contract ---------------------------------------

    @staticmethod
    def test_client_exposes_settings_through_public_properties() -> None:
        """The client surfaces the settings namespace it was built from."""
        configured = settings.clone(
            Api={"base_url": "https://service.example", "timeout": 9.5},
        )
        client = FlextApiClient(runtime_settings=configured)
        tm.that(client.base_url, eq=configured.Api.base_url)
        tm.that(client.timeout, eq=pytest.approx(configured.Api.timeout))

    @staticmethod
    def test_client_execute_reports_success() -> None:
        """A configured client executes its lifecycle successfully."""
        client = FlextApiClient(runtime_settings=settings)
        result = client.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)

    @staticmethod
    def test_facade_execute_reports_success_and_retains_settings() -> None:
        """The facade executes successfully and preserves its settings."""
        configured = settings.clone(
            Api={"base_url": "https://api.example", "timeout": 4.0},
        )
        api = FlextApi(runtime_settings=configured)
        result = api.execute()
        tm.that(result.success, eq=True)
        tm.that(result.value, eq=True)
        tm.that(api.settings.Api.base_url, eq=configured.Api.base_url)
        tm.that(api.settings.Api.timeout, eq=pytest.approx(configured.Api.timeout))

    @staticmethod
    def test_facade_default_settings_provide_base_url() -> None:
        """A facade built without settings still exposes a usable base_url."""
        api = FlextApi()
        tm.that(api.settings.Api.base_url, is_=str)
        tm.that(api.execute().success, eq=True)
