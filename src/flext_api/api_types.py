"""FLEXT API types and field definitions."""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

import aiohttp.hdrs
from flext_core.fields import FlextFieldCore, FlextFields

from flext_api.typings import FlextTypes

# =============================================================================
# PROJECT TYPE VARIABLES
# =============================================================================

T_Response = TypeVar("T_Response")
T_Request = TypeVar("T_Request")
T_Payload = TypeVar("T_Payload")

# Legacy compatibility
TData = TypeVar("TData")

# =============================================================================
# API-SPECIFIC TYPE SYSTEM
# =============================================================================


class APITypes:
    """API-specific type system extending flext-core foundation."""

    # Import core types for convenience
    Core = FlextTypes.Core

    class HTTP:
        """HTTP and REST API specific types."""

        # HTTP method and endpoint types
        type Method = str  # GET, POST, PUT, DELETE, etc.
        type Endpoint = str  # /api/v1/resource
        type StatusCode = int  # 200, 404, 500, etc.
        type ContentType = str  # application/json, text/html

        # Request/Response types with generics
        class Request(Generic[T_Request]):
            """Generic HTTP request type."""

        class Response(Generic[T_Response]):
            """Generic HTTP response type."""

        # Header and query types
        type Headers = dict[str, str]
        type QueryParams = dict[str, str | list[str]]
        type PathParams = dict[str, str]

        # Authentication types
        type AuthToken = str
        type APIKey = str
        type BearerToken = str

    class Validation:
        """API validation and error types."""

        # Error response types
        type ErrorCode = str
        type ErrorMessage = str
        type ErrorDetails = FlextTypes.Core.JsonDict

        # Validation types
        type ValidationErrors = dict[str, list[str]]
        type FieldError = dict[str, str]

    class Serialization:
        """Data serialization types."""

        # JSON types
        type JSONData = FlextTypes.Core.JsonDict
        type JSONArray = list[object]
        type JSONString = str

        # Schema types
        type SchemaVersion = str
        type SchemaDefinition = FlextTypes.Core.JsonDict


# =============================================================================
# FIELD DEFINITIONS
# =============================================================================


class FlextAPIFieldCore:
    """Field factory for API-specific field definitions with validation patterns."""

    @classmethod
    def _create_auth_field(
        cls,
        field_type: str,
        description: str,
        min_length: int,
        max_length: int,
        pattern: str,
        **kwargs: TData,
    ) -> FlextTypes.Core.JsonDict:
        """Create authentication field with common properties.

        DRY principle: Eliminates duplication between API key and bearer token
        field creation by centralizing common authentication field properties.
        """
        return {
            "field_type": field_type,
            "description": description,
            "sensitive": True,
            "required": True,
            "min_length": min_length,
            "max_length": max_length,
            "pattern": pattern,
            **kwargs,
        }

    @classmethod
    def api_key_field(
        cls,
        description: str = "API key for authentication",
        **kwargs: TData,
    ) -> FlextTypes.Core.JsonDict:
        """Create API key field definition using DRY factory method."""
        return cls._create_auth_field(
            field_type="api_key",
            description=description,
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
    ) -> FlextTypes.Core.JsonDict:
        """Create bearer token field definition using DRY factory method."""
        return cls._create_auth_field(
            field_type="bearer_token",
            description=description,
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
    ) -> FlextTypes.Core.JsonDict:
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
    ) -> FlextTypes.Core.JsonDict:
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
    ) -> FlextTypes.Core.JsonDict:
        """Create user role field definition."""
        return {
            "field_type": "user_role",
            "description": description,
            "required": True,
            "data_type": "string",
            "allowed_values": ["REDACTED_LDAP_BIND_PASSWORD", "user", "readonly", "operator"],
            **kwargs,
        }

    @classmethod
    def endpoint_path_field(
        cls,
        description: str = "API endpoint path",
        **kwargs: TData,
    ) -> FlextTypes.Core.JsonDict:
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
    ) -> FlextTypes.Core.JsonDict:
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
    ) -> FlextTypes.Core.JsonDict:
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
    """Pre-defined field configurations for common API patterns."""

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
    USERNAME: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "username",
        "description": "User login name",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_]{3,50}$",
        "min_length": 3,
        "max_length": 50,
    }

    EMAIL: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "email",
        "description": "User email address",
        "required": True,
        "data_type": "string",
        "pattern": r"^[^@]+@[^@]+\.[^@]+$",
        "max_length": 255,
    }

    PASSWORD: ClassVar[FlextTypes.Core.JsonDict] = {
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
    PIPELINE_NAME: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "pipeline_name",
        "description": "Pipeline identifier name",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_-]{1,100}$",
        "min_length": 1,
        "max_length": 100,
    }

    PIPELINE_DESCRIPTION: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "pipeline_description",
        "description": "Pipeline description text",
        "required": False,
        "data_type": "string",
        "max_length": 500,
    }

    PIPELINE_TIMEOUT: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "pipeline_timeout",
        "description": "Pipeline execution timeout in seconds",
        "required": False,
        "data_type": "integer",
        "min_value": 1,
        "max_value": 3600,
        "default": 300,
    }

    # Plugin fields
    PLUGIN_ID: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "plugin_id",
        "description": "Plugin unique identifier",
        "required": True,
        "data_type": "string",
        "pattern": r"^[a-zA-Z0-9_-]+$",
        "min_length": 1,
        "max_length": 100,
    }

    PLUGIN_VERSION: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "plugin_version",
        "description": "Plugin version string",
        "required": True,
        "data_type": "string",
        "pattern": r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$",
        "max_length": 50,
    }

    PLUGIN_ENABLED: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "plugin_enabled",
        "description": "Plugin enabled status",
        "required": False,
        "data_type": "boolean",
        "default": True,
    }

    # System fields
    SYSTEM_STATUS: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "system_status",
        "description": "System health status",
        "required": True,
        "data_type": "string",
        "allowed_values": ["healthy", "degraded", "unhealthy", "maintenance"],
    }

    LOG_LEVEL: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "log_level",
        "description": "Logging level",
        "required": False,
        "data_type": "string",
        "allowed_values": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "default": "INFO",
    }

    # Request/Response fields
    REQUEST_ID: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "request_id",
        "description": "Unique request identifier",
        "required": True,
        "data_type": "string",
        "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    CORRELATION_ID: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "correlation_id",
        "description": "Request correlation identifier",
        "required": False,
        "data_type": "string",
        "pattern": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    }

    TIMESTAMP: ClassVar[FlextTypes.Core.JsonDict] = {
        "field_type": "timestamp",
        "description": "ISO 8601 timestamp",
        "required": True,
        "data_type": "string",
        "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{6})?Z?$",
    }


# =============================================================================
# CONVENIENCE FIELD FUNCTIONS
# =============================================================================


def api_key_field[TData](
    description: str = "API key for authentication",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create API key field definition."""
    return FlextAPIFieldCore.api_key_field(description=description, **kwargs)


def bearer_token_field[TData](
    description: str = "Bearer token for authentication",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create bearer token field definition."""
    return FlextAPIFieldCore.bearer_token_field(description=description, **kwargs)


def pipeline_config_field[TData](
    description: str = "Pipeline configuration data",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create pipeline configuration field definition."""
    return FlextAPIFieldCore.pipeline_config_field(description=description, **kwargs)


def plugin_config_field[TData](
    description: str = "Plugin configuration data",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create plugin configuration field definition."""
    return FlextAPIFieldCore.plugin_config_field(description=description, **kwargs)


def user_role_field[TData](
    description: str = "User role for authorization",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create user role field definition."""
    return FlextAPIFieldCore.user_role_field(description=description, **kwargs)


def endpoint_path_field[TData](
    description: str = "API endpoint path",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create endpoint path field definition."""
    return FlextAPIFieldCore.endpoint_path_field(description=description, **kwargs)


def http_method_field[TData](
    description: str = "HTTP method",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create HTTP method field definition."""
    return FlextAPIFieldCore.http_method_field(description=description, **kwargs)


def response_format_field[TData](
    description: str = "Response format type",
    **kwargs: TData,
) -> FlextTypes.Core.JsonDict:
    """Create response format field definition."""
    return FlextAPIFieldCore.response_format_field(description=description, **kwargs)


# =============================================================================
# COMPATIBILITY LAYER
# =============================================================================


class APITypesCompat:
    """Compatibility aliases for migration from old API type patterns."""

    # Legacy HTTP aliases
    HTTPMethod = APITypes.HTTP.Method
    HTTPEndpoint = APITypes.HTTP.Endpoint
    HTTPStatusCode = APITypes.HTTP.StatusCode
    HTTPHeaders = APITypes.HTTP.Headers

    # Legacy response aliases
    APIResponse = APITypes.HTTP.Response
    APIRequest = APITypes.HTTP.Request

    # Legacy validation aliases
    ValidationError = APITypes.Validation.ValidationErrors


# =============================================================================
# MIGRATION HELPERS
# =============================================================================


def get_api_types() -> FlextTypes.Core.JsonDict:
    """Get all API-specific type definitions.

    Returns:
        Dictionary of API type names mapped to their type definitions

    """
    return {
        "Method": APITypes.HTTP.Method,
        "Endpoint": APITypes.HTTP.Endpoint,
        "StatusCode": APITypes.HTTP.StatusCode,
        "Request": APITypes.HTTP.Request,
        "Response": APITypes.HTTP.Response,
        "Headers": APITypes.HTTP.Headers,
        "QueryParams": APITypes.HTTP.QueryParams,
        "ValidationErrors": APITypes.Validation.ValidationErrors,
        "JSONData": APITypes.Serialization.JSONData,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Type System
    "APITypes",
    "APITypesCompat",
    # Field System
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "FlextFieldCore",  # Re-export from flext_core
    "FlextFields",  # Re-export from flext_core
    # Type Variables
    "TData",  # Legacy compatibility
    "T_Payload",
    "T_Request",
    "T_Response",
    # Field Functions
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "get_api_types",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
]
