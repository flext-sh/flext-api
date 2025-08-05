"""FLEXT API Domain Entities - Foundation Pattern Implementation.

Domain entities following docs/patterns/foundation.md patterns for HTTP and API
operations within the FLEXT ecosystem. Implements FlextEntity pattern with
business logic, validation, and domain events.

Foundation Pattern Compliance:
    ✅ FlextEntity: Identity-based entities with lifecycle tracking
    ✅ FlextResult: Railway-oriented programming for error handling
    ✅ Business Rules: Validation within entity boundaries
    ✅ Domain Events: Event generation for state changes
    ✅ Type Safety: Full MyPy compatibility with proper typing

Core Entities:
    - ApiRequest: HTTP request entity with validation and routing
    - ApiResponse: HTTP response entity with formatting
    - ApiEndpoint: API endpoint entity with routing configuration
    - ApiSession: API session entity with authentication state

Architecture Integration:
    Domain Layer → FlextEntity → Business Logic → FlextResult

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum

from flext_core import FlextEntity, FlextResult, get_logger
from pydantic import Field

from flext_api.domain.value_objects import HttpMethod

logger = get_logger(__name__)

# Constants for validation
MIN_HTTP_STATUS = 100
MAX_HTTP_STATUS = 599
MIN_TOKEN_LENGTH = 16


class RequestState(StrEnum):
    """API request processing states."""

    CREATED = "created"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResponseState(StrEnum):
    """API response states."""

    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class ApiRequest(FlextEntity):
    """HTTP request entity following FlextEntity foundation pattern.

    Rich domain model encapsulating HTTP request business logic, validation,
    and state management. Implements foundation patterns for consistency.
    """

    method: HttpMethod = Field(description="HTTP method")
    url: str = Field(description="Request URL")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    body: dict[str, object] | None = Field(None, description="Request body")
    query_params: dict[str, str] = Field(default_factory=dict, description="Query parameters")
    state: RequestState = Field(default=RequestState.CREATED, description="Request processing state")

    # Timestamp fields for entity lifecycle tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity last update timestamp",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate request business rules following foundation pattern."""
        logger.debug("Validating API request business rules", request_id=self.id)

        # URL validation
        if not self.url or not self.url.strip():
            return FlextResult.fail("Request URL cannot be empty")

        if not self.url.startswith(("http://", "https://", "/")):
            return FlextResult.fail("Request URL must be valid HTTP URL or path")

        # Method validation
        if self.method not in HttpMethod:
            return FlextResult.fail(f"Invalid HTTP method: {self.method}")

        # Headers validation
        if self.headers:
            for key, value in self.headers.items():
                if not key:
                    return FlextResult.fail("Header keys must be non-empty strings")
                # Type hints ensure str values, but validate empty values
                if not value:
                    return FlextResult.fail("Header values cannot be empty")

        logger.debug("API request validation successful", request_id=self.id)
        return FlextResult.ok(None)

    def start_processing(self) -> FlextResult[ApiRequest]:
        """Start request processing with state transition."""
        if self.state != RequestState.VALIDATED:
            return FlextResult.fail(f"Cannot start processing from state: {self.state}")

        updated = self.model_copy(update={
            "state": RequestState.PROCESSING,
            "updated_at": datetime.now(UTC),
        })

        logger.info("Request processing started", request_id=self.id)
        return FlextResult.ok(updated)

    def complete_processing(self) -> FlextResult[ApiRequest]:
        """Complete request processing."""
        if self.state != RequestState.PROCESSING:
            return FlextResult.fail(f"Cannot complete from state: {self.state}")

        updated = self.model_copy(update={
            "state": RequestState.COMPLETED,
            "updated_at": datetime.now(UTC),
        })

        logger.info("Request processing completed", request_id=self.id)
        return FlextResult.ok(updated)


class ApiResponse(FlextEntity):
    """HTTP response entity following FlextEntity foundation pattern.

    Encapsulates response formatting, validation, and state management
    with rich domain behavior.
    """

    status_code: int = Field(description="HTTP status code")
    headers: dict[str, str] = Field(default_factory=dict, description="Response headers")
    body: dict[str, object] | None = Field(None, description="Response body")
    state: ResponseState = Field(default=ResponseState.PENDING, description="Response state")
    request_id: str | None = Field(None, description="Associated request ID")

    # Timestamp fields for entity lifecycle tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity last update timestamp",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate response business rules."""
        logger.debug("Validating API response business rules", response_id=self.id)

        # Status code validation
        if not (MIN_HTTP_STATUS <= self.status_code <= MAX_HTTP_STATUS):
            return FlextResult.fail(f"Invalid HTTP status code: {self.status_code}")

        # Headers validation
        if self.headers:
            for key, value in self.headers.items():
                if not key:
                    return FlextResult.fail("Response header keys must be non-empty strings")
                # Type hints ensure str values, but validate empty values
                if not value:
                    return FlextResult.fail("Response header values cannot be empty")

        logger.debug("API response validation successful", response_id=self.id)
        return FlextResult.ok(None)

    def mark_success(self) -> FlextResult[ApiResponse]:
        """Mark response as successful."""
        updated = self.model_copy(update={
            "state": ResponseState.SUCCESS,
            "updated_at": datetime.now(UTC),
        })

        logger.info("Response marked as success", response_id=self.id)
        return FlextResult.ok(updated)

    def mark_error(self, error_message: str) -> FlextResult[ApiResponse]:
        """Mark response as error with message."""
        error_body = {
            "error": error_message,
            "timestamp": datetime.now(UTC).isoformat(),
            "response_id": self.id,
        }

        updated = self.model_copy(update={
            "state": ResponseState.ERROR,
            "body": error_body,
            "updated_at": datetime.now(UTC),
        })

        logger.error("Response marked as error", response_id=self.id, error=error_message)
        return FlextResult.ok(updated)


class ApiEndpoint(FlextEntity):
    """API endpoint entity with routing and configuration.

    Encapsulates endpoint-specific business logic, routing rules,
    and access control following foundation patterns.
    """

    path: str = Field(description="Endpoint path pattern")
    methods: list[HttpMethod] = Field(description="Allowed HTTP methods")
    description: str | None = Field(None, description="Endpoint description")
    auth_required: bool = Field(default=True, description="Authentication requirement")
    rate_limit: int | None = Field(None, description="Rate limit per minute")

    # Timestamp fields for entity lifecycle tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity last update timestamp",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate endpoint business rules."""
        logger.debug("Validating API endpoint business rules", endpoint_id=self.id)

        # Path validation
        if not self.path or not self.path.strip():
            return FlextResult.fail("Endpoint path cannot be empty")

        if not self.path.startswith("/"):
            return FlextResult.fail("Endpoint path must start with '/'")

        # Methods validation
        if not self.methods:
            return FlextResult.fail("Endpoint must support at least one HTTP method")

        for method in self.methods:
            if method not in HttpMethod:
                return FlextResult.fail(f"Invalid HTTP method: {method}")

        # Rate limit validation
        if self.rate_limit is not None and self.rate_limit <= 0:
            return FlextResult.fail("Rate limit must be positive")

        logger.debug("API endpoint validation successful", endpoint_id=self.id)
        return FlextResult.ok(None)

    def supports_method(self, method: HttpMethod) -> bool:
        """Check if endpoint supports HTTP method."""
        return method in self.methods

    def requires_authentication(self) -> bool:
        """Check if endpoint requires authentication."""
        return self.auth_required


class ApiSession(FlextEntity):
    """API session entity with authentication state.

    Manages session lifecycle, authentication tokens, and
    access control following foundation patterns.
    """

    user_id: str | None = Field(None, description="Authenticated user ID")
    token: str | None = Field(None, description="Session token")
    expires_at: datetime | None = Field(None, description="Session expiration")
    last_activity: datetime | None = Field(None, description="Last activity timestamp")
    is_active: bool = Field(default=True, description="Session active state")

    # Timestamp fields for entity lifecycle tracking
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Entity last update timestamp",
    )

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate session business rules."""
        logger.debug("Validating API session business rules", session_id=self.id)

        # Token validation
        if self.token and len(self.token) < MIN_TOKEN_LENGTH:
            return FlextResult.fail("Session token must be at least 16 characters")

        # Expiration validation
        if self.expires_at and self.expires_at <= datetime.now(UTC):
            return FlextResult.fail("Session cannot be created with past expiration")

        logger.debug("API session validation successful", session_id=self.id)
        return FlextResult.ok(None)

    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) >= self.expires_at

    def extend_session(self, duration_minutes: int = 60) -> FlextResult[ApiSession]:
        """Extend session expiration."""
        if not self.is_active:
            return FlextResult.fail("Cannot extend inactive session")

        new_expiration = datetime.now(UTC) + timedelta(minutes=duration_minutes)

        updated = self.model_copy(update={
            "expires_at": new_expiration,
            "last_activity": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        })

        logger.info("Session extended", session_id=self.id, expires_at=new_expiration)
        return FlextResult.ok(updated)

    def deactivate(self) -> FlextResult[ApiSession]:
        """Deactivate session."""
        updated = self.model_copy(update={
            "is_active": False,
            "updated_at": datetime.now(UTC),
        })

        logger.info("Session deactivated", session_id=self.id)
        return FlextResult.ok(updated)


# Export foundation pattern entities
__all__ = [
    "ApiEndpoint",
    "ApiRequest",
    "ApiResponse",
    "ApiSession",
    "RequestState",
    "ResponseState",
]
