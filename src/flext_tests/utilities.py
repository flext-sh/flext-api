"""FLEXT Test Utilities - Helper functions for testing.

Provides utility functions for FLEXT ecosystem testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

from flext_core import FlextResult, FlextTypes


class FlextTestsUtilities:
    """Test utilities and helper functions.

    Provides common testing utilities following FLEXT patterns.
    """

    @staticmethod
    def create_temp_file(
        content: str = "",
        suffix: str = ".txt",
        prefix: str = "test_",
    ) -> Path:
        """Create a temporary file with content.

        Args:
            content: File content
            suffix: File extension
            prefix: File prefix

        Returns:
            Path to created temporary file

        """
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=suffix,
            prefix=prefix,
            delete=False,
        ) as f:
            f.write(content)
            return Path(f.name)

    @staticmethod
    def create_temp_json_file(data: FlextTypes.Dict) -> Path:
        """Create a temporary JSON file with data.

        Args:
            data: Data to serialize as JSON

        Returns:
            Path to created temporary JSON file

        """
        return FlextTestsUtilities.create_temp_file(
            content=json.dumps(data, indent=2),
            suffix=".json",
        )

    @staticmethod
    def parse_json_result(result: FlextResult[str]) -> FlextResult[FlextTypes.Dict]:
        """Parse JSON string result into dictionary.

        Args:
            result: FlextResult containing JSON string

        Returns:
            FlextResult containing parsed dictionary or error

        """
        if result.is_failure:
            return FlextResult[FlextTypes.Dict].fail(
                result.error or "Failed to parse JSON"
            )

        try:
            data = json.loads(result.unwrap())
            return FlextResult[FlextTypes.Dict].ok(data)
        except (json.JSONDecodeError, TypeError) as e:
            return FlextResult[FlextTypes.Dict].fail(f"Invalid JSON: {e}")

    @staticmethod
    def validate_response_structure(
        response: FlextTypes.Dict,
        expected_keys: list[str] | None = None,
    ) -> FlextResult[None]:
        """Validate response structure.

        Args:
            response: Response to validate
            expected_keys: Keys that should be present

        Returns:
            FlextResult indicating validation success or failure

        """
        if not isinstance(response, dict):
            return FlextResult[None].fail("Response must be a dictionary")

        if expected_keys:
            missing_keys = [key for key in expected_keys if key not in response]
            if missing_keys:
                return FlextResult[None].fail(f"Missing keys: {missing_keys}")

        return FlextResult[None].ok(None)

    @staticmethod
    def mock_http_response(
        status_code: int = 200,
        json_data: FlextTypes.Dict | None = None,
        text: str | None = None,
        headers: FlextTypes.StringDict | None = None,
    ) -> Any:
        """Create a mock HTTP response object.

        Args:
            status_code: HTTP status code
            json_data: JSON response data
            text: Text response data
            headers: Response headers

        Returns:
            Mock response object

        """

        class MockResponse:
            def __init__(
                self, status: int, json_data: Any, text: str, headers: Any
            ) -> None:
                self.status_code = status
                self._json_data = json_data
                self._text = text
                self.headers = headers or {}

            def json(self):
                return self._json_data

            def text(self):
                return self._text

            async def ajson(self):
                return self._json_data

            async def atext(self):
                return self._text

        return MockResponse(status_code, json_data, text or "", headers)


__all__ = ["FlextTestsUtilities"]
