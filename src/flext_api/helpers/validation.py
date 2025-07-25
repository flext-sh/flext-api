"""FlextValidator - Powerful Validation Utilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive validation utilities that reduce boilerplate code.
"""

from __future__ import annotations

import re
import uuid
import warnings
from typing import Any

from flext_core import FlextResult


class FlextApiValidator:
    """FlextApi powerful validation utility class.

    Provides chainable validation with detailed error messages.

    Example:
        validator = FlextApiValidator()
        result = (validator
                  .validate_required("email", email)
                  .validate_email("email", email)
                  .validate_min_length("password", password, 8)
                  .get_result())

        if not result.success:
            return {"errors": result.error}

    """

    def __init__(self) -> None:
        """Initialize validator."""
        self._errors: list[str] = []
        self._field_errors: dict[str, list[str]] = {}

    def validate_required(self, field: str, value: Any) -> FlextApiValidator:
        """Validate that a field is required (not None, empty, or whitespace)."""
        if value is None:
            self._add_error(field, f"{field} is required")
        elif (isinstance(value, str) and not value.strip()) or (
            isinstance(value, (list, dict)) and len(value) == 0
        ):
            self._add_error(field, f"{field} cannot be empty")
        return self

    def validate_email(self, field: str, value: str | None) -> FlextApiValidator:
        """Validate email format."""
        if value is None:
            return self

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, value):
            self._add_error(field, f"{field} must be a valid email address")
        return self

    def validate_password(self, field: str, value: str | None) -> FlextApiValidator:
        """Validate password strength."""
        if value is None:
            return self

        if len(value) < 8:
            self._add_error(field, f"{field} must be at least 8 characters long")

        if not re.search(r"[A-Z]", value):
            self._add_error(
                field, f"{field} must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            self._add_error(
                field, f"{field} must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            self._add_error(field, f"{field} must contain at least one digit")

        return self

    def validate_uuid(self, field: str, value: str | None) -> FlextApiValidator:
        """Validate UUID format."""
        if value is None:
            return self

        try:
            uuid.UUID(value)
        except ValueError:
            self._add_error(field, f"{field} must be a valid UUID")
        return self

    def validate_min_length(
        self, field: str, value: str | None, min_len: int
    ) -> FlextApiValidator:
        """Validate minimum length."""
        if value is None:
            return self

        if len(value) < min_len:
            self._add_error(
                field, f"{field} must be at least {min_len} characters long"
            )
        return self

    def validate_max_length(
        self, field: str, value: str | None, max_len: int
    ) -> FlextApiValidator:
        """Validate maximum length."""
        if value is None:
            return self

        if len(value) > max_len:
            self._add_error(
                field, f"{field} must be no more than {max_len} characters long"
            )
        return self

    def validate_range(
        self, field: str, value: float | None, min_val: float, max_val: float
    ) -> FlextApiValidator:
        """Validate numeric range."""
        if value is None:
            return self

        if value < min_val or value > max_val:
            self._add_error(field, f"{field} must be between {min_val} and {max_val}")
        return self

    def validate_choices(
        self, field: str, value: Any, choices: list[Any]
    ) -> FlextApiValidator:
        """Validate that value is in allowed choices."""
        if value is None:
            return self

        if value not in choices:
            self._add_error(
                field, f"{field} must be one of: {', '.join(map(str, choices))}"
            )
        return self

    def validate_regex(
        self, field: str, value: str | None, pattern: str, message: str | None = None
    ) -> FlextApiValidator:
        """Validate against regex pattern."""
        if value is None:
            return self

        if not re.match(pattern, value):
            error_msg = message or f"{field} format is invalid"
            self._add_error(field, error_msg)
        return self

    def validate_custom(
        self,
        field: str,
        value: Any,
        validator_func: callable,
        message: str | None = None,
    ) -> FlextApiValidator:
        """Validate using custom function."""
        if value is None:
            return self

        try:
            if not validator_func(value):
                error_msg = message or f"{field} is invalid"
                self._add_error(field, error_msg)
        except Exception as e:
            self._add_error(field, f"{field} validation failed: {e!s}")
        return self

    def _add_error(self, field: str, message: str) -> None:
        """Add validation error."""
        if field not in self._field_errors:
            self._field_errors[field] = []
        self._field_errors[field].append(message)
        self._errors.append(f"{field}: {message}")

    def has_errors(self) -> bool:
        """Check if there are any validation errors."""
        return len(self._errors) > 0

    def get_errors(self) -> list[str]:
        """Get all validation errors."""
        return self._errors.copy()

    def get_field_errors(self) -> dict[str, list[str]]:
        """Get validation errors grouped by field."""
        return self._field_errors.copy()

    def get_result(self) -> FlextResult[dict[str, Any]]:
        """Get validation result."""
        if self.has_errors():
            # Return the error details in the data field for failed validation
            return FlextResult[dict[str, Any]](
                success=False,
                error="Validation failed",
                data={
                    "message": "Validation failed",
                    "errors": self._errors,
                    "field_errors": self._field_errors,
                },
            )
        return FlextResult.ok({"message": "Validation passed"})

    def reset(self) -> FlextApiValidator:
        """Reset validator state."""
        self._errors.clear()
        self._field_errors.clear()
        return self


# FlextApi validation functions with prefixes
def flext_api_validate_email(email: str) -> bool:
    """Quick email validation."""
    if not email:
        return False
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def flext_api_validate_password(password: str) -> bool:
    """Quick password validation."""
    if not password or len(password) < 8:
        return False

    # Check for at least one uppercase, lowercase, and digit
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))

    return has_upper and has_lower and has_digit


def flext_api_validate_uuid(value: str) -> bool:
    """Quick UUID validation."""
    if not value:
        return False
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False


def flext_api_validate_phone(phone: str) -> bool:
    """Quick phone number validation (international format)."""
    if not phone:
        return False
    # Basic international phone number pattern
    phone_pattern = r"^\+?[1-9]\d{1,14}$"
    return bool(re.match(phone_pattern, phone.replace(" ", "").replace("-", "")))


def flext_api_validate_url(url: str) -> bool:
    """Quick URL validation."""
    if not url:
        return False
    url_pattern = r"^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$"
    return bool(re.match(url_pattern, url))


def flext_api_validate_ip_address(ip: str) -> bool:
    """Quick IP address validation (IPv4 and IPv6)."""
    if not ip:
        return False

    # IPv4 pattern
    ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    if re.match(ipv4_pattern, ip):
        return True

    # IPv6 pattern (simplified)
    ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
    return bool(re.match(ipv6_pattern, ip))


# Data validation utilities
def flext_api_sanitize_string(value: str, max_length: int | None = None) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        value = str(value)

    # Strip whitespace
    value = value.strip()

    # Truncate if needed
    if max_length and len(value) > max_length:
        value = value[:max_length]

    return value


def flext_api_sanitize_email(email: str) -> str:
    """Sanitize email input."""
    if not isinstance(email, str):
        email = str(email)

    # Convert to lowercase and strip
    return email.lower().strip()


def flext_api_normalize_phone(phone: str) -> str:
    """Normalize phone number (remove formatting)."""
    if not isinstance(phone, str):
        phone = str(phone)

    # Remove common formatting characters
    return re.sub(r"[^\d+]", "", phone)


# ===== LEGACY COMPATIBILITY WITH DEPRECATION WARNINGS =====


def _validation_deprecation_warning(old_name: str, new_name: str) -> None:
    """Issue deprecation warning for validation functions."""
    warnings.warn(
        f"{old_name} is deprecated, use {new_name} instead",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy class alias
FlextValidator = FlextApiValidator


# Legacy function aliases
def validate_email(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("validate_email", "flext_api_validate_email")
    return flext_api_validate_email(*args, **kwargs)


def validate_password(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("validate_password", "flext_api_validate_password")
    return flext_api_validate_password(*args, **kwargs)


def validate_uuid(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("validate_uuid", "flext_api_validate_uuid")
    return flext_api_validate_uuid(*args, **kwargs)


def validate_phone(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("validate_phone", "flext_api_validate_phone")
    return flext_api_validate_phone(*args, **kwargs)


def validate_url(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("validate_url", "flext_api_validate_url")
    return flext_api_validate_url(*args, **kwargs)


def validate_ip_address(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning(
        "validate_ip_address", "flext_api_validate_ip_address"
    )
    return flext_api_validate_ip_address(*args, **kwargs)


def sanitize_string(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("sanitize_string", "flext_api_sanitize_string")
    return flext_api_sanitize_string(*args, **kwargs)


def sanitize_email(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("sanitize_email", "flext_api_sanitize_email")
    return flext_api_sanitize_email(*args, **kwargs)


def normalize_phone(*args: Any, **kwargs: object) -> Any:
    """Legacy wrapper with deprecation warning."""
    _validation_deprecation_warning("normalize_phone", "flext_api_normalize_phone")
    return flext_api_normalize_phone(*args, **kwargs)
