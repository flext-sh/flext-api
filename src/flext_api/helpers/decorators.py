"""FLEXT-API Decorators for Massive Code Reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Powerful decorators that eliminate repetitive FastAPI route code.
"""

from __future__ import annotations

import functools
import time
import warnings
from typing import TYPE_CHECKING, Any, ParamSpec, TypeVar

from fastapi import HTTPException, Request, status
from flext_core import FlextResult, get_logger
from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


def flext_api_handle_errors(
    *,
    default_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    log_errors: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to handle exceptions and convert to HTTP responses.

    Eliminates try/catch boilerplate in every route handler.

    Args:
        default_status: Default HTTP status for unhandled errors
        log_errors: Whether to log errors

    Example:
        @handle_errors(default_status=400)
        async def my_route():
            # No need for try/catch - decorator handles it
            result = risky_operation()
            return result

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                result = await func(*args, **kwargs)

                # Handle FlextResult automatically
                if isinstance(result, FlextResult):
                    if not result.success:
                        if log_errors:
                            logger.warning(f"Operation failed: {result.error}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST, detail=result.error
                        )
                    return result.data

                return result

            except HTTPException:
                raise
            except ValidationError as e:
                if log_errors:
                    logger.warning(f"Validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
                ) from e
            except Exception as e:
                if log_errors:
                    logger.exception("Unhandled error in route")
                raise HTTPException(status_code=default_status, detail=str(e)) from e

        return wrapper

    return decorator


def flext_api_log_execution(
    *,
    log_args: bool = False,
    log_result: bool = False,
    log_duration: bool = True,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to log function execution.

    Eliminates manual logging boilerplate.

    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        log_duration: Whether to log execution duration

    Example:
        @log_execution(log_duration=True)
        async def slow_operation():
            # Automatically logs execution time
            pass

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            start_time = time.time()
            func_name = f"{func.__module__}.{func.__name__}"

            if log_args:
                logger.debug(f"Executing {func_name} with args={args}, kwargs={kwargs}")
            else:
                logger.debug(f"Executing {func_name}")

            try:
                result = await func(*args, **kwargs)

                duration = time.time() - start_time
                if log_duration:
                    logger.info(f"{func_name} completed in {duration:.3f}s")

                if log_result:
                    logger.debug(f"{func_name} result: {result}")

                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.exception(f"{func_name} failed after {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


def flext_api_validate_request(
    model: type[BaseModel],
    *,
    source: str = "json",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to validate request data against Pydantic model.

    Eliminates manual validation boilerplate.

    Args:
        model: Pydantic model to validate against
        source: Source of data ('json', 'form', 'query')

    Example:
        @validate_request(UserCreateRequest)
        async def create_user(request: Request):
            # request.validated_data contains validated UserCreateRequest
            user_data = request.validated_data
            return create_user_service(user_data)

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Find Request object in arguments
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request validation decorator requires Request parameter",
                )

            try:
                # Get data based on source
                if source == "json":
                    data = await request.json()
                elif source == "form":
                    form_data = await request.form()
                    data = dict(form_data)
                elif source == "query":
                    data = dict(request.query_params)
                else:
                    raise ValueError(f"Unsupported source: {source}")

                # Validate data
                validated_data = model(**data)

                # Attach validated data to request
                request.validated_data = validated_data

                return await func(*args, **kwargs)

            except ValidationError as e:
                logger.warning(f"Request validation failed: {e}")
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.errors()
                ) from e

        return wrapper

    return decorator


def flext_api_require_json() -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to require JSON content type.

    Eliminates manual content-type checking.

    Example:
        @require_json()
        async def api_endpoint(request: Request):
            # Guaranteed to have JSON content-type
            data = await request.json()
            return process_data(data)

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Find Request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="require_json decorator requires Request parameter",
                )

            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Content-Type must be application/json",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def flext_api_rate_limit(
    *,
    calls: int = 100,
    period: int = 60,
    key_func: Callable[[Request], str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator for rate limiting endpoints.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds
        key_func: Function to generate rate limit key from request

    Example:
        @rate_limit(calls=10, period=60)
        async def expensive_operation():
            # Limited to 10 calls per minute
            pass

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        # Simple in-memory rate limiter (production should use Redis)
        call_history: dict[str, list[float]] = {}

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Find Request object in args or kwargs
            request = None

            # Check positional arguments
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # Check keyword arguments
            if not request:
                for value in kwargs.values():
                    if isinstance(value, Request):
                        request = value
                        break

            if not request:
                return await func(*args, **kwargs)

            # Generate key
            if key_func:
                key = key_func(request)
            else:
                key = request.client.host if request.client else "unknown"

            now = time.time()

            # Clean old calls
            if key in call_history:
                call_history[key] = [
                    call_time
                    for call_time in call_history[key]
                    if now - call_time < period
                ]
            else:
                call_history[key] = []

            # DEBUG: Print current state
            logger.debug(
                f"Rate limit check: key={key}, current_calls={len(call_history[key])}, limit={calls}"
            )

            # Check rate limit
            if len(call_history[key]) >= calls:
                logger.warning(
                    f"Rate limit exceeded for key={key}: {len(call_history[key])} >= {calls}"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {calls} calls per {period} seconds",
                )

            # Record this call
            call_history[key].append(now)
            logger.debug(
                f"Recorded call for key={key}, total_calls={len(call_history[key])}"
            )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def flext_api_cache_response(
    *,
    ttl: int = 300,
    key_func: Callable[..., str] | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to cache response data.

    Args:
        ttl: Time to live in seconds
        key_func: Function to generate cache key

    Example:
        @cache_response(ttl=600)
        async def get_expensive_data():
            # Response cached for 10 minutes
            return expensive_computation()

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        # Simple in-memory cache (production should use Redis)
        cache: dict[str, tuple[float, Any]] = {}

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            now = time.time()

            # Check cache
            if key in cache:
                cached_time, cached_result = cache[key]
                if now - cached_time < ttl:
                    logger.debug(f"Cache hit for {key}")
                    return cached_result
                del cache[key]

            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[key] = (now, result)
            logger.debug(f"Cached result for {key}")

            return result

        return wrapper

    return decorator


def flext_api_authenticated(
    *,
    token_header: str = "Authorization",
    token_prefix: str = "Bearer ",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """FlextApi decorator to require authentication.

    Validates JWT tokens using flext-auth integration.

    Args:
        token_header: Header name for token
        token_prefix: Token prefix (e.g., "Bearer ")

    Example:
        @flext_api_authenticated()
        async def protected_endpoint(request: Request):
            # request.user contains authenticated user info
            user = request.user
            return {"user_id": user.id}

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Find Request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication decorator requires Request parameter",
                )

            # Extract token
            auth_header = request.headers.get(token_header)
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not auth_header.startswith(token_prefix):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token format",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = auth_header[len(token_prefix) :]
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Empty authentication token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Validate token using flext-auth patterns
            try:
                from flext_api.infrastructure.ports import FlextJWTAuthService

                auth_service = FlextJWTAuthService()
                result = auth_service.validate_token(token)

                if not result.success:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid or expired token",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

                # Attach user info to request
                request.user = result.data
                logger.debug(
                    f"Authenticated user: {result.data.get('user_id', 'unknown')}"
                )

                return await func(*args, **kwargs)

            except ImportError:
                logger.exception(
                    "FlextJWTAuthService not available - authentication failed"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication service unavailable",
                ) from None
            except Exception as e:
                logger.exception(f"Authentication error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from e

        return wrapper

    return decorator


def flext_api_authorize_roles(
    *roles: str,
    token_header: str = "Authorization",
    token_prefix: str = "Bearer ",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """FlextApi decorator to require specific roles.

    Combines authentication with role-based authorization.

    Args:
        roles: Required roles
        token_header: Header name for token
        token_prefix: Token prefix

    Example:
        @flext_api_authorize_roles("REDACTED_LDAP_BIND_PASSWORD", "moderator")
        async def REDACTED_LDAP_BIND_PASSWORD_endpoint(request: Request):
            # Only REDACTED_LDAP_BIND_PASSWORD or moderator can access
            user = request.user
            return {"REDACTED_LDAP_BIND_PASSWORD_action": "completed"}

    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # First ensure authentication
            auth_wrapper = flext_api_authenticated(
                token_header=token_header, token_prefix=token_prefix
            )(func)

            # Execute authentication
            result = await auth_wrapper(*args, **kwargs)

            # Find Request object for role validation
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request or not hasattr(request, "user"):
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authorization decorator requires authenticated user",
                )

            # Check roles
            user_roles = request.user.get("roles", [])
            if isinstance(user_roles, str):
                user_roles = [user_roles]

            if not any(role in user_roles for role in roles):
                logger.warning(
                    f"Access denied: user roles {user_roles} do not match required {roles}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {', '.join(roles)}",
                )

            logger.debug(f"Authorized user with roles {user_roles} for endpoint")
            return result

        return wrapper

    return decorator


# ===== LEGACY COMPATIBILITY WITH DEPRECATION WARNINGS =====


def _auth_deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue deprecation warning for auth decorators."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


def authenticated(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("authenticated", "flext_api_authenticated")
    return flext_api_authenticated(*args, **kwargs)


def authorize_roles(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("authorize_roles", "flext_api_authorize_roles")
    return flext_api_authorize_roles(*args, **kwargs)


def handle_errors(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("handle_errors", "flext_api_handle_errors")
    return flext_api_handle_errors(*args, **kwargs)


def log_execution(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("log_execution", "flext_api_log_execution")
    return flext_api_log_execution(*args, **kwargs)


def validate_request(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("validate_request", "flext_api_validate_request")
    return flext_api_validate_request(*args, **kwargs)


def require_json(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("require_json", "flext_api_require_json")
    return flext_api_require_json(*args, **kwargs)


def rate_limit(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("rate_limit", "flext_api_rate_limit")
    return flext_api_rate_limit(*args, **kwargs)


def cache_response(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _auth_deprecation_warning("cache_response", "flext_api_cache_response")
    return flext_api_cache_response(*args, **kwargs)
