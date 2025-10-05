"""FLEXT Test Domains - Test data factories and domain objects.

Provides test domain objects and data factories for FLEXT ecosystem testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from flext_core import FlextTypes


class FlextTestsDomains:
    """Test domain data factories and utilities.

    Provides consistent test data creation following FLEXT patterns.
    """

    @staticmethod
    def create_configuration() -> FlextTypes.Dict:
        """Create test configuration dictionary.

        Returns:
            Test configuration with standard values.

        """
        return {
            "environment": "test",
            "debug": True,
            "log_level": "DEBUG",
            "storage_backend": "memory",
            "namespace": "test",
            "enable_caching": True,
            "cache_ttl": 300,
            "api_timeout": 30,
            "max_retries": 3,
        }

    @staticmethod
    def create_payload(
        data_type: str = "user",
        **overrides: FlextTypes.JsonValue,
    ) -> FlextTypes.Dict:
        """Create test payload data.

        Args:
            data_type: Type of payload to create
            **overrides: Override default values

        Returns:
            Test payload dictionary

        """
        base_payloads = {
            "user": {
                "id": str(uuid.uuid4()),
                "name": "Test User",
                "email": "test@example.com",
                "created_at": datetime.now(UTC).isoformat(),
            },
            "order": {
                "id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "amount": 99.99,
                "status": "pending",
                "created_at": datetime.now(UTC).isoformat(),
            },
            "api_request": {
                "method": "GET",
                "url": "/api/test",
                "headers": {"Content-Type": "application/json"},
                "body": None,
            },
        }

        payload = base_payloads.get(data_type, {}).copy()
        payload.update(overrides)
        return payload

    @staticmethod
    def create_api_response(
        status_code: int = 200,
        data: FlextTypes.JsonValue = None,
        message: str = "Success",
        **overrides: FlextTypes.JsonValue,
    ) -> FlextTypes.Dict:
        """Create test API response.

        Args:
            status_code: HTTP status code
            data: Response data
            message: Response message
            **overrides: Override default values

        Returns:
            Test API response dictionary

        """
        response = {
            "status": "success" if status_code < 400 else "error",
            "data": data,
            "message": message,
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": str(uuid.uuid4()),
        }
        response.update(overrides)
        return response

    @staticmethod
    def create_error_response(
        message: str = "An error occurred",
        code: str = "ERROR",
        status_code: int = 500,
        **overrides: FlextTypes.JsonValue,
    ) -> FlextTypes.Dict:
        """Create test error response.

        Args:
            message: Error message
            code: Error code
            status_code: HTTP status code
            **overrides: Override default values

        Returns:
            Test error response dictionary

        """
        response = {
            "status": "error",
            "error": {"code": code, "message": message},
            "timestamp": datetime.now(UTC).isoformat(),
            "request_id": str(uuid.uuid4()),
        }
        response.update(overrides)
        return response


__all__ = ["FlextTestsDomains"]
