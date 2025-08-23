"""FLEXT API utility functions and classes.

Provides utility classes and functions following SOLID principles
and flext-core patterns for common operations.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from flext_core import FlextResult, get_logger

if TYPE_CHECKING:
    import aiohttp

logger = get_logger(__name__)


class FlextApiUtilities:
    """Static utility methods for common FLEXT API operations.

    Follows Single Responsibility Principle by grouping related utility functions.
    """

    @staticmethod
    def parse_json_response_data(
        json_data: object,
    ) -> dict[str, object] | list[object] | str | int | float | bool | None:
        """Parse JSON response data with type safety.

        Extracts complex parsing logic to reduce cyclomatic complexity.
        """
        if isinstance(json_data, dict):
            # Type-safe dict processing with explicit casting
            # Cast to specific types for PyRight type inference
            dict_data = cast("dict[str, object]", json_data)
            # Use dict comprehension for performance
            return {
                dict_key: dict_value
                for dict_key, dict_value in dict_data.items()
                if dict_key
            }

        if isinstance(json_data, list):
            # Type-safe list processing with explicit casting
            # Cast to specific types for PyRight type inference
            list_data = cast("list[object]", json_data)
            # Use list comprehension for performance
            return [
                list_element for list_element in list_data if list_element is not None
            ]

        if json_data is None:
            return None

        if isinstance(json_data, (str, int, float, bool)):
            return json_data  # Return actual type instead of converting to string

        # For any other types, convert to string representation
        return str(json_data)

    @staticmethod
    def parse_fallback_text_data(
        text_data: str,
    ) -> dict[str, object] | list[object] | str | None:
        """Parse fallback text data as JSON.

        Extracts fallback parsing logic to reduce cyclomatic complexity.
        """
        try:
            parsed_data: object = json.loads(text_data)
            if isinstance(parsed_data, dict):
                # Cast to specific types for PyRight type inference
                dict_data = cast("dict[str, object]", parsed_data)
                # Use dict comprehension for performance
                return {
                    parsed_key: parsed_value
                    for parsed_key, parsed_value in dict_data.items()
                    if parsed_key
                }
            if isinstance(parsed_data, list):
                # Cast to specific types for PyRight type inference
                list_data = cast("list[object]", parsed_data)
                # Use list comprehension for performance
                return [
                    parsed_element
                    for parsed_element in list_data
                    if parsed_element is not None
                ]
            return text_data
        except Exception:
            return text_data

    @staticmethod
    def parse_final_json_attempt(
        text_trim: str,
    ) -> dict[str, object] | list[object] | str:
        """Parse final JSON attempt with fallback.

        Extracts final JSON parsing logic to reduce cyclomatic complexity.
        """
        try:
            fallback_parsed_data: object = json.loads(text_trim)
            if isinstance(fallback_parsed_data, dict):
                # Cast to specific types for PyRight type inference
                dict_data = cast("dict[str, object]", fallback_parsed_data)
                # Use dict comprehension for performance
                return {
                    fallback_key: fallback_value
                    for fallback_key, fallback_value in dict_data.items()
                    if fallback_key
                }
            if isinstance(fallback_parsed_data, list):
                # Cast to specific types for PyRight type inference
                list_data = cast("list[object]", fallback_parsed_data)
                # Use list comprehension for performance
                return [
                    fallback_element
                    for fallback_element in list_data
                    if fallback_element is not None
                ]
            return text_trim
        except Exception:
            return text_trim

    @staticmethod
    async def read_response_data_safely(
        response: aiohttp.ClientResponse,
    ) -> dict[str, object] | list[object] | str | bytes | int | float | bool | None:
        """Read response data with comprehensive type safety.

        Refactored from complex _read_response_data method to reduce complexity.
        Uses utility methods to handle different parsing scenarios.
        """
        content_type = response.headers.get("content-type", "")
        logger.debug(
            "Processing response", content_type=content_type, status=response.status
        )

        # JSON content handling
        if "application/json" in content_type or "text/json" in content_type:
            try:
                json_data: object = await response.json()
                return FlextApiUtilities.parse_json_response_data(json_data)
            except Exception:
                # Fallback: read text and attempt JSON parse
                try:
                    text_data = await response.text()
                    return FlextApiUtilities.parse_fallback_text_data(text_data)
                except Exception:
                    return await response.text()

        # Non-JSON content
        text = await response.text()
        # If it looks like JSON, attempt to parse
        text_trim = text.strip()
        if text_trim.startswith(("{", "[")):
            return FlextApiUtilities.parse_final_json_attempt(text_trim)

        return text

    @staticmethod
    def validate_client_config(
        config: dict[str, object] | None,
    ) -> FlextResult[dict[str, object]]:
        """Validate client configuration with comprehensive checks.

        Extracts validation logic to reduce create_client complexity.
        """
        if config is None:
            return FlextResult[dict[str, object]].ok(
                {
                    "base_url": "",
                    "timeout": 30,
                    "max_retries": 3,
                }
            )

        # Apply defaults for missing values, validating headers type
        headers_raw = config.get("headers", {})
        headers: dict[str, str] = headers_raw if isinstance(headers_raw, dict) else {}

        validated_config: dict[str, object] = {
            "base_url": config.get("base_url", ""),
            "timeout": config.get("timeout", 30),
            "max_retries": config.get("max_retries", 3),
            "headers": headers,  # Use validated headers
            **{
                k: v
                for k, v in config.items()
                if k not in ["base_url", "timeout", "max_retries", "headers"]
            },  # Include other values
        }

        # Validate base_url - allow empty string but require string type
        base_url = validated_config.get("base_url")
        if not isinstance(base_url, str):
            return FlextResult[dict[str, object]].fail("base_url must be a string")

        # Validate timeout
        timeout = validated_config.get("timeout")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            return FlextResult[dict[str, object]].fail(
                "timeout must be a positive number"
            )

        # Validate max_retries
        max_retries = validated_config.get("max_retries")
        if not isinstance(max_retries, int) or max_retries < 0:
            return FlextResult[dict[str, object]].fail(
                "max_retries must be a non-negative integer"
            )

        return FlextResult[dict[str, object]].ok(validated_config)
