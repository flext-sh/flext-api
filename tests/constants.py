"""Constants for flext-api tests.

Provides TestsFlextApiConstants, extending FlextTestsConstants with flext-api-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- FlextApiConstants (production) - Provides .Api.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final, TypeAlias

from flext_api import t
from flext_api.constants import FlextApiConstants
from flext_tests.constants import FlextTestsConstants


class TestsFlextApiConstants(FlextTestsConstants, FlextApiConstants):
    """Constants for flext-api tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsConstants - for test infrastructure (.Tests.*)
    2. FlextApiConstants - for domain constants (.Api.*)

    Access patterns:
    - tc.Tests.Docker.* (container testing)
    - tc.Tests.Matcher.* (assertion messages)
    - tc.Tests.Factory.* (test data generation)
    - tc.Api.* (domain constants from production)
    - tc.TestApi.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or FlextApiConstants
    - Only flext-api-specific test constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from FlextApiConstants
    """

    class Paths:
        """Test path constants."""

        TEST_INPUT_DIR: Final[str] = "tests/fixtures/data/input"
        TEST_OUTPUT_DIR: Final[str] = "tests/fixtures/data/output"
        TEST_TEMP_PREFIX: Final[str] = "flext_api_test_"

    class TestApi:
        """API test server constants."""

        DEFAULT_HOST: Final[str] = "localhost"
        DEFAULT_PORT: Final[int] = 8000
        DEFAULT_BASE_URL: Final[str] = "http://localhost:8000"
        TEST_API_VERSION: Final[str] = "v1"
        CONNECTION_TIMEOUT: Final[int] = 5
        OPERATION_TIMEOUT: Final[int] = 10

    class TestHTTP:
        """HTTP test constants."""

        TEST_ENDPOINT: Final[str] = "/api/v1/test"
        TEST_HEADERS: Final[dict[str, str]] = {"Content-Type": "application/json"}
        TEST_QUERY_PARAMS: Final[dict[str, str]] = {"page": "1", "limit": "10"}

    class TestResponses:
        """API response test constants."""

        TEST_SUCCESS_RESPONSE: Final[dict[str, t.GeneralValueType]] = {
            "status": "success",
            "data": {"message": "test"},
        }
        TEST_ERROR_RESPONSE: Final[dict[str, t.GeneralValueType]] = {
            "status": "error",
            "error": "test_error",
        }

    class TestMethods:
        """HTTP method test constants."""

        TEST_GET: Final[str] = "GET"
        TEST_POST: Final[str] = "POST"
        TEST_PUT: Final[str] = "PUT"
        TEST_DELETE: Final[str] = "DELETE"

    class Literals:
        """Literal type aliases for test constants (Python 3.13 pattern).

        These type aliases reuse production Literals from FlextApiConstants
        to ensure consistency between tests and production code.
        """

        # Reuse production Literals for consistency (Python 3.13+ best practices)
        # HTTP method literal (reusing production type)
        HttpMethodLiteral: TypeAlias = FlextApiConstants.Api.MethodLiteral

        # Content type literal (reusing production type)
        ContentTypeLiteral: TypeAlias = FlextApiConstants.Api.ContentTypeLiteral

        # Status literal (reusing production type)
        StatusLiteral: TypeAlias = FlextApiConstants.Api.StatusLiteral

        # Serialization format literal (reusing production type)
        SerializationFormatLiteral: TypeAlias = (
            FlextApiConstants.Api.SerializationFormatLiteral
        )


# Short aliases per FLEXT convention
tc = TestsFlextApiConstants  # Primary test constants alias
c = TestsFlextApiConstants  # Alternative alias for compatibility

__all__ = [
    "TestsFlextApiConstants",
    "c",
    "tc",
]
