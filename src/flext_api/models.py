"""FLEXT API Models - HTTP Domain Models extending flext-core.

Unified namespace class that extends flext-core FlextModels with HTTP-specific
domain entities. Provides Pydantic v2 models for HTTP operations following
Clean Architecture patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from collections.abc import (
    Mapping,
)
from typing import Annotated, ClassVar

from flext_web import m, u

from flext_api import c, t


class FlextApiModels(m):
    """HTTP domain models for flext-api."""

    class Api:
        """Api Models."""

        @staticmethod
        def _normalize_request_body(v: t.JsonValue) -> t.Api.RequestBody:
            """Normalize body - empty dict is valid."""
            if v is None:
                return {}
            return t.Api.REQUEST_BODY_ADAPTER.validate_python(v)

        @staticmethod
        def _normalize_response_body(v: t.JsonValue) -> t.Api.ResponseBody:
            """Normalize body - None is valid for empty responses (e.g., 204), default is empty dict."""
            if v is None:
                return None  # Explicit None is valid (e.g., for 204 responses)
            return t.Api.RESPONSE_BODY_ADAPTER.validate_python(v)

        # =========================================================================
        # HTTP REQUEST/RESPONSE VALUE OBJECTS (Immutable)
        # =========================================================================

        class HttpRequest(m.Value):
            """Immutable HTTP request value object.

            Represents a complete HTTP request with all necessary parameters.
            Follows Value Object pattern: immutable, compared by value, no identity.
            """

            method: Annotated[
                c.Api.Method | str,
                u.Field(
                    default="GET",
                    description="HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)",
                    pattern=r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)$",
                ),
            ]
            url: Annotated[
                t.NonEmptyStr,
                u.Field(
                    ..., max_length=c.Api.MAX_URL_LENGTH, description="Request URL"
                ),
            ]
            headers: Annotated[
                t.StrMapping,
                u.Field(description="HTTP request headers"),
            ] = u.Field(default_factory=dict)
            body: Annotated[
                Annotated[
                    t.Api.RequestBody,
                    m.BeforeValidator(
                        lambda v: FlextApiModels.Api._normalize_request_body(v)
                    ),
                ],
                u.Field(description="Request body"),
            ] = u.Field(default_factory=dict)

            query_params: Annotated[
                t.Api.WebParams,
                u.Field(description="Query parameters"),
            ] = u.Field(default_factory=dict)
            timeout: Annotated[
                t.PositiveTimeout,
                u.Field(
                    default=float(c.Api.DEFAULT_TIMEOUT),
                    description="Request timeout in seconds",
                ),
            ]

            @u.computed_field(return_type=str)
            @property
            def content_type(self) -> str:
                """Get content type from headers."""
                # Check Content-Type header (case-insensitive)
                # c.Api.HEADER_CONTENT_TYPE = c.Api.HEADER_CONTENT_TYPE
                if c.Api.HEADER_CONTENT_TYPE in self.headers:
                    return self.headers[c.Api.HEADER_CONTENT_TYPE]
                # Check lowercase variant
                if c.Api.HEADER_CONTENT_TYPE.lower() in self.headers:
                    return self.headers[c.Api.HEADER_CONTENT_TYPE.lower()]
                # Default from Constants
                return c.Api.ContentType.JSON

        class HttpResponse(m.Value):
            """Immutable HTTP response value object.

            Represents a complete HTTP response with all returned data.
            Follows Value Object pattern: immutable, compared by value, no identity.
            """

            status_code: Annotated[
                t.HttpStatusCode,
                u.Field(
                    ...,
                    description=f"HTTP status code ({c.Api.HTTP_STATUS_MIN}-{c.Api.HTTP_STATUS_MAX})",
                ),
            ]
            headers: Annotated[
                t.StrMapping,
                u.Field(description="HTTP response headers"),
            ] = u.Field(default_factory=dict)
            body: Annotated[
                Annotated[
                    t.Api.ResponseBody,
                    m.BeforeValidator(
                        lambda v: FlextApiModels.Api._normalize_response_body(v)
                    ),
                ],
                u.Field(
                    description="Response body (empty dict by default, None allowed for 204)"
                ),
            ] = u.Field(default_factory=dict)

            request_id: Annotated[
                str,
                u.Field(default="", description="Associated request ID for tracking"),
            ]

            @u.computed_field(return_type=bool)
            @property
            def client_error(self) -> bool:
                """Check if response indicates client error (4xx status code)."""
                return (
                    c.Api.HTTP_CLIENT_ERROR_MIN
                    <= self.status_code
                    < c.Api.HTTP_CLIENT_ERROR_MAX
                )

            @u.computed_field(return_type=bool)
            @property
            def error(self) -> bool:
                """Check if response indicates any error (4xx or 5xx status code)."""
                return self.status_code >= c.Api.HTTP_ERROR_MIN

            @u.computed_field(return_type=bool)
            @property
            def redirect(self) -> bool:
                """Check if response indicates redirect (3xx status code)."""
                return (
                    c.Api.HTTP_REDIRECT_MIN
                    <= self.status_code
                    < c.Api.HTTP_REDIRECT_MAX
                )

            @u.computed_field(return_type=bool)
            @property
            def server_error(self) -> bool:
                """Check if response indicates server error (5xx status code)."""
                return self.status_code >= c.Api.HTTP_SERVER_ERROR_MIN

            @u.computed_field(return_type=bool)
            @property
            def success(self) -> bool:
                """Check if response indicates success (2xx status code)."""
                return (
                    c.Api.HTTP_SUCCESS_MIN <= self.status_code < c.Api.HTTP_SUCCESS_MAX
                )

        # =========================================================================
        # CONFIGURATION MODELS
        # =========================================================================

        class ClientConfig(m.Value):
            """HTTP client configuration model (immutable value object)."""

            base_url: Annotated[
                str,
                u.Field(
                    default=c.Api.DEFAULT_BASE_URL,
                    max_length=c.Api.MAX_URL_LENGTH,
                    description="Base URL for all requests",
                ),
            ]
            timeout: Annotated[
                t.PositiveTimeout,
                u.Field(
                    default=float(c.Api.DEFAULT_TIMEOUT),
                    description="Request timeout in seconds",
                ),
            ]
            max_retries: Annotated[
                t.RetryCount,
                u.Field(
                    default=c.MAX_RETRY_ATTEMPTS, description="Maximum retry attempts"
                ),
            ]
            headers: Annotated[
                t.StrMapping,
                u.Field(description="Default headers for all requests"),
            ] = u.Field(default_factory=dict)
            verify_ssl: Annotated[
                bool,
                u.Field(default=True, description="Verify SSL certificates"),
            ]

            @u.computed_field(return_type=bool)
            @property
            def configured(self) -> bool:
                """Check if configuration is valid."""
                if not self.base_url:
                    return False
                return self.timeout > 0

        @classmethod
        def create_config(
            cls,
            base_url: str | None = None,
            timeout: float | None = None,
            max_retries: int | None = None,
            headers: t.StrMapping | None = None,
            *,
            verify_ssl: bool = True,
        ) -> ClientConfig:
            """Create ClientConfig from parameters.

            Args:
            base_url: Base URL for all requests (uses Constants default if None)
            timeout: Request timeout in seconds (uses Constants default if None)
            max_retries: Maximum retry attempts (uses Constants default if None)
            headers: Default headers for all requests (None for empty dict)
            verify_ssl: Verify SSL certificates

            Returns:
            ClientConfig instance with defaults from Constants

            """
            # Use Constants defaults when None - Config has priority but uses Constants as base
            config_base_url = (
                base_url if base_url is not None else c.Api.DEFAULT_BASE_URL
            )
            config_timeout = (
                float(timeout) if timeout is not None else float(c.Api.DEFAULT_TIMEOUT)
            )
            config_max_retries = (
                max_retries if max_retries is not None else c.MAX_RETRY_ATTEMPTS
            )
            config_headers: t.StrMapping = headers if headers is not None else {}

            return cls.ClientConfig(
                base_url=config_base_url,
                timeout=config_timeout,
                max_retries=config_max_retries,
                headers=config_headers,
                verify_ssl=verify_ssl,
            )

        # =========================================================================
        # FACTORY METHODS - Model creation utilities
        # =========================================================================

        @classmethod
        def create_response(
            cls,
            status_code: int,
            body: t.Api.ResponseBody | None = None,
            headers: t.StrMapping | None = None,
            request_id: str | None = None,
        ) -> HttpResponse:
            """Create HttpResponse from parameters.

            Args:
            status_code: HTTP status code
            body: Response body (JSON, string, bytes, or None for empty dict)
            headers: Response headers dictionary (None for empty dict)
            request_id: Associated request ID for tracking (None for empty string)

            Returns:
            HttpResponse instance with defaults from model

            """
            # Use model defaults - body defaults to empty dict, not None
            response_body: t.Api.ResponseBody = body if body is not None else {}
            response_headers: t.StrMapping = headers if headers is not None else {}
            response_id: str = request_id if request_id is not None else ""

            return cls.HttpResponse(
                status_code=status_code,
                body=response_body,
                headers=response_headers,
                request_id=response_id,
            )

        # =========================================================================
        # SCHEMA u.FIELD MODELS - Moved from schemas/_shared.py
        # =========================================================================

        class DictField(m.Value):
            """Pydantic model for validating dictionary fields (immutable value object)."""

            value: Annotated[
                t.JsonMapping,
                u.Field(description="Dictionary value"),
            ] = u.Field(default_factory=dict)

        class StringField(m.Value):
            """Pydantic model for validating string fields (immutable value object)."""

            value: Annotated[str, u.Field(..., description="String value")]

        class IntField(m.Value):
            """Pydantic model for validating integer fields (immutable value object)."""

            value: Annotated[int, u.Field(..., description="Integer value")]

        # =========================================================================
        # PRIVATE INTERNAL MODELS (moved from protocol_impls for MRO compliance)
        # =========================================================================

        class HttpRequestCallArgs(m.Value):
            """Internal model for validating HTTP request call arguments."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                arbitrary_types_allowed=True,
            )

            method: Annotated[str, u.Field(..., description="HTTP method")]
            url: Annotated[str, u.Field(..., description="Request URL")]
            headers: Annotated[
                t.StrMapping,
                u.Field(description="HTTP headers"),
            ] = u.Field(default_factory=dict)
            params: Annotated[
                t.StrMapping,
                u.Field(description="Query parameters"),
            ] = u.Field(default_factory=dict)
            data: Annotated[
                t.JsonMapping | None,
                u.Field(None, description="Form request body"),
            ]
            json_body: Annotated[
                t.JsonValue | None,
                u.Field(None, description="JSON request body"),
            ]
            content: Annotated[
                bytes | None,
                u.Field(None, description="Raw content body"),
            ]
            timeout: Annotated[
                float | None,
                u.Field(None, description="Request timeout"),
            ]

        class MappingBodyModel(m.Value):
            """Internal model for wrapping mapping body data."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                arbitrary_types_allowed=True,
            )

            body: Annotated[
                t.JsonMapping,
                u.Field(..., description="Request body as mapping"),
            ]

        class HttpClientRequestOptions(m.Value):
            """Internal model for HTTP client request options."""

            model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                arbitrary_types_allowed=True,
            )

            params: Annotated[
                t.StrMapping | None,
                u.Field(None, description="Query parameters"),
            ]
            json_data: Annotated[
                t.JsonValue | None,
                u.Field(None, description="JSON body"),
            ]
            content: Annotated[
                bytes | None,
                u.Field(None, description="Raw content body"),
            ]
            data: Annotated[
                t.JsonMapping | None,
                u.Field(None, description="Form data"),
            ]
            timeout: Annotated[
                float | None,
                u.Field(None, description="Request timeout"),
            ]
            headers: t.StrMapping = u.Field(default_factory=dict)

        class HeadersRequest(m.Value):
            """Encapsulates RFC header constraint for requests."""

            headers: t.StrMapping = u.Field(default_factory=dict)

        class MethodRequest(m.Value):
            """Encapsulates RFC method constraint for requests."""

            method: Annotated[
                str, u.Field(min_length=1, description="HTTP method (GET, POST, etc.)")
            ]

            @u.field_validator("method")
            @classmethod
            def _validate_method(cls, value: str) -> str:
                method_upper = value.upper()
                valid_methods = {
                    "GET",
                    "POST",
                    "PUT",
                    "DELETE",
                    "PATCH",
                    "HEAD",
                    "OPTIONS",
                    "TRACE",
                    "CONNECT",
                }
                if method_upper not in valid_methods:
                    msg = f"Invalid HTTP method: {method_upper} (RFC 7231)"
                    raise ValueError(msg)
                return method_upper

        class TimeoutRequest(m.Value):
            """Encapsulates timeout constraints for RFC request URLs."""

            timeout: Annotated[
                t.PositiveTimeout,
                u.Field(..., description="Request timeout in seconds"),
            ]

        class UrlRequest(m.Value):
            """Encapsulates URL validation constraints for RFC requests."""

            url: Annotated[
                str, u.Field(min_length=1, description="Target URL for the request")
            ]

            @u.field_validator("url")
            @classmethod
            def _validate_url(cls, value: str) -> str:
                if not value.strip():
                    msg = "URL cannot be empty (RFC 7230)"
                    raise ValueError(msg)
                if not value.startswith(("http://", "https://")):
                    msg = "URL must start with http:// or https://"
                    raise ValueError(msg)
                return value

        class StatusCodeValue(m.Value):
            """Validates status code values according to RFC conventions."""

            status_code: Annotated[
                t.HttpStatusCode,
                u.Field(..., description="HTTP response status code"),
            ]

        class SendRequestSseOptions(m.Value):
            """Options for SSE request sending behavior."""

            method: Annotated[
                str,
                u.Field("GET", min_length=1, description="HTTP method for SSE"),
            ]
            max_events: Annotated[
                t.PositiveInt,
                u.Field(1, description="Maximum SSE events to receive"),
            ]
            auto_reconnect: Annotated[
                bool | None,
                u.Field(None, description="Enable automatic reconnection"),
            ]
            reconnect_max_attempts: Annotated[
                t.NonNegativeInt | None,
                u.Field(None, description="Maximum reconnection attempts"),
            ]
            reconnect_backoff_factor: Annotated[
                t.PositiveFloat | None,
                u.Field(None, description="Reconnection backoff multiplier"),
            ]
            retry_timeout: Annotated[
                t.NonNegativeInt | None,
                u.Field(None, description="Retry timeout in seconds"),
            ]

        class SendRequestWsOptions(m.Value):
            """Options for sending a WebSocket message request."""

            message: Annotated[
                str | bytes | None,
                u.Field(None, description="WebSocket message payload"),
            ]
            message_type: Annotated[
                str,
                u.Field(
                    "text",
                    min_length=1,
                    description="WebSocket message type (text or binary)",
                ),
            ]

        class InboundMessage(m.Value):
            """Model for inbound WebSocket messages."""

            message: str | bytes = u.Field(
                description="Inbound WebSocket message content"
            )

        # =========================================================================
        # STORAGE MODELS
        # =========================================================================

        class Storage:
            """Storage-related models namespace."""

            class Settings(m.Value):
                """Canonical storage settings."""

                namespace: str = u.Field(
                    "flext_api",
                    description="Logical namespace for this storage instance",
                    validate_default=True,
                )
                backend: str = u.Field(
                    "memory",
                    description="Storage backend identifier",
                    validate_default=True,
                )
                max_size: int | None = u.Field(
                    None,
                    description="Maximum number of entries kept in memory",
                    gt=0,
                    validate_default=True,
                )
                default_ttl: int | None = u.Field(
                    None,
                    description="Default entry TTL in seconds",
                    gt=0,
                    validate_default=True,
                )

            class Metadata(m.Value):
                """Internal metadata for stored values (using Pydantic for validation)."""

                value: t.JsonValue
                timestamp: str
                ttl: float | int | None = None
                created_at: float = u.Field(default_factory=time.time)

                @property
                def expired(self) -> bool:
                    """Return whether the entry is expired."""
                    if self.ttl is None:
                        return False
                    elapsed = time.time() - self.created_at
                    return elapsed > self.ttl

            class State(m.FlexibleInternalModel):
                """Mutable storage runtime state kept in one central model."""

                model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                    extra="forbid",
                    validate_assignment=True,
                )

                entries: dict[str, FlextApiModels.Api.Storage.Metadata] = u.Field(
                    default_factory=dict
                )
                operations_count: int = u.Field(
                    0,
                    description="Total operations performed by this storage",
                    validate_default=True,
                )
                cache_hits: int = u.Field(
                    0, description="Successful cache reads", validate_default=True
                )
                cache_misses: int = u.Field(
                    0, description="Failed cache reads", validate_default=True
                )
                created_at: str = u.Field(
                    default_factory=u.generate_iso_timestamp,
                    description="Creation timestamp for this storage instance",
                )

            class Stats(m.Value):
                """Storage statistics using Pydantic (automatic validation)."""

                total_operations: int = u.Field(
                    0,
                    description="Total storage operations count",
                    validate_default=True,
                )
                cache_hits: int = u.Field(
                    0, description="Number of cache hits", validate_default=True
                )
                cache_misses: int = u.Field(
                    0, description="Number of cache misses", validate_default=True
                )
                storage_size: int = u.Field(
                    0,
                    description="Current storage size in entries",
                    validate_default=True,
                )
                memory_usage: int = u.Field(
                    0,
                    description="Estimated memory usage in bytes",
                    validate_default=True,
                )
                namespace: str = u.Field(
                    "flext",
                    description="Storage namespace identifier",
                    validate_default=True,
                )

                @property
                def hit_ratio(self) -> float:
                    """Return cache hit ratio."""
                    if self.total_operations == 0:
                        return 0.0
                    return self.cache_hits / self.total_operations

        class Webhook:
            """Webhook-related models namespace."""

            class Settings(m.Value):
                """Canonical webhook runtime settings."""

                secret: Annotated[
                    str | None,
                    u.Field(
                        None,
                        description="Shared secret used for signature verification",
                    ),
                ] = None
                signature_header: Annotated[
                    str,
                    u.Field(
                        "X-Webhook-Signature",
                        description="Header name containing the webhook signature",
                        min_length=1,
                    ),
                ] = "X-Webhook-Signature"
                algorithm: Annotated[
                    t.Api.WebhookAlgorithm,
                    u.Field("sha256", description="Supported HMAC signature algorithm"),
                ] = "sha256"
                max_retries: Annotated[
                    int,
                    u.Field(3, description="Maximum retry attempts per event", ge=0),
                ] = 3
                retry_delay: Annotated[
                    float,
                    u.Field(1.0, description="Initial retry delay in seconds", gt=0),
                ] = 1.0
                retry_backoff: Annotated[
                    float,
                    u.Field(2.0, description="Retry backoff multiplier", gt=0),
                ] = 2.0
                queue_limit: Annotated[
                    int,
                    u.Field(
                        1000,
                        description="Maximum number of events kept in the main queue",
                        gt=0,
                    ),
                ] = 1000
                retry_queue_limit: Annotated[
                    int,
                    u.Field(
                        500,
                        description="Maximum number of events kept in the retry queue",
                        gt=0,
                    ),
                ] = 500

            class Event(m.Value):
                """Canonical webhook event envelope."""

                id: str = u.Field(description="Unique event identifier", min_length=1)
                type: str = u.Field(description="Canonical event type", min_length=1)
                data: t.JsonMapping = u.Field(description="Normalized event payload")
                timestamp: float = u.Field(
                    default_factory=time.time, description="Event creation timestamp"
                )
                attempts: Annotated[
                    int,
                    u.Field(0, description="Number of processing attempts", ge=0),
                ] = 0

            class Delivery(m.Value):
                """Canonical delivery status for one webhook event."""

                event_type: str = u.Field(
                    description="Associated event type", min_length=1
                )
                timestamp: float = u.Field(
                    default_factory=time.time, description="Delivery status timestamp"
                )
                status: t.Api.WebhookDeliveryStatus = u.Field(
                    description="Delivery terminal status"
                )
                attempts: Annotated[
                    int | None,
                    u.Field(
                        default=None,
                        description="Attempts performed before reaching this status",
                        ge=0,
                    ),
                ] = None
                error: Annotated[
                    str | None,
                    u.Field(
                        default=None,
                        description="Terminal failure message when delivery failed",
                    ),
                ] = None

            class State(m.FlexibleInternalModel):
                """Mutable webhook runtime state centralized in one model.

                Enforcement exemption: webhook runtime state with mutable
                handlers/queues accumulated during event dispatch.
                """

                model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                    extra="forbid",
                    validate_assignment=True,
                    arbitrary_types_allowed=True,
                )

                handlers: Mapping[str, list[t.Api.WebhookHandler]] = u.Field(
                    default_factory=dict
                )
                event_queue: list[FlextApiModels.Api.Webhook.Event] = u.Field(
                    default_factory=list
                )
                retry_queue: list[FlextApiModels.Api.Webhook.Event] = u.Field(
                    default_factory=list
                )
                deliveries: Mapping[
                    str,
                    FlextApiModels.Api.Webhook.Delivery,
                ] = u.Field(default_factory=dict)

                @property
                def event_queue_size(self) -> int:
                    """Return current main queue length."""
                    return len(self.event_queue)

                @property
                def retry_queue_size(self) -> int:
                    """Return current retry queue length."""
                    return len(self.retry_queue)

                @property
                def total_deliveries(self) -> int:
                    """Return number of delivery confirmations."""
                    return len(self.deliveries)

                @property
                def successful_deliveries(self) -> int:
                    """Return number of successful deliveries."""
                    return sum(
                        1
                        for delivery in self.deliveries.values()
                        if delivery.status in {"delivered", "delivered_after_retry"}
                    )

                @property
                def failed_deliveries(self) -> int:
                    """Return number of failed deliveries."""
                    return sum(
                        1
                        for delivery in self.deliveries.values()
                        if delivery.status == c.Api.WebhookDeliveryStatus.FAILED.value
                    )


m = FlextApiModels

__all__: list[str] = ["FlextApiModels", "m"]
