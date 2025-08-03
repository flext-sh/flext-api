"""FLEXT API Infrastructure Module - Infrastructure Layer Aggregation.

Infrastructure module aggregation providing unified access to infrastructure components,
dependency injection, configuration management, and external service integration for
the FLEXT API ecosystem. Implements clean architecture infrastructure patterns.

Module Role in Architecture:
    Infrastructure Layer → Infrastructure Module → External Services → System

    This module serves as the infrastructure layer entry point that:
    - Aggregates infrastructure components for unified access
    - Provides dependency injection container and service registration
    - Manages configuration loading and environment integration
    - Handles external service integration and adapter patterns
    - Implements cross-cutting concerns like logging and monitoring

Core Design Patterns:
    1. Infrastructure Aggregation: Unified access to infrastructure services
    2. Dependency Injection: Service registration and container management
    3. Adapter Pattern: External service integration with clean boundaries
    4. Configuration Management: Environment-aware configuration loading
    5. Cross-Cutting Concerns: Logging, monitoring, and observability

Infrastructure Architecture:
    Configuration Management:
        - Environment variable integration with type safety
        - Configuration validation and error handling
        - Multi-environment configuration support
        - Secret management and security patterns

    Dependency Injection:
        - Service container with lifecycle management
        - Automatic dependency resolution and injection
        - Interface-based service registration
        - Scoped service management (singleton, transient, scoped)

    External Service Integration:
        - HTTP client configuration and connection pooling
        - Database connection management and transaction support
        - Cache service integration with TTL and invalidation
        - Message queue integration for async processing

Development Status (v0.9.0 → 1.0.0):
    ✅ Production Ready: Basic infrastructure structure, configuration management
    🔄 Enhancement: Advanced DI container, service discovery, health monitoring
    📋 TODO Migration: Full Clean Architecture compliance, observability integration

Critical Compliance TODOs (from docs/TODO.md):
    🚨 PRIORITY 1 - Documentation Alignment (Score: 70% compliance):
        - Current: Basic infrastructure documentation
        - Required: Update docstrings to follow comprehensive flext-core patterns
        - Must implement: Add type documentation and comprehensive examples
        - Impact: Developer experience and ecosystem consistency

    🚨 PRIORITY 2 - Clean Architecture Gaps (Score: 75% compliance):
        - Current: Infrastructure layer mostly compliant
        - Required: Full Clean Architecture compliance with clear boundaries
        - Must implement: Infrastructure abstraction patterns and interface segregation
        - Impact: Architectural consistency across ecosystem projects

Infrastructure Components:
    Configuration Services:
        - Environment-specific configuration loading
        - Validation and type conversion for settings
        - Configuration hot-reload and change detection
        - Secret management with encryption and rotation

    Service Container:
        - Type-safe service registration and resolution
        - Lifecycle management with proper disposal
        - Circular dependency detection and resolution
        - Performance monitoring and service health checks

    External Adapters:
        - Database adapters with connection pooling
        - HTTP service adapters with retry and circuit breaker
        - Cache adapters with distributed caching support
        - Monitoring adapters with metrics and tracing

Usage Patterns:
    # Infrastructure service access
    from flext_api.infrastructure import container, config

    # Dependency injection container
    from flext_api.infrastructure.container import ServiceContainer

    container = ServiceContainer()
    container.register_singleton(UserRepository, SqlUserRepository)
    container.register_transient(EmailService, SmtpEmailService)

    # Service resolution with type safety
    user_repo = container.resolve(UserRepository)
    email_service = container.resolve(EmailService)

    # Configuration management
    from flext_api.infrastructure.config import InfrastructureConfig

    config = InfrastructureConfig.load_from_environment()
    database_url = config.database.connection_url
    cache_settings = config.cache.get_settings()

    # External service integration
    from flext_api.infrastructure.adapters import DatabaseAdapter, CacheAdapter

    db_adapter = DatabaseAdapter(config.database)
    cache_adapter = CacheAdapter(config.cache)

Quality Standards:
    - All infrastructure components follow clean architecture principles
    - Service registration follows interface segregation principle
    - Configuration validation with comprehensive error reporting
    - External service integration with proper error handling
    - Performance monitoring and health check integration

Integration Points:
    - config.py: Infrastructure-specific configuration management
    - Domain Layer: Infrastructure service consumption through interfaces
    - Application Layer: Service injection and dependency resolution
    - External Services: Adapter pattern for clean service integration

See Also:
    config.py: Infrastructure configuration management and validation
    docs/TODO.md: Advanced infrastructure patterns and service integration
    flext-core: Base infrastructure patterns and dependency injection

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
