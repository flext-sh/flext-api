"""FLEXT-API Fields - Simple field definitions for the API layer.

This module provides basic field definitions for FLEXT-API domain concepts.
Since the complex FlextFieldCore implementation is not available, we provide
simple dictionary-based field definitions for testing and documentation purposes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from flext_api.types import TData

import aiohttp.hdrs

# Re-export from flext-core for compatibility
from flext_core import FlextFieldCore, FlextFields

__all__ = [
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "FlextFieldCore",
    "FlextFields",
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
]


class FlextAPIFieldCore:
    """Simple field core for FLEXT-API domain."""

    @classmethod
    def api_key_field(
        cls,
        description: str = "API key for authentication",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create API key field definition."""
        return {
            "field_type": "api_key",
            "description": description,
            "sensitive": True,
            "required": True,
            "min_length": 32,
            "max_length": 128,
            "pattern": r"^[A-Za-z0-9_-]+$",
            **kwargs,
        }

    @classmethod
    def bearer_token_field(
        cls,
        description: str = "Bearer token for authentication",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create bearer token field definition."""
        return {
            "field_type": "bearer_token",
            "description": description,
            "sensitive": True,
            "required": True,
            "min_length": 50,
            "max_length": 2048,
            "pattern": r"^[A-Za-z0-9._-]+$",
            **kwargs,
        }

    @classmethod
    def pipeline_config_field(
        cls,
        description: str = "Pipeline configuration data",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create pipeline configuration field definition."""
        return {
            "field_type": "pipeline_config",
            "description": description,
            "required": True,
            "data_type": "dict",
            "validation_rules": [
                "must_contain_name",
                "must_contain_steps",
                "steps_must_be_list",
            ],
            **kwargs,
        }

    @classmethod
    def plugin_config_field(
        cls,
        description: str = "Plugin configuration data",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create plugin configuration field definition."""
        return {
            "field_type": "plugin_config",
            "description": description,
            "required": True,
            "data_type": "dict",
            "validation_rules": [
                "must_contain_plugin_id",
                "must_contain_version",
            ],
            **kwargs,
        }

    @classmethod
    def user_role_field(
        cls,
        description: str = "User role for authorization",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create user role field definition."""
        return {
            "field_type": "user_role",
            "description": description,
            "required": True,
            "data_type": "string",
            "allowed_values": ["admin", "user", "readonly", "operator"],
            **kwargs,
        }

    @classmethod
    def endpoint_path_field(
        cls,
        description: str = "API endpoint path",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create endpoint path field definition."""
        return {
            "field_type": "endpoint_path",
            "description": description,
            "required": True,
            "data_type": "string",
            "pattern": r"^/[a-zA-Z0-9/_-]*$",
            "min_length": 1,
            "max_length": 255,
            **kwargs,
        }

    @classmethod
    def http_method_field(
        cls,
        description: str = "HTTP method",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create HTTP method field definition."""
        return {
            "field_type": "http_method",
            "description": description,
            "required": True,
            "data_type": "string",
            "allowed_values": [
                aiohttp.hdrs.METH_GET,
                aiohttp.hdrs.METH_POST,
                aiohttp.hdrs.METH_PUT,
                aiohttp.hdrs.METH_PATCH,
                aiohttp.hdrs.METH_DELETE,
                aiohttp.hdrs.METH_HEAD,
                aiohttp.hdrs.METH_OPTIONS,
            ],
            **kwargs,
        }

    @classmethod
    def response_format_field(
        cls,
        description: str = "Response format type",
        **kwargs: TData,
    ) -> dict[str, object]:
        """Create response format field definition."""
        return {
            "field_type": "response_format",
            "description": description,
            "required": False,
            "data_type": "string",
            "allowed_values": ["json", "xml", "text", "html"],
            "default": "json",
            **kwargs,
        }


class FlextAPIFields:
    """Simple fields collection for FLEXT-API domain."""

    # Authentication fields
    API_KEY = FlextAPIFieldCore.api_key_field()
    BEARER_TOKEN = FlextAPIFieldCore.bearer_token_field()

    # Configuration fields
    PIPELINE_CONFIG = FlextAPIFieldCore.pipeline_config_field()
    PLUGIN_CONFIG = FlextAPIFieldCore.plugin_config_field()

    # Authorization fields
    USER_ROLE = FlextAPIFieldCore.user_role_field()

    # API fields
    ENDPOINT_PATH = FlextAPIFieldCore.endpoint_path_field()
    HTTP_METHOD = FlextAPIFieldCore.http_method_field()
    RESPONSE_FORMAT = FlextAPIFieldCore.response_format_field()

    # User management fields
    USERNAME: ClassVar[dict[str, object]] = {
        "field_type": "username",
        "description": "User login name",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_]{3,50}$",
        "min_length": 3,
        "max_length": 50,
    }

    EMAIL: ClassVar[dict[str, object]] = {
        "field_type": "email",
        "description": "User email address",
        "required": True,
        "data_type": "string",
        "pattern": r"^[^@]+@[^@]+\.[^@]+$",
        "max_length": 255,
    }

    PASSWORD: ClassVar[dict[str, object]] = {
        "field_type": "password",
        "description": "User password",
        "required": True,
        "data_type": "string",
        "sensitive": True,
        "min_length": 8,
        "max_length": 128,
        "validation_rules": [
            "must_contain_uppercase",
            "must_contain_lowercase",
            "must_contain_digit",
            "must_contain_special_char",
        ],
    }

    # Pipeline fields
    PIPELINE_NAME: ClassVar[dict[str, object]] = {
        "field_type": "pipeline_name",
        "description": "Pipeline identifier name",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_-]{1,100}$",
        "min_length": 1,
        "max_length": 100,
    }

    PIPELINE_DESCRIPTION: ClassVar[dict[str, object]] = {
        "field_type": "pipeline_description",
        "description": "Pipeline description text",
        "required": False,
        "data_type": "string",
        "max_length": 500,
    }

    PIPELINE_TIMEOUT: ClassVar[dict[str, object]] = {
        "field_type": "pipeline_timeout",
        "description": "Pipeline execution timeout in seconds",
        "required": False,
        "data_type": "integer",
        "min_value": 1,
        "max_value": 3600,
        "default": 300,
    }

    # Plugin fields
    PLUGIN_ID: ClassVar[dict[str, object]] = {
        "field_type": "plugin_id",
        "description": "Plugin unique identifier",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_-]+$",
        "min_length": 1,
        "max_length": 100,
    }

    PLUGIN_VERSION: ClassVar[dict[str, object]] = {
        "field_type": "plugin_version",
        "description": "Plugin version string",
        "required": True,
        "data_type": "string",
        "pattern": r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$",
        "max_length": 50,
    }

    PLUGIN_ENABLED: ClassVar[dict[str, object]] = {
        "field_type": "plugin_enabled",
        "description": "Plugin enabled status",
        "required": False,
        "data_type": "boolean",
        "default": True,
    }

    # System fields
    SYSTEM_STATUS: ClassVar[dict[str, object]] = {
        "field_type": "system_status",
        "description": "System health status",
        "required": True,
        "data_type": "string",
        "allowed_values": ["healthy", "degraded", "unhealthy", "maintenance"],
    }

    LOG_LEVEL: ClassVar[dict[str, object]] = {
        "field_type": "log_level",
        "description": "Logging level",
        "required": False,
        "data_type": "string",
        "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "default": "INFO",
    }

    # Request/Response fields
    REQUEST_ID: ClassVar[dict[str, object]] = {
        "field_type": "request_id",
        "description": "Unique request identifier",
        "required": True,
        "data_type": "string",
        "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    CORRELATION_ID: ClassVar[dict[str, object]] = {
        "field_type": "correlation_id",
        "description": "Request correlation identifier",
        "required": False,
        "data_type": "string",
        "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    TIMESTAMP: ClassVar[dict[str, object]] = {
        "field_type": "timestamp",
        "description": "ISO 8601 timestamp",
        "required": True,
        "data_type": "string",
        "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?Z?$",
    }


# Convenience field builders
def api_key_field(
    description: str = "API key for authentication",
    **kwargs: TData,
) -> dict[str, object]:
    """Create API key field definition."""
    return FlextAPIFieldCore.api_key_field(description=description, **kwargs)


def bearer_token_field(
    description: str = "Bearer token for authentication",
    **kwargs: TData,
) -> dict[str, object]:
    """Create bearer token field definition."""
    return FlextAPIFieldCore.bearer_token_field(description=description, **kwargs)


def pipeline_config_field(
    description: str = "Pipeline configuration data",
    **kwargs: TData,
) -> dict[str, object]:
    """Create pipeline configuration field definition."""
    return FlextAPIFieldCore.pipeline_config_field(description=description, **kwargs)


def plugin_config_field(
    description: str = "Plugin configuration data",
    **kwargs: TData,
) -> dict[str, object]:
    """Create plugin configuration field definition."""
    return FlextAPIFieldCore.plugin_config_field(description=description, **kwargs)


def user_role_field(
    description: str = "User role for authorization",
    **kwargs: TData,
) -> dict[str, object]:
    """Create user role field definition."""
    return FlextAPIFieldCore.user_role_field(description=description, **kwargs)


def endpoint_path_field(
    description: str = "API endpoint path",
    **kwargs: TData,
) -> dict[str, object]:
    """Create endpoint path field definition."""
    return FlextAPIFieldCore.endpoint_path_field(description=description, **kwargs)


def http_method_field(
    description: str = "HTTP method",
    **kwargs: TData,
) -> dict[str, object]:
    """Create HTTP method field definition."""
    return FlextAPIFieldCore.http_method_field(description=description, **kwargs)


def response_format_field(
    description: str = "Response format type",
    **kwargs: TData,
) -> dict[str, object]:
    """Create response format field definition."""
    return FlextAPIFieldCore.response_format_field(description=description, **kwargs)
