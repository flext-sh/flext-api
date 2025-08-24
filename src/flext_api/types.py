"""FLEXT API types and field definitions."""

from __future__ import annotations

from typing import ClassVar, Generic, TypeVar

import aiohttp.hdrs
from flext_core import FlextFieldCore, FlextFields

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
# MAIN FLEXT API TYPES CLASS - Inherits from FlextTypes
# =============================================================================


class FlextApiTypes(FlextTypes):
    """Main API types class inheriting from FlextTypes with API-specific extensions.

    This class follows the FLEXT pattern of having a single Flext[Area][Module] class
    that inherits from the equivalent FlextCore class and provides all functionality
    through internal method delegation.
    """

    # Inherit all FlextTypes functionality and extend with API-specific types

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
    # FIELD CORE FUNCTIONALITY - Internal methods for field definitions
    # =============================================================================

    class FieldCore:
        """Internal field factory for API-specific field definitions."""

        @staticmethod
        def create_auth_field(
            field_type: str,
            description: str,
            min_length: int,
            max_length: int,
            pattern: str,
            **kwargs: object,
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

        @staticmethod
        def create_api_key_field(
            description: str = "API key for authentication",
            **kwargs: object,
        ) -> FlextTypes.Core.JsonDict:
            """Create API key field definition using DRY factory method."""
            return FlextApiTypes.FieldCore.create_auth_field(
                field_type="api_key",
                description=description,
                min_length=32,
                max_length=128,
                pattern=r"^[A-Za-z0-9_-]+$",
                **kwargs,
            )

        @staticmethod
        def create_bearer_token_field(
            description: str = "Bearer token for authentication",
            **kwargs: object,
        ) -> FlextTypes.Core.JsonDict:
            """Create bearer token field definition using DRY factory method."""
            return FlextApiTypes.FieldCore.create_auth_field(
                field_type="bearer_token",
                description=description,
                min_length=50,
                max_length=2048,
                pattern=r"^[A-Za-z0-9._-]+$",
                **kwargs,
            )

        @staticmethod
        def create_pipeline_config_field(
            description: str = "Pipeline configuration data",
            **kwargs: object,
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

        @staticmethod
        def create_plugin_config_field(
            description: str = "Plugin configuration data",
            **kwargs: object,
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

        @staticmethod
        def create_user_role_field(
            description: str = "User role for authorization",
            **kwargs: object,
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

        @staticmethod
        def create_endpoint_path_field(
            description: str = "API endpoint path",
            **kwargs: object,
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

        @staticmethod
        def create_http_method_field(
            description: str = "HTTP method",
            **kwargs: object,
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

        @staticmethod
        def create_response_format_field(
            description: str = "Response format type",
            **kwargs: object,
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

    # =============================================================================
    # PREDEFINED FIELD CONFIGURATIONS - Internal field constants
    # =============================================================================

    class Fields:
        """Internal pre-defined field configurations for common API patterns."""

        # Authentication fields
        API_KEY = None  # Lazy-loaded
        BEARER_TOKEN = None  # Lazy-loaded

        # Configuration fields
        PIPELINE_CONFIG = None  # Lazy-loaded
        PLUGIN_CONFIG = None  # Lazy-loaded

        # Authorization fields
        USER_ROLE = None  # Lazy-loaded

        # API fields
        ENDPOINT_PATH = None  # Lazy-loaded
        HTTP_METHOD = None  # Lazy-loaded
        RESPONSE_FORMAT = None  # Lazy-loaded

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

        @classmethod
        def _ensure_lazy_loaded(cls) -> None:
            """Ensure lazy-loaded fields are initialized."""
            if cls.API_KEY is None:
                cls.API_KEY = FlextApiTypes.FieldCore.create_api_key_field()
            if cls.BEARER_TOKEN is None:
                cls.BEARER_TOKEN = FlextApiTypes.FieldCore.create_bearer_token_field()
            if cls.PIPELINE_CONFIG is None:
                cls.PIPELINE_CONFIG = FlextApiTypes.FieldCore.create_pipeline_config_field()
            if cls.PLUGIN_CONFIG is None:
                cls.PLUGIN_CONFIG = FlextApiTypes.FieldCore.create_plugin_config_field()
            if cls.USER_ROLE is None:
                cls.USER_ROLE = FlextApiTypes.FieldCore.create_user_role_field()
            if cls.ENDPOINT_PATH is None:
                cls.ENDPOINT_PATH = FlextApiTypes.FieldCore.create_endpoint_path_field()
            if cls.HTTP_METHOD is None:
                cls.HTTP_METHOD = FlextApiTypes.FieldCore.create_http_method_field()
            if cls.RESPONSE_FORMAT is None:
                cls.RESPONSE_FORMAT = FlextApiTypes.FieldCore.create_response_format_field()

    # =============================================================================
    # PUBLIC API METHODS - Single entry point for all functionality
    # =============================================================================

    @classmethod
    def get_api_types(cls) -> FlextTypes.Core.JsonDict:
        """Get all API-specific type definitions.

        Returns:
          Dictionary of API type names mapped to their type definitions

        """
        return {
            "Method": cls.HTTP.Method,
            "Endpoint": cls.HTTP.Endpoint,
            "StatusCode": cls.HTTP.StatusCode,
            "Request": cls.HTTP.Request,
            "Response": cls.HTTP.Response,
            "Headers": cls.HTTP.Headers,
            "QueryParams": cls.HTTP.QueryParams,
            "ValidationErrors": cls.Validation.ValidationErrors,
            "JSONData": cls.Serialization.JSONData,
        }

    @classmethod
    def get_field_definitions(cls) -> dict[str, FlextTypes.Core.JsonDict]:
        """Get all pre-defined field configurations.

        Returns:
          Dictionary of field names mapped to their configurations

        """
        cls.Fields._ensure_lazy_loaded()
        return {
            "API_KEY": cls.Fields.API_KEY,
            "BEARER_TOKEN": cls.Fields.BEARER_TOKEN,
            "PIPELINE_CONFIG": cls.Fields.PIPELINE_CONFIG,
            "PLUGIN_CONFIG": cls.Fields.PLUGIN_CONFIG,
            "USER_ROLE": cls.Fields.USER_ROLE,
            "ENDPOINT_PATH": cls.Fields.ENDPOINT_PATH,
            "HTTP_METHOD": cls.Fields.HTTP_METHOD,
            "RESPONSE_FORMAT": cls.Fields.RESPONSE_FORMAT,
            "USERNAME": cls.Fields.USERNAME,
            "EMAIL": cls.Fields.EMAIL,
            "PASSWORD": cls.Fields.PASSWORD,
            "PIPELINE_NAME": cls.Fields.PIPELINE_NAME,
            "PIPELINE_DESCRIPTION": cls.Fields.PIPELINE_DESCRIPTION,
            "PIPELINE_TIMEOUT": cls.Fields.PIPELINE_TIMEOUT,
            "PLUGIN_ID": cls.Fields.PLUGIN_ID,
            "PLUGIN_VERSION": cls.Fields.PLUGIN_VERSION,
            "PLUGIN_ENABLED": cls.Fields.PLUGIN_ENABLED,
            "SYSTEM_STATUS": cls.Fields.SYSTEM_STATUS,
            "LOG_LEVEL": cls.Fields.LOG_LEVEL,
            "REQUEST_ID": cls.Fields.REQUEST_ID,
            "CORRELATION_ID": cls.Fields.CORRELATION_ID,
            "TIMESTAMP": cls.Fields.TIMESTAMP,
        }

    @classmethod
    def create_api_key_field(
        cls,
        description: str = "API key for authentication",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create API key field definition."""
        return cls.FieldCore.create_api_key_field(description=description, **kwargs)

    @classmethod
    def create_bearer_token_field(
        cls,
        description: str = "Bearer token for authentication",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create bearer token field definition."""
        return cls.FieldCore.create_bearer_token_field(description=description, **kwargs)

    @classmethod
    def create_pipeline_config_field(
        cls,
        description: str = "Pipeline configuration data",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create pipeline configuration field definition."""
        return cls.FieldCore.create_pipeline_config_field(description=description, **kwargs)

    @classmethod
    def create_plugin_config_field(
        cls,
        description: str = "Plugin configuration data",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create plugin configuration field definition."""
        return cls.FieldCore.create_plugin_config_field(description=description, **kwargs)

    @classmethod
    def create_user_role_field(
        cls,
        description: str = "User role for authorization",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create user role field definition."""
        return cls.FieldCore.create_user_role_field(description=description, **kwargs)

    @classmethod
    def create_endpoint_path_field(
        cls,
        description: str = "API endpoint path",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create endpoint path field definition."""
        return cls.FieldCore.create_endpoint_path_field(description=description, **kwargs)

    @classmethod
    def create_http_method_field(
        cls,
        description: str = "HTTP method",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create HTTP method field definition."""
        return cls.FieldCore.create_http_method_field(description=description, **kwargs)

    @classmethod
    def create_response_format_field(
        cls,
        description: str = "Response format type",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create response format field definition."""
        return cls.FieldCore.create_response_format_field(description=description, **kwargs)


# =============================================================================
# LEGACY ALIASES - Redirect to FlextApiTypes
# =============================================================================

# Main alias for backward compatibility
APITypes = FlextApiTypes

# =============================================================================
# LEGACY FIELD CLASSES - Redirect to FlextApiTypes internal methods
# =============================================================================


class FlextAPIFieldCore:
    """Legacy field factory - redirects to FlextApiTypes.FieldCore."""

    @classmethod
    def _create_auth_field(
        cls,
        field_type: str,
        description: str,
        min_length: int,
        max_length: int,
        pattern: str,
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create authentication field with common properties."""
        return FlextApiTypes.FieldCore.create_auth_field(
            field_type, description, min_length, max_length, pattern, **kwargs
        )

    @classmethod
    def api_key_field(
        cls,
        description: str = "API key for authentication",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create API key field definition."""
        return FlextApiTypes.create_api_key_field(description=description, **kwargs)

    @classmethod
    def bearer_token_field(
        cls,
        description: str = "Bearer token for authentication",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create bearer token field definition."""
        return FlextApiTypes.create_bearer_token_field(description=description, **kwargs)

    @classmethod
    def pipeline_config_field(
        cls,
        description: str = "Pipeline configuration data",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create pipeline configuration field definition."""
        return FlextApiTypes.create_pipeline_config_field(description=description, **kwargs)

    @classmethod
    def plugin_config_field(
        cls,
        description: str = "Plugin configuration data",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create plugin configuration field definition."""
        return FlextApiTypes.create_plugin_config_field(description=description, **kwargs)

    @classmethod
    def user_role_field(
        cls,
        description: str = "User role for authorization",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create user role field definition."""
        return FlextApiTypes.create_user_role_field(description=description, **kwargs)

    @classmethod
    def endpoint_path_field(
        cls,
        description: str = "API endpoint path",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create endpoint path field definition."""
        return FlextApiTypes.create_endpoint_path_field(description=description, **kwargs)

    @classmethod
    def http_method_field(
        cls,
        description: str = "HTTP method",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create HTTP method field definition."""
        return FlextApiTypes.create_http_method_field(description=description, **kwargs)

    @classmethod
    def response_format_field(
        cls,
        description: str = "Response format type",
        **kwargs: object,
    ) -> FlextTypes.Core.JsonDict:
        """Create response format field definition."""
        return FlextApiTypes.create_response_format_field(description=description, **kwargs)


class FlextAPIFields:
    """Legacy pre-defined field configurations - redirects to FlextApiTypes.Fields."""

    # Initialize with lazy loading
    _initialized = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure fields are initialized with lazy loading."""
        if not cls._initialized:
            FlextApiTypes.Fields._ensure_lazy_loaded()
            # Set class attributes dynamically
            cls.API_KEY = FlextApiTypes.Fields.API_KEY
            cls.BEARER_TOKEN = FlextApiTypes.Fields.BEARER_TOKEN
            cls.PIPELINE_CONFIG = FlextApiTypes.Fields.PIPELINE_CONFIG
            cls.PLUGIN_CONFIG = FlextApiTypes.Fields.PLUGIN_CONFIG
            cls.USER_ROLE = FlextApiTypes.Fields.USER_ROLE
            cls.ENDPOINT_PATH = FlextApiTypes.Fields.ENDPOINT_PATH
            cls.HTTP_METHOD = FlextApiTypes.Fields.HTTP_METHOD
            cls.RESPONSE_FORMAT = FlextApiTypes.Fields.RESPONSE_FORMAT
            cls._initialized = True

    def __init_subclass__(cls) -> None:
        """Initialize when class is accessed."""
        super().__init_subclass__()
        cls._ensure_initialized()

    def __class_getitem__(cls, item: str) -> FlextTypes.Core.JsonDict:
        """Get field by name with lazy loading."""
        cls._ensure_initialized()
        return getattr(cls, item)

    # Direct aliases for static fields that don't need lazy loading
    USERNAME: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.USERNAME
    EMAIL: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.EMAIL
    PASSWORD: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PASSWORD
    PIPELINE_NAME: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PIPELINE_NAME
    PIPELINE_DESCRIPTION: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PIPELINE_DESCRIPTION
    PIPELINE_TIMEOUT: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PIPELINE_TIMEOUT
    PLUGIN_ID: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PLUGIN_ID
    PLUGIN_VERSION: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PLUGIN_VERSION
    PLUGIN_ENABLED: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.PLUGIN_ENABLED
    SYSTEM_STATUS: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.SYSTEM_STATUS
    LOG_LEVEL: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.LOG_LEVEL
    REQUEST_ID: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.REQUEST_ID
    CORRELATION_ID: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.CORRELATION_ID
    TIMESTAMP: ClassVar[FlextTypes.Core.JsonDict] = FlextApiTypes.Fields.TIMESTAMP


# =============================================================================
# CONVENIENCE FIELD FUNCTIONS - Redirect to FlextApiTypes
# =============================================================================


def api_key_field(
    description: str = "API key for authentication",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create API key field definition."""
    return FlextApiTypes.create_api_key_field(description=description, **kwargs)


def bearer_token_field(
    description: str = "Bearer token for authentication",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create bearer token field definition."""
    return FlextApiTypes.create_bearer_token_field(description=description, **kwargs)


def pipeline_config_field(
    description: str = "Pipeline configuration data",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create pipeline configuration field definition."""
    return FlextApiTypes.create_pipeline_config_field(description=description, **kwargs)


def plugin_config_field(
    description: str = "Plugin configuration data",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create plugin configuration field definition."""
    return FlextApiTypes.create_plugin_config_field(description=description, **kwargs)


def user_role_field(
    description: str = "User role for authorization",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create user role field definition."""
    return FlextApiTypes.create_user_role_field(description=description, **kwargs)


def endpoint_path_field(
    description: str = "API endpoint path",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create endpoint path field definition."""
    return FlextApiTypes.create_endpoint_path_field(description=description, **kwargs)


def http_method_field(
    description: str = "HTTP method",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create HTTP method field definition."""
    return FlextApiTypes.create_http_method_field(description=description, **kwargs)


def response_format_field(
    description: str = "Response format type",
    **kwargs: object,
) -> FlextTypes.Core.JsonDict:
    """Create response format field definition."""
    return FlextApiTypes.create_response_format_field(description=description, **kwargs)


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


# Legacy function - now delegates to FlextApiTypes
def get_api_types() -> FlextTypes.Core.JsonDict:
    """Get all API-specific type definitions.

    Returns:
      Dictionary of API type names mapped to their type definitions

    """
    return FlextApiTypes.get_api_types()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Main Type System (Primary API)
    "FlextApiTypes",
    # Legacy Type System Aliases
    "APITypes",
    "APITypesCompat",
    # Legacy Field System (for backward compatibility)
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "FlextFieldCore",  # Re-export from flext_core
    "FlextFields",  # Re-export from flext_core
    # Type Variables
    "TData",  # Legacy compatibility
    "T_Payload",
    "T_Request",
    "T_Response",
    # Field Functions (legacy convenience functions)
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
