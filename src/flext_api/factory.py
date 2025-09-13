"""FLEXT API - Factory functions for creating API clients.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextTypes

from flext_api.client import FlextApiClient
from flext_api.models import FlextApiModels

# Default values as constants
_DEFAULT_TIMEOUT = 30.0
_DEFAULT_MAX_RETRIES = 3


def create_flext_api(config_dict: dict[str, object] | None = None) -> FlextApiClient:
    """Create and return a new FlextApiClient instance.

    Args:
        config_dict: Optional configuration dictionary

    Returns:
        FlextApiClient: A configured HTTP client instance.

    """
    if config_dict is None:
        client_config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        return FlextApiClient(config=client_config)

    # Create config with provided base_url
    base_url = config_dict.get("base_url", "https://api.example.com")
    timeout = config_dict.get("timeout", 30.0)
    max_retries = config_dict.get("max_retries", 3)
    headers = config_dict.get("headers", {})

    # Type-safe conversion with proper checks
    base_url_str = str(base_url) if base_url is not None else "https://api.example.com"
    timeout_val = (
        float(timeout) if isinstance(timeout, (int, float)) else _DEFAULT_TIMEOUT
    )
    max_retries_val = (
        int(max_retries) if isinstance(max_retries, int) else _DEFAULT_MAX_RETRIES
    )
    headers_dict = dict(headers) if isinstance(headers, dict) else {}

    # Create client config that matches the provided settings
    client_config = FlextApiModels.ClientConfig(
        base_url=base_url_str,
        timeout=timeout_val,
        max_retries=max_retries_val,
        headers=headers_dict,
    )

    return FlextApiClient(config=client_config)


__all__: FlextTypes.Core.StringList = [
    "create_flext_api",
]
