"""FLEXT API infrastructure configuration compatibility module.

Clean Architecture
------------------
The flext-api project follows Clean Architecture with clear layer boundaries:
- Domain Layer: Entities, Value Objects, domain rules
- Application Layer: Services, use cases, handlers
- Infrastructure Layer: Adapters, persistence, HTTP clients, configuration
- Presentation Layer: FastAPI application

Dependency Injection
--------------------
Dependency Injection (DI) is a core pattern. The `flext-core` container enables
loose coupling, composability, and testability. Dependencies are provided by
factories and injected across layers via constructor injection and provider
functions. This enables clear separation of concerns.

Module Role in Architecture
--------------------------
This module explains the role of the Infrastructure package in Clean Architecture.
It focuses on configuration, adapters to external service integration, and
cross-cutting concerns, ensuring the application layer remains decoupled.

Configuration Management
------------------------
Configuration is centralized via Pydantic-based settings (`FlextApiSettings`)
with Validation, Environment Variables overrides, and Secret management. External
Service Integration is configured declaratively with typed settings.

External Service Integration
----------------------------
External Service Integration uses `FlextApiClient` with retry, caching, and
future Circuit Breaker plugins. Adapters encapsulate protocols (HTTP/gRPC/Kafka)
so that domain logic stays pure.

Cross-Cutting Concerns
----------------------
Logging, Metrics, Tracing, and Error Handling are implemented via middleware and
plugins. Observability integrates with flext-core utilities. Error Handling
propagates structured context across layers.

Core Design Patterns
--------------------
- Repository, Strategy, Factory, Builder, Decorator
- CQRS, Value Objects, Entities, Service Layer
- Dependency Injection, Configuration Management

Performance Characteristics
---------------------------
Timeouts, connection pooling, efficient JSON processing, and streaming are
considered. Benchmarks inform tuning. GZip and caching reduce latency.

Service Registration
--------------------
Services are registered in the container and resolved via interfaces, enabling
clear dependency graphs and easier testing/mocking.

Cache
-----
Cache backends (in-memory or external) are part of the infrastructure and can be
plugged via configuration. They are used by HTTP clients and repositories.

Error Handling
--------------
Errors are normalized with `FlextResult` and specific exceptions. Validation and
configuration errors are surfaced early with clear messages.

Future Expansion
----------------
Future Expansion includes additional protocols (gRPC, Kafka), alternative
persistence layers, and scalable observability backends. New adapters can be
added without changing domain or application layers.

Usage Examples
--------------
from flext_api.infrastructure import config
print(config.__doc__)

Usage Patterns
--------------
- Instantiate ServiceContainer
- Perform service registration of adapters and repositories
- Configure Multi-environment settings via Environment Variables
- Validate configuration before bootstrapping

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""
