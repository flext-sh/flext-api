#!/usr/bin/env python3
"""FlextApi Universal API Client - Request/Response Validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Comprehensive validation system for API client requests and responses.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from flext_core import FlextResult, get_logger
from pydantic import BaseModel, ValidationError, field_validator

if TYPE_CHECKING:
    from collections.abc import Callable

    from flext_api.client.core import FlextApiClientRequest, FlextApiClientResponse

logger = get_logger(__name__)


# ==============================================================================
# VALIDATION SCHEMAS
# ==============================================================================

class FlextApiRequestSchema(BaseModel):
    """Base schema for request validation."""

    method: str
    url: str
    headers: dict[str, str] = {}
    params: dict[str, Any] = {}
    timeout: float = 30.0

    @field_validator("method")
    @classmethod
    def validate_method(cls, v: str) -> str:
        """Validate HTTP method."""
        allowed_methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
        if v.upper() not in allowed_methods:
            raise ValueError(f"Invalid HTTP method: {v}")
        return v.upper()

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v:
            raise ValueError("URL cannot be empty")

        # Basic URL validation
        url_pattern = re.compile(
            r"^(?:http[s]?://)?"  # Optional protocol
            r"(?:[A-Za-z0-9-._~:/?#[\]@!$&\'()*+,;=])*"  # URL characters
            r"$"
        )

        if not url_pattern.match(v):
            raise ValueError(f"Invalid URL format: {v}")

        return v

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: float) -> float:
        """Validate timeout value."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        if v > 3600:  # 1 hour max
            raise ValueError("Timeout cannot exceed 3600 seconds")
        return v


class FlextApiResponseSchema(BaseModel):
    """Base schema for response validation."""

    status_code: int
    headers: dict[str, str] = {}
    data: Any = None
    execution_time_ms: float = 0.0

    @field_validator("status_code")
    @classmethod
    def validate_status_code(cls, v: int) -> int:
        """Validate HTTP status code."""
        if not (100 <= v <= 599):
            raise ValueError(f"Invalid HTTP status code: {v}")
        return v

    @field_validator("execution_time_ms")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time."""
        if v < 0:
            raise ValueError("Execution time cannot be negative")
        return v


# ==============================================================================
# VALIDATION RULES
# ==============================================================================

@dataclass
class FlextApiValidationRule:
    """Single validation rule."""

    name: str
    validator: Callable[[Any], bool]
    error_message: str
    required: bool = True
    field_path: str = ""


@dataclass
class FlextApiValidationRuleset:
    """Collection of validation rules."""

    name: str
    rules: list[FlextApiValidationRule] = field(default_factory=list)
    enabled: bool = True

    def add_rule(self, rule: FlextApiValidationRule) -> None:
        """Add validation rule."""
        self.rules.append(rule)

    def validate(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate data against all rules."""
        if not self.enabled:
            return FlextResult.ok(data)

        errors = []

        for rule in self.rules:
            try:
                # Extract field value
                value = self._get_field_value(data, rule.field_path or rule.name)

                # Check if field is missing
                if value is None and rule.required:
                    errors.append(f"{rule.name}: Field is required")
                    continue

                # Skip validation if field is optional and missing
                if value is None and not rule.required:
                    continue

                # Run validator
                if not rule.validator(value):
                    errors.append(f"{rule.name}: {rule.error_message}")

            except Exception as e:
                errors.append(f"{rule.name}: Validation error - {e}")

        if errors:
            return FlextResult.fail("Validation failed", {"errors": errors})

        return FlextResult.ok(data)

    def _get_field_value(self, data: dict[str, Any], field_path: str) -> Any:
        """Extract field value using dot notation path."""
        if not field_path:
            return None

        current = data
        for part in field_path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current


# ==============================================================================
# BUILT-IN VALIDATORS
# ==============================================================================

class FlextApiValidators:
    """Collection of built-in validators."""

    @staticmethod
    def url_validator(value: Any) -> bool:
        """Validate URL format."""
        if not isinstance(value, str):
            return False

        url_pattern = re.compile(
            r"^(?:http[s]?://)?"
            r"(?:[A-Za-z0-9-._~:/?#[\]@!$&\'()*+,;=])+$"
        )

        return bool(url_pattern.match(value))

    @staticmethod
    def email_validator(value: Any) -> bool:
        """Validate email format."""
        if not isinstance(value, str):
            return False

        email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )

        return bool(email_pattern.match(value))

    @staticmethod
    def json_validator(value: Any) -> bool:
        """Validate JSON format."""
        if isinstance(value, (dict, list)):
            return True

        if not isinstance(value, str):
            return False

        try:
            json.loads(value)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    @staticmethod
    def non_empty_validator(value: Any) -> bool:
        """Validate non-empty value."""
        if value is None:
            return False

        if isinstance(value, str):
            return len(value.strip()) > 0

        if isinstance(value, (list, dict)):
            return len(value) > 0

        return True

    @staticmethod
    def numeric_validator(value: Any) -> bool:
        """Validate numeric value."""
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def positive_validator(value: Any) -> bool:
        """Validate positive number."""
        return FlextApiValidators.numeric_validator(value) and value > 0

    @staticmethod
    def range_validator(min_val: float, max_val: float) -> Callable[[Any], bool]:
        """Create range validator."""
        def validator(value: Any) -> bool:
            if not FlextApiValidators.numeric_validator(value):
                return False
            return min_val <= value <= max_val

        return validator

    @staticmethod
    def length_validator(min_len: int = 0, max_len: int | None = None) -> Callable[[Any], bool]:
        """Create length validator."""
        def validator(value: Any) -> bool:
            if not isinstance(value, (str, list, dict)):
                return False

            length = len(value)

            if length < min_len:
                return False

            return not (max_len is not None and length > max_len)

        return validator

    @staticmethod
    def regex_validator(pattern: str, flags: int = 0) -> Callable[[Any], bool]:
        """Create regex validator."""
        compiled_pattern = re.compile(pattern, flags)

        def validator(value: Any) -> bool:
            if not isinstance(value, str):
                return False
            return bool(compiled_pattern.match(value))

        return validator

    @staticmethod
    def choices_validator(choices: list[Any]) -> Callable[[Any], bool]:
        """Create choices validator."""
        def validator(value: Any) -> bool:
            return value in choices

        return validator


# ==============================================================================
# REQUEST VALIDATOR
# ==============================================================================

@dataclass
class FlextApiRequestValidatorConfig:
    """Configuration for request validator."""

    validate_schema: bool = True
    validate_headers: bool = True
    validate_params: bool = True
    validate_body: bool = True
    custom_rulesets: list[FlextApiValidationRuleset] = field(default_factory=list)
    strict_mode: bool = False


class FlextApiRequestValidator:
    """Comprehensive request validator."""

    # Common header validation rules
    COMMON_HEADER_RULES: ClassVar[dict[str, FlextApiValidationRule]] = {
        "content-type": FlextApiValidationRule(
            name="content-type",
            validator=lambda v: isinstance(v, str) and len(v.strip()) > 0,
            error_message="Content-Type must be a non-empty string",
            required=False
        ),
        "authorization": FlextApiValidationRule(
            name="authorization",
            validator=lambda v: isinstance(v, str) and len(v.strip()) > 0,
            error_message="Authorization must be a non-empty string",
            required=False
        ),
        "user-agent": FlextApiValidationRule(
            name="user-agent",
            validator=FlextApiValidators.length_validator(1, 500),
            error_message="User-Agent must be 1-500 characters",
            required=False
        ),
    }

    def __init__(self, config: FlextApiRequestValidatorConfig | None = None) -> None:
        self.config = config or FlextApiRequestValidatorConfig()
        self._setup_default_rulesets()

    def _setup_default_rulesets(self) -> None:
        """Setup default validation rulesets."""
        # URL validation ruleset
        url_ruleset = FlextApiValidationRuleset("url_validation")
        url_ruleset.add_rule(FlextApiValidationRule(
            name="url",
            validator=FlextApiValidators.url_validator,
            error_message="Invalid URL format"
        ))

        # Method validation ruleset
        method_ruleset = FlextApiValidationRuleset("method_validation")
        method_ruleset.add_rule(FlextApiValidationRule(
            name="method",
            validator=FlextApiValidators.choices_validator(
                ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
            ),
            error_message="Invalid HTTP method"
        ))

        # Timeout validation ruleset
        timeout_ruleset = FlextApiValidationRuleset("timeout_validation")
        timeout_ruleset.add_rule(FlextApiValidationRule(
            name="timeout",
            validator=FlextApiValidators.range_validator(0.1, 3600.0),
            error_message="Timeout must be between 0.1 and 3600 seconds"
        ))

        self._default_rulesets = [url_ruleset, method_ruleset, timeout_ruleset]

    def validate_request(self, request: FlextApiClientRequest) -> FlextResult[dict[str, Any]]:
        """Validate API request."""
        request_data = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers,
            "params": request.params,
            "timeout": request.timeout,
            "data": request.data,
            "json": request.json,
        }

        errors = []

        # Schema validation
        if self.config.validate_schema:
            schema_result = self._validate_schema(request_data)
            if not schema_result.success:
                errors.extend(schema_result.data.get("errors", []))

        # Header validation
        if self.config.validate_headers:
            header_result = self._validate_headers(request.headers)
            if not header_result.success:
                errors.extend(header_result.data.get("errors", []))

        # Parameter validation
        if self.config.validate_params:
            param_result = self._validate_params(request.params)
            if not param_result.success:
                errors.extend(param_result.data.get("errors", []))

        # Body validation
        if self.config.validate_body:
            body_result = self._validate_body(request.data, request.json)
            if not body_result.success:
                errors.extend(body_result.data.get("errors", []))

        # Custom ruleset validation
        for ruleset in self.config.custom_rulesets + self._default_rulesets:
            ruleset_result = ruleset.validate(request_data)
            if not ruleset_result.success:
                errors.extend(ruleset_result.data.get("errors", []))

        if errors:
            return FlextResult.fail("Request validation failed", {"errors": errors})

        return FlextResult.ok(request_data)

    def _validate_schema(self, request_data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate request against Pydantic schema."""
        try:
            FlextApiRequestSchema(**request_data)
            return FlextResult.ok(request_data)
        except ValidationError as e:
            errors = [f"Schema validation: {error['msg']}" for error in e.errors()]
            return FlextResult.fail("Schema validation failed", {"errors": errors})

    def _validate_headers(self, headers: dict[str, str]) -> FlextResult[dict[str, Any]]:
        """Validate request headers."""
        errors = []

        for header_name, header_value in headers.items():
            # Check common headers
            rule = self.COMMON_HEADER_RULES.get(header_name.lower())
            if rule and not rule.validator(header_value):
                errors.append(f"Header {header_name}: {rule.error_message}")

            # General header validation
            if not isinstance(header_name, str) or not header_name.strip():
                errors.append(f"Header name must be non-empty string: {header_name}")

            if not isinstance(header_value, str):
                errors.append(f"Header value must be string: {header_name}")

        if errors:
            return FlextResult.fail("Header validation failed", {"errors": errors})

        return FlextResult.ok(headers)

    def _validate_params(self, params: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate request parameters."""
        errors = []

        for param_name, param_value in params.items():
            if not isinstance(param_name, str) or not param_name.strip():
                errors.append(f"Parameter name must be non-empty string: {param_name}")

            # Validate parameter values are serializable
            try:
                json.dumps(param_value)
            except (TypeError, ValueError):
                errors.append(f"Parameter value not serializable: {param_name}")

        if errors:
            return FlextResult.fail("Parameter validation failed", {"errors": errors})

        return FlextResult.ok(params)

    def _validate_body(self, data: Any, json_data: dict[str, Any] | None) -> FlextResult[dict[str, Any]]:
        """Validate request body."""
        errors = []

        # Validate JSON data if present
        if json_data is not None:
            try:
                json.dumps(json_data)
            except (TypeError, ValueError):
                errors.append("JSON data is not serializable")

        # Validate raw data if present
        if data is not None and json_data is None:
            # Check if data is serializable for common types
            if isinstance(data, dict):
                try:
                    json.dumps(data)
                except (TypeError, ValueError):
                    errors.append("Data is not JSON serializable")

        if errors:
            return FlextResult.fail("Body validation failed", {"errors": errors})

        return FlextResult.ok({"data": data, "json": json_data})


# ==============================================================================
# RESPONSE VALIDATOR
# ==============================================================================

@dataclass
class FlextApiResponseValidatorConfig:
    """Configuration for response validator."""

    validate_schema: bool = True
    validate_status_codes: bool = True
    validate_headers: bool = True
    validate_content_type: bool = True
    expected_status_codes: list[int] = field(default_factory=lambda: [200, 201, 202, 204])
    allowed_content_types: list[str] = field(default_factory=lambda: [
        "application/json", "text/plain", "text/html", "application/xml"
    ])
    custom_rulesets: list[FlextApiValidationRuleset] = field(default_factory=list)


class FlextApiResponseValidator:
    """Comprehensive response validator."""

    def __init__(self, config: FlextApiResponseValidatorConfig | None = None) -> None:
        self.config = config or FlextApiResponseValidatorConfig()

    def validate_response(self, response: FlextApiClientResponse) -> FlextResult[dict[str, Any]]:
        """Validate API response."""
        response_data = {
            "status_code": response.status_code,
            "headers": response.headers,
            "data": response.data,
            "text": response.text,
            "execution_time_ms": response.execution_time_ms,
        }

        errors = []

        # Schema validation
        if self.config.validate_schema:
            schema_result = self._validate_schema(response_data)
            if not schema_result.success:
                errors.extend(schema_result.data.get("errors", []))

        # Status code validation
        if self.config.validate_status_codes:
            status_result = self._validate_status_code(response.status_code)
            if not status_result.success:
                errors.extend(status_result.data.get("errors", []))

        # Header validation
        if self.config.validate_headers:
            header_result = self._validate_response_headers(response.headers)
            if not header_result.success:
                errors.extend(header_result.data.get("errors", []))

        # Content type validation
        if self.config.validate_content_type:
            content_result = self._validate_content_type(response.headers)
            if not content_result.success:
                errors.extend(content_result.data.get("errors", []))

        # Custom ruleset validation
        for ruleset in self.config.custom_rulesets:
            ruleset_result = ruleset.validate(response_data)
            if not ruleset_result.success:
                errors.extend(ruleset_result.data.get("errors", []))

        if errors:
            return FlextResult.fail("Response validation failed", {"errors": errors})

        return FlextResult.ok(response_data)

    def _validate_schema(self, response_data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Validate response against Pydantic schema."""
        try:
            FlextApiResponseSchema(**response_data)
            return FlextResult.ok(response_data)
        except ValidationError as e:
            errors = [f"Schema validation: {error['msg']}" for error in e.errors()]
            return FlextResult.fail("Schema validation failed", {"errors": errors})

    def _validate_status_code(self, status_code: int) -> FlextResult[dict[str, Any]]:
        """Validate response status code."""
        if status_code not in self.config.expected_status_codes:
            return FlextResult.fail(
                f"Unexpected status code: {status_code}",
                {"errors": [f"Expected one of {self.config.expected_status_codes}, got {status_code}"]}
            )

        return FlextResult.ok({"status_code": status_code})

    def _validate_response_headers(self, headers: dict[str, str]) -> FlextResult[dict[str, Any]]:
        """Validate response headers."""
        errors = []

        # Check for required security headers in strict mode

        for header_name, header_value in headers.items():
            if not isinstance(header_name, str) or not header_name.strip():
                errors.append(f"Header name must be non-empty string: {header_name}")

            if not isinstance(header_value, str):
                errors.append(f"Header value must be string: {header_name}")

        if errors:
            return FlextResult.fail("Header validation failed", {"errors": errors})

        return FlextResult.ok(headers)

    def _validate_content_type(self, headers: dict[str, str]) -> FlextResult[dict[str, Any]]:
        """Validate response content type."""
        content_type = headers.get("content-type", "").lower()

        if not content_type:
            return FlextResult.ok({"content_type": None})

        # Extract main content type (ignore charset, etc.)
        main_type = content_type.split(";")[0].strip()

        if main_type not in self.config.allowed_content_types:
            return FlextResult.fail(
                f"Unsupported content type: {main_type}",
                {"errors": [f"Content type {main_type} not in allowed types: {self.config.allowed_content_types}"]}
            )

        return FlextResult.ok({"content_type": main_type})


# ==============================================================================
# VALIDATION MANAGER
# ==============================================================================

class FlextApiValidationManager:
    """Central manager for request/response validation."""

    def __init__(self,
                 request_config: FlextApiRequestValidatorConfig | None = None,
                 response_config: FlextApiResponseValidatorConfig | None = None) -> None:
        self.request_validator = FlextApiRequestValidator(request_config)
        self.response_validator = FlextApiResponseValidator(response_config)
        self._validation_metrics = {
            "requests_validated": 0,
            "responses_validated": 0,
            "validation_failures": 0,
        }

    def validate_request(self, request: FlextApiClientRequest) -> FlextResult[dict[str, Any]]:
        """Validate request."""
        self._validation_metrics["requests_validated"] += 1

        result = self.request_validator.validate_request(request)

        if not result.success:
            self._validation_metrics["validation_failures"] += 1
            logger.warning(f"Request validation failed: {result.message}")

        return result

    def validate_response(self, response: FlextApiClientResponse) -> FlextResult[dict[str, Any]]:
        """Validate response."""
        self._validation_metrics["responses_validated"] += 1

        result = self.response_validator.validate_response(response)

        if not result.success:
            self._validation_metrics["validation_failures"] += 1
            logger.warning(f"Response validation failed: {result.message}")

        return result

    def add_request_ruleset(self, ruleset: FlextApiValidationRuleset) -> None:
        """Add custom request validation ruleset."""
        self.request_validator.config.custom_rulesets.append(ruleset)
        logger.info(f"Added request validation ruleset: {ruleset.name}")

    def add_response_ruleset(self, ruleset: FlextApiValidationRuleset) -> None:
        """Add custom response validation ruleset."""
        self.response_validator.config.custom_rulesets.append(ruleset)
        logger.info(f"Added response validation ruleset: {ruleset.name}")

    def get_metrics(self) -> dict[str, Any]:
        """Get validation metrics."""
        total_validations = (
            self._validation_metrics["requests_validated"] +
            self._validation_metrics["responses_validated"]
        )

        return {
            **self._validation_metrics,
            "total_validations": total_validations,
            "success_rate": (
                (total_validations - self._validation_metrics["validation_failures"]) /
                max(total_validations, 1)
            ) * 100,
        }
