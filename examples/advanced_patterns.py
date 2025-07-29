"""Advanced FLEXT-API Patterns and Use Cases.

This file demonstrates advanced patterns for maximum code reduction and productivity.
"""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from flext_api import (
    FlextAPIBuilder,
    FlextQueryBuilder,
    FlextResponseBuilder,
    FlextValidator,
    authenticated,
    authorize_roles,
    cache_response,
    handle_errors,
    log_execution,
    rate_limit,
    validate_request,
)

if TYPE_CHECKING:
    from fastapi import Request


# =============================================================================
# EXAMPLE 1: Custom API Builder for Complex Applications
# =============================================================================
def create_enterprise_api() -> object:
    """Create enterprise API with custom configuration."""
    from flext_api.helpers.api_builder import FlextAPIConfig

    # Custom configuration
    config = FlextAPIConfig(
        title="Enterprise Data Platform",
        version="2.0.0",
        description="High-performance data processing API",
        cors_origins=["https://app.company.com", "https://admin.company.com"],
        rate_limit_per_minute=1000,  # Higher limits for enterprise
        enable_request_logging=True,
        enable_response_logging=False,  # Reduce noise in production
    )

    # Build with custom middleware and handlers
    return (
        FlextAPIBuilder(config)
        .with_cors()
        .with_rate_limiting()
        .with_security()
        .with_logging()
        .with_trusted_hosts(["api.company.com", "*.company.com"])
        .add_health_checks()
        .add_info_endpoint()
        .with_global_exception_handler()
        .add_startup_task(initialize_database)
        .add_shutdown_task(cleanup_resources)
        .build()
    )


async def initialize_database() -> None:
    """Startup task for database initialization."""
    # Database initialization logic here


async def cleanup_resources() -> None:
    """Shutdown task for resource cleanup."""
    # Cleanup logic here


# =============================================================================
# EXAMPLE 2: Advanced Decorator Patterns
# =============================================================================
class DataProcessingRequest(BaseModel):
    """Data processing request model."""

    data_source: str
    filters: dict[str, Any] = {}
    aggregations: list[str] = []
    output_format: str = "json"


# Create the enterprise API
app = create_enterprise_api()


@app.post("/data/process")
@handle_errors(default_status=422)  # Custom error status
@log_execution(log_duration=True, log_args=False)
@rate_limit(calls=10, period=60)  # Strict rate limiting for expensive operations
@cache_response(ttl=300)  # Cache results for 5 minutes
@authenticated()  # Require authentication
@authorize_roles("data_analyst", "admin")  # Role-based access
@validate_request(DataProcessingRequest)
async def process_data(request: Request) -> dict[str, Any]:
    """Process data with multiple layers of middleware."""
    data_request = request.validated_data

    # Simulate expensive data processing
    await simulate_data_processing(data_request.data_source)

    result = {
        "processed_records": 10000,
        "data_source": data_request.data_source,
        "filters_applied": len(data_request.filters),
        "output_format": data_request.output_format,
        "processing_time_ms": 1500,
    }

    return (
        FlextResponseBuilder()
        .success("Data processing completed")
        .with_data(result)
        .with_performance(execution_time_ms=1500, cached=False)
        .build()
    )


async def simulate_data_processing(data_source: str) -> None:
    """Simulate expensive data processing operation."""
    # Simulate processing time
    await asyncio.sleep(0.1)


# =============================================================================
# EXAMPLE 3: Complex Query Building for Analytics
# =============================================================================
class AnalyticsRequest(BaseModel):
    """Analytics query request."""

    metrics: list[str]
    dimensions: list[str]
    date_range: dict[str, str]
    filters: dict[str, Any] = {}
    limit: int = 1000


@app.post("/analytics/query")
@handle_errors()
@log_execution()
@validate_request(AnalyticsRequest)
async def run_analytics_query(request: Request) -> dict[str, Any]:
    """Run complex analytics query with dynamic filtering."""
    analytics_request = request.validated_data

    # Build complex analytics query
    query_builder = FlextQueryBuilder()

    # Add date range filter
    date_range = analytics_request.date_range
    if "start_date" in date_range and "end_date" in date_range:
        query_builder.between("date", date_range["start_date"], date_range["end_date"])

    # Add dynamic filters
    for field, value in analytics_request.filters.items():
        if isinstance(value, list):
            query_builder.in_values(field, value)
        elif isinstance(value, dict):
            # Handle range filters
            if "min" in value:
                query_builder.greater_than_or_equal(field, value["min"])
            if "max" in value:
                query_builder.less_than_or_equal(field, value["max"])
        else:
            query_builder.equals(field, value)

    # Add metrics as selected fields
    query_builder.select_fields(
        *analytics_request.metrics, *analytics_request.dimensions,
    )

    # Add limit
    query_builder.limit(analytics_request.limit)

    # Add grouping metadata
    query_builder.with_metadata("group_by", analytics_request.dimensions)
    query_builder.with_metadata("aggregations", analytics_request.metrics)

    query = query_builder.build()

    # Simulate analytics processing
    results = await process_analytics_query(query)

    return (
        FlextResponseBuilder()
        .success("Analytics query completed")
        .with_data(results)
        .with_metadata("query", query)
        .with_metadata("execution_plan", "optimized_scan")
        .build()
    )


async def process_analytics_query(query: dict[str, Any]) -> dict[str, Any]:
    """Process analytics query and return results."""
    # Simulate analytics processing
    return {
        "total_rows": 50000,
        "aggregated_results": [
            {"dimension": "product_A", "metric_1": 1000, "metric_2": 2000},
            {"dimension": "product_B", "metric_1": 1500, "metric_2": 2500},
        ],
        "query_time_ms": 250,
    }


# =============================================================================
# EXAMPLE 4: Batch Operations with Validation
# =============================================================================
class BatchOperation(BaseModel):
    """Individual batch operation."""

    operation: str  # "create", "update", "delete"
    entity_type: str
    entity_id: str | None = None
    data: dict[str, Any] = {}


class BatchRequest(BaseModel):
    """Batch operations request."""

    operations: list[BatchOperation]
    atomic: bool = True  # All operations succeed or all fail
    max_operations: int = 100


@app.post("/batch/operations")
@handle_errors()
@log_execution(log_duration=True)
@rate_limit(calls=5, period=60)  # Strict limits for batch operations
@validate_request(BatchRequest)
async def execute_batch_operations(request: Request) -> dict[str, Any]:
    """Execute batch operations with comprehensive validation."""
    batch_request = request.validated_data

    # Validate batch size
    validator = FlextValidator()
    validator.validate_range(
        "operations_count",
        len(batch_request.operations),
        1,
        batch_request.max_operations,
    )

    # Validate each operation
    for i, operation in enumerate(batch_request.operations):
        validator.validate_choices(
            f"operation[{i}].operation",
            operation.operation,
            ["create", "update", "delete"],
        )

        if operation.operation in {"update", "delete"}:
            validator.validate_required(
                f"operation[{i}].entity_id", operation.entity_id,
            )

        if operation.operation in {"create", "update"}:
            validator.validate_required(f"operation[{i}].data", operation.data)

    validation_result = validator.get_result()
    if not validation_result.success:
        return FlextResponseBuilder().from_result(validation_result).build()

    # Execute operations
    results = []
    failed_operations = []

    for i, operation in enumerate(batch_request.operations):
        try:
            result = await execute_single_operation(operation)
            results.append({"index": i, "status": "success", "result": result})
        except Exception as e:
            error_info = {"index": i, "status": "failed", "error": str(e)}
            failed_operations.append(error_info)
            results.append(error_info)

    # Check if atomic operation failed
    if batch_request.atomic and failed_operations:
        return (
            FlextResponseBuilder()
            .error("Batch operation failed (atomic mode)", "Some operations failed")
            .with_data({"failed_operations": failed_operations})
            .build()
        )

    # Return results
    success_count = len([r for r in results if r["status"] == "success"])

    return (
        FlextResponseBuilder()
        .success(
            f"Batch operation completed: {success_count}/{len(results)} successful",
        )
        .with_data(results)
        .with_metadata("total_operations", len(results))
        .with_metadata("successful_operations", success_count)
        .with_metadata("failed_operations", len(failed_operations))
        .build()
    )


async def execute_single_operation(operation: BatchOperation) -> dict[str, Any]:
    """Execute a single batch operation."""
    # Simulate operation execution
    if operation.operation == "create":
        return {"id": "new_entity_123", "created": True}
    if operation.operation == "update":
        return {"id": operation.entity_id, "updated": True}
    if operation.operation == "delete":
        return {"id": operation.entity_id, "deleted": True}
    msg = f"Unknown operation: {operation.operation}"
    raise ValueError(msg)


# =============================================================================
# EXAMPLE 5: Real-time Data Streaming with Validation
# =============================================================================
class StreamConfig(BaseModel):
    """Stream configuration."""

    stream_name: str
    buffer_size: int = 1000
    flush_interval_ms: int = 5000
    filters: dict[str, Any] = {}


@app.post("/streams/create")
@handle_errors()
@log_execution()
@validate_request(StreamConfig)
async def create_data_stream(request: Request) -> dict[str, Any]:
    """Create a real-time data stream."""
    stream_config = request.validated_data

    # Validate stream configuration
    validator = (
        FlextValidator()
        .validate_min_length("stream_name", stream_config.stream_name, 3)
        .validate_max_length("stream_name", stream_config.stream_name, 50)
        .validate_range("buffer_size", stream_config.buffer_size, 100, 10000)
        .validate_range(
            "flush_interval_ms", stream_config.flush_interval_ms, 1000, 60000,
        )
    )

    validation_result = validator.get_result()
    if not validation_result.success:
        return FlextResponseBuilder().from_result(validation_result).build()

    # Create stream (simulation)
    stream_id = f"stream_{int(time.time())}"

    stream_info = {
        "stream_id": stream_id,
        "stream_name": stream_config.stream_name,
        "status": "active",
        "created_at": time.time(),
        "config": stream_config.dict(),
    }

    return (
        FlextResponseBuilder()
        .success("Data stream created successfully")
        .with_data(stream_info)
        .with_metadata("endpoint", f"/streams/{stream_id}/data")
        .build()
    )


# =============================================================================
# EXAMPLE 6: Advanced Response Building with Metrics
# =============================================================================
@app.get("/system/metrics")
@handle_errors()
@cache_response(ttl=60)  # Cache for 1 minute
async def get_system_metrics() -> dict[str, Any]:
    """Get system metrics with comprehensive response."""
    start_time = time.time()

    # Simulate metrics collection
    metrics = await collect_system_metrics()

    execution_time = (time.time() - start_time) * 1000

    return (
        FlextResponseBuilder()
        .success("System metrics retrieved")
        .with_data(metrics)
        .with_performance(execution_time_ms=execution_time, cached=False)
        .with_metadata("collection_time", time.time())
        .with_metadata("metrics_count", len(metrics))
        .with_metadata("next_update", time.time() + 60)
        .build()
    )


async def collect_system_metrics() -> dict[str, Any]:
    """Collect system metrics."""
    return {
        "cpu_usage": 45.2,
        "memory_usage": 67.8,
        "disk_usage": 23.1,
        "active_connections": 150,
        "requests_per_minute": 2500,
        "error_rate": 0.1,
    }


# =============================================================================
# CODE REDUCTION ANALYSIS
# =============================================================================
"""
TRADITIONAL ENTERPRISE API SETUP (500+ lines):
- Custom middleware for CORS, security, logging
- Manual request validation for each endpoint
- Custom error handling in every route
- Manual response formatting
- Complex query building from scratch
- Manual authentication and authorization
- Custom rate limiting implementation
- Manual caching logic
- Extensive boilerplate for batch operations

FLEXT-API ENTERPRISE SETUP (100-150 lines):
- One-line API creation with FlextAPIBuilder
- Decorator-based request validation
- Automatic error handling and logging
- Standardized response building
- Built-in query building with FlextQueryBuilder
- Decorator-based auth and rate limiting
- Built-in caching decorators
- Powerful validation chains
- Batch operation helpers

RESULT: 70-80% CODE REDUCTION with enhanced functionality and maintainability.

Additional Benefits:
- Consistent error responses across all endpoints
- Automatic request/response logging
- Built-in performance monitoring
- Standardized validation patterns
- Easy to test and mock
- Self-documenting API structure
"""
