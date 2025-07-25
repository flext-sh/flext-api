"""FLEXT-API Middleware for FastAPI Applications.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Reusable middleware classes for common API functionality.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import Request, Response
from flext_core import get_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)


class FlextLoggingMiddleware(BaseHTTPMiddleware):
    """Request and response logging middleware."""

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
        """Process request and response with logging."""
        start_time = time.time()
        request_id = f"{int(start_time * 1000000)}"

        # Log request
        if self.log_requests:
            await self._log_request(request, request_id)

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        if self.log_responses:
            await self._log_response(request, response, request_id, duration)

        return response

    async def _log_request(self, request: Request, request_id: str) -> None:
        """Log incoming request."""
        client_ip = request.client.host if request.client else "unknown"

        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "headers": dict(request.headers),
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

        logger.info("Incoming request", extra=log_data)

    async def _log_response(
        self,
        request: Request,
        response: Response,
        request_id: str,
        duration: float,
    ) -> None:
        """Log outgoing response."""
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_headers": dict(response.headers),
        }

        logger.info("Outgoing response", extra=log_data)


class FlextSecurityMiddleware(BaseHTTPMiddleware):
    """Security headers middleware."""

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

        # Add security headers
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


class FlextRateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""

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
        """Apply rate limiting."""
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
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {self.limit} requests per {self.window} seconds"
            )

        # Record this request
        self.call_history[key].append(now)

        return await call_next(request)


class FlextCORSMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS middleware with better defaults."""

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
        """Handle CORS."""
        origin = request.headers.get("origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.status_code = 200
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
