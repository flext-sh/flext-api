"""FLEXT API Domain Module - Domain Layer Aggregation - Domain Layer.

Domain module aggregation providing unified access to domain entities, value objects,
and domain services for the FLEXT API ecosystem. Implements domain-driven design
patterns with clean boundaries and type-safe domain modeling.

Module Role in Architecture:
    Domain Layer → Domain Module → Entity/Value Object Access → Business Logic

    This module serves as the domain layer entry point that:
    - Aggregates domain entities and value objects for unified access
    - Provides clean domain boundaries with encapsulated business logic
    - Implements domain-driven design patterns with rich domain models
    - Supports railway-oriented programming with FlextResult error handling
    - Maintains domain integrity through validation and business rules

Core Design Patterns:
    1. Domain Aggregation: Unified access to domain concepts and models
    2. Clean Boundaries: Clear separation between domain and infrastructure
    3. Rich Domain Models: Entities and value objects with embedded business logic
    4. Domain Services: Business logic that doesn't naturally fit in entities
    5. Type Safety: Comprehensive type definitions for domain operations

Domain Architecture:
    Domain Entities:
        - API entities representing core business concepts
        - Rich domain models with embedded business logic
        - Validation rules and business constraints
        - Domain events for cross-boundary communication

    Value Objects:
        - Immutable domain values with validation
        - HTTP-specific value objects (URLs, headers, tokens)
        - Configuration value objects with type safety
        - Comparison and equality operations

    Domain Services:
        - Business logic that spans multiple entities
        - Complex business operations and workflows
        - Cross-cutting domain concerns and validations
        - Integration with external domain concepts

Development Status (v0.9.0 → 1.0.0):
    ✅ Production Ready: Basic domain structure, entity/value object patterns
    🔄 Enhancement: Rich domain models, domain services, domain events
    📋 TODO Migration: CQRS integration, event sourcing, aggregate patterns

Domain Concepts:
    HTTP Domain Models:
        - HTTP request and response entities with business logic
        - API endpoint entities with routing and validation
        - Authentication entities with security business rules
        - Configuration entities with validation and defaults

    Business Logic:
        - Request validation with business rules
        - Response formatting with consistency rules
        - Error handling with domain-specific error types
        - Performance optimization with domain constraints

Usage Patterns:
    # Domain entity access
    from flext_api.domain import entities, value_objects

    # Rich domain models with business logic
    api_request = entities.ApiRequest.create({
        "method": "GET",
        "url": "/users",
        "headers": {"Authorization": "Bearer token"}
    })

    # Value objects with validation
    endpoint = value_objects.Endpoint("https://api.example.com/v1")

    # Domain service operations
    from flext_api.domain.services import RequestValidationService

    validator = RequestValidationService()
    validation_result = validator.validate_request(api_request)

Quality Standards:
    - All domain models follow domain-driven design principles
    - Business logic encapsulated within appropriate domain objects
    - Type safety maintained through comprehensive annotations
    - Domain boundaries clearly defined and enforced
    - Integration with railway-oriented programming patterns

Integration Points:
    - entities.py: Domain entities with rich business logic
    - value_objects.py: Immutable value objects with validation
    - Application Layer: Domain model consumption in use cases
    - Infrastructure Layer: Domain model persistence and serialization

See Also:
    entities.py: Domain entities with embedded business logic
    value_objects.py: Immutable value objects with validation
    docs/TODO.md: Domain modeling enhancement plans

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
