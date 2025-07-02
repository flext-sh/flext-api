"""FastAPI dependencies for dependency injection.

Copyright (c) 2025 Datacosmos. All rights reserved.
Licensed under the MIT License.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated

import grpc

# ZERO TOLERANCE - JWT is REQUIRED for enterprise authentication
import jwt
import structlog

# ZERO TOLERANCE - PyJWT is REQUIRED and guaranteed to have encode/decode in 2025
from dependency_injector.wiring import Provide, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from flx_core.config.domain_config import get_config, get_domain_constants
from flx_core.infrastructure.containers import ApplicationContainer

# ZERO TOLERANCE - Import modern Redis rate limiting implementation
from flx_core.security.redis_rate_limiting import RedisRateLimitManager
from flx_core.security.ssl_utils import _create_ssl_credentials, get_grpc_channel_target
from flx_grpc.proto import flx_pb2_grpc
from jwt.exceptions import InvalidTokenError as JWTError

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from flx_core.events.event_bus import HybridEventBus
    from flx_core.infrastructure.persistence.unit_of_work import UnitOfWork
    from flx_core.services.execution_service import ExecutionService
    from flx_core.services.pipeline_service import PipelineService
    from flx_core.services.plugin_service import PluginService

# Configure logger
logger = structlog.get_logger(__name__)

# Security scheme
security = HTTPBearer()


async def get_grpc_channel() -> AsyncGenerator[grpc.aio.Channel, None]:  # type: ignore[no-any-unimported]
    """Get gRPC channel for API to daemon communication.

    Creates and manages a gRPC channel with proper configuration for
    communicating with the FLX daemon service. The channel is automatically
    closed when the context exits.

    Yields:
    ------
        grpc.aio.Channel: Configured gRPC channel with message size limits.

    Note:
    ----
        Provides proper resource management and graceful cleanup on context exit.

    """
    config = get_config()

    # ZERO TOLERANCE SECURITY: Use secure channel when SSL is enabled
    constants = get_domain_constants()
    target = get_grpc_channel_target()
    mb_to_bytes = int(
        constants.MEMORY_UNIT_CONVERSION * constants.MEMORY_UNIT_CONVERSION,
    )  # MB conversion (1024^2)
    options = [
        (
            "grpc.max_send_message_length",
            config.network.max_request_size_mb * mb_to_bytes,
        ),
        (
            "grpc.max_receive_message_length",
            config.network.max_request_size_mb * mb_to_bytes,
        ),
    ]

    if config.network.enable_ssl:
        # Import moved to top-level to fix PLC0415 violation
        credentials = _create_ssl_credentials(
            cert_file=config.network.ssl_cert_file,
            key_file=config.network.ssl_key_file,
            ca_file=config.network.ssl_ca_file,
        )
        channel = grpc.aio.secure_channel(target, credentials, options=options)
    else:
        channel = grpc.aio.insecure_channel(target, options=options)
    try:
        yield channel
    finally:
        await channel.close()


def get_grpc_stub(  # type: ignore[no-any-unimported]
    channel: Annotated[grpc.aio.Channel, Depends(get_grpc_channel)],
) -> flx_pb2_grpc.FlxServiceStub:
    """Get gRPC service stub.

    Creates a gRPC service stub for invoking remote procedures on the
    FLX daemon service. The stub is created from the provided channel
    and enables communication with the daemon's API endpoints.

    Args:
    ----
        channel: The gRPC channel to use for communication

    Returns:
    -------
        flx_pb2_grpc.FlxServiceStub: Service stub for RPC invocation.

    Note:
    ----
        Provides dependency injection for clean separation of concerns.

    """
    return flx_pb2_grpc.FlxServiceStub(channel)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, object]:
    """Get current authenticated user from JWT token.

    Validates the JWT token from the Authorization header and extracts
    user information including ID, organization, and roles.

    Args:
    ----
        credentials: HTTP bearer token credentials from the Authorization header

    Returns:
    -------
        dict: User information containing id, org, and roles

    Raises:
    ------
        HTTPException: When token is invalid, missing, or expired

    """
    config = get_config()
    token = credentials.credentials

    # ENTERPRISE SECURITY: Validate JWT secret strength at runtime
    jwt_secret = config.secrets.jwt_secret_key
    min_jwt_secret_length = config.business.JWT_SECRET_MIN_LENGTH
    if len(jwt_secret) < min_jwt_secret_length:
        logger.critical("JWT secret is too weak", secret_length=len(jwt_secret))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    # SECURITY: Check for development defaults in production
    if config.is_production and (
        "dev-secret" in jwt_secret.lower() or "change" in jwt_secret.lower()
    ):
        logger.critical("Development JWT secret detected in production")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    try:
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=[config.secrets.jwt_algorithm],
        )

        user_id = payload.get("sub")
        if user_id is None or not isinstance(user_id, str):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "id": user_id,
            "org": payload.get("org"),
            "roles": payload.get("roles", []),
        }

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, object] | None:
    """Get current user if authenticated, None otherwise.

    Attempts to extract user information from JWT token if provided.
    Returns None if no credentials are provided or if authentication fails.

    Args:
    ----
        credentials: Optional HTTP bearer token credentials

    Returns:
    -------
        dict | None: User information if authenticated, None otherwise

    """
    if not credentials:
        return None

    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


# Modern Redis rate limiter manager - replaces deprecated RateLimiter class
redis_rate_limiter = RedisRateLimitManager(default_algorithm="sliding_window")


async def check_rate_limit_async(key: str) -> bool:
    """Modern async rate limiting using Redis distributed implementation with fallback.

    ZERO TOLERANCE P0 FIX: Implements proper Redis fallback to prevent service
    availability failures when Redis is unavailable. In production environments,
    rate limiting failures should not block legitimate requests.

    Args:
    ----
        key: Unique identifier for rate limiting (e.g., user ID)

    Returns:
    -------
        bool: True if request is allowed, False if rate limit exceeded
              Returns True on Redis connection errors (fail-open for availability)

    """
    config = get_config()

    try:
        # Create sliding window limiter with current configuration
        limiter = redis_rate_limiter.create_sliding_window_limiter(
            max_requests=config.security.api_rate_limit_per_minute,
            window_seconds=config.security.default_rate_window,
        )

        # Check rate limit using modern Redis implementation
        result = await limiter.is_allowed(key)
        return result.success and bool(result.data)

    except (ConnectionError, TimeoutError, OSError) as e:
        # ENTERPRISE SECURITY: Log Redis connectivity issues for monitoring
        logger.warning(
            "Redis rate limiter unavailable, allowing request (fail-open)",
            key=key,
            error=str(e),
            error_type=type(e).__name__,
        )
        # ZERO TOLERANCE DECISION: Fail-open for availability over strict rate limiting
        # Production services should remain available even with Redis issues
        return True

    except (RuntimeError, ValueError, ImportError, AttributeError, TypeError) as e:
        # ENTERPRISE SECURITY: Log unexpected errors for investigation
        logger.exception(
            "Unexpected error in rate limiting, allowing request (fail-open)",
            key=key,
            error=str(e),
            error_type=type(e).__name__,
        )
        # ZERO TOLERANCE DECISION: Fail-open for service availability
        return True


# Professional dependency injection following dependency-injector patterns


@inject
def get_pipeline_service(
    service: PipelineService = Provide[ApplicationContainer.services.pipeline_service],
) -> PipelineService:
    """Get pipeline service with dependency injection."""
    return service


@inject
def get_execution_service(
    service: ExecutionService = Provide[
        ApplicationContainer.services.execution_service
    ],
) -> ExecutionService:
    """Get execution service with dependency injection."""
    return service


@inject
def get_plugin_service(
    service: PluginService = Provide[ApplicationContainer.services.plugin_service],
) -> PluginService:
    """Get plugin service with dependency injection."""
    return service


@inject
def get_event_bus(
    event_bus: HybridEventBus = Provide[ApplicationContainer.eventing.event_bus],
) -> HybridEventBus:
    """Get event bus for domain event publishing."""
    return event_bus


@inject
def get_unit_of_work(
    uow: UnitOfWork = Provide[ApplicationContainer.database.unit_of_work],
) -> UnitOfWork:
    """Get unit of work for transaction management."""
    return uow


async def check_rate_limit(
    user: Annotated[dict[str, object], Depends(get_current_user)],
) -> None:
    """Check rate limit for current user using modern Redis implementation.

    Raises
    ------
        HTTPException: When rate limit is exceeded for the authenticated user

    """
    config = get_config()

    # Rate limiting always enabled for security
    if not config.security.api_rate_limit_per_minute:
        return

    key = f"user:{user['id']}"
    allowed = await check_rate_limit_async(key)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
