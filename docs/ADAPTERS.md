# Protocol Adapters Guide

**flext-api Protocol Adaptation System**
**Version**: 1.0.0 | **Last Updated**: 2025-10-01

## Overview

The flext-api adapter system enables seamless conversion between different API protocols and formats, including HTTP ↔ WebSocket, HTTP ↔ GraphQL, schema format conversions, and legacy API integration.

## Available Adapters

### 1. HTTP to WebSocket Adapter

**Purpose**: Convert HTTP requests to WebSocket messages and vice versa

**Use Cases**:
- Bridge HTTP clients to WebSocket servers
- Convert REST API calls to real-time WebSocket communication
- Protocol gateway implementations

**Usage**:
```python
from flext_api.adapters import HttpToWebSocketAdapter
from flext_api.models import FlextApiModels

adapter = HttpToWebSocketAdapter()

# Adapt HTTP request to WebSocket message
request = FlextApiModels.HttpRequest(
    method="GET",
    url="/api/users",
    headers={"Authorization": "Bearer token123"}
)

result = adapter.adapt_request(request)

if result.is_success:
    ws_message = result.unwrap()
    # ws_message = {
    #     "type": "request",
    #     "method": "GET",
    #     "url": "/api/users",
    #     "headers": {"Authorization": "Bearer token123"},
    #     "body": {}
    # }

# Adapt WebSocket message to HTTP response
ws_response = {
    "status": 200,
    "body": {"users": [{"id": 1, "name": "John"}]},
    "headers": {"Content-Type": "application/json"},
    "url": "/api/users",
    "method": "GET"
}

result = adapter.adapt_response(ws_response)

if result.is_success:
    http_response = result.unwrap()
    print(f"Status: {http_response.status_code}")
    print(f"Body: {http_response.body}")
```

### 2. GraphQL to HTTP Adapter

**Purpose**: Convert GraphQL queries/mutations to HTTP requests and responses

**Use Cases**:
- GraphQL client over HTTP
- GraphQL gateway implementations
- REST to GraphQL migration
- Schema introspection

**Configuration**:
```python
from flext_api.adapters import GraphQLToHttpAdapter

# Create adapter with custom endpoint
adapter = GraphQLToHttpAdapter(endpoint="/api/graphql")

# Default endpoint is "/graphql"
default_adapter = GraphQLToHttpAdapter()
```

**Usage**:
```python
from flext_api.adapters import GraphQLToHttpAdapter

adapter = GraphQLToHttpAdapter()

# Convert GraphQL query to HTTP request
query = """
query GetUser($id: ID!) {
    user(id: $id) {
        id
        name
        email
    }
}
"""

variables = {"id": "123"}

result = adapter.adapt_query_to_request(query, variables)

if result.is_success:
    http_request = result.unwrap()
    # http_request.method = "POST"
    # http_request.url = "/graphql"
    # http_request.body = {
    #     "query": "query GetUser($id: ID!) { ... }",
    #     "variables": {"id": "123"}
    # }

# Convert HTTP response to GraphQL result
from flext_api.models import FlextApiModels

http_response = FlextApiModels.HttpResponse(
    status_code=200,
    body={
        "data": {
            "user": {
                "id": "123",
                "name": "John",
                "email": "john@example.com"
            }
        }
    },
    url="/graphql",
    method="POST"
)

result = adapter.adapt_response_to_result(http_response)

if result.is_success:
    graphql_result = result.unwrap()
    # graphql_result = {
    #     "user": {
    #         "id": "123",
    #         "name": "John",
    #         "email": "john@example.com"
    #     }
    # }
```

**Error Handling**:
```python
# GraphQL errors
http_response = FlextApiModels.HttpResponse(
    status_code=200,
    body={
        "errors": [
            {"message": "Field 'email' not found on type 'User'"}
        ]
    },
    url="/graphql",
    method="POST"
)

result = adapter.adapt_response_to_result(http_response)

if result.is_failure:
    print(f"GraphQL Error: {result.error}")
    # Output: "GraphQL errors: Field 'email' not found on type 'User'"

# HTTP errors
http_response = FlextApiModels.HttpResponse(
    status_code=500,
    body={},
    url="/graphql",
    method="POST"
)

result = adapter.adapt_response_to_result(http_response)

if result.is_failure:
    print(f"HTTP Error: {result.error}")
    # Output: "GraphQL request failed with status 500"
```

### 3. Schema Adapter

**Purpose**: Convert between OpenAPI, API, and GraphQL schema formats

**Use Cases**:
- API documentation migration
- Multi-protocol API development
- Schema validation and transformation
- Code generation from schemas

**OpenAPI to API**:
```python
from flext_api.adapters import SchemaAdapter

adapter = SchemaAdapter()

openapi_schema = {
    "openapi": "3.0.0",
    "info": {"title": "User API", "version": "1.0.0"},
    "paths": {
        "/users": {
            "get": {
                "operationId": "getUsers",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {"type": "object"}
                        }
                    }
                }
            }
        }
    }
}

result = adapter.openapi_toapi(openapi_schema)

if result.is_success:
    api_schema = result.unwrap()
    # api_schema = {
    #     "api": "3.0.0",
    #     "info": {"title": "User API", "version": "1.0.0"},
    #     "channels": {
    #         "users": {
    #             "subscribe": {
    #                 "operationId": "getUsers",
    #                 "message": {"payload": {"type": "object"}}
    #             }
    #         }
    #     }
    # }
```

**OpenAPI to GraphQL SDL**:
```python
from flext_api.adapters import SchemaAdapter

adapter = SchemaAdapter()

openapi_schema = {
    "openapi": "3.0.0",
    "info": {"title": "User API", "version": "1.0.0"},
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "email": {"type": "string"}
                }
            }
        }
    },
    "paths": {
        "/users": {
            "get": {"operationId": "getUsers"},
            "post": {"operationId": "createUser"}
        }
    }
}

result = adapter.openapi_to_graphql_schema(openapi_schema)

if result.is_success:
    graphql_sdl = result.unwrap()
    # Output:
    # type User {
    #     id: Int
    #     name: String
    #     email: String
    # }
    #
    # type Query {
    #     getUsers: [User]
    # }
    #
    # type Mutation {
    #     createUser: User
    # }
```

### 4. Legacy API Adapter

**Purpose**: Integrate legacy APIs with modern applications

**Features**:
- Field name transformation (camelCase ↔ snake_case)
- Authentication header conversion
- Status code mapping
- URL rewriting

**Configuration**:
```python
from flext_api.adapters import LegacyApiAdapter

# Create adapter with legacy API base URL
adapter = LegacyApiAdapter(base_url="https://legacy.api.com")
```

**Modern to Legacy Request**:
```python
from flext_api.adapters import LegacyApiAdapter
from flext_api.models import FlextApiModels

adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

# Modern request with camelCase
modern_request = FlextApiModels.HttpRequest(
    method="POST",
    url="/users",
    headers={"Authorization": "Bearer token123"},
    body={"userName": "john", "firstName": "John", "lastName": "Doe"}
)

result = adapter.adapt_request(modern_request)

if result.is_success:
    legacy_request = result.unwrap()
    # legacy_request.url = "https://legacy.api.com/users"
    # legacy_request.headers = {"X-API-Key": "token123"}
    # legacy_request.body = {
    #     "user_name": "john",
    #     "first_name": "John",
    #     "last_name": "Doe"
    # }
```

**Legacy to Modern Response**:
```python
from flext_api.adapters import LegacyApiAdapter
from flext_api.models import FlextApiModels

adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

# Legacy response with snake_case
legacy_response = FlextApiModels.HttpResponse(
    status_code=200,
    body={
        "user_name": "john",
        "first_name": "John",
        "last_name": "Doe",
        "created_at": "2025-01-01"
    },
    url="/users",
    method="GET"
)

result = adapter.adapt_response(legacy_response)

if result.is_success:
    modern_response = result.unwrap()
    # modern_response.body = {
    #     "userName": "john",
    #     "firstName": "John",
    #     "lastName": "Doe",
    #     "createdAt": "2025-01-01"
    # }
```

**Status Code Mapping**:
```python
from flext_api.adapters import LegacyApiAdapter

adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

# Legacy APIs often use custom status codes
# The adapter maps them to standard HTTP codes:
# 1 → 200 (Success)
# 2 → 400 (Validation error)
# 3 → 401 (Authentication error)
# 4 → 404 (Not found)
# 5 → 500 (Server error)
# Other codes are preserved

modern_status = adapter._adapt_status_code(1)  # Returns 200
error_status = adapter._adapt_status_code(3)   # Returns 401
```

## Advanced Usage

### Chaining Adapters

Combine multiple adapters for complex transformations:

```python
from flext_api.adapters import (
    LegacyApiAdapter,
    HttpToWebSocketAdapter
)

# Step 1: Adapt modern request to legacy format
legacy_adapter = LegacyApiAdapter(base_url="https://legacy.api.com")
legacy_request_result = legacy_adapter.adapt_request(modern_request)

if legacy_request_result.is_success:
    legacy_request = legacy_request_result.unwrap()

    # Step 2: Convert legacy HTTP request to WebSocket message
    ws_adapter = HttpToWebSocketAdapter()
    ws_message_result = ws_adapter.adapt_request(legacy_request)

    if ws_message_result.is_success:
        ws_message = ws_message_result.unwrap()
        # Now you have a WebSocket message for legacy API
```

### Custom Field Name Transformations

Extend the LegacyApiAdapter for custom transformations:

```python
from flext_api.adapters import LegacyApiAdapter
from typing import object

class CustomLegacyAdapter(LegacyApiAdapter):
    """Custom adapter with additional transformations."""

    def _transform_payload(self, payload: dict[str, object]) -> dict[str, object]:
        """Add custom field transformations."""
        transformed = super()._transform_payload(payload)

        # Add custom logic
        if "timestamp" in transformed:
            # Convert ISO to legacy format
            transformed["timestamp"] = self._convert_timestamp(
                transformed["timestamp"]
            )

        return transformed

    def _convert_timestamp(self, iso_timestamp: str) -> str:
        """Convert timestamp format."""
        # Custom timestamp conversion logic
        return iso_timestamp.replace("T", " ")
```

### Error Recovery

Handle adaptation failures gracefully:

```python
from flext_api.adapters import GraphQLToHttpAdapter
from flext_core import FlextResult

def safe_graphql_query(query: str, variables: dict) -> FlextResult[dict]:
    """Execute GraphQL query with error recovery."""
    adapter = GraphQLToHttpAdapter()

    # Try to adapt query
    request_result = adapter.adapt_query_to_request(query, variables)

    if request_result.is_failure:
        # Log error and return failure
        print(f"Query adaptation failed: {request_result.error}")
        return FlextResult[dict].fail(request_result.error)

    # Send HTTP request (implementation specific)
    # response = http_client.send(request_result.unwrap())

    # Adapt response
    # result = adapter.adapt_response_to_result(response)
    # return result

    return FlextResult[dict].ok({"status": "prepared"})
```

## Best Practices

### 1. Use Appropriate Adapters

- **HTTP ↔ WebSocket**: Real-time API gateways, protocol bridges
- **HTTP ↔ GraphQL**: GraphQL client implementations, REST migration
- **Schema Adapters**: Documentation generation, multi-protocol APIs
- **Legacy Adapters**: Modernization projects, API facade patterns

### 2. Handle Bidirectional Conversions

Always consider both directions when using adapters:

```python
# Forward: Modern → Legacy
legacy_request = adapter.adapt_request(modern_request)

# Reverse: Legacy → Modern
modern_response = adapter.adapt_response(legacy_response)
```

### 3. Validate After Adaptation

```python
def validate_adapted_request(adapted_result: FlextResult):
    """Validate adapted request before sending."""
    if adapted_result.is_failure:
        return adapted_result

    adapted_request = adapted_result.unwrap()

    # Validate required fields
    if not adapted_request.url:
        return FlextResult.fail("Missing URL in adapted request")

    return adapted_result
```

### 4. Log Adaptations for Debugging

```python
from flext_core import get_logger

logger = get_logger("adapters")

def logged_adaptation(adapter, request):
    """Adapt with logging."""
    logger.info("Adapting request", url=request.url, method=request.method)

    result = adapter.adapt_request(request)

    if result.is_success:
        logger.info("Adaptation successful")
    else:
        logger.error("Adaptation failed", error=result.error)

    return result
```

## Testing

```python
import pytest
from flext_api.adapters import HttpToWebSocketAdapter
from flext_api.models import FlextApiModels

def test_http_to_websocket_roundtrip():
    """Test HTTP to WebSocket bidirectional conversion."""
    adapter = HttpToWebSocketAdapter()

    # Create HTTP request
    original_request = FlextApiModels.HttpRequest(
        method="POST",
        url="/api/users",
        headers={"Content-Type": "application/json"},
        body={"name": "John"}
    )

    # Adapt to WebSocket
    ws_result = adapter.adapt_request(original_request)
    assert ws_result.is_success

    ws_message = ws_result.unwrap()
    assert ws_message["method"] == "POST"
    assert ws_message["url"] == "/api/users"

    # Simulate WebSocket response
    ws_response = {
        "status": 201,
        "body": {"id": 1, "name": "John"},
        "headers": {"Content-Type": "application/json"},
        "url": "/api/users",
        "method": "POST"
    }

    # Adapt back to HTTP
    http_result = adapter.adapt_response(ws_response)
    assert http_result.is_success

    http_response = http_result.unwrap()
    assert http_response.status_code == 201
    assert http_response.body["id"] == 1
```

## Troubleshooting

### GraphQL Adaptation Errors

**Problem**: `GraphQL errors: Field not found`

**Solution**: Check GraphQL schema and query syntax
```python
# Verify query is valid GraphQL
result = adapter.adapt_query_to_request(query, variables)
if result.is_failure:
    print(f"Invalid query: {result.error}")
```

### Legacy API Field Mapping

**Problem**: Fields not converting correctly

**Solution**: Debug transformation process
```python
adapter = LegacyApiAdapter(base_url="https://legacy.api.com")

# Test field transformation
camel_case = "userName"
snake_case = adapter._camel_to_snake(camel_case)
print(f"{camel_case} → {snake_case}")  # userName → user_name
```

### WebSocket Message Format

**Problem**: WebSocket server doesn't accept adapted messages

**Solution**: Customize message format
```python
class CustomWSAdapter(HttpToWebSocketAdapter):
    def adapt_request(self, request):
        result = super().adapt_request(request)
        if result.is_success:
            message = result.unwrap()
            # Add custom fields
            message["timestamp"] = time.time()
        return result
```

## API Reference

### HttpToWebSocketAdapter
- `adapt_request(request: HttpRequest) -> FlextResult[dict]`
- `adapt_response(message: dict) -> FlextResult[HttpResponse]`

### GraphQLToHttpAdapter
- `__init__(endpoint: str = "/graphql")`
- `adapt_query_to_request(query: str, variables: dict) -> FlextResult[HttpRequest]`
- `adapt_response_to_result(response: HttpResponse) -> FlextResult[dict]`

### SchemaAdapter
- `openapi_toapi(schema: dict) -> FlextResult[dict]`
- `openapi_to_graphql_schema(schema: dict) -> FlextResult[str]`

### LegacyApiAdapter
- `__init__(base_url: str)`
- `adapt_request(request: HttpRequest) -> FlextResult[HttpRequest]`
- `adapt_response(response: HttpResponse) -> FlextResult[HttpResponse]`
- `_camel_to_snake(name: str) -> str`
- `_snake_to_camel(name: str) -> str`
- `_adapt_status_code(code: int) -> int`

---

**Copyright (c) 2025 FLEXT Team. All rights reserved.**
**License**: MIT
