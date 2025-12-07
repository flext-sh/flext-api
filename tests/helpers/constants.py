"""Test constants for flext-api tests.

Centralized constants for test fixtures, factories, and test data.
Does NOT duplicate src/flext_api/constants.py - only test-specific constants.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final, TypeAlias

from flext_api.constants import c


class TestsConstants(c):
    """Test constants extending c.

    Provides test-specific constants without duplicating parent functionality.
    All parent constants are accessible via inheritance hierarchy.
    """

    class Paths:
        """Test path constants."""

        TEST_INPUT_DIR: Final[str] = "tests/fixtures/data/input"
        TEST_OUTPUT_DIR: Final[str] = "tests/fixtures/data/output"
        TEST_TEMP_PREFIX: Final[str] = "flext_api_test_"

    class API:
        """API test server constants."""

        DEFAULT_HOST: Final[str] = "localhost"
        DEFAULT_PORT: Final[int] = 8000
        DEFAULT_BASE_URL: Final[str] = "http://localhost:8000"
        TEST_API_VERSION: Final[str] = "v1"
        CONNECTION_TIMEOUT: Final[int] = 5
        OPERATION_TIMEOUT: Final[int] = 10

    class HTTP:
        """HTTP test constants."""

        TEST_ENDPOINT: Final[str] = "/api/v1/test"
        TEST_HEADERS: Final[dict[str, str]] = {"Content-Type": "application/json"}
        TEST_QUERY_PARAMS: Final[dict[str, str]] = {"page": "1", "limit": "10"}

    class Responses:
        """API response test constants."""

        TEST_SUCCESS_RESPONSE: Final[dict[str, object]] = {
            "status": "success",
            "data": {"message": "test"},
        }
        TEST_ERROR_RESPONSE: Final[dict[str, object]] = {
            "status": "error",
            "error": "test_error",
        }

    class Methods:
        """HTTP method test constants."""

        TEST_GET: Final[str] = "GET"
        TEST_POST: Final[str] = "POST"
        TEST_PUT: Final[str] = "PUT"
        TEST_DELETE: Final[str] = "DELETE"

    class Literals:
        """Literal type aliases for test constants (Python 3.13 pattern).

        These type aliases reuse production Literals from c
        to ensure consistency between tests and production code.
        """

        # Reuse production Literals for consistency (Python 3.13+ best practices)
        # HTTP method literal (reusing production type)
        HttpMethodLiteral: TypeAlias = c.Api.MethodLiteral

        # Content type literal (reusing production type)
        ContentTypeLiteral: TypeAlias = c.Api.ContentTypeLiteral

        # Status literal (reusing production type)
        StatusLiteral: TypeAlias = c.Api.StatusLiteral

        # Serialization format literal (reusing production type)
        SerializationFormatLiteral: TypeAlias = c.Api.SerializationFormatLiteral

        # Protocol literals (reusing production types)
        WebSocketProtocolLiteral: TypeAlias = c.Api.WebSocketProtocolLiteral
        HttpProtocolLiteral: TypeAlias = c.Api.HttpProtocolLiteral
        SseProtocolLiteral: TypeAlias = c.Api.SseProtocolLiteral
        GraphQLProtocolLiteral: TypeAlias = c.Api.GraphQLProtocolLiteral


# Standardized short name for use in tests (same pattern as flext-core)
c = TestsConstants

__all__ = ["TestsConstants", "c"]
