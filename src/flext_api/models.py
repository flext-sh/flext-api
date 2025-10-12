"""FLEXT API Models - Data models only (constants/tipos vêm de constants & typings).

Remove duplicações: usar diretamente `FlextApiConstants` e `FlextApiTypes` em vez de
classes internas de constantes/field/endpoints/status. Este módulo agora expõe
somente modelos (Request/Response/Config/Query/Storage/URL) seguindo padrão flext-core.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from typing import Self
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_serializer,
    field_validator,
    model_validator,
)

from flext_api.constants import FlextApiConstants
from flext_api.typings import FlextApiTypes


class FlextApiModels:
    """Flext API models - Pydantic models only.

    Contains all API-specific Pydantic models as nested classes.
    Uses FlextCore patterns and types.
    """

    # Simple API-specific models extending FlextCore.Models base classes
    class HttpRequest(BaseModel):
        """HTTP client request model.

        Core HTTP request fields with validation and computed properties.
        """

        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            str_strip_whitespace=True,
        )

        url: str = Field(..., description="Request URL")
        method: str = Field(..., description="HTTP method")
        headers: dict[str, str] | None = Field(
            default_factory=dict, description="Request headers"
        )
        body: str | bytes | dict | None = Field(
            default=None, description="Request body"
        )
        timeout: float | None = Field(
            default=None, description="Request timeout in seconds"
        )

        tracking_id: str | None = Field(
            default=None, description="Request tracking ID for logging"
        )

    class HttpResponse(BaseModel):
        """HTTP response model."""
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
        )

        status_code: int = Field(..., description="HTTP status code")
        headers: dict[str, str] = Field(default_factory=dict, description="Response headers")
        body: str | bytes | dict | None = Field(default=None, description="Response body")

            return self

        @field_serializer("body")
        def serialize_response_body(
            self, value: str | dict[str, FlextApiTypes.JsonValue] | None
        ) -> str | dict | None:
            """Serialize response body for storage/transmission - CLIENT SPECIFIC."""
            if value is None:
                return None
            if isinstance(value, dict):
                # Ensure response dict is JSON serializable
                try:
                    json.dumps(value)
                    return value
                except (TypeError, ValueError):
                    return {"serialized_content": str(value)}
            return str(value)

    class ClientConfig(FlextCore.Models.Value):
        """Streamlined client configuration extending FlextCore.Models.Value."""

        # Essential configuration only
        base_url: str = Field(
            default=FlextApiConstants.DEFAULT_BASE_URL, description="Base URL"
        )
        timeout: float = Field(
            default=FlextApiConstants.DEFAULT_TIMEOUT,
            gt=1,
            le=300,
            description="Request timeout",
        )
        max_retries: int = Field(
            default=FlextApiConstants.DEFAULT_MAX_RETRIES,
            ge=0,
            le=FlextApiConstants.MAX_RETRIES,
            description="Maximum retries",
        )
        headers: FlextCore.Types.StringDict = Field(
            default_factory=dict, description="Default headers"
        )

        # Authentication - consolidated
        auth_token: str | None = Field(default=None, description="Authentication token")
        api_key: str | None = Field(default=None, description="API key")

        @model_validator(mode="after")
        def validate_client_config(self) -> Self:
            """Cross-field validation for client configuration."""
            # Note: Both auth_token and api_key can be specified - auth_token takes priority
            # This allows flexible authentication configuration with fallback options

            # Validate retry configuration
            if self.max_retries > FlextApiConstants.MAX_RETRIES:
                msg = f"Max retries should not exceed {FlextApiConstants.MAX_RETRIES}"
                raise ValueError(msg)

            return self

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL using centralized FlextCore.Models validation."""
            validation_result = FlextCore.Models.create_validated_http_url(v.strip())
            if validation_result.is_failure:
                error_msg = validation_result.error or "Invalid base URL"
                if (
                    "URL must start with http:// or https://" in error_msg
                    or "URL cannot be empty" in error_msg
                    or "URL must have a valid hostname" in error_msg
                ):
                    error_msg = "URL must be a non-empty string"
                msg = f"Invalid base URL: {error_msg}"
                raise ValueError(msg)

            url_obj = validation_result.unwrap()
            return str(url_obj.url) if hasattr(url_obj, "url") else str(url_obj)

        @field_serializer("auth_token", "api_key")
        def serialize_auth_fields(self, value: str | None) -> str | None:
            """Serialize authentication fields securely."""
            if value is None:
                return None
            # Mask sensitive authentication data for logging/serialization
            if len(value) <= FlextApiConstants.MASK_AUTH_THRESHOLD:
                return "***MASKED***"
            return f"{value[:4]}***{value[-4:]}"

        def get_auth_header(self) -> FlextCore.Types.StringDict:
            """Get authentication header if configured."""
            if self.auth_token:
                return {
                    FlextApiConstants.Http.AUTHORIZATION_HEADER: f"Bearer {self.auth_token}"
                }
            if self.api_key:
                return {
                    FlextApiConstants.Http.AUTHORIZATION_HEADER: f"Bearer {self.api_key}"
                }
            return {}

        def get_default_headers(self) -> FlextCore.Types.StringDict:
            """Get all default headers including auth."""
            headers = {
                FlextApiConstants.USER_AGENT_HEADER: FlextApiConstants.DEFAULT_USER_AGENT,
                **self.headers,
            }
            headers.update(self.get_auth_header())
            return headers

    class HttpQuery(FlextCore.Models.Query):
        """HTTP query parameters model extending FlextCore.Models.Query."""

        # Core fields using direct Pydantic 2 field names
        filter_conditions: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Filter conditions"
        )
        sort_fields: FlextCore.Types.StringList = Field(
            default_factory=list, description="Sort fields"
        )
        page_number: int = Field(
            default=FlextApiConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextApiConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Page number",
        )
        page_size_value: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )

        @model_validator(mode="after")
        def validate_query_params(self) -> Self:
            """Cross-field validation for query parameters."""
            # Validate sort fields format
            for field in self.sort_fields:
                if not field.strip():
                    msg = "Sort field names cannot be empty"
                    raise ValueError(msg)

            # Validate pagination consistency
            if self.page_size_value > FlextApiConstants.MAX_PAGE_SIZE_PERFORMANCE:
                msg = "Page size too large for performance"
                raise ValueError(msg)

            return self

        def add_filter(
            self, key: str, value: FlextApiTypes.JsonValue
        ) -> FlextCore.Result[None]:
            """Add a filter to the query."""
            if not key or not key.strip():
                return FlextCore.Result[None].fail("Filter key cannot be empty")
            self.filter_conditions[key.strip()] = value
            return FlextCore.Result[None].ok(None)

        def to_query_params(self) -> dict[str, FlextApiTypes.JsonValue]:
            """Convert to query parameters dict with Python 3.13+ computational optimization."""
            # Python 3.13+ optimized dict merge with walrus operator
            # Use direct field names (no aliases)
            params = self.model_dump(exclude_none=True)
            # Computational optimization: direct merge avoiding update() call
            return {
                **params,
                **(
                    filter_conditions
                    if (filter_conditions := params.pop("filter_conditions", {}))
                    else {}
                ),
            }

    class PaginationConfig(FlextCore.Models.Value):
        """Pagination configuration extending FlextCore.Models.Value."""

        page_size: int = Field(
            default=FlextApiConstants.DEFAULT_PAGE_SIZE,
            ge=FlextApiConstants.MIN_PAGE_SIZE,
            le=FlextApiConstants.MAX_PAGE_SIZE,
            description="Page size",
        )
        current_page: int = Field(
            default=FlextApiConstants.Performance.DEFAULT_PAGE_NUMBER,
            ge=FlextApiConstants.Performance.DEFAULT_PAGE_NUMBER,
            description="Current page",
        )
        max_pages: int | None = Field(default=None, ge=1, description="Maximum pages")
        total: int = Field(default=0, ge=0, description="Total items")

        @model_validator(mode="after")
        def validate_pagination(self) -> Self:
            """Cross-field validation for pagination configuration."""
            if self.max_pages is not None and self.current_page > self.max_pages:
                msg = "Current page cannot exceed max pages"
                raise ValueError(msg)

            if self.total > 0 and self.page_size > 0:
                calculated_max_pages = (
                    self.total + self.page_size - 1
                ) // self.page_size
                if self.current_page > calculated_max_pages:
                    msg = "Current page exceeds pages based on total items"
                    raise ValueError(msg)

            return self

    class StorageConfig(FlextCore.Models.Value):
        """Storage configuration extending FlextCore.Models.Value."""

        backend: str = Field(default="memory", description="Storage backend")
        namespace: str = Field(default="flext_api", description="Storage namespace")
        max_size: int | None = Field(default=None, description="Maximum storage size")
        default_ttl: int | None = Field(default=None, description="Default TTL")

        @model_validator(mode="after")
        def validate_storage_config(self) -> Self:
            """Cross-field validation for storage configuration."""
            if self.max_size is not None and self.max_size <= 0:
                msg = "Max size must be positive"
                raise ValueError(msg)

            if self.default_ttl is not None and self.default_ttl <= 0:
                msg = "TTL must be positive"
                raise ValueError(msg)

            return self

    class ApiRequest(FlextCore.Models.Command):
        """API request model extending FlextCore.Models.Command."""

        url: str = Field(description="Request URL")
        method: str = Field(
            default=FlextApiConstants.Http.Method.GET, description="HTTP method"
        )
        headers: FlextCore.Types.StringDict = Field(
            default_factory=dict, description="Request headers"
        )
        body: str | dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Request body"
        )

        @model_validator(mode="after")
        def validate_api_request(self) -> Self:
            """Cross-field validation for API requests."""
            # Validate method-body consistency
            methods_without_body = {"GET", "HEAD", "DELETE"}
            if self.method in methods_without_body and self.body is not None:
                error_msg = f"HTTP {self.method} requests should not have a body"
                raise ValueError(error_msg)

            return self

    class ApiResponse(FlextCore.Models.Entity):
        """API response model extending FlextCore.Models.Entity."""

        status_code: int = Field(
            ge=FlextApiConstants.Http.HTTP_STATUS_MIN,
            le=FlextApiConstants.Http.HTTP_STATUS_MAX,
            description="HTTP status code",
        )
        body: str | dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Response body"
        )
        headers: FlextCore.Types.StringDict = Field(
            default_factory=dict, description="Response headers"
        )
        domain_events: FlextCore.Types.List = Field(
            default_factory=list, description="Domain events"
        )

        @model_validator(mode="after")
        def validate_api_response(self) -> Self:
            """Cross-field validation for API responses."""
            # Validate status code and body consistency
            if (
                self.status_code == FlextApiConstants.Http.HTTP_NO_CONTENT and self.body
            ):  # No Content
                error_msg = "HTTP 204 responses should not have a body"
                raise ValueError(error_msg)

            return self

    class UrlModel(FlextCore.Models.Value):
        """URL model for parsing and validation extending FlextCore.Models.Value."""

        raw_url: str = Field(min_length=1, description="Raw URL")
        scheme: str | None = Field(default=None, description="URL scheme")
        host: str | None = Field(default=None, description="URL host")
        port: int | None = Field(default=None, description="URL port")
        path: str | None = Field(default=None, description="URL path")
        query: str | None = Field(default=None, description="URL query")
        fragment: str | None = Field(default=None, description="URL fragment")

        @model_validator(mode="after")
        def validate_url_components(self) -> Self:
            """Cross-field validation for URL components."""
            if self.port is not None and (
                self.port < FlextApiConstants.MIN_PORT
                or self.port > FlextApiConstants.MAX_PORT
            ):
                msg = f"Port must be between {FlextApiConstants.MIN_PORT} and {FlextApiConstants.MAX_PORT}"
                raise ValueError(msg)

            if self.scheme and self.scheme not in {"http", "https", "ftp", "ftps"}:
                msg = "Unsupported URL scheme"
                raise ValueError(msg)

            return self

        def validate_business_rules(self) -> FlextCore.Result[None]:
            """Validate URL business rules."""
            if not self.raw_url:
                return FlextCore.Result[None].fail("URL cannot be empty")
            return FlextCore.Result[None].ok(None)

    class Builder:
        """Response builder for API responses."""

        def create(
            self,
            response_type: str = "success",
            **kwargs: FlextApiTypes.JsonValue,
        ) -> dict[str, FlextApiTypes.JsonValue]:
            """Create response using Python 3.13+ pattern matching optimization."""
            # Python 3.13+ match-case for computational efficiency
            match response_type:
                case "error":
                    # Direct return avoiding method call overhead
                    return {
                        "status": "error",
                        "error": {
                            "code": kwargs.get("code", "error"),
                            "message": kwargs.get("message", "Error occurred"),
                        },
                        "timestamp": FlextCore.Utilities.Generators.generate_iso_timestamp(),
                        "request_id": FlextCore.Utilities.Generators.generate_entity_id(),
                    }
                case _:
                    # Direct return for success case
                    return {
                        "status": "success",
                        "data": kwargs.get("data"),
                        "message": kwargs.get("message", ""),
                        "timestamp": FlextCore.Utilities.Generators.generate_iso_timestamp(),
                        "request_id": FlextCore.Utilities.Generators.generate_entity_id(),
                    }

        @staticmethod
        def success(
            *, data: FlextApiTypes.JsonValue = None, message: str = ""
        ) -> dict[str, FlextApiTypes.JsonValue]:
            """Build success response using flext-core generators."""
            return {
                "status": "success",
                "data": data,
                "message": message,
                "timestamp": FlextCore.Utilities.Generators.generate_iso_timestamp(),
                "request_id": FlextCore.Utilities.Generators.generate_entity_id(),
            }

        @staticmethod
        def error(
            message: str, code: str = "error"
        ) -> dict[str, FlextApiTypes.JsonValue]:
            """Build error response using flext-core generators."""
            return {
                "status": "error",
                "error": {"code": code, "message": message},
                "timestamp": FlextCore.Utilities.Generators.generate_iso_timestamp(),
                "request_id": FlextCore.Utilities.Generators.generate_entity_id(),
            }

    class AppConfig(FlextCore.Models.Value):
        """FastAPI application configuration model extending FlextCore.Models.Value."""

        title: str = Field(min_length=1, description="Application title")
        app_version: str = Field(min_length=1, description="Application version")
        description: str = Field(
            default="FlextAPI Application", description="Application description"
        )
        docs_url: str = Field(default="/docs", description="Swagger docs URL")
        redoc_url: str = Field(default="/redoc", description="ReDoc URL")
        openapi_url: str = Field(
            default="/openapi.json", description="OpenAPI schema URL"
        )

        @model_validator(mode="after")
        def validate_app_config(self) -> Self:
            """Cross-field validation for app configuration."""
            # Validate URL paths start with /
            if self.docs_url and not self.docs_url.startswith("/"):
                msg = "docs_url must start with /"
                raise ValueError(msg)
            if self.redoc_url and not self.redoc_url.startswith("/"):
                msg = "redoc_url must start with /"
                raise ValueError(msg)
            if self.openapi_url and not self.openapi_url.startswith("/"):
                msg = "openapi_url must start with /"
                raise ValueError(msg)

            return self

        @field_validator("title", "app_version")
        @classmethod
        def validate_required_fields(cls, v: str) -> str:
            """Validate required string fields."""
            if not v or not v.strip():
                error_message = "Field cannot be empty"
                raise ValueError(error_message)
            return v.strip()

    # Phase 3: WebSocket & SSE Models

    class WebSocketMessage(FlextCore.Models.Value):
        """WebSocket message model."""

        message: str | bytes = Field(description="Message content")
        message_type: str = Field(
            default="text", description="Message type (text or binary)"
        )
        timestamp: str = Field(description="Message timestamp")
        event_id: str | None = Field(default=None, description="Optional event ID")

        @field_validator("message_type")
        @classmethod
        def validate_message_type(cls, v: str) -> str:
            """Validate message type."""
            if v.lower() not in {"text", "binary"}:
                msg = "Message type must be 'text' or 'binary'"
                raise ValueError(msg)
            return v.lower()

    class WebSocketConnection(FlextCore.Models.Entity):
        """WebSocket connection model."""

        url: str = Field(description="WebSocket URL (ws:// or wss://)")
        state: str = Field(default="connecting", description="Connection state")
        headers: FlextCore.Types.StringDict = Field(
            default_factory=dict, description="Connection headers"
        )
        subprotocols: FlextCore.Types.StringList = Field(
            default_factory=list, description="WebSocket subprotocols"
        )
        ping_interval: float = Field(
            default=20.0, ge=0.0, description="Ping interval in seconds"
        )
        connected_at: str | None = Field(
            default=None, description="Connection timestamp"
        )
        last_ping_at: str | None = Field(
            default=None, description="Last ping timestamp"
        )
        messages_sent: int = Field(
            default=0, ge=0, description="Number of messages sent"
        )
        messages_received: int = Field(
            default=0, ge=0, description="Number of messages received"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate connection state."""
            valid_states = {
                "connecting",
                "connected",
                "disconnecting",
                "disconnected",
                "error",
            }
            if v.lower() not in valid_states:
                msg = f"Connection state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @field_validator("url")
        @classmethod
        def validate_url(cls, v: str) -> str:
            """Validate WebSocket URL."""
            if not v.startswith(("ws://", "wss://")):
                msg = "WebSocket URL must start with ws:// or wss://"
                raise ValueError(msg)
            return v

        @computed_field
        @property
        def is_connected(self) -> bool:
            """Check if connection is active."""
            return self.state == "connected"

        @computed_field
        @property
        def is_secure(self) -> bool:
            """Check if connection is secure (wss://)."""
            return self.url.startswith("wss://")

    class SSEEvent(FlextCore.Models.Value):
        """Server-Sent Events event model."""

        event_type: str = Field(default="message", description="Event type")
        data: str = Field(description="Event data")
        event_id: str | None = Field(default=None, description="Event ID for replay")
        retry: int | None = Field(
            default=None, ge=0, description="Retry timeout in milliseconds"
        )
        timestamp: str = Field(description="Event timestamp")

        @computed_field
        @property
        def has_id(self) -> bool:
            """Check if event has ID."""
            return self.event_id is not None and len(self.event_id) > 0

        @computed_field
        @property
        def data_length(self) -> int:
            """Get data length."""
            return len(self.data)

    class SSEConnection(FlextCore.Models.Entity):
        """Server-Sent Events connection model."""

        url: str = Field(description="SSE endpoint URL")
        state: str = Field(default="connecting", description="Connection state")
        headers: FlextCore.Types.StringDict = Field(
            default_factory=dict, description="Connection headers"
        )
        last_event_id: str = Field(default="", description="Last received event ID")
        retry_timeout: int = Field(
            default=3000, ge=0, description="Retry timeout in milliseconds"
        )
        connected_at: str | None = Field(
            default=None, description="Connection timestamp"
        )
        events_received: int = Field(
            default=0, ge=0, description="Number of events received"
        )
        reconnect_count: int = Field(
            default=0, ge=0, description="Number of reconnections"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate connection state."""
            valid_states = {
                "connecting",
                "connected",
                "disconnecting",
                "disconnected",
                "error",
            }
            if v.lower() not in valid_states:
                msg = f"Connection state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @computed_field
        @property
        def is_connected(self) -> bool:
            """Check if connection is active."""
            return self.state == "connected"

        @computed_field
        @property
        def has_last_event_id(self) -> bool:
            """Check if has last event ID."""
            return len(self.last_event_id) > 0

        @computed_field
        @property
        def retry_timeout_seconds(self) -> float:
            """Get retry timeout in seconds."""
            return self.retry_timeout / 1000.0

    # Phase 4: GraphQL Models

    class GraphQLQuery(FlextCore.Models.Command):
        """GraphQL query model."""

        query: str = Field(description="GraphQL query string")
        variables: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Query variables"
        )
        operation_name: str | None = Field(default=None, description="Operation name")
        fragments: FlextCore.Types.StringList = Field(
            default_factory=list, description="GraphQL fragments"
        )

        @computed_field
        @property
        def has_variables(self) -> bool:
            """Check if query has variables."""
            return len(self.variables) > 0

        @computed_field
        @property
        def has_fragments(self) -> bool:
            """Check if query has fragments."""
            return len(self.fragments) > 0

        @computed_field
        @property
        def query_length(self) -> int:
            """Get query string length."""
            return len(self.query)

    class GraphQLResponse(FlextCore.Models.Entity):
        """GraphQL response model."""

        data: dict[str, FlextApiTypes.JsonValue] | None = Field(
            default=None, description="Response data"
        )
        errors: list[dict[str, FlextApiTypes.JsonValue]] = Field(
            default_factory=list, description="GraphQL errors"
        )
        extensions: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Response extensions"
        )

        @computed_field
        @property
        def has_errors(self) -> bool:
            """Check if response has errors."""
            return len(self.errors) > 0

        @computed_field
        @property
        def has_data(self) -> bool:
            """Check if response has data."""
            return self.data is not None

        @computed_field
        @property
        def is_success(self) -> bool:
            """Check if response is successful."""
            return self.has_data and not self.has_errors

        @computed_field
        @property
        def error_count(self) -> int:
            """Get error count."""
            return len(self.errors)

    class GraphQLSchema(FlextCore.Models.Value):
        """GraphQL schema model."""

        schema_string: str = Field(description="GraphQL schema SDL string")
        types: FlextCore.Types.StringList = Field(
            default_factory=list, description="Schema types"
        )
        queries: FlextCore.Types.StringList = Field(
            default_factory=list, description="Available queries"
        )
        mutations: FlextCore.Types.StringList = Field(
            default_factory=list, description="Available mutations"
        )
        subscriptions: FlextCore.Types.StringList = Field(
            default_factory=list, description="Available subscriptions"
        )
        directives: FlextCore.Types.StringList = Field(
            default_factory=list, description="Schema directives"
        )

        @computed_field
        @property
        def has_queries(self) -> bool:
            """Check if schema has queries."""
            return len(self.queries) > 0

        @computed_field
        @property
        def has_mutations(self) -> bool:
            """Check if schema has mutations."""
            return len(self.mutations) > 0

        @computed_field
        @property
        def has_subscriptions(self) -> bool:
            """Check if schema has subscriptions."""
            return len(self.subscriptions) > 0

        @computed_field
        @property
        def operation_count(self) -> int:
            """Get total operation count."""
            return len(self.queries) + len(self.mutations) + len(self.subscriptions)

    class GraphQLSubscription(FlextCore.Models.Entity):
        """GraphQL subscription model."""

        subscription: str = Field(description="GraphQL subscription string")
        variables: dict[str, FlextApiTypes.JsonValue] = Field(
            default_factory=dict, description="Subscription variables"
        )
        operation_name: str | None = Field(default=None, description="Operation name")
        state: str = Field(default="pending", description="Subscription state")
        events_received: int = Field(
            default=0, ge=0, description="Number of events received"
        )
        started_at: str | None = Field(
            default=None, description="Subscription start time"
        )

        @field_validator("state")
        @classmethod
        def validate_state(cls, v: str) -> str:
            """Validate subscription state."""
            valid_states = {"pending", "active", "completed", "error", "cancelled"}
            if v.lower() not in valid_states:
                msg = f"Subscription state must be one of: {', '.join(valid_states)}"
                raise ValueError(msg)
            return v.lower()

        @computed_field
        @property
        def is_active(self) -> bool:
            """Check if subscription is active."""
            return self.state == "active"

        @computed_field
        @property
        def has_variables(self) -> bool:
            """Check if subscription has variables."""
            return len(self.variables) > 0

    # =========================================================================
    # UTILITY METHODS - Direct access following FLEXT standards
    # =========================================================================

    @classmethod
    def create_validated_http_url(cls, url: str) -> FlextCore.Result[str]:
        """Create and validate an HTTP URL.

        Args:
            url: URL string to validate and create

        Returns:
            FlextCore.Result containing validated URL object or error

        """
        try:
            if not url or not isinstance(url, str):
                return FlextCore.Result[str].fail("URL must be a non-empty string")

            url = url.strip()
            if not url:
                return FlextCore.Result[str].fail("URL cannot be empty")

            # Parse URL
            parsed = urlparse(url)

            # Validate scheme
            if not parsed.scheme:
                # Default to https for relative URLs
                url = f"https://{url}"
                parsed = urlparse(url)
            elif parsed.scheme not in {"http", "https"}:
                return FlextCore.Result[str].fail(
                    f"URL scheme must be http or https, got: {parsed.scheme}"
                )

            # Validate hostname
            if not parsed.hostname:
                return FlextCore.Result[str].fail("URL must have a valid hostname")

            # Check hostname length
            if len(parsed.hostname) > FlextApiConstants.MAX_HOSTNAME_LENGTH:
                return FlextCore.Result[str].fail("Hostname too long")

            # Validate port if specified
            if parsed.port is not None and not (
                FlextApiConstants.MIN_PORT <= parsed.port <= FlextApiConstants.MAX_PORT
            ):
                return FlextCore.Result[str].fail("Invalid port number")

            return FlextCore.Result[str].ok(parsed)

        except Exception as e:
            return FlextCore.Result[str].fail(f"URL validation failed: {e}")

    # =========================================================================
    # CQRS COMMAND AND EVENT MODELS - For handlers.py
    # =========================================================================

    # Command Models (extending FlextCore.Models.Command)
    class CreateResourceCommand(FlextCore.Models.Command):
        """Command to create a resource."""

        resource_type: str
        data: FlextCore.Types.Dict
        metadata: FlextCore.Types.Dict | None = None

    class UpdateResourceCommand(FlextCore.Models.Command):
        """Command to update a resource."""

        resource_id: str
        resource_type: str
        data: FlextCore.Types.Dict
        metadata: FlextCore.Types.Dict | None = None

    class DeleteResourceCommand(FlextCore.Models.Command):
        """Command to delete a resource."""

        resource_id: str
        resource_type: str
        metadata: FlextCore.Types.Dict | None = None

    # Query Models (extending FlextCore.Models.Query)
    class GetResourceQuery(FlextCore.Models.Query):
        """Query to get a single resource."""

        resource_id: str
        resource_type: str
        include_metadata: bool = False

    class ListResourcesQuery(FlextCore.Models.Query):
        """Query to list resources."""

        resource_type: str
        filters: FlextCore.Types.Dict | None = None
        pagination: FlextCore.Types.Dict | None = None
        include_metadata: bool = False

    class SearchResourcesQuery(FlextCore.Models.Query):
        """Query to search resources."""

        resource_type: str
        search_term: str
        filters: FlextCore.Types.Dict | None = None
        pagination: FlextCore.Types.Dict | None = None
        include_metadata: bool = False

    # Event Models (extending FlextCore.Models.DomainEvent)
    class ResourceCreatedEvent(FlextCore.Models.DomainEvent):
        """Event emitted when a resource is created."""

        resource_id: str
        resource_type: str
        data: FlextCore.Types.Dict
        metadata: FlextCore.Types.Dict | None = None

    class ResourceUpdatedEvent(FlextCore.Models.DomainEvent):
        """Event emitted when a resource is updated."""

        resource_id: str
        resource_type: str
        old_data: FlextCore.Types.Dict
        new_data: FlextCore.Types.Dict
        metadata: FlextCore.Types.Dict | None = None

    class ResourceDeletedEvent(FlextCore.Models.DomainEvent):
        """Event emitted when a resource is deleted."""

        resource_id: str
        resource_type: str
        metadata: FlextCore.Types.Dict | None = None

    # Response Models for queries
    class ResourceData(FlextCore.Models.Value):
        """Data model for a single resource."""

        resource_id: str
        resource_type: str
        data: FlextCore.Types.Dict
        metadata: FlextCore.Types.Dict | None = None
        created_at: str
        updated_at: str

    class ResourceList(FlextCore.Models.Value):
        """Data model for a list of resources."""

        resources: list[FlextCore.Types.Dict]
        total_count: int
        pagination: FlextCore.Types.Dict | None = None
        metadata: FlextCore.Types.Dict | None = None


__all__ = [
    "FlextApiModels",
]
