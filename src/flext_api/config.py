"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_core import FlextConstants


class FlextApiLoggingConstants:
    """API-specific logging constants for FLEXT API module.

    Provides domain-specific logging defaults, levels, and configuration
    options tailored for API operations, request/response logging, and
    API performance monitoring.
    """

    # API-specific log levels
    DEFAULT_LEVEL = FlextConstants.Config.LogLevel.INFO
    REQUEST_LEVEL = FlextConstants.Config.LogLevel.INFO
    RESPONSE_LEVEL = FlextConstants.Config.LogLevel.INFO
    ERROR_LEVEL = FlextConstants.Config.LogLevel.ERROR
    PERFORMANCE_LEVEL = FlextConstants.Config.LogLevel.WARNING
    SECURITY_LEVEL = FlextConstants.Config.LogLevel.WARNING

    # Request/Response logging configuration
    LOG_REQUESTS = True
    LOG_RESPONSES = True
    LOG_REQUEST_BODY = False  # Don't log request body by default (privacy/security)
    LOG_RESPONSE_BODY = False  # Don't log response body by default
    LOG_REQUEST_HEADERS = True
    LOG_RESPONSE_HEADERS = False  # Don't log response headers by default
    LOG_QUERY_PARAMETERS = True
    LOG_PATH_PARAMETERS = True

    # Performance tracking for API operations
    TRACK_API_PERFORMANCE = True
    API_PERFORMANCE_THRESHOLD_WARNING = 1000.0  # 1 second
    API_PERFORMANCE_THRESHOLD_CRITICAL = 5000.0  # 5 seconds
    TRACK_RESPONSE_SIZE = True
    LARGE_RESPONSE_THRESHOLD = 1024 * 1024  # 1MB

    # Security logging
    LOG_AUTHENTICATION_HEADERS = False  # Don't log auth headers
    LOG_SENSITIVE_HEADERS = False
    MASK_API_KEYS = True
    MASK_AUTHORIZATION_HEADERS = True
    LOG_RATE_LIMITING = True
    LOG_ACCESS_CONTROL = True

    # Error logging specifics
    LOG_4XX_ERRORS = True
    LOG_5XX_ERRORS = True
    LOG_VALIDATION_ERRORS = True
    LOG_BUSINESS_LOGIC_ERRORS = True
    LOG_EXTERNAL_SERVICE_ERRORS = True

    # Context information to include
    INCLUDE_REQUEST_ID = True
    INCLUDE_CORRELATION_ID = True
    INCLUDE_USER_ID = True
    INCLUDE_CLIENT_IP = True
    INCLUDE_USER_AGENT = False  # Privacy consideration
    INCLUDE_API_VERSION = True
    INCLUDE_ENDPOINT = True

    # Audit logging
    ENABLE_API_AUDIT_LOGGING = True
    AUDIT_LOG_LEVEL = FlextConstants.Config.LogLevel.INFO
    AUDIT_LOG_FILE = "flext_api_audit.log"

    # Message templates for API operations
    class Messages:
        """API-specific log message templates."""

        # Request/Response messages
        REQUEST_RECEIVED = "API request received: {method} {endpoint} from {client_ip}"
        REQUEST_PROCESSING = "Processing API request: {request_id} {method} {endpoint}"
        RESPONSE_SENT = (
            "API response sent: {status_code} {method} {endpoint} in {duration}ms"
        )
        REQUEST_COMPLETED = (
            "API request completed: {request_id} {status_code} {duration}ms"
        )

        # Error messages
        REQUEST_ERROR = "API request error: {error} for {method} {endpoint}"
        VALIDATION_ERROR = "API validation error: {error} for {method} {endpoint}"
        BUSINESS_LOGIC_ERROR = (
            "API business logic error: {error} for {method} {endpoint}"
        )
        EXTERNAL_SERVICE_ERROR = (
            "External service error: {error} for {method} {endpoint}"
        )

        # Performance messages
        SLOW_REQUEST = "Slow API request: {method} {endpoint} took {duration}ms"
        LARGE_RESPONSE = "Large API response: {method} {endpoint} {size} bytes"
        HIGH_MEMORY_USAGE = (
            "High memory usage for API request: {method} {endpoint} {memory}MB"
        )

        # Security messages
        UNAUTHORIZED_ACCESS = (
            "Unauthorized API access attempt: {method} {endpoint} from {client_ip}"
        )
        RATE_LIMIT_EXCEEDED = "Rate limit exceeded: {client_ip} for {method} {endpoint}"
        SUSPICIOUS_REQUEST = (
            "Suspicious API request: {method} {endpoint} from {client_ip}"
        )

        # Authentication messages
        AUTH_REQUIRED = "Authentication required for API request: {method} {endpoint}"
        AUTH_SUCCESS = (
            "API authentication successful: {user_id} for {method} {endpoint}"
        )
        AUTH_FAILED = "API authentication failed: {reason} for {method} {endpoint}"

        # Service messages
        SERVICE_STARTED = "API service started on {host}:{port}"
        SERVICE_STOPPED = "API service stopped"
        SERVICE_ERROR = "API service error: {error}"
        HEALTH_CHECK = "API health check: {status}"

        # Middleware messages
        MIDDLEWARE_PROCESSING = (
            "Middleware processing: {middleware} for {method} {endpoint}"
        )
        MIDDLEWARE_ERROR = (
            "Middleware error: {middleware} {error} for {method} {endpoint}"
        )

    class Environment:
        """Environment-specific API logging configuration."""

        DEVELOPMENT: ClassVar[dict[str, object]] = {
            "log_request_body": True,  # Log request body in dev
            "log_response_body": True,  # Log response body in dev
            "log_response_headers": True,  # Log response headers in dev
            "include_user_agent": True,  # Include user agent in dev
            "audit_log_level": FlextConstants.Config.LogLevel.DEBUG,
        }

        STAGING: ClassVar[dict[str, object]] = {
            "log_request_body": False,
            "log_response_body": False,
            "log_response_headers": False,
            "include_user_agent": False,
            "audit_log_level": FlextConstants.Config.LogLevel.INFO,
        }

        PRODUCTION: ClassVar[dict[str, object]] = {
            "log_request_body": False,
            "log_response_body": False,
            "log_response_headers": False,
            "include_user_agent": False,
            "audit_log_level": FlextConstants.Config.LogLevel.WARNING,
        }

        TESTING: ClassVar[dict[str, object]] = {
            "log_request_body": True,
            "log_response_body": True,
            "log_response_headers": True,
            "include_user_agent": True,
            "audit_log_level": FlextConstants.Config.LogLevel.DEBUG,
        }


class FlextApiConfig(BaseSettings):
    """FLEXT API Configuration class.

    Provides comprehensive configuration for FLEXT API operations including
    logging, performance tracking, security settings, and CORS configuration.
    Uses Pydantic BaseSettings for validation and environment variable support.
    """

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_API_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API configuration
    api_base_url: str = Field(
        default="http://localhost:8000", description="Base URL for API"
    )
    api_timeout: int = Field(default=30, description="API timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")

    # CORS configuration
    cors_origins: ClassVar[list[str]] = ["*"]
    cors_methods: ClassVar[list[str]] = ["GET", "POST", "PUT", "DELETE"]
    cors_headers: ClassVar[list[str]] = [
        FlextConstants.Platform.HEADER_CONTENT_TYPE,
        FlextConstants.Platform.HEADER_AUTHORIZATION,
    ]
    cors_allow_credentials: bool = True

    # API-specific logging configuration using FlextApiLoggingConstants
    log_requests: bool = Field(
        default=FlextApiLoggingConstants.LOG_REQUESTS,
        description="Log API requests",
    )

    log_responses: bool = Field(
        default=FlextApiLoggingConstants.LOG_RESPONSES,
        description="Log API responses",
    )

    log_request_body: bool = Field(
        default=FlextApiLoggingConstants.LOG_REQUEST_BODY,
        description="Log request body content",
    )

    log_response_body: bool = Field(
        default=FlextApiLoggingConstants.LOG_RESPONSE_BODY,
        description="Log response body content",
    )

    log_request_headers: bool = Field(
        default=FlextApiLoggingConstants.LOG_REQUEST_HEADERS,
        description="Log request headers",
    )

    log_response_headers: bool = Field(
        default=FlextApiLoggingConstants.LOG_RESPONSE_HEADERS,
        description="Log response headers",
    )

    log_query_parameters: bool = Field(
        default=FlextApiLoggingConstants.LOG_QUERY_PARAMETERS,
        description="Log query parameters",
    )

    log_path_parameters: bool = Field(
        default=FlextApiLoggingConstants.LOG_PATH_PARAMETERS,
        description="Log path parameters",
    )

    # Performance tracking for API operations
    track_api_performance: bool = Field(
        default=FlextApiLoggingConstants.TRACK_API_PERFORMANCE,
        description="Track API performance metrics",
    )

    api_performance_threshold_warning: float = Field(
        default=FlextApiLoggingConstants.API_PERFORMANCE_THRESHOLD_WARNING,
        description="API performance warning threshold in milliseconds",
    )

    api_performance_threshold_critical: float = Field(
        default=FlextApiLoggingConstants.API_PERFORMANCE_THRESHOLD_CRITICAL,
        description="API performance critical threshold in milliseconds",
    )

    track_response_size: bool = Field(
        default=FlextApiLoggingConstants.TRACK_RESPONSE_SIZE,
        description="Track response size metrics",
    )

    large_response_threshold: int = Field(
        default=FlextApiLoggingConstants.LARGE_RESPONSE_THRESHOLD,
        description="Large response size threshold in bytes",
    )

    # Security logging
    log_authentication_headers: bool = Field(
        default=FlextApiLoggingConstants.LOG_AUTHENTICATION_HEADERS,
        description="Log authentication headers",
    )

    log_sensitive_headers: bool = Field(
        default=FlextApiLoggingConstants.LOG_SENSITIVE_HEADERS,
        description="Log sensitive headers",
    )

    mask_api_keys: bool = Field(
        default=FlextApiLoggingConstants.MASK_API_KEYS,
        description="Mask API keys in log messages",
    )

    mask_authorization_headers: bool = Field(
        default=FlextApiLoggingConstants.MASK_AUTHORIZATION_HEADERS,
        description="Mask authorization headers in log messages",
    )

    log_rate_limiting: bool = Field(
        default=FlextApiLoggingConstants.LOG_RATE_LIMITING,
        description="Log rate limiting events",
    )

    log_access_control: bool = Field(
        default=FlextApiLoggingConstants.LOG_ACCESS_CONTROL,
        description="Log access control events",
    )

    # Error logging
    log_4xx_errors: bool = Field(
        default=FlextApiLoggingConstants.LOG_4XX_ERRORS,
        description="Log 4xx client errors",
    )

    log_5xx_errors: bool = Field(
        default=FlextApiLoggingConstants.LOG_5XX_ERRORS,
        description="Log 5xx server errors",
    )

    log_validation_errors: bool = Field(
        default=FlextApiLoggingConstants.LOG_VALIDATION_ERRORS,
        description="Log validation errors",
    )

    log_business_logic_errors: bool = Field(
        default=FlextApiLoggingConstants.LOG_BUSINESS_LOGIC_ERRORS,
        description="Log business logic errors",
    )

    log_external_service_errors: bool = Field(
        default=FlextApiLoggingConstants.LOG_EXTERNAL_SERVICE_ERRORS,
        description="Log external service errors",
    )

    # Context information to include in logs
    include_request_id: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_REQUEST_ID,
        description="Include request ID in log messages",
    )

    include_correlation_id: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_CORRELATION_ID,
        description="Include correlation ID in log messages",
    )

    include_user_id: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_USER_ID,
        description="Include user ID in log messages",
    )

    include_client_ip: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_CLIENT_IP,
        description="Include client IP address in log messages",
    )

    include_user_agent: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_USER_AGENT,
        description="Include user agent in log messages",
    )

    include_api_version: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_API_VERSION,
        description="Include API version in log messages",
    )

    include_endpoint: bool = Field(
        default=FlextApiLoggingConstants.INCLUDE_ENDPOINT,
        description="Include endpoint in log messages",
    )

    # Audit logging
    enable_api_audit_logging: bool = Field(
        default=FlextApiLoggingConstants.ENABLE_API_AUDIT_LOGGING,
        description="Enable API audit logging",
    )

    audit_log_level: str = Field(
        default=FlextApiLoggingConstants.AUDIT_LOG_LEVEL,
        description="API audit log level",
    )

    audit_log_file: str = Field(
        default=FlextApiLoggingConstants.AUDIT_LOG_FILE,
        description="API audit log file path",
    )

    def get_api_logging_config(self) -> dict[str, object]:
        """Get API-specific logging configuration dictionary."""
        return {
            "log_requests": self.log_requests,
            "log_responses": self.log_responses,
            "log_request_body": self.log_request_body,
            "log_response_body": self.log_response_body,
            "log_request_headers": self.log_request_headers,
            "log_response_headers": self.log_response_headers,
            "log_query_parameters": self.log_query_parameters,
            "log_path_parameters": self.log_path_parameters,
            "track_api_performance": self.track_api_performance,
            "api_performance_threshold_warning": self.api_performance_threshold_warning,
            "api_performance_threshold_critical": self.api_performance_threshold_critical,
            "track_response_size": self.track_response_size,
            "large_response_threshold": self.large_response_threshold,
            "log_authentication_headers": self.log_authentication_headers,
            "log_sensitive_headers": self.log_sensitive_headers,
            "mask_api_keys": self.mask_api_keys,
            "mask_authorization_headers": self.mask_authorization_headers,
            "log_rate_limiting": self.log_rate_limiting,
            "log_access_control": self.log_access_control,
            "log_4xx_errors": self.log_4xx_errors,
            "log_5xx_errors": self.log_5xx_errors,
            "log_validation_errors": self.log_validation_errors,
            "log_business_logic_errors": self.log_business_logic_errors,
            "log_external_service_errors": self.log_external_service_errors,
            "include_request_id": self.include_request_id,
            "include_correlation_id": self.include_correlation_id,
            "include_user_id": self.include_user_id,
            "include_client_ip": self.include_client_ip,
            "include_user_agent": self.include_user_agent,
            "include_api_version": self.include_api_version,
            "include_endpoint": self.include_endpoint,
            "enable_api_audit_logging": self.enable_api_audit_logging,
            "audit_log_level": self.audit_log_level,
            "audit_log_file": self.audit_log_file,
        }

    def get_default_headers(self) -> dict[str, str]:
        """Get default headers for API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "FlextApiClient/1.0.0",
        }


__all__ = [
    "FlextApiConfig",
]
