"""FLEXT API Client Factory - Standalone client factory module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import client as _client_module
from flext_api.client import FlextApiClient
from flext_core import FlextResult, FlextService


class FlextApiClientFactory(FlextService[FlextApiClient]):
    """Single unified API client factory class following FLEXT standards.

    Contains all factory methods for creating API clients with different configurations.
    Follows FLEXT pattern: one class per module with nested subclasses.
    """

    @staticmethod
    async def create_production_client(
        base_url: str,
    ) -> FlextResult[FlextApiClient]:
        """Create production-ready HTTP client with enterprise settings.

        Args:
            base_url: Base URL for the API client

        Returns:
            FlextResult containing configured FlextApiClient or error.

        """
        return await _client_module.FlextApiClient.create(
            base_url=base_url,
            request_timeout=30,
            max_retries=3,
            headers={
                "User-Agent": "FlextApiClient-Production/1.0.0",
                "Accept": "application/json",
                "Cache-Control": "no-cache",
            },
        )

    @staticmethod
    async def create_development_client(
        base_url: str,
    ) -> FlextResult[FlextApiClient]:
        """Create development HTTP client with extended timeouts.

        Args:
            base_url: Base URL for the API client

        Returns:
            FlextResult containing configured FlextApiClient or error.

        """
        return await _client_module.FlextApiClient.create(
            base_url=base_url,
            request_timeout=60,
            max_retries=1,
            headers={
                "User-Agent": "FlextApiClient-Dev/1.0.0",
                "Accept": "application/json",
            },
        )

    @staticmethod
    async def create_testing_client(
        base_url: str,
    ) -> FlextResult[FlextApiClient]:
        """Create testing HTTP client with minimal timeouts.

        Args:
            base_url: Base URL for the API client

        Returns:
            FlextResult containing configured FlextApiClient or error.

        """
        return await _client_module.FlextApiClient.create(
            base_url=base_url,
            request_timeout=10,
            max_retries=0,
            headers={
                "User-Agent": "FlextApiClient-Test/1.0.0",
                "Accept": "application/json",
            },
        )

    @staticmethod
    async def create_monitoring_client(
        base_url: str,
    ) -> FlextResult[FlextApiClient]:
        """Create monitoring HTTP client for health checks and metrics.

        Args:
            base_url: Base URL for the API client

        Returns:
            FlextResult containing configured FlextApiClient or error.

        """
        return await _client_module.FlextApiClient.create(
            base_url=base_url,
            request_timeout=5,
            max_retries=1,
            headers={
                "User-Agent": "FlextApiClient-Monitor/1.0.0",
                "Accept": "application/json",
                "X-Monitoring": "true",
            },
        )

    @classmethod
    def get_supported_environments(cls: object) -> list[str]:
        """Get list of supported client environment configurations.

        Returns:
            List of environment names with preconfigured settings.

        """
        return ["production", "development", "testing", "monitoring"]

    @classmethod
    async def create_for_environment(
        cls,
        environment: str,
        base_url: str,
    ) -> FlextResult[FlextApiClient]:
        """Create client for specified environment.

        Args:
            environment: Environment name (production, development, testing, monitoring)
            base_url: Base URL for the API client

        Returns:
            FlextResult containing configured FlextApiClient or error.

        """
        if environment == "production":
            return await cls.create_production_client(base_url)
        if environment == "development":
            return await cls.create_development_client(base_url)
        if environment == "testing":
            return await cls.create_testing_client(base_url)
        if environment == "monitoring":
            return await cls.create_monitoring_client(base_url)
        return FlextResult["FlextApiClient"].fail(
            f"Unsupported environment: {environment}. "
            f"Supported environments: {cls.get_supported_environments()}"
        )


__all__ = ["FlextApiClientFactory"]
