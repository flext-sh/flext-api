"""FLEXT API Domain Value Objects - Immutable Domain Values - Domain Layer.

Domain value objects implementing immutable domain values with embedded validation
and behavior for HTTP and API operations. Follows domain-driven design principles
with value objects as first-class domain concepts representing domain values.

Module Role in Architecture:
    Domain Layer → Domain Value Objects → Immutable Values → Validation Logic

    This module provides domain value objects that:
    - Encapsulate domain values with validation and behavior
    - Maintain immutability and value semantics throughout operations
    - Implement equality and comparison based on value rather than identity
    - Support railway-oriented programming with FlextResult validation
    - Provide type safety and domain modeling for complex values

Core Design Patterns:
    1. Value Object Pattern: Immutable objects with value-based equality
    2. Validation Logic: Embedded validation within value object construction
    3. Domain Modeling: HTTP concepts as first-class domain values
    4. Type Safety: Comprehensive type definitions for value operations
    5. Railway-Oriented Programming: FlextResult integration for validation

Value Object Architecture:
    HTTP Value Objects:
        - URL: HTTP URL with validation and parsing logic
        - HttpHeader: HTTP header with name/value validation
        - HttpMethod: HTTP method with allowed verb constraints
        - StatusCode: HTTP status code with semantic meaning

    Authentication Value Objects:
        - BearerToken: JWT/OAuth token with format validation
        - ApiKey: API key with format and security validation
        - Credentials: Authentication credentials with encoding
        - Permission: Authorization permission with scope validation

    Configuration Value Objects:
        - Timeout: Timeout duration with bounds validation
        - Port: Network port with range validation
        - Host: Network host with format validation
        - Endpoint: API endpoint with URL and validation logic

Development Status (v0.9.0 → 1.0.0):
    ✅ Production Ready: Basic value object structure, validation patterns
    🔄 Enhancement: Rich validation logic, complex value compositions
    📋 TODO Migration: Advanced validation, custom serialization, domain rules

Critical Compliance TODOs (from docs/TODO.md):
    🚨 PRIORITY 1 - Domain Modeling Anemic (Score: 10% compliance):
        - Current: Comprehensive docstring but needs rich value object implementations
        - Required: Full FlextValueObject implementations with embedded validation
        - Must implement: Complex domain validation rules and business logic
        - Impact: Violates DDD principles and immutable value semantics

    🚨 PRIORITY 2 - Value Object Composition (Score: 35% compliance):
        - Current: Basic value object concepts without full implementation
        - Required: Composition patterns with other value objects and entities
        - Must implement: Domain-specific validation and transformation rules
        - Impact: Limited domain modeling expressiveness and type safety

Value Object Implementation Patterns:
    Immutability and Equality:
        - Immutable construction with validation at creation time
        - Value-based equality comparison for meaningful equivalence
        - Hash code implementation based on value content
        - Comparison operations for ordered value objects

    Validation and Construction:
        - Validation logic embedded within value object construction
        - Factory methods for complex value object creation
        - Error handling with detailed validation context
        - Type conversion and normalization during construction

    Domain Behavior:
        - Domain operations as value object methods
        - Transformation operations returning new value objects
        - Formatting and serialization with domain rules
        - Integration with other value objects and entities

Usage Patterns:
    # Value object creation with validation
    from flext_api.domain.value_objects import URL, HttpHeader, BearerToken

    # URL value object with validation
    url_result = URL.create("https://api.example.com/v1/users")
    if url_result.success:
        url = url_result.data
        base_url = url.base_url()
        path = url.path()
        is_secure = url.is_https()

    # HTTP header value object
    header_result = HttpHeader.create("Authorization", "Bearer token123")
    if header_result.success:
        header = header_result.data
        header_dict = header.to_dict()
        is_auth_header = header.is_authorization()

    # Bearer token with validation
    token_result = BearerToken.create("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    if token_result.success:
        token = token_result.data
        is_expired = token.is_expired()
        claims = token.get_claims()

    # Value object composition
    endpoint_result = Endpoint.create({
        "url": "https://api.example.com",
        "method": "POST",
        "headers": [("Content-Type", "application/json")]
    })

Validation Examples:
    URL Validation:
        - URL scheme validation (http/https)
        - Host format validation with DNS compliance
        - Path validation with encoding requirements
        - Query parameter validation with type safety

    Token Validation:
        - JWT format validation with structure checking
        - Expiration time validation with current time comparison
        - Signature validation with key verification
        - Claims validation with required field checking

    Configuration Validation:
        - Port range validation (1-65535)
        - Timeout bounds validation with reasonable limits
        - Host format validation with IP and DNS support
        - Environment-specific validation rules

Error Handling Philosophy:
    - Value object creation returns FlextResult for validation errors
    - Validation errors include detailed context and suggestions
    - Immutable objects prevent invalid state after construction
    - Type safety prevents invalid value combinations
    - Domain rules enforced through validation logic

Performance Characteristics:
    - Immutable objects enable safe sharing and caching
    - Value-based equality with efficient hash code implementation
    - Fast validation with optimized pattern matching
    - Memory-efficient construction with minimal overhead
    - Lazy evaluation for expensive validation operations

Quality Standards:
    - All value objects are immutable after construction
    - Validation logic comprehensive with meaningful error messages
    - Type safety maintained through proper type annotations
    - Equality and hash code implemented correctly for collections
    - Integration with railway-oriented programming patterns

Integration Points:
    - entities.py: Value objects used within entity composition
    - Validation Framework: Type-safe validation with detailed feedback
    - Serialization: Custom serialization with domain rules
    - Configuration: Type-safe configuration with validation

See Also:
    entities.py: Domain entities that compose value objects
    docs/TODO.md: Advanced value object patterns and validation
    flext-core/value_objects.py: Base value object patterns and DDD

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations
