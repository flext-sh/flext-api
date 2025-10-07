"""FLEXT Test Matchers - Assertion utilities for testing.

Provides custom pytest matchers and assertion helpers for FLEXT ecosystem testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextResult, FlextTypes


class FlextTestsMatchers:
    """Test matchers and assertion utilities.

    Provides custom matchers for common FLEXT patterns.
    """

    class TestDataBuilder:
        """Builder for test datasets."""

        def __init__(self) -> None:
            """Initialize test data builder."""
            super().__init__()
            self._data: dict[str, object] = {}

        def with_users(self, count: int = 5) -> FlextTestsMatchers.TestDataBuilder:
            """Add users to dataset."""
            self._data["users"] = [
                {
                    "id": f"USER-{i}",
                    "name": f"User {i}",
                    "email": f"user{i}@example.com",
                    "age": 20 + i,
                }
                for i in range(count)
            ]
            return self

        def with_configs(
            self, *, production: bool = False
        ) -> FlextTestsMatchers.TestDataBuilder:
            """Add configuration to dataset."""
            self._data["configs"] = {
                "environment": "production" if production else "development",
                "debug": not production,
                "database_url": "postgresql://localhost/testdb",
                "api_timeout": 30,
                "max_connections": 10,
            }
            return self

        def with_validation_fields(
            self, count: int = 5
        ) -> FlextTestsMatchers.TestDataBuilder:
            """Add validation fields to dataset."""
            self._data["validation_fields"] = {
                "valid_emails": [f"user{i}@example.com" for i in range(count)],
                "invalid_emails": ["invalid", "no-at-sign.com", ""],
                "valid_hostnames": ["example.com", "localhost"],
                "invalid_hostnames": ["invalid..hostname", ""],
            }
            return self

        def build(self) -> dict[str, object]:
            """Build the dataset."""
            return dict(self._data)

    @staticmethod
    def assert_flext_result_success(
        result: FlextResult[FlextTypes.JsonValue],
        expected_data: FlextTypes.JsonValue | None = None,
    ) -> None:
        """Assert that a FlextResult is successful.

        Args:
            result: The FlextResult to check
            expected_data: Expected data if provided

        Raises:
            AssertionError: If result is not successful

        """
        assert result.is_success, f"Expected success, got failure: {result.error}"
        if expected_data is not None:
            assert result.unwrap() == expected_data

    @staticmethod
    def assert_flext_result_failure(
        result: FlextResult[object],
        expected_error: str | None = None,
    ) -> None:
        """Assert that a FlextResult is a failure.

        Args:
            result: The FlextResult to check
            expected_error: Expected error message if provided

        Raises:
            AssertionError: If result is not a failure

        """
        assert result.is_failure, f"Expected failure, got success: {result.unwrap()}"
        if expected_error is not None:
            assert result.error == expected_error

    @staticmethod
    def assert_dict_contains_keys(
        data: FlextTypes.Dict,
        required_keys: list[str],
    ) -> None:
        """Assert that a dictionary contains all required keys.

        Args:
            data: Dictionary to check
            required_keys: Keys that must be present

        Raises:
            AssertionError: If any required key is missing

        """
        missing_keys = [key for key in required_keys if key not in data]
        assert not missing_keys, f"Missing required keys: {missing_keys}"

    @staticmethod
    def assert_api_response_format(response: FlextTypes.Dict) -> None:
        """Assert that a response follows the standard API format.

        Args:
            response: API response to validate

        Raises:
            AssertionError: If response format is invalid

        """
        required_keys = ["status", "timestamp", "request_id"]
        FlextTestsMatchers.assert_dict_contains_keys(response, required_keys)

        assert response["status"] in {"success", "error"}, (
            f"Invalid status: {response['status']}"
        )

        if response["status"] == "success":
            assert "data" in response, "Success response missing 'data' field"
        else:
            assert "error" in response, "Error response missing 'error' field"
            error_data = response["error"]
            if isinstance(error_data, dict):
                assert "code" in error_data, "Error missing 'code' field"
                assert "message" in error_data, "Error missing 'message' field"


__all__ = ["FlextTestsMatchers"]
