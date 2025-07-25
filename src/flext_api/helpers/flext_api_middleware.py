"""FlextApi Middleware - Middleware Enterprise para FastAPI.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Middleware reutilizável baseado em padrões flext-core.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request, Response
from flext_core import get_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)


class FlextApiLoggingMiddleware(BaseHTTPMiddleware):
    """Request and response logging middleware integrado com flext-observability."""

    def __init__(
        self,
        app: Any,
        *,
        log_requests: bool = True,
        log_responses: bool = True,
        log_body: bool = False,
        max_body_size: int = 1024,
    ) -> None:
        """Initialize logging middleware.

        Args:
            app: FastAPI application
            log_requests: Whether to log incoming requests
            log_responses: Whether to log outgoing responses
            log_body: Whether to log request/response body
            max_body_size: Maximum body size to log

        """
        super().__init__(app)
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_body = log_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Process request and response with logging integrado com flext-core."""
        start_time = time.time()
        request_id = f"flext_api_{int(start_time * 1000000)}"

        # Log request usando flext-core logger
        if self.log_requests:
            await self._flext_log_request(request, request_id)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response usando flext-core logger
        if self.log_responses:
            await self._flext_log_response(request, response, request_id, duration)

        return response

    async def _flext_log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request usando padrões flext-core."""
        client_ip = request.client.host if request.client else "unknown"

        log_data = {
            "flext_api_request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "headers": dict(request.headers),
            "flext_api_component": "middleware",
        }

        if self.log_body and request.method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    log_data["body"] = body.decode("utf-8")
                else:
                    log_data["body"] = f"<truncated: {len(body)} bytes>"
            except Exception as e:
                log_data["body_error"] = str(e)

        logger.info("FlextApi: Incoming request", extra=log_data)

    async def _flext_log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        duration: float,
    ) -> None:
        """Log outgoing response usando padrões flext-core."""
        log_data = {
            "flext_api_request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_headers": dict(response.headers),
            "flext_api_component": "middleware",
        }

        logger.info("FlextApi: Outgoing response", extra=log_data)


class FlextApiSecurityMiddleware(BaseHTTPMiddleware):
    """Security headers middleware com defaults enterprise."""

    def __init__(
        self,
        app: Any,
        *,
        enable_hsts: bool = True,
        enable_content_type_options: bool = True,
        enable_frame_options: bool = True,
        enable_xss_protection: bool = True,
        custom_headers: dict[str, str] | None = None,
    ) -> None:
        """Initialize security middleware.

        Args:
            app: FastAPI application
            enable_hsts: Enable HTTP Strict Transport Security
            enable_content_type_options: Enable X-Content-Type-Options
            enable_frame_options: Enable X-Frame-Options
            enable_xss_protection: Enable X-XSS-Protection
            custom_headers: Additional custom security headers

        """
        super().__init__(app)
        self.enable_hsts = enable_hsts
        self.enable_content_type_options = enable_content_type_options
        self.enable_frame_options = enable_frame_options
        self.enable_xss_protection = enable_xss_protection
        self.custom_headers = custom_headers or {}

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Add FlextApi security headers
        response.headers["X-Powered-By"] = "flext-api"

        # Add standard security headers
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        if self.enable_content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"

        if self.enable_frame_options:
            response.headers["X-Frame-Options"] = "DENY"

        if self.enable_xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"

        # Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value

        return response


class FlextApiRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware simples mas efetivo."""

    def __init__(
        self,
        app: Any,
        *,
        limit: int = 100,
        window: int = 60,
        key_func: Any = None,
    ) -> None:
        """Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            limit: Number of requests allowed
            window: Time window in seconds
            key_func: Function to generate rate limit key

        """
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.key_func = key_func or self._default_key_func
        self.call_history: dict[str, list[float]] = {}

    def _default_key_func(self, request: Request) -> str:
        """Default key function using client IP."""
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Apply rate limiting com logging flext-core."""
        key = self.key_func(request)
        now = time.time()

        # Clean old entries
        if key in self.call_history:
            self.call_history[key] = [
                call_time for call_time in self.call_history[key]
                if now - call_time < self.window
            ]
        else:
            self.call_history[key] = []

        # Check rate limit
        if len(self.call_history[key]) >= self.limit:
            logger.warning(
                f"FlextApi: Rate limit exceeded for {key}",
                extra={
                    "client_key": key,
                    "limit": self.limit,
                    "window": self.window,
                    "flext_api_component": "rate_limiter",
                }
            )

            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"FlextApi: Rate limit exceeded: {self.limit} requests per {self.window} seconds"
            )

        # Record this request
        self.call_history[key].append(now)

        return await call_next(request)


class FlextApiCORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware com defaults enterprise."""

    def __init__(
        self,
        app: Any,
        *,
        allow_origins: list[str] | None = None,
        allow_methods: list[str] | None = None,
        allow_headers: list[str] | None = None,
        allow_credentials: bool = True,
        expose_headers: list[str] | None = None,
        max_age: int = 600,
    ) -> None:
        """Initialize CORS middleware.

        Args:
            app: FastAPI application
            allow_origins: Allowed origins
            allow_methods: Allowed methods
            allow_headers: Allowed headers
            allow_credentials: Allow credentials
            expose_headers: Headers to expose to browser
            max_age: Preflight cache time

        """
        super().__init__(app)
        self.allow_origins = allow_origins or ["*"]
        self.allow_methods = allow_methods or ["*"]
        self.allow_headers = allow_headers or ["*"]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or []
        self.max_age = max_age

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Handle CORS com logging flext-core."""
        origin = request.headers.get("origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.status_code = 200
            logger.debug(
                f"FlextApi: CORS preflight request from {origin}",
                extra={"origin": origin, "flext_api_component": "cors"}
            )
        else:
            response = await call_next(request)

        # Add CORS headers
        if origin and self._is_allowed_origin(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allow_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"

        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"

        if self.allow_methods:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)

        if self.allow_headers:
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)

        response.headers["Access-Control-Max-Age"] = str(self.max_age)

        return response

    def _is_allowed_origin(self, origin: str) -> bool:
        """Check if origin is allowed."""
        return origin in self.allow_origins or "*" in self.allow_origins


class FlextApiMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware para coleta de métricas integrado com flext-observability."""

    def __init__(self, app: Any) -> None:
        """Initialize metrics middleware."""
        super().__init__(app)
        self.request_count = 0
        self.total_processing_time = 0.0
        self.status_code_counts: dict[int, int] = {}

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Collect metrics durante request processing."""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Update metrics
        duration = time.time() - start_time
        self.request_count += 1
        self.total_processing_time += duration

        status_code = response.status_code
        self.status_code_counts[status_code] = self.status_code_counts.get(status_code, 0) + 1

        # Log metrics usando flext-core
        if self.request_count % 100 == 0:  # Log every 100 requests
            avg_response_time = self.total_processing_time / self.request_count
            logger.info(
                f"FlextApi: Processed {self.request_count} requests",
                extra={
                    "request_count": self.request_count,
                    "avg_response_time_ms": round(avg_response_time * 1000, 2),
                    "status_code_distribution": self.status_code_counts,
                    "flext_api_component": "metrics",
                }
            )

        return response

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        avg_response_time = (
            self.total_processing_time / self.request_count if self.request_count > 0 else 0
        )

        return {
            "request_count": self.request_count,
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "total_processing_time_s": round(self.total_processing_time, 2),
            "status_code_distribution": self.status_code_counts.copy(),
        }
