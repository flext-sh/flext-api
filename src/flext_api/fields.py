"""Compatibility fields module mapping to api_types.

Re-exports field helpers and types for tests that import flext_api.fields.
"""

from __future__ import annotations

from flext_api.api_types import (
    FlextAPIFieldCore,
    FlextAPIFields,
    api_key_field,
    bearer_token_field,
    endpoint_path_field,
    http_method_field,
    pipeline_config_field,
    plugin_config_field,
    response_format_field,
    user_role_field,
)

__all__ = [
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
]
