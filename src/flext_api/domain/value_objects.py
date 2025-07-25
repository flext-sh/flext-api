"""Value objects for FLEXT-API.

REFACTORED:
Uses flext-core FlextValueObject - NO duplication.
"""

from __future__ import annotations

# Import ONLY what actually exists in flext-core
from flext_core import FlextValidationError, FlextValueObject

# Field comes from pydantic, NOT flext-core
from pydantic import Field, field_validator


class ApiEndpoint(FlextValueObject):
    """API endpoint value object with validation."""

    path: str = Field(
        ...,
        min_length=1,
        description="API endpoint path",
    )
    method: str = Field(
        default="GET",
        pattern=r"^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$",
        description="HTTP method",
    )

    @field_validator("path")
    @classmethod
    def validate_path_format(cls, v: str) -> str:
        """Validate and normalize path format.

        Args:
            v: Path value to validate.,

        Returns:
            Normalized path with leading slash.

        """
        if not v.startswith("/"):
            return f"/{v}"
        return v

    @property
    def full_path(self) -> str:
        """Get full HTTP method and path.

        Returns:
            Combined HTTP method and path string.

        """
        return f"{self.method} {self.path}"

    @field_validator("method")
    @classmethod
    def validate_method_uppercase(cls, v: str) -> str:
        """Ensure HTTP method is uppercase.

        Args:
            v: HTTP method to validate.,

        Returns:
            Uppercase HTTP method.

        """
        return v.upper()

    @property
    def is_safe_method(self) -> bool:
        """Check if HTTP method is safe.

        Returns:
            True if method is safe (GET, HEAD, OPTIONS).

        """
        return self.method in {"GET", "HEAD", "OPTIONS"}

    @property
    def is_idempotent(self) -> bool:
        """Check if HTTP method is idempotent.

        Returns:
            True if method is idempotent.

        """
        return self.method in {"GET", "HEAD", "PUT", "DELETE", "OPTIONS"}

    def validate_domain_rules(self) -> None:
        """Validate ApiEndpoint domain rules."""
        if not self.path or not self.path.strip():
            msg = "Endpoint path cannot be empty"
            raise FlextValidationError(msg)

        if not self.path.startswith("/"):
            msg = "Endpoint path must start with '/'"
            raise FlextValidationError(msg)


class RateLimit(FlextValueObject):
    """Rate limit configuration value object."""

    requests_per_minute: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum requests per minute",
    )
    burst_size: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Maximum burst size",
    )

    @property
    def requests_per_second(self) -> float:
        """Calculate requests per second from per minute.

        Returns:
            Maximum requests allowed per second.

        """
        return self.requests_per_minute / 60

    @property
    def is_strict_limit(self) -> bool:
        """Check if rate limit is strict.

        Returns:
            True if burst size is small (strict).

        """
        return self.burst_size <= 5

    @property
    def window_seconds(self) -> int:
        """Get rate limit window in seconds.

        Returns:
            Rate limit window duration in seconds.

        """
        return 60

    def validate_domain_rules(self) -> None:
        """Validate RateLimit domain rules."""
        if self.requests_per_minute <= 0:
            msg = "Requests per minute must be positive"
            raise FlextValidationError(msg)

        if self.burst_size <= 0:
            msg = "Burst size must be positive"
            raise FlextValidationError(msg)

        if self.burst_size > self.requests_per_minute:
            msg = "Burst size cannot exceed requests per minute"
            raise FlextValidationError(msg)


class ApiVersion(FlextValueObject):
    """API version value object with validation."""

    major: int = Field(default=1, ge=0, description="Major version")
    minor: int = Field(default=0, ge=0, description="Minor version")
    patch: int = Field(default=0, ge=0, description="Patch version")

    @property
    def version_string(self) -> str:
        """Get formatted version string.

        Returns:
            Version in major.minor.patch format.

        """
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def is_stable(self) -> bool:
        """Check if version is stable.

        Returns:
            True if major version >= 1.

        """
        return self.major >= 1

    @field_validator("major", "minor", "patch")
    @classmethod
    def validate_version_numbers(cls, v: int) -> int:
        """Validate version number components.

        Args:
            v: Version number to validate.,

        Returns:
            Validated version number.

        Raises:
            ValueError: If version number is negative.,

        """
        if v < 0:
            msg = "Version number cannot be negative"
            raise FlextValidationError(msg)
        return v

    def is_compatible_with(self, other: ApiVersion) -> bool:
        """Check if this version is compatible with another.

        Args:
            other: Version to check compatibility with.,

        Returns:
            True if major versions match.

        """
        return self.major == other.major

    def is_newer_than(self, other: ApiVersion) -> bool:
        """Check if this version is newer than another.

        Args:
            other: Version to compare with.,

        Returns:
            True if this version is newer.

        """
        return (
            self.major > other.major
            or (self.major == other.major and self.minor > other.minor)
            or (
                self.major == other.major
                and self.minor == other.minor
                and self.patch > other.patch
            )
        )

    def validate_domain_rules(self) -> None:
        """Validate ApiVersion domain rules."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            msg = "Version components cannot be negative"
            raise FlextValidationError(msg)


class CorsOrigin(FlextValueObject):
    """CORS origin value object with validation."""

    url: str = Field(..., description="CORS origin URL")

    @field_validator("url")
    @classmethod
    def validate_origin_format(cls, v: str) -> str:
        """Validate CORS origin format.

        Args:
            v: Origin value to validate.,

        Returns:
            Validated origin.

        Raises:
            ValueError: If origin format is invalid.,

        """
        if v == "*":
            return v

        # Basic URL validation
        if not (v.startswith(("http://", "https://"))):
            msg = "Origin must start with http:// or https://"
            raise FlextValidationError(msg)

        # Remove trailing slash
        return v.rstrip("/")

    def validate_domain_rules(self) -> None:
        """Validate CorsOrigin domain rules."""
        # Basic validation - can be enhanced per specific needs
        return


class ApiKey(FlextValueObject):
    """API key value object with validation."""

    key: str = Field(..., min_length=16, description="API key value")

    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v: str) -> str:
        """Validate API key format and security.

        Args:
            v: API key to validate.,

        Returns:
            Validated API key.

        Raises:
            ValueError: If key format is invalid or insecure.,

        """
        # Minimum length validation
        if len(v) < 16:
            msg = "API key must be at least 16 characters long"
            raise FlextValidationError(msg)

        # Must be alphanumeric with optional hyphens
        if not v.replace("-", "").isalnum():
            msg = "API key must contain only alphanumeric characters and hyphens"
            raise FlextValidationError(msg)

        return v

    @property
    def masked(self) -> str:
        """Get masked version of API key.

        Returns:
            Masked API key for safe display.

        """
        if len(self.key) < 8:
            return "***"
        return f"{self.key[:4]}...{self.key[-4:]}"

    def validate_domain_rules(self) -> None:
        """Validate ApiKey domain rules."""
        # Basic validation - can be enhanced per specific needs
        return


class RequestTimeout(FlextValueObject):
    """Request timeout configuration value object."""

    value: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Request timeout in seconds",
    )

    @field_validator("value")
    @classmethod
    def validate_timeout_range(cls, v: int) -> int:
        """Validate timeout is within acceptable range.

        Args:
            v: Timeout value to validate.,

        Returns:
            Validated timeout value.

        Raises:
            ValueError: If timeout is out of acceptable range.,

        """
        if not 1 <= v <= 300:
            msg = "Timeout must be between 1 and 300 seconds"
            raise FlextValidationError(msg)
        return v

    def validate_domain_rules(self) -> None:
        """Validate RequestTimeout domain rules."""
        # Basic validation - can be enhanced per specific needs
        return


class PipelineId(FlextValueObject):
    """Pipeline identifier value object."""

    value: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Pipeline unique identifier",
    )

    @field_validator("value")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate pipeline ID format.

        Args:
            v: Pipeline ID to validate.,

        Returns:
            Validated pipeline ID.

        """
        return v.strip()

    def validate_domain_rules(self) -> None:
        """Validate PipelineId domain rules."""
        # Basic validation - can be enhanced per specific needs
        return


class PluginId(FlextValueObject):
    """Plugin identifier value object."""

    value: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Plugin unique identifier",
    )

    @field_validator("value")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate plugin ID format.

        Args:
            v: Plugin ID to validate.,

        Returns:
            Validated plugin ID.

        """
        return v.strip()

    def validate_domain_rules(self) -> None:
        """Validate PluginId domain rules."""
        # Basic validation - can be enhanced per specific needs
        return


class RequestId(FlextValueObject):
    """Request identifier value object."""

    value: str = Field(
        ...,
        min_length=1,
        max_length=200,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Request unique identifier",
    )

    @field_validator("value")
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """Validate request ID format.

        Args:
            v: Request ID to validate.,

        Returns:
            Validated request ID.

        """
        return v.strip()

    def validate_domain_rules(self) -> None:
        """Validate RequestId domain rules."""
        # Basic validation - can be enhanced per specific needs
        return
