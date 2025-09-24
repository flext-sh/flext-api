"""FLEXT API Configuration - Settings using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from flext_api.constants import FlextApiConstants
from flext_core import FlextConfig, FlextConstants


class FlextApiConfig(FlextConfig):
    """FLEXT API Configuration class.

    Provides comprehensive configuration for FLEXT API operations including
    logging, performance tracking, security settings, and CORS configuration.
    Uses Pydantic BaseSettings for validation and environment variable support.
    """

    # Inherits model_config from FlextConfig with FLEXT_API_ prefix

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
        default=FlextApiConstants.Logging.LOG_REQUESTS,
        description="Log API requests",
    )

    log_responses: bool = Field(
        default=FlextApiConstants.Logging.LOG_RESPONSES,
        description="Log API responses",
    )

    log_request_body: bool = Field(
        default=FlextApiConstants.Logging.LOG_REQUEST_BODY,
        description="Log request body content",
    )

    log_response_body: bool = Field(
        default=FlextApiConstants.Logging.LOG_RESPONSE_BODY,
        description="Log response body content",
    )

    log_request_headers: bool = Field(
        default=FlextApiConstants.Logging.LOG_REQUEST_HEADERS,
        description="Log request headers",
    )

    log_response_headers: bool = Field(
        default=FlextApiConstants.Logging.LOG_RESPONSE_HEADERS,
        description="Log response headers",
    )

    log_query_parameters: bool = Field(
        default=FlextApiConstants.Logging.LOG_QUERY_PARAMETERS,
        description="Log query parameters",
    )

    log_path_parameters: bool = Field(
        default=FlextApiConstants.Logging.LOG_PATH_PARAMETERS,
        description="Log path parameters",
    )

    # Performance tracking for API operations
    track_api_performance: bool = Field(
        default=FlextApiConstants.Logging.TRACK_API_PERFORMANCE,
        description="Track API performance metrics",
    )

    api_performance_threshold_warning: float = Field(
        default=FlextApiConstants.Logging.API_PERFORMANCE_THRESHOLD_WARNING,
        description="API performance warning threshold in milliseconds",
    )

    api_performance_threshold_critical: float = Field(
        default=FlextApiConstants.Logging.API_PERFORMANCE_THRESHOLD_CRITICAL,
        description="API performance critical threshold in milliseconds",
    )

    track_response_size: bool = Field(
        default=FlextApiConstants.Logging.TRACK_RESPONSE_SIZE,
        description="Track response size metrics",
    )

    large_response_threshold: int = Field(
        default=FlextApiConstants.Logging.LARGE_RESPONSE_THRESHOLD,
        description="Large response size threshold in bytes",
    )

    # Security logging
    log_authentication_headers: bool = Field(
        default=FlextApiConstants.Logging.LOG_AUTHENTICATION_HEADERS,
        description="Log authentication headers",
    )

    log_sensitive_headers: bool = Field(
        default=FlextApiConstants.Logging.LOG_SENSITIVE_HEADERS,
        description="Log sensitive headers",
    )

    mask_api_keys: bool = Field(
        default=FlextApiConstants.Logging.MASK_API_KEYS,
        description="Mask API keys in log messages",
    )

    mask_authorization_headers: bool = Field(
        default=FlextApiConstants.Logging.MASK_AUTHORIZATION_HEADERS,
        description="Mask authorization headers in log messages",
    )

    log_rate_limiting: bool = Field(
        default=FlextApiConstants.Logging.LOG_RATE_LIMITING,
        description="Log rate limiting events",
    )

    log_access_control: bool = Field(
        default=FlextApiConstants.Logging.LOG_ACCESS_CONTROL,
        description="Log access control events",
    )

    # Error logging
    log_4xx_errors: bool = Field(
        default=FlextApiConstants.Logging.LOG_4XX_ERRORS,
        description="Log 4xx client errors",
    )

    log_5xx_errors: bool = Field(
        default=FlextApiConstants.Logging.LOG_5XX_ERRORS,
        description="Log 5xx server errors",
    )

    log_validation_errors: bool = Field(
        default=FlextApiConstants.Logging.LOG_VALIDATION_ERRORS,
        description="Log validation errors",
    )

    log_business_logic_errors: bool = Field(
        default=FlextApiConstants.Logging.LOG_BUSINESS_LOGIC_ERRORS,
        description="Log business logic errors",
    )

    log_external_service_errors: bool = Field(
        default=FlextApiConstants.Logging.LOG_EXTERNAL_SERVICE_ERRORS,
        description="Log external service errors",
    )

    # Context information to include in logs
    include_request_id: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_REQUEST_ID,
        description="Include request ID in log messages",
    )

    include_correlation_id: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_CORRELATION_ID,
        description="Include correlation ID in log messages",
    )

    include_user_id: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_USER_ID,
        description="Include user ID in log messages",
    )

    include_client_ip: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_CLIENT_IP,
        description="Include client IP address in log messages",
    )

    include_user_agent: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_USER_AGENT,
        description="Include user agent in log messages",
    )

    include_api_version: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_API_VERSION,
        description="Include API version in log messages",
    )

    include_endpoint: bool = Field(
        default=FlextApiConstants.Logging.INCLUDE_ENDPOINT,
        description="Include endpoint in log messages",
    )

    # Audit logging
    enable_api_audit_logging: bool = Field(
        default=FlextApiConstants.Logging.ENABLE_API_AUDIT_LOGGING,
        description="Enable API audit logging",
    )

    audit_log_level: str = Field(
        default=FlextApiConstants.Logging.AUDIT_LOG_LEVEL,
        description="API audit log level",
    )

    audit_log_file: str = Field(
        default=FlextApiConstants.Logging.AUDIT_LOG_FILE,
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
