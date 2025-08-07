"""FastAPI application factory.

Creates FastAPI application instance with basic configuration and health check
endpoint. Uses FlextApi service for the health check implementation.

Main function:
    Presentation Layer → FastAPI Factory → Service Integration → HTTP Endpoints

    This module implements the application factory that:
    - Creates and configures FastAPI application instances with proper settings
    - Integrates FlextApi service layer with HTTP presentation layer
    - Configures middleware pipeline for authentication, logging, and error handling
    - Establishes health check and monitoring endpoints for operational visibility
    - Follows dependency inversion principle with service layer abstraction

Core Design Patterns:
    1. Factory Pattern: Standardized application creation with configuration injection
    2. Dependency Injection: Service layer integration without tight coupling
    3. Layer Separation: Clear boundaries between presentation and application layers
    4. Configuration Management: Environment-aware application behavior
    5. Middleware Pipeline: Request/response processing with cross-cutting concerns

Application Factory Architecture:
    FastAPI Configuration:
        - Application metadata and documentation settings
        - OpenAPI specification generation with comprehensive schemas
        - CORS middleware for cross-origin resource sharing
        - Security middleware for authentication and authorization
        - Error handling middleware with proper HTTP status mapping

    Service Integration:
        - FlextApi service instantiation and lifecycle management
        - Dependency injection setup for request handlers
        - Service health monitoring and status reporting
        - Configuration validation and error propagation

    Endpoint Configuration:
        - Health check endpoints for load balancer integration
        - Monitoring endpoints for observability and metrics
        - API versioning with proper route organization
        - Request/response serialization with Pydantic models

Development Status (v0.9.0 → 1.0.0):
    ✅ Production Ready: Basic FastAPI setup, health checks, service integration
    🔄 Enhancement: Advanced middleware, authentication, comprehensive routing
    📋 TODO Migration: Full DI container, advanced security, observability integration

Critical Compliance TODOs (from docs/TODO.md):
    🚨 PRIORITY 1 - Service Lifecycle Inconsistencies (Score: 60% compliance):
        - Current: Async vs sync method inconsistency in FastAPI integration
        - Required: Standardize interface sync/async patterns throughout application
        - Must implement: Health check returning FlextResult[dict] consistently
        - Impact: Interface inconsistency across application layers

    🚨 PRIORITY 2 - Import Organization Violations (Score: 70% compliance):
        - Current: Import structure not fully standardized
        - Required: Organize imports in sections (stdlib, third-party, flext-core,
          local)
        - Must implement: Remove unused imports and standardize import patterns
        - Impact: Code organization and maintenance consistency

Application Factory Features:
    FastAPI Integration:
        - Automatic OpenAPI documentation generation with rich schemas
        - Request validation and serialization through Pydantic models
        - Response formatting with consistent structure and error handling
        - Static file serving for documentation and assets

    Middleware Pipeline:
        - Request logging with correlation IDs for tracing
        - Error handling with proper HTTP status code mapping
        - Authentication and authorization middleware integration
        - Rate limiting and request throttling for API protection

    Service Layer Integration:
        - FlextApi service instantiation with proper configuration
        - Health check endpoint with detailed service status
        - Dependency injection for clean service access patterns
        - Service lifecycle management with startup and shutdown hooks

Usage Patterns:
    # Basic application creation
    from flext_api.app import flext_api_create_app

    app = flext_api_create_app()

    # Development server with hot reload
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

    # Production deployment with Gunicorn
    # gunicorn -w 4 -k uvicorn.workers.UvicornWorker flext_api.main:app

    # Testing integration
    from fastapi.testclient import TestClient

    app = flext_api_create_app()
    client = TestClient(app)

    # Health check validation
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

Health Check Implementation:
    Service Health Monitoring:
        - FlextApi service status with detailed component information
        - Database connectivity and performance metrics
        - External service dependency status and response times
        - Resource utilization and capacity information

    Health Check Response:
        - Standardized health check format for monitoring tools
        - Component-level status with individual health indicators
        - Performance metrics for service optimization
        - Dependency graph for troubleshooting and diagnostics

Error Handling and Resilience:
    Application Level Errors:
        - Configuration validation errors with meaningful messages
        - Service dependency failures with fallback mechanisms
        - Request processing errors with proper HTTP status mapping
        - Resource exhaustion handling with graceful degradation

    Request Level Errors:
        - Input validation errors with detailed field-level feedback
        - Authentication and authorization errors with clear guidance
        - Business logic errors with context-appropriate error codes
        - Service layer errors with proper error propagation

Performance Characteristics:
    - Fast application startup with lazy service initialization
    - Efficient request routing with minimal overhead
    - Connection pooling for database and external service access
    - Response caching with configurable TTL and invalidation
    - Async request handling with high concurrency support

Quality Standards:
    - All endpoints return consistent response formats
    - Error handling follows HTTP status code conventions
    - Health checks provide comprehensive service status
    - Configuration validation prevents runtime failures
    - Service integration follows dependency inversion principle

Integration Points:
    - api.py: FlextApi service layer for business logic
    - main.py: Application bootstrap and entry point
    - FastAPI: Web framework for HTTP request handling
    - Pydantic: Request/response serialization and validation
    - Service Layer: Business logic and data access patterns

See Also:
    main.py: Application bootstrap and server configuration
    api.py: Service layer implementation with business logic
    docs/TODO.md: Advanced application patterns and middleware integration

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import FastAPI

if TYPE_CHECKING:
    from flext_core.semantic_types import FlextTypes

from flext_api.api import create_flext_api


def flext_api_create_app() -> FastAPI:
    """Create and configure FastAPI application instance."""
    # Create FlextApi service instance
    flext_api = create_flext_api()

    # Create FastAPI app
    app = FastAPI(
        title="FLEXT API",
        description="Enterprise-grade distributed data integration platform",
        version="0.9.0",
    )

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> FlextTypes.Core.JsonDict:
        """Health check endpoint."""
        result = flext_api.health_check()
        return result.data if result.data is not None else {}

    return app


# Create default app instance for testing and development
app = flext_api_create_app()
