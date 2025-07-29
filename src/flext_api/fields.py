"""FLEXT-API Fields - Extending flext-core fields system.

This module provides domain-specific field definitions built on top of flext-core's
robust fields system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextFieldCore, FlextFields

from flext_api.constants import FlextAPIFieldType

if TYPE_CHECKING:
    from flext_api.types import TData

# Re-export flext-core fields
__all__ = [
    "FlextAPIFieldCore",
    # Domain-specific fields
    "FlextAPIFields",
    # Flext-core base fields
    "FlextFieldCore",
    "FlextFields",
    # Field builders
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
]


class FlextAPIFieldCore(FlextFieldCore):
    """Extended field core for FLEXT-API domain."""

    @classmethod
    def api_key_field(
        cls,
        description: str = "API key for authentication",
        **kwargs: TData,
    ) -> TData:
        """Create API key field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.API_KEY,
            description=description,
            sensitive=True,
            required=True,
            min_length=32,
            max_length=128,
            pattern=r"^[A-Za-z0-9_-]+$",
            **kwargs,
        )

    @classmethod
    def bearer_token_field(
        cls,
        description: str = "Bearer token for authentication",
        **kwargs: TData,
    ) -> TData:
        """Create bearer token field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.BEARER_TOKEN,
            description=description,
            sensitive=True,
            required=True,
            min_length=50,
            max_length=2048,
            pattern=r"^[A-Za-z0-9._-]+$",
            **kwargs,
        )

    @classmethod
    def pipeline_config_field(
        cls,
        description: str = "Pipeline configuration data",
        **kwargs: TData,
    ) -> TData:
        """Create pipeline configuration field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.PIPELINE_CONFIG,
            description=description,
            required=True,
            data_type="dict",
            validation_rules=[
                "must_contain_name",
                "must_contain_steps",
                "steps_must_be_list",
            ],
            **kwargs,
        )

    @classmethod
    def plugin_config_field(
        cls,
        description: str = "Plugin configuration data",
        **kwargs: TData,
    ) -> TData:
        """Create plugin configuration field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.PLUGIN_CONFIG,
            description=description,
            required=True,
            data_type="dict",
            validation_rules=[
                "must_contain_plugin_id",
                "must_contain_version",
            ],
            **kwargs,
        )

    @classmethod
    def user_role_field(
        cls,
        description: str = "User role for authorization",
        **kwargs: TData,
    ) -> TData:
        """Create user role field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.USER_ROLE,
            description=description,
            required=True,
            data_type="string",
            allowed_values=["REDACTED_LDAP_BIND_PASSWORD", "user", "readonly", "operator"],
            **kwargs,
        )

    @classmethod
    def endpoint_path_field(
        cls,
        description: str = "API endpoint path",
        **kwargs: TData,
    ) -> TData:
        """Create endpoint path field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.ENDPOINT_PATH,
            description=description,
            required=True,
            data_type="string",
            pattern=r"^/[a-zA-Z0-9/_-]*$",
            min_length=1,
            max_length=255,
            **kwargs,
        )

    @classmethod
    def http_method_field(
        cls,
        description: str = "HTTP method",
        **kwargs: TData,
    ) -> TData:
        """Create HTTP method field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.HTTP_METHOD,
            description=description,
            required=True,
            data_type="string",
            allowed_values=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
            **kwargs,
        )

    @classmethod
    def response_format_field(
        cls,
        description: str = "Response format type",
        **kwargs: TData,
    ) -> TData:
        """Create response format field definition."""
        return cls._create_field(
            field_type=FlextAPIFieldType.RESPONSE_FORMAT,
            description=description,
            required=False,
            data_type="string",
            allowed_values=["json", "xml", "text", "html"],
            default="json",
            **kwargs,
        )


class FlextAPIFields(FlextFields):
    """Extended fields collection for FLEXT-API domain."""

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
    USERNAME = FlextAPIFieldCore._create_field(
        field_type="username",
        description="User login name",
        required=True,
        data_type="string",
        pattern=r"^[a-zA-Z0-9_]{3,50}$",
        min_length=3,
        max_length=50,
    )

    EMAIL = FlextAPIFieldCore._create_field(
        field_type="email",
        description="User email address",
        required=True,
        data_type="string",
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
        max_length=255,
    )

    PASSWORD = FlextAPIFieldCore._create_field(
        field_type="password",
        description="User password",
        required=True,
        data_type="string",
        sensitive=True,
        min_length=8,
        max_length=128,
        validation_rules=[
            "must_contain_uppercase",
            "must_contain_lowercase",
            "must_contain_digit",
            "must_contain_special_char",
        ],
    )

    # Pipeline fields
    PIPELINE_NAME = FlextAPIFieldCore._create_field(
        field_type="pipeline_name",
        description="Pipeline identifier name",
        required=True,
        data_type="string",
        pattern=r"^[a-zA-Z0-9_-]{1,100}$",
        min_length=1,
        max_length=100,
    )

    PIPELINE_DESCRIPTION = FlextAPIFieldCore._create_field(
        field_type="pipeline_description",
        description="Pipeline description text",
        required=False,
        data_type="string",
        max_length=500,
    )

    PIPELINE_TIMEOUT = FlextAPIFieldCore._create_field(
        field_type="pipeline_timeout",
        description="Pipeline execution timeout in seconds",
        required=False,
        data_type="integer",
        min_value=1,
        max_value=3600,
        default=300,
    )

    # Plugin fields
    PLUGIN_ID = FlextAPIFieldCore._create_field(
        field_type="plugin_id",
        description="Plugin unique identifier",
        required=True,
        data_type="string",
        pattern=r"^[a-zA-Z0-9_-]+$",
        min_length=1,
        max_length=100,
    )

    PLUGIN_VERSION = FlextAPIFieldCore._create_field(
        field_type="plugin_version",
        description="Plugin version string",
        required=True,
        data_type="string",
        pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$",
        max_length=50,
    )

    PLUGIN_ENABLED = FlextAPIFieldCore._create_field(
        field_type="plugin_enabled",
        description="Plugin enabled status",
        required=False,
        data_type="boolean",
        default=True,
    )

    # System fields
    SYSTEM_STATUS = FlextAPIFieldCore._create_field(
        field_type="system_status",
        description="System health status",
        required=True,
        data_type="string",
        allowed_values=["healthy", "degraded", "unhealthy", "maintenance"],
    )

    LOG_LEVEL = FlextAPIFieldCore._create_field(
        field_type="log_level",
        description="Logging level",
        required=False,
        data_type="string",
        allowed_values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
    )

    # Request/Response fields
    REQUEST_ID = FlextAPIFieldCore._create_field(
        field_type="request_id",
        description="Unique request identifier",
        required=True,
        data_type="string",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    )

    CORRELATION_ID = FlextAPIFieldCore._create_field(
        field_type="correlation_id",
        description="Request correlation identifier",
        required=False,
        data_type="string",
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    )

    TIMESTAMP = FlextAPIFieldCore._create_field(
        field_type="timestamp",
        description="ISO 8601 timestamp",
        required=True,
        data_type="string",
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?Z?$",
    )


# Convenience field builders
def api_key_field(
    description: str = "API key for authentication",
    **kwargs: TData,
) -> TData:
    """Create API key field definition."""
    return FlextAPIFieldCore.api_key_field(description=description, **kwargs)


def bearer_token_field(
    description: str = "Bearer token for authentication",
    **kwargs: TData,
) -> TData:
    """Create bearer token field definition."""
    return FlextAPIFieldCore.bearer_token_field(description=description, **kwargs)


def pipeline_config_field(
    description: str = "Pipeline configuration data",
    **kwargs: TData,
) -> TData:
    """Create pipeline configuration field definition."""
    return FlextAPIFieldCore.pipeline_config_field(description=description, **kwargs)


def plugin_config_field(
    description: str = "Plugin configuration data",
    **kwargs: TData,
) -> TData:
    """Create plugin configuration field definition."""
    return FlextAPIFieldCore.plugin_config_field(description=description, **kwargs)


def user_role_field(
    description: str = "User role for authorization",
    **kwargs: TData,
) -> TData:
    """Create user role field definition."""
    return FlextAPIFieldCore.user_role_field(description=description, **kwargs)


def endpoint_path_field(
    description: str = "API endpoint path",
    **kwargs: TData,
) -> TData:
    """Create endpoint path field definition."""
    return FlextAPIFieldCore.endpoint_path_field(description=description, **kwargs)


def http_method_field(description: str = "HTTP method", **kwargs: TData) -> TData:
    """Create HTTP method field definition."""
    return FlextAPIFieldCore.http_method_field(description=description, **kwargs)


def response_format_field(
    description: str = "Response format type",
    **kwargs: TData,
) -> TData:
    """Create response format field definition."""
    return FlextAPIFieldCore.response_format_field(description=description, **kwargs)
