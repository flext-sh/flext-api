# C4 Model - Code

<!-- TOC START -->

- [Overview](#overview)
- [Code Diagram](#code-diagram)
- [Code Structure Analysis](#code-structure-analysis)
  - [Core Module Relationships](#core-module-relationships)
  - [Key Classes and Their Responsibilities](#key-classes-and-their-responsibilities)
  - [Test Fixtures](#test-fixtures)
- [Transport, Pooling and Authentication](#transport-pooling-and-authentication)

<!-- TOC END -->

## Overview

This document describes the **Code** level of the C4 model for FLEXT-API, showing the
actual implementation details, class relationships, and code organization.

## Code Diagram

```plantuml
@startuml FLEXT-API Code Structure
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Code.puml

title FLEXT-API Code Structure

package "flext_api" as flext_api {
    package "__init__.py" as init {
        class FlextApi
        class FlextApiClient
        class FlextApiApp
        class FlextApiSettings
        class FlextApiConstants
        class FlextApiModels
        class FlextApiUtilities
    }

    package "api.py" as api {
        class FlextApi
        note right: Thin facade for all functionality
    }

    package "client.py" as client {
        class FlextApiClient
        class FlextWebOperations
        class LifecycleManager
        class ConfigurationManager

        FlextApiClient --> FlextWebOperations
        FlextApiClient --> LifecycleManager
        FlextApiClient --> ConfigurationManager
    }

    package "app.py" as app {
        class FlextApiApp
        class create_fastapi_app

        note right: FastAPI application factory
    }

    package "models.py" as models {
        class FlextApiModels
        class FlextApiModels.HttpRequest
        class FlextApiModels.HttpResponse
        class FlextWebEndpoint
        class ApiConfiguration

        FlextApiModels --> FlextApiModels.HttpRequest
        FlextApiModels --> FlextApiModels.HttpResponse
        FlextApiModels --> FlextWebEndpoint
        FlextApiModels --> ApiConfiguration
    }

    package "settings.py" as settings {
        class FlextApiSettings
        class EnvironmentConfig
        class FileConfig

        FlextApiSettings --> EnvironmentConfig
        FlextApiSettings --> FileConfig
    }

    package "constants.py" as constants {
        class FlextApiConstants
        note right: HTTP status codes, timeouts, limits
    }

    package "protocols/" as protocols {
        package "__init__.py" {
            class FlextApiProtocols
            class Base
            interface ProtocolInterface
        }

        package "http.py" {
            class FlextWeb
            class FlextWebClientImplementation
        }

        package "graphql.py" {
            class GraphQL
            class GraphQLClient
        }

        package "websocket.py" {
            class WebSocket
            class WebSocketClient
        }

        BaseextWebFlextWeb
        BaseaphQLGraphQL
        BasebSockeWebSocket
    }

    package "storage.py" as storage {
        class FlextApiStorage
        class StorageBackend
        class S3Backend
        class GCSBackend
        class LocalBackend

        StorageBackend <|-- S3Backend
        StorageBackend <|-- GCSBackend
        StorageBackend <|-- LocalBackend
    }

    package "utilities.py" as utilities {
        class FlextApiUtilities
        class FlextWebUtilities
        class ValidationUtilities
        class EncodingUtilities
    }
}

package "flext_core" as flext_core {
    class r
    class FlextContainer
    class FlextModels
    class FlextLogger
    class s
    class FlextBus
    class FlextContext
}

package "External Libraries" as external {
    package "httpx" {
        class AsyncClient
        class Client
    }

    package "fastapi" {
        class FastAPI
        class Request
        class Response
    }

    package "pydantic" {
        class BaseModel
        class u.Field
        class validator
    }

    package "websockets" {
        class WebSocketClient
    }
}

' Relationships
FlextApiClient --> r : uses
FlextApiClient --> AsyncClient : uses
FlextApiModels --> BaseModel : extends
FlextApiSettings --> BaseModel : extends
FlextApi --> s : extends
FlextApiClient --> s : extends

FlextWebncClient : uses
WebSocketSockeWebSocketClient

create_fastapi_app --> FastAPI : creates
create_fastapi_app --> FlextApiClient : integrates

@enduml
```

## Code Structure Analysis

### Core Module Relationships

```text
flext_api/
├── __init__.py          # Public API exports
├── api.py              # Main facade class
├── client.py           # HTTP client implementation
├── app.py              # FastAPI application factory
├── models.py           # Data models and validation
├── settings.py           # Configuration management
├── constants.py        # Constants and enumerations
├── protocols/          # Protocol implementations
├── storage.py          # Storage abstractions
└── utilities.py        # Utility functions
```

### Key Classes and Their Responsibilities

#### FlextApi (api.py)

```python
from __future__ import annotations
```

### Test Fixtures

Shared fixtures live in `tests/conftest.py` and use the `flext_tests` facades (`tm`, typed
fixtures under `tests/fixtures/`); mocks and patches are not used.

## Transport, Pooling and Authentication

Connection reuse, timeouts and retries belong to the shared client
(`src/flext_api/services/client.py`, `FlextApiClient`) configured through
`FlextApiSettings`. Response caching and pluggable authentication handlers are not
implemented; when they are, they arrive as `p` protocols injected at the composition root.

---

**C4 Model Complete**: This concludes the C4 model documentation for FLEXT-API, showing
the progression from high-level system context down to implementation details.
