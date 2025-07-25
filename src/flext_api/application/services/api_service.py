"""API application service using flext-core patterns.

This module provides the application service for API management
implementing business logic using domain entities and clean architecture.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger

from flext_api.application.services.base import DualRepositoryService
from flext_api.domain.entities import APIResponseLog, FlextAPIRequest

if TYPE_CHECKING:
    from flext_api.infrastructure.repositories import (
        APIRequestRepository,
        APIResponseRepository,
    )

logger = get_logger(__name__)


class FlextAPIService(DualRepositoryService):
    """Service for managing API operations and tracking."""

    def __init__(
        self,
        request_repo: APIRequestRepository | None = None,
        response_repo: APIResponseRepository | None = None,
    ) -> None:
        """Initialize API service with optional repositories."""
        super().__init__(request_repo, response_repo)
        # Use primary_repo and secondary_repo directly
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
    ) -> FlextResult[Any]:
        """Track incoming API request.

        Args:
            request_id: Unique request identifier,
            endpoint: API endpoint being accessed,
            method: HTTP method,
            headers: Request headers,
            query_params: Query parameters,
            body: Request body,
            client_ip: Client IP address,
            user_agent: Client user agent,

        Returns:
            FlextResult containing the tracked API request

        """
        try:
            api_request = FlextAPIRequest(
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

            logger.info("API request tracked successfully")
            return FlextResult.ok(api_request)

        except Exception as e:
            logger.exception(f"Failed to track API request - request_id: {request_id}")
            return FlextResult.fail(f"Failed to track API request: {e}")

    async def track_response(
        self,
        request_id: str,
        response_id: str,
        status_code: int,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
        processing_start_time: datetime | None = None,
    ) -> FlextResult[Any]:
        """Track API response.

        Args:
            request_id: Corresponding request identifier,
            response_id: Unique response identifier,
            status_code: HTTP status code,
            headers: Response headers,
            body: Response body,
            processing_start_time: When processing started,

        Returns:
            FlextResult containing the tracked API response

        """
        try:
            # Create API response with required constructor arguments
            api_response = APIResponseLog(
                request_id=request_id,
                response_id=response_id,
                status_code=status_code,
                headers=headers or {},
                body=body,
            )

            # Set processing duration if start time provided and method exists
            if processing_start_time and hasattr(
                api_response, "set_processing_duration"
            ):
                api_response.set_processing_duration(processing_start_time)

            # Store if repository is available
            if self.response_repo:
                # Type casting to satisfy repository interface
                await self.response_repo.save(api_response)  # type: ignore[arg-type]

            logger.info("API response tracked successfully")
            return FlextResult.ok(api_response)

        except Exception as e:
            logger.exception(
                f"Failed to track API response - request_id: {request_id}"
            )
            return FlextResult.fail(f"Failed to track API response: {e}")

    async def get_request_metrics(
        self, start_time: datetime | None = None, end_time: datetime | None = None
    ) -> FlextResult[Any]:
        """Get API request metrics.

        Args:
            start_time: Start time for metrics calculation,
            end_time: End time for metrics calculation,

        Returns:
            FlextResult containing request metrics

        """
        try:
            if not self.request_repo:
                return FlextResult.fail("Request repository not available")

            # Calculate actual metrics from repository data
            try:
                # Query all requests in the specified time period
                all_requests_result = await self._get_requests_in_period(start_time, end_time)
                all_requests = all_requests_result.data if all_requests_result.success and all_requests_result.data else []

                # Ensure all_requests is a list
                if not isinstance(all_requests, list):
                    all_requests = []

                # Calculate comprehensive metrics
                total_requests = len(all_requests)
                requests_by_method = self._count_by_attribute(all_requests, "method")
                requests_by_endpoint = self._count_by_attribute(
                    all_requests, "endpoint"
                )

                # Get response data for additional metrics
                all_responses_result = await self._get_responses_for_requests(
                    [req.request_id for req in all_requests if hasattr(req, "request_id")] if all_requests else []
                )
                all_responses = all_responses_result.data if all_responses_result.success and all_responses_result.data else []

                # Ensure all_responses is a list
                if not isinstance(all_responses, list):
                    all_responses = []
                requests_by_status = self._count_by_attribute(
                    all_responses, "status_code"
                )

                # Calculate response time and error rate
                response_times = [
                    resp.processing_duration_ms
                    for resp in all_responses
                    if hasattr(resp, "processing_duration_ms")
                    and resp.processing_duration_ms
                ]

                average_response_time_ms = (
                    sum(response_times) / len(response_times) if response_times else 0.0
                )

                error_responses = [
                    resp
                    for resp in all_responses
                    if hasattr(resp, "status_code") and resp.status_code >= 400
                ]
                error_rate = (
                    len(error_responses) / total_requests if total_requests > 0 else 0.0
                )

                metrics = {
                    "total_requests": total_requests,
                    "requests_by_method": requests_by_method,
                    "requests_by_endpoint": requests_by_endpoint,
                    "requests_by_status": requests_by_status,
                    "average_response_time_ms": round(average_response_time_ms, 2),
                    "error_rate": round(error_rate, 4),
                    "period": {
                        "start": start_time.isoformat() if start_time else None,
                        "end": end_time.isoformat() if end_time else None,
                    },
                    "last_updated": datetime.now(UTC).isoformat(),
                }
            except Exception as query_error:
                # Fallback to empty metrics if repository query fails
                logger.warning(
                    f"Failed to query repository for metrics: {query_error}"
                )
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
                    "query_error": str(query_error),
                }
                logger.info("API request metrics calculated successfully")
            return FlextResult.ok(metrics)

        except Exception as e:
            logger.exception("Failed to calculate API request metrics")
            return FlextResult.fail(f"Failed to calculate metrics: {e}")

    async def _get_requests_in_period(
        self, start_time: datetime | None, end_time: datetime | None
    ) -> FlextResult[Any]:
        """Get all requests in the specified time period.

        Args:
            start_time: Start time for filtering,
            end_time: End time for filtering,

        Returns:
            List of API requests in the time period

        """
        if not self.request_repo:
            return FlextResult.ok([])

        try:
            # If repository has time-based query methods, use them
            if hasattr(self.request_repo, "find_by_time_range"):
                result = await self.request_repo.find_by_time_range(
                    start_time, end_time
                )
                return FlextResult.ok(result if isinstance(result, list) else [])
            if hasattr(self.request_repo, "find_all"):
                # Fallback: get all and filter in memory
                all_requests = await self.request_repo.find_all()

                if start_time is None and end_time is None:
                    return FlextResult.ok(all_requests if isinstance(all_requests, list) else [])

                # Filter by time if timestamps are available
                filtered = []
                for req in all_requests:
                    if hasattr(req, "timestamp") and req.timestamp:
                        if start_time and req.timestamp < start_time:
                            continue
                        if end_time and req.timestamp > end_time:
                            continue
                    filtered.append(req)
                return FlextResult.ok(filtered)
            return FlextResult.ok([])
        except Exception as e:
            logger.warning(f"Failed to query requests by time period: {e}")
            return FlextResult.ok([])

    async def _get_responses_for_requests(
        self, request_ids: list[str]
    ) -> FlextResult[Any]:
        """Get responses for the given request IDs.

        Args:
            request_ids: List of request IDs to find responses for,

        Returns:
            List of API responses for the request IDs

        """
        if not self.response_repo or not request_ids:
            return FlextResult.ok([])

        try:
            responses = []
            for request_id in request_ids:
                if hasattr(self.response_repo, "find_by_request_id"):
                    response = await self.response_repo.find_by_request_id(request_id)
                    if response:
                        responses.append(response)
                elif hasattr(self.response_repo, "find_all"):
                    # Less efficient fallback
                    all_responses = await self.response_repo.find_all()
                    for resp in all_responses:
                        if (
                            hasattr(resp, "request_id")
                            and resp.request_id == request_id
                        ):
                            responses.append(resp)
                            break
            return FlextResult.ok(responses)
        except Exception as e:
            logger.warning(f"Failed to query responses for requests: {e}")
            return FlextResult.ok([])

    def _count_by_attribute(self, items: list[Any], attribute: str) -> dict[str, int]:
        """Count items by a specific attribute.

        Args:
            items: List of items to count,
            attribute: Attribute name to count by,

        Returns:
            Dictionary with attribute values as keys and counts as values

        """
        counts: dict[str, int] = {}
        for item in items:
            if hasattr(item, attribute):
                value = getattr(item, attribute)
                # Convert to string for consistent dictionary keys
                key = str(value) if value is not None else "unknown"
                counts[key] = counts.get(key, 0) + 1
        return counts

    async def _check_repository_health(self, repository: Any) -> bool:
        """Check if a repository is healthy and responsive.

        Args:
            repository: Repository instance to check,

        Returns:
            True if repository is healthy, False otherwise

        """
        try:
            # Try to perform a simple operation to test repository health
            if hasattr(repository, "health_check"):
                # Use repository's own health check if available
                result = await repository.health_check()
                return result is True or (
                    hasattr(result, "is_success") and result.is_success
                )
            if hasattr(repository, "ping"):
                # Alternative health check method
                await repository.ping()
                return True
            if hasattr(repository, "find_all"):
                # Test basic query operation with limit to avoid loading all data
                try:
                    if hasattr(repository, "find_with_limit"):
                        await repository.find_with_limit(1)
                    else:
                        # This is a basic connectivity test, not a full data fetch
                        await asyncio.wait_for(repository.find_all(), timeout=1.0)
                    return True
                except TimeoutError:
                    # Repository is slow but responsive
                    return True
            else:
                # No standard methods available, assume healthy if no errors
                return True
        except Exception as e:
            logger.debug(f"Repository health check failed: {e}")
            return False

    async def health_check(self) -> FlextResult[Any]:
        """Perform API service health check.

        Returns:
            FlextResult containing health status

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
                    # Perform actual repository health check
                    repo_healthy = await self._check_repository_health(
                        self.request_repo
                    )
                    health_data["repositories"]["request_repo_status"] = (
                        "healthy" if repo_healthy else "unhealthy"
                    )
                    if not repo_healthy:
                        health_data["status"] = "degraded"
                except (ConnectionError, TimeoutError, OSError, ValueError) as e:
                    health_data["repositories"]["request_repo_status"] = "unhealthy"
                    health_data["status"] = "degraded"
                    logger.warning(
                        f"Request repository health check failed: {e}"
                    )

            if self.response_repo:
                try:
                    # Perform actual repository health check
                    repo_healthy = await self._check_repository_health(
                        self.response_repo
                    )
                    health_data["repositories"]["response_repo_status"] = (
                        "healthy" if repo_healthy else "unhealthy"
                    )
                    if not repo_healthy:
                        health_data["status"] = "degraded"
                except (ConnectionError, TimeoutError, OSError, ValueError) as e:
                    health_data["repositories"]["response_repo_status"] = "unhealthy"
                    health_data["status"] = "degraded"
                    logger.warning(
                        f"Response repository health check failed: {e}"
                    )

            logger.info("API service health check completed successfully")
            return FlextResult.ok(health_data)

        except Exception as e:
            logger.exception("API service health check failed")
            return FlextResult.fail(f"Health check failed: {e}")
