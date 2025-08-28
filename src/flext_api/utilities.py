"""FLEXT API Utilities - EXTENDING FlextUtilities from flext-core.

Provides API-specific utility extensions while inheriting ALL functionality
from FlextUtilities. Follows the FLEXT pattern of creating a single
FlextApi[Module] class that extends the flext-core equivalent.

Extensions include:
- HTTP/JSON response parsing
- API client configuration validation
- Response data processing
- Type-safe data extraction for API operations

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# JSON operations use FlextUtilities.ProcessingUtils - no direct json import needed
from typing import cast

import aiohttp  # HTTP client specific - not available in core utilities
from flext_core import FlextLogger, FlextResult, FlextUtilities

logger: FlextLogger = FlextLogger(__name__)


class FlextApiUtilities(FlextUtilities):
    """CONSOLIDATED API utilities class extending FlextUtilities.

    Follows FLEXT architectural pattern:
    - INHERITS ALL functionality from flext-core FlextUtilities
    - EXTENDS with API-specific utilities (HTTP, JSON, client validation)
    - SINGLE consolidated class per module pattern
    - Uses FlextResult for all operations that can fail
    - Provides type-safe data extraction for API operations

    INHERITED FEATURES from FlextUtilities:
    - ID generation (generate_uuid, generate_entity_id, etc.)
    - Time operations (generate_timestamp, generate_iso_timestamp, etc.)
    - Text processing (truncate, clean_text, mask_sensitive, etc.)
    - Type conversions (safe_int, safe_float, safe_str, to_bool)
    - Type guards (is_string, is_email, is_uuid, is_url, etc.)
    - Performance tracking (@track_performance decorator)
    - JSON operations (safe_json_parse, safe_json_stringify)
    - Result utilities (chain_results, first_success, etc.)
    - LDAP converters (safe_convert_value_to_str, etc.)
    - Factory patterns (SimpleFactory, SimpleBuilder)

    EXTENDED FEATURES for flext-api:
    - HTTP response parsing with type safety
    - API client configuration validation
    - Response data processing for REST APIs
    - Type-safe data extraction from complex JSON structures
    """

    # =============================================================================
    # API-SPECIFIC UTILITIES - Extensions to FlextUtilities
    # =============================================================================

    # =============================================================================
    # API-SPECIFIC EXTENSIONS to FlextUtilities
    # =============================================================================

    @classmethod
    def parse_json_response_data(
        cls,
        json_data: object,
    ) -> dict[str, object] | list[object] | str | int | float | bool | None:
        """Parse JSON response data with type safety.

        Uses inherited ProcessingUtils.safe_json_parse for base JSON operations
        and extends with API-specific response data parsing logic.

        Args:
            json_data: Raw JSON data from HTTP response

        Returns:
            Parsed and type-safe JSON data suitable for API responses

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

        if isinstance(json_data, str | int | float | bool):
            return json_data  # Return actual type instead of converting to string

        # For any other types, convert to string representation
        return str(json_data)

    @classmethod
    def parse_fallback_text_data(
        cls,
        text_data: str,
    ) -> dict[str, object] | str:
        """Parse fallback text data as JSON.

        Extracts fallback parsing logic to reduce cyclomatic complexity.
        """
        try:
            parsed_data = FlextUtilities.ProcessingUtils.safe_json_parse(text_data)
            # safe_json_parse always returns dict[str, object], so simplify
            return {
                parsed_key: parsed_value
                for parsed_key, parsed_value in parsed_data.items()
                if parsed_key
            }
        except Exception:
            return text_data

    @classmethod
    def parse_final_json_attempt(
        cls,
        text_trim: str,
    ) -> dict[str, object] | str:
        """Parse final JSON attempt with fallback.

        Extracts final JSON parsing logic to reduce cyclomatic complexity.
        """
        try:
            fallback_parsed_data = FlextUtilities.ProcessingUtils.safe_json_parse(text_trim)
            # safe_json_parse always returns dict[str, object], so simplify
            return {
                fallback_key: fallback_value
                for fallback_key, fallback_value in fallback_parsed_data.items()
                if fallback_key
            }
        except Exception:
            return text_trim

    @classmethod
    async def read_response_data_safely(
        cls,
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
                return cls.parse_json_response_data(json_data)
            except Exception:
                # Fallback: read text and attempt JSON parse
                try:
                    text_data = await response.text()
                    return cls.parse_fallback_text_data(text_data)
                except Exception:
                    return await response.text()

        # Non-JSON content
        text = await response.text()
        # If it looks like JSON, attempt to parse
        text_trim = text.strip()
        if text_trim.startswith(("{", "[")):
            return cls.parse_final_json_attempt(text_trim)

        return text

    @classmethod
    def validate_client_config(
        cls,
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
        # Type-safe headers validation using cast
        headers: dict[str, str]
        if isinstance(headers_raw, dict):
            # Cast to dict with unknown values then convert safely
            unknown_dict = cast("dict[str, object]", headers_raw)
            headers = {k: str(v) for k, v in unknown_dict.items() if v is not None}
        else:
            headers = {}

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
        if not isinstance(timeout, int | float) or timeout <= 0:
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


# =============================================================================
# LEGACY COMPATIBILITY - Function aliases for backward compatibility
# =============================================================================


def parse_json_response_data(
    json_data: object,
) -> dict[str, object] | list[object] | str | int | float | bool | None:
    """Parse JSON response data with type safety."""
    return FlextApiUtilities.parse_json_response_data(json_data)


def parse_fallback_text_data(
    text_data: str,
) -> dict[str, object] | list[object] | str | None:
    """Parse fallback text data as JSON."""
    return FlextApiUtilities.parse_fallback_text_data(text_data)


def parse_final_json_attempt(
    text_trim: str,
) -> dict[str, object] | list[object] | str:
    """Parse final JSON attempt with fallback."""
    return FlextApiUtilities.parse_final_json_attempt(text_trim)


async def read_response_data_safely(
    response: aiohttp.ClientResponse,
) -> dict[str, object] | list[object] | str | bytes | int | float | bool | None:
    """Read response data with comprehensive type safety."""
    return await FlextApiUtilities.read_response_data_safely(response)


def validate_client_config(
    config: dict[str, object] | None,
) -> FlextResult[dict[str, object]]:
    """Validate client configuration with comprehensive checks."""
    return FlextApiUtilities.validate_client_config(config)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main Utilities Class (Primary API)
    "FlextApiUtilities",
    "parse_fallback_text_data",
    "parse_final_json_attempt",
    # Legacy Function Aliases (for backward compatibility)
    "parse_json_response_data",
    "read_response_data_safely",
    "validate_client_config",
]
