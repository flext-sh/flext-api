"""FLEXT Test Matchers - Assertion utilities for testing.

Provides custom pytest matchers and assertion helpers for FLEXT ecosystem testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Any

from flext_core import FlextResult, FlextTypes


class FlextTestsMatchers:
    """Test matchers and assertion utilities.

    Provides custom matchers for common FLEXT patterns.
    """

    @staticmethod
    def assert_flext_result_success(
        result: FlextResult[Any],
        expected_data: Any = None,
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
        result: FlextResult[Any],
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
            assert "code" in response["error"], "Error missing 'code' field"
            assert "message" in response["error"], "Error missing 'message' field"


__all__ = ["FlextTestsMatchers"]
