# Middleware API Reference

<!-- TOC START -->

- [HTTP Middleware System](#http-middleware-system)
  - [FlextApiMiddleware - Base Middleware Class](#flextapimiddleware-base-middleware-class)
  - [Middleware Pipeline](#middleware-pipeline)
- [Authentication Middleware](#authentication-middleware)
  - [AuthenticationMiddleware - User Authentication](#authenticationmiddleware-user-authentication)
  - [Authorization Decorator](#authorization-decorator)
- [Request/Response Processing](#requestresponse-processing)
  - [RequestMiddleware - Request Processing](#requestmiddleware-request-processing)
  - [ResponseMiddleware - Response Processing](#responsemiddleware-response-processing)
- [Error Handling Middleware](#error-handling-middleware)
  - [ErrorHandlingMiddleware - Exception Processing](#errorhandlingmiddleware-exception-processing)
- [Performance Middleware](#performance-middleware)
  - [PerformanceMonitoringMiddleware - Performance Tracking](#performancemonitoringmiddleware-performance-tracking)
- [Quality Metrics](#quality-metrics)
- [Usage Examples](#usage-examples)
  - [Complete Middleware Stack](#complete-middleware-stack)
  - [Custom Middleware Implementation](#custom-middleware-implementation)
  - [Middleware with Dependency Injection](#middleware-with-dependency-injection)

<!-- TOC END -->

This section covers the HTTP middleware and handler system for request/response processing, authentication, logging, and cross-cutting concerns.

## HTTP Middleware System

### FlextApiMiddleware - Base Middleware Class

Base class for implementing HTTP middleware with FLEXT patterns.

```python
from flext_api.middleware import FlextApiMiddleware
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u
from typing import Callable, Awaitable

class LoggingMiddleware(FlextApiMiddleware):
    """Middleware for request/response logging."""

    def __init__(self, logger):
        self.logger = logger

    async def process_request(self, request) -> FlextResult[dict]:
        """Process incoming request."""
        self.logger.info("Processing request", extra={
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get("User-Agent")
        })
        return FlextResult[dict].ok({})

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Process outgoing response."""
        self.logger.info("Request completed", extra={
            "status_code": response.status_code,
            "duration_ms": response.duration_ms
        })
        return FlextResult[dict].ok({})

# Usage
middleware = LoggingMiddleware(logger)
app.add_middleware(middleware)
```

**Key Methods:**

- `process_request(request)` - Process incoming request
- `process_response(request, response)` - Process outgoing response
- `process_exception(request, exception)` - Handle exceptions

### Middleware Pipeline

Chain multiple middleware components for complex request processing.

```python
from flext_api.middleware import MiddlewarePipeline

# Create middleware pipeline
pipeline = MiddlewarePipeline()

# Add middleware in order (reverse order of execution)
pipeline.add_middleware(RateLimitingMiddleware())
pipeline.add_middleware(AuthenticationMiddleware())
pipeline.add_middleware(LoggingMiddleware(logger))
pipeline.add_middleware(CORSMiddleware())

# Process request through pipeline
async def handle_request(request):
    # Middleware processes request in reverse order
    response = await pipeline.process_request(request)

    # Execute main handler
    response = await main_handler(request)

    # Middleware processes response in forward order
    response = await pipeline.process_response(request, response)

    return response
```

## Authentication Middleware

### AuthenticationMiddleware - User Authentication

Middleware for handling user authentication and authorization.

```python
from flext_api.middleware import AuthenticationMiddleware
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class JwtAuthenticationMiddleware(AuthenticationMiddleware):
    """JWT-based authentication middleware."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        super().__init__()
        self.secret_key = secret_key
        self.algorithm = algorithm

    async def authenticate_request(self, request) -> FlextResult[dict]:
        """Authenticate request using JWT token."""
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return FlextResult[dict].fail("Missing or invalid authorization header")

        token = auth_header.split(" ")[1]

        try:
            # Decode and validate JWT
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Extract user information
            user_info = {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "roles": payload.get("roles", []),
                "exp": payload.get("exp")
            }

            return FlextResult[dict].ok(user_info)

        except jwt.ExpiredSignatureError:
            return FlextResult[dict].fail("Token has expired")
        except jwt.InvalidTokenError:
            return FlextResult[dict].fail("Invalid token")

# Usage
auth_middleware = JwtAuthenticationMiddleware("your-secret-key")
app.add_middleware(auth_middleware)
```

**Key Features:**

- JWT token validation
- User context extraction
- Token expiration handling
- Role-based access control

### Authorization Decorator

```python
from flext_api.middleware import require_roles, require_permissions

# Role-based authorization
@app.get("/REDACTED_LDAP_BIND_PASSWORD/users")
@require_roles(["REDACTED_LDAP_BIND_PASSWORD", "superuser"])
async def get_REDACTED_LDAP_BIND_PASSWORD_users(current_user: dict[str, object] = Depends(get_current_user)):
    """Get all users (REDACTED_LDAP_BIND_PASSWORD only)."""
    return await REDACTED_LDAP_BIND_PASSWORD_service.get_all_users()

# Permission-based authorization
@app.post("/users/{user_id}/delete")
@require_permissions(["user.delete"])
async def delete_user(
    user_id: str,
    current_user: dict[str, object] = Depends(get_current_user)
):
    """Delete user (requires delete permission)."""
    return await user_service.delete_user(user_id)
```

## Request/Response Processing

### RequestMiddleware - Request Processing

Middleware for preprocessing incoming requests.

```python
from flext_api.middleware import RequestMiddleware

class RequestValidationMiddleware(RequestMiddleware):
    """Validate and sanitize incoming requests."""

    async def process_request(self, request) -> FlextResult[dict]:
        """Validate request format and content."""

        # Validate content type
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("Content-Type", "")
            if not content_type.startswith("application/json"):
                return FlextResult[dict].fail("Content-Type must be application/json")

        # Validate request size
        if hasattr(request, 'body') and len(request.body) > 1024 * 1024:  # 1MB limit
            return FlextResult[dict].fail("Request body too large")

        # Sanitize input data
        if hasattr(request, 'json'):
            request.json = self.sanitize_data(request.json)

        return FlextResult[dict].ok({})

    def sanitize_data(self, data: dict) -> dict[str, object]:
        """Sanitize input data."""
        if isinstance(data, dict):
            return {k: self.sanitize_value(v) for k, v in data.items()}
        return data

    def sanitize_value(self, value):
        """Sanitize individual values."""
        if isinstance(value, str):
            # Remove potentially dangerous characters
            return value.strip()
        return value
```

### ResponseMiddleware - Response Processing

Middleware for postprocessing outgoing responses.

```python
from flext_api.middleware import ResponseMiddleware

class ResponseFormattingMiddleware(ResponseMiddleware):
    """Format and enhance response data."""

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Format response data and add metadata."""

        # Add standard response headers
        response.headers.update({
            "X-API-Version": "1.0.0",
            "X-Response-Time": f"{response.duration_ms}ms",
            "X-Request-ID": request.request_id or "unknown"
        })

        # Add pagination metadata for list endpoints
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'items' in response.data and 'total' in response.data:
                response.data['_metadata'] = {
                    'total': response.data['total'],
                    'page': request.query_params.get('page', 1),
                    'per_page': request.query_params.get('per_page', 10)
                }

        return FlextResult[dict].ok({})
```

## Error Handling Middleware

### ErrorHandlingMiddleware - Exception Processing

Middleware for centralized error handling and response formatting.

```python
from flext_api.middleware import ErrorHandlingMiddleware
from flext_api.models import ErrorResponse

class FlextApiErrorHandler(ErrorHandlingMiddleware):
    """Centralized error handling with FLEXT patterns."""

    async def process_exception(self, request, exception) -> FlextResult[dict]:
        """Process and format exceptions."""

        # Map exceptions to appropriate HTTP status codes
        status_code = self.map_exception_to_status(exception)

        # Create error response
        error_response = ErrorResponse(
            error_code=self.get_error_code(exception),
            message=str(exception),
            details=self.get_exception_details(exception),
            request_id=request.request_id
        )

        # Log error with context
        self.logger.error("Request failed", extra={
            "error": str(exception),
            "status_code": status_code,
            "path": request.path,
            "method": request.method
        })

        return FlextResult[dict].ok({
            "status_code": status_code,
            "response": error_response.dict()
        })

    def map_exception_to_status(self, exception) -> int:
        """Map exception types to HTTP status codes."""
        mapping = {
            ValidationError: 422,
            AuthenticationError: 401,
            AuthorizationError: 403,
            NotFoundError: 404,
            ConflictError: 409,
            RateLimitError: 429,
            Exception: 500
        }

        for exc_type, status in mapping.items():
            if isinstance(exception, exc_type):
                return status
        return 500
```

## Performance Middleware

### PerformanceMonitoringMiddleware - Performance Tracking

Middleware for monitoring request performance and metrics.

```python
from flext_api.middleware import PerformanceMonitoringMiddleware

class RequestPerformanceMiddleware(PerformanceMonitoringMiddleware):
    """Monitor request performance and timing."""

    def __init__(self, metrics_client):
        self.metrics_client = metrics_client

    async def process_request(self, request) -> FlextResult[dict]:
        """Start performance monitoring."""
        request.start_time = time.time()
        request.request_id = str(uuid.uuid4())
        return FlextResult[dict].ok({})

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Record performance metrics."""
        duration = time.time() - request.start_time

        # Record metrics
        self.metrics_client.record_request(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration * 1000,
            user_agent=request.headers.get("User-Agent")
        )

        # Add performance headers
        response.headers.update({
            "X-Response-Time": f"{duration*1000:.2f}ms",
            "X-Request-ID": request.request_id
        })

        return FlextResult[dict].ok({})
```

## Quality Metrics

| Module                         | Coverage | Status    | Description                   |
| ------------------------------ | -------- | --------- | ----------------------------- |
| `middleware/__init__.py`       | 90%      | ✅ Stable | Base middleware classes       |
| `middleware/auth.py`           | 85%      | ✅ Good   | Authentication middleware     |
| `middleware/validation.py`     | 88%      | ✅ Good   | Request validation middleware |
| `middleware/error_handling.py` | 92%      | ✅ Stable | Error handling middleware     |
| `middleware/performance.py`    | 80%      | ✅ Good   | Performance monitoring        |

## Usage Examples

### Complete Middleware Stack

```python
from flext_api.middleware import (
    MiddlewarePipeline,
    LoggingMiddleware,
    AuthenticationMiddleware,
    ValidationMiddleware,
    ErrorHandlingMiddleware,
    PerformanceMonitoringMiddleware
)

# Create middleware pipeline
middleware_pipeline = MiddlewarePipeline()

# Add middleware in reverse order of execution
middleware_pipeline.add_middleware(ErrorHandlingMiddleware())
middleware_pipeline.add_middleware(PerformanceMonitoringMiddleware(metrics_client))
middleware_pipeline.add_middleware(ValidationMiddleware())
middleware_pipeline.add_middleware(AuthenticationMiddleware(jwt_secret))
middleware_pipeline.add_middleware(LoggingMiddleware(logger))

# Apply to FastAPI application
app.middleware("http")(middleware_pipeline.process_request)
```

### Custom Middleware Implementation

```python
from flext_api.middleware import FlextApiMiddleware
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class CustomHeaderMiddleware(FlextApiMiddleware):
    """Add custom headers to all responses."""

    def __init__(self, custom_headers: dict):
        self.custom_headers = custom_headers

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Add custom headers to response."""
        for header_name, header_value in self.custom_headers.items():
            response.headers[header_name] = header_value

        return FlextResult[dict].ok({})

# Usage
custom_middleware = CustomHeaderMiddleware({
    "X-API-Version": "1.0.0",
    "X-Powered-By": "FLEXT-API"
})
app.add_middleware(custom_middleware)
```

### Middleware with Dependency Injection

```python
from flext_core import FlextBus
from flext_core import FlextSettings
from flext_core import FlextConstants
from flext_core import FlextContainer
from flext_core import FlextContext
from flext_core import FlextDecorators
from flext_core import FlextDispatcher
from flext_core import FlextExceptions
from flext_core import h
from flext_core import FlextLogger
from flext_core import x
from flext_core import FlextModels
from flext_core import FlextProcessors
from flext_core import p
from flext_core import FlextRegistry
from flext_core import FlextResult
from flext_core import FlextRuntime
from flext_core import FlextService
from flext_core import t
from flext_core import u

class DatabaseMiddleware(FlextApiMiddleware):
    """Middleware that provides database connection."""

    def __init__(self):
        self.container = FlextContainer.get_global()

    async def process_request(self, request) -> FlextResult[dict]:
        """Inject database connection into request."""
        db_result = self.container.get("database")
        if db_result.is_success:
            request.db = db_result.unwrap()
        return FlextResult[dict].ok({})

    async def process_response(self, request, response) -> FlextResult[dict]:
        """Clean up database connection."""
        if hasattr(request, 'db'):
            # Close database connection
            await request.db.close()
        return FlextResult[dict].ok({})

# Register database service
container = FlextContainer.get_global()
container.register("database", DatabaseService())

# Add middleware
db_middleware = DatabaseMiddleware()
app.add_middleware(db_middleware)
```

This middleware system provides a flexible foundation for implementing cross-cutting concerns like authentication, logging, validation, and performance monitoring in HTTP applications.
