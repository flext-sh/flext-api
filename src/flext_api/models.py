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
    MutableMapping,
    MutableSequence,
)
from types import MappingProxyType
from typing import Annotated, ClassVar

from flext_api import c, t
from flext_core import FlextModels
from flext_web import m, u


class FlextApiModels(FlextModels):
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

            _flext_enforcement_exempt: ClassVar[bool] = True

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
            ] = u.Field(default_factory=lambda: MappingProxyType({}))
            body: Annotated[
                t.Api.RequestBody | None,
                m.BeforeValidator(
                    lambda v: FlextApiModels.Api._normalize_request_body(v)
                ),
                u.Field(description="Request body"),
            ] = None

            query_params: Annotated[
                t.Api.WebParams | None,
                u.Field(description="Query parameters"),
            ] = None
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
                if c.Api.HEADER_CONTENT_TYPE in self.headers:
                    header_value: str = self.headers[c.Api.HEADER_CONTENT_TYPE]
                    return header_value
                # Check lowercase variant
                if c.Api.HEADER_CONTENT_TYPE.lower() in self.headers:
                    lowercase_header_value: str = self.headers[
                        c.Api.HEADER_CONTENT_TYPE.lower()
                    ]
                    return lowercase_header_value
                # Default from Constants
                return str(c.Api.ContentType.JSON)

        class HttpResponse(m.Value):
            """Immutable HTTP response value object.

            Represents a complete HTTP response with all returned data.
            Follows Value Object pattern: immutable, compared by value, no identity.
            """

            _flext_enforcement_exempt: ClassVar[bool] = True

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
            ] = u.Field(default_factory=lambda: MappingProxyType({}))
            body: Annotated[
                t.Api.ResponseBody | None,
                m.BeforeValidator(
                    lambda v: FlextApiModels.Api._normalize_response_body(v)
                ),
                u.Field(
                    description="Response body (empty dict by default, None allowed for 204)"
                ),
            ] = None

            request_id: Annotated[
                str,
                u.Field(default="", description="Associated request ID for tracking"),
            ]

            @u.computed_field(return_type=bool)
            @property
            def client_error(self) -> bool:
                """Check if response indicates client error (4xx status code)."""
                is_client_error: bool = (
                    c.Api.HTTP_CLIENT_ERROR_MIN
                    <= self.status_code
                    < c.Api.HTTP_CLIENT_ERROR_MAX
                )
                return is_client_error

            @u.computed_field(return_type=bool)
            @property
            def error(self) -> bool:
                """Check if response indicates any error (4xx or 5xx status code)."""
                has_error: bool = self.status_code >= c.Api.HTTP_ERROR_MIN
                return has_error

            @u.computed_field(return_type=bool)
            @property
            def redirect(self) -> bool:
                """Check if response indicates redirect (3xx status code)."""
                is_redirect: bool = (
                    c.Api.HTTP_REDIRECT_MIN
                    <= self.status_code
                    < c.Api.HTTP_REDIRECT_MAX
                )
                return is_redirect

            @u.computed_field(return_type=bool)
            @property
            def server_error(self) -> bool:
                """Check if response indicates server error (5xx status code)."""
                has_server_error: bool = self.status_code >= c.Api.HTTP_SERVER_ERROR_MIN
                return has_server_error

            @u.computed_field(return_type=bool)
            @property
            def success(self) -> bool:
                """Check if response indicates success (2xx status code)."""
                is_success: bool = (
                    c.Api.HTTP_SUCCESS_MIN <= self.status_code < c.Api.HTTP_SUCCESS_MAX
                )
                return is_success

        # =========================================================================
        # CONFIGURATION MODELS
        # =========================================================================

        class ClientConfig(m.Value):
            """HTTP client configuration model (immutable value object)."""

            _flext_enforcement_exempt: ClassVar[bool] = True

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
            ] = u.Field(default_factory=lambda: MappingProxyType({}))
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
                is_configured: bool = self.timeout > 0
                return is_configured

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
            # Preserve the public factory default of an empty mapping.
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
        # PRIVATE INTERNAL MODELS (moved from protocol_impls for MRO compliance)
        # =========================================================================

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

                _flext_enforcement_exempt: ClassVar[bool] = True

                value: Annotated[
                    t.JsonValue,
                    u.Field(description="Stored JSON-compatible value payload"),
                ]
                timestamp: Annotated[
                    str,
                    u.Field(description="Entry creation timestamp in ISO format"),
                ]
                ttl: Annotated[
                    t.Numeric | None,
                    u.Field(
                        default=None,
                        description="Optional time-to-live in seconds for the entry",
                    ),
                ] = None
                created_at: Annotated[
                    float,
                    u.Field(
                        default_factory=time.time,
                        description="Monotonic creation timestamp used for expiry checks",
                    ),
                ]

                @property
                def expired(self) -> bool:
                    """Return whether the entry is expired."""
                    if self.ttl is None:
                        return False
                    elapsed = time.time() - self.created_at
                    return elapsed > float(self.ttl)

            class State(m.FlexibleInternalModel):
                """Mutable storage runtime state kept in one central model."""

                model_config: ClassVar[m.ConfigDict] = m.ConfigDict(
                    extra="forbid",
                    validate_assignment=True,
                )

                entries: MutableMapping[str, FlextApiModels.Api.Storage.Metadata] = (
                    u.Field(
                        default_factory=dict,
                        description="Storage entries by key",
                    )
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
                ] = c.Api.WebhookAlgorithm.SHA256
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

                handlers: MutableMapping[str, MutableSequence[t.Api.WebhookHandler]] = (
                    u.Field(
                        default_factory=dict,
                        description="Registered webhook handlers by event type",
                    )
                )
                event_queue: MutableSequence[FlextApiModels.Api.Webhook.Event] = (
                    u.Field(default_factory=list, description="Main event queue")
                )
                retry_queue: MutableSequence[FlextApiModels.Api.Webhook.Event] = (
                    u.Field(default_factory=list, description="Retry event queue")
                )
                deliveries: MutableMapping[
                    str,
                    FlextApiModels.Api.Webhook.Delivery,
                ] = u.Field(
                    default_factory=dict,
                    description="Delivery records by event id",
                )

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

__all__: t.MutableSequenceOf[str] = ["FlextApiModels", "m"]
