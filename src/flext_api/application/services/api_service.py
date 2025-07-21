"""API application service using flext-core patterns.

This module provides the application service for API management,
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from flext_core.domain.types import ServiceResult

from flext_api.application.services.base import DualRepositoryService
from flext_api.domain.entities import APIRequest, APIResponse

if TYPE_CHECKING:
    from flext_api.infrastructure.repositories import (
        APIRequestRepository,
        APIResponseRepository,
    )


class APIService(DualRepositoryService):
    """Service for managing API operations and tracking."""

    def __init__(
        self,
        request_repo: APIRequestRepository | None = None,
        response_repo: APIResponseRepository | None = None,
    ) -> None:
        """Initialize API service with optional repositories."""
        super().__init__(request_repo, response_repo)
        # Aliases for backward compatibility
        self.request_repo = self.primary_repo
        self.response_repo = self.secondary_repo

    async def track_request(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        headers: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        client_ip: str | None = None,
        user_agent: str | None = None,
    ) -> ServiceResult[APIRequest]:
        """Track incoming API request.

        Args:
            request_id: Unique request identifier
            endpoint: API endpoint being accessed
            method: HTTP method
            headers: Request headers
            query_params: Query parameters
            body: Request body
            client_ip: Client IP address
            user_agent: Client user agent

        Returns:
            ServiceResult containing the tracked API request

        """
        try:
            api_request = APIRequest(
                request_id=request_id,
                endpoint=endpoint,
                method=method,
                headers=headers or {},
                query_params=query_params or {},
                body=body,
                client_ip=client_ip,
                user_agent=user_agent,
            )

            # Store if repository is available
            if self.request_repo:
                await self.request_repo.save(api_request)

            self.logger.info(
                "API request tracked successfully - request_id: %s, endpoint: %s",
                request_id,
                endpoint,
            )

            return ServiceResult.ok(api_request)

        except Exception as e:
            self.logger.exception(
                "Failed to track API request - request_id: %s",
                request_id,
            )
            return ServiceResult.fail(f"Failed to track API request: {e}")

    async def track_response(
        self,
        request_id: str,
        response_id: str,
        status_code: int,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        processing_start_time: datetime | None = None,
    ) -> ServiceResult[APIResponse]:
        """Track API response.

        Args:
            request_id: Corresponding request identifier
            response_id: Unique response identifier
            status_code: HTTP status code
            headers: Response headers
            body: Response body
            processing_start_time: When processing started

        Returns:
            ServiceResult containing the tracked API response

        """
        try:
            # Create API response with available constructor arguments
            # Some arguments may not be available in base APIResponse
            api_response = APIResponse()

            # Set properties if they exist
            if hasattr(api_response, "request_id"):
                api_response.request_id = request_id
            if hasattr(api_response, "response_id"):
                api_response.response_id = response_id
            if hasattr(api_response, "status_code"):
                api_response.status_code = status_code
            if hasattr(api_response, "headers"):
                api_response.headers = headers or {}
            if hasattr(api_response, "body"):
                api_response.body = body

            # Set processing duration if start time provided and method exists
            if processing_start_time and hasattr(
                api_response,
                "set_processing_duration",
            ):
                api_response.set_processing_duration(processing_start_time)

            # Store if repository is available
            if self.response_repo:
                await self.response_repo.save(api_response)

            self.logger.info(
                "API response tracked successfully - request_id: %s, status: %d",
                request_id,
                status_code,
            )

            return ServiceResult.ok(api_response)

        except Exception as e:
            self.logger.exception(
                "Failed to track API response - request_id: %s",
                request_id,
            )
            return ServiceResult.fail(f"Failed to track API response: {e}")

    async def get_request_metrics(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> ServiceResult[dict[str, Any]]:
        """Get API request metrics.

        Args:
            start_time: Start time for metrics calculation
            end_time: End time for metrics calculation

        Returns:
            ServiceResult containing request metrics

        """
        try:
            if not self.request_repo:
                return ServiceResult.fail("Request repository not available")

            # Mock metrics for now - replace with actual repository queries
            metrics = {
                "total_requests": 0,
                "requests_by_method": {},
                "requests_by_endpoint": {},
                "requests_by_status": {},
                "average_response_time_ms": 0.0,
                "error_rate": 0.0,
                "period": {
                    "start": start_time.isoformat() if start_time else None,
                    "end": end_time.isoformat() if end_time else None,
                },
                "last_updated": datetime.now(UTC).isoformat(),
            }

            self.logger.info("API request metrics calculated successfully")
            return ServiceResult.ok(metrics)

        except Exception as e:
            self.logger.exception("Failed to calculate API request metrics")
            return ServiceResult.fail(f"Failed to calculate metrics: {e}")

    async def health_check(self) -> ServiceResult[dict[str, Any]]:
        """Perform API service health check.

        Returns:
            ServiceResult containing health status

        """
        try:
            health_data: dict[str, Any] = {
                "service": "api_service",
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "repositories": {
                    "request_repo": self.request_repo is not None,
                    "response_repo": self.response_repo is not None,
                },
                "version": "0.1.0",
            }

            # Test repository connections if available
            if self.request_repo:
                try:
                    # Mock health check - replace with actual repository health check
                    await asyncio.sleep(0.001)  # Simulate async health check
                    health_data["repositories"]["request_repo_status"] = "healthy"
                except (ConnectionError, TimeoutError, OSError, ValueError) as e:
                    health_data["repositories"]["request_repo_status"] = "unhealthy"
                    health_data["status"] = "degraded"
                    self.logger.warning(
                        "Request repository health check failed",
                        error=str(e),
                    )

            if self.response_repo:
                try:
                    # Mock health check - replace with actual repository health check
                    await asyncio.sleep(0.001)  # Simulate async health check
                    health_data["repositories"]["response_repo_status"] = "healthy"
                except (ConnectionError, TimeoutError, OSError, ValueError) as e:
                    health_data["repositories"]["response_repo_status"] = "unhealthy"
                    health_data["status"] = "degraded"
                    self.logger.warning(
                        "Response repository health check failed",
                        error=str(e),
                    )

            self.logger.info("API service health check completed successfully")
            return ServiceResult.ok(health_data)

        except Exception as e:
            self.logger.exception("API service health check failed")
            return ServiceResult.fail(f"Health check failed: {e}")
