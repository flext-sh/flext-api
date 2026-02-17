# Core API Reference

This section covers the core HTTP client and server classes that form the foundation of FLEXT-API.

## Core HTTP Client

### FlextApiClient - Main HTTP Client

The primary HTTP client for all HTTP operations within the FLEXT ecosystem, providing type-safe operations with FlextResult patterns.

```python
from flext_api import FlextApiClient
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

# Create client instance
client = FlextApiClient(
    base_url="https://api.example.com",
    timeout=30.0,
    max_retries=3,
    headers={"User-Agent": "FLEXT-API/0.9.9"}
)

# HTTP methods with automatic error handling
get_result = client.get("/users")
post_result = client.post("/users", json={"name": "Alice"})
put_result = client.put("/users/123", json={"name": "Bob"})
delete_result = client.delete("/users/123")

# Handle responses
if get_result.is_success:
    users = get_result.unwrap()
    print(f"Found {len(users)} users")
else:
    print(f"Error: {get_result.error}")
```

**Key Features:**

- Type-safe HTTP operations
- Automatic retry logic
- Request/response interceptors
- Connection pooling
- Timeout management

**Configuration Options:**

- `base_url`: Base URL for all requests
- `timeout`: Request timeout in seconds
- `max_retries`: Maximum retry attempts
- `headers`: Default headers for all requests
- `auth`: Authentication handler
- `proxies`: Proxy configuration

### HTTP Methods

**GET Requests:**

```python
# Simple GET
result = client.get("/users")

# GET with query parameters
result = client.get("/users", params={"limit": 10, "offset": 0})

# GET with custom headers
result = client.get("/users", headers={"Accept": "application/json"})

# Conditional requests
result = client.get("/users", headers={"If-Modified-Since": "Wed, 21 Oct 2025 07:28:00 GMT"})
```

**POST/PUT Requests:**

```python
# POST with JSON data
user_data = {"name": "Alice", "email": "alice@example.com"}
result = client.post("/users", json=user_data)

# POST with form data
form_data = {"file": file_object, "description": "Upload"}
result = client.post("/upload", files=form_data)

# PUT with data
result = client.put("/users/123", json={"name": "Updated Name"})
```

**DELETE Requests:**

```python
# Simple DELETE
result = client.delete("/users/123")

# DELETE with body
result = client.delete("/users/123", json={"reason": "User requested deletion"})
```

## FastAPI Application Factory

### create_fastapi_app() - Application Factory

Creates FastAPI applications with FLEXT patterns and configuration.

```python
from flext_api import create_fastapi_app, FlextApiSettings
from fastapi import FastAPI

# Create configuration
config = FlextApiSettings(
    title="Enterprise API",
    version="2.0.0",
    description="Enterprise-grade REST API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create application
app = create_fastapi_app(config=config)

# Application is now ready for route registration
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

**Configuration Options:**

- `title`: API title for documentation
- `version`: API version
- `description`: API description
- `docs_url`: OpenAPI docs URL
- `redoc_url`: ReDoc URL
- `openapi_url`: OpenAPI schema URL

### FlextApiSettings - Configuration Model

Pydantic model for API configuration with validation.

```python
from flext_api import FlextApiSettings

class MyApiConfig(FlextApiSettings):
    """Custom API configuration."""
    custom_setting: str = "default_value"
    feature_flags: dict[str, object] = {}
```

## HTTP Models and Schemas

### Request/Response Models

Type-safe models for HTTP requests and responses using Pydantic v2.

```python
from flext_api.models import FlextApiModels
from typing import Optional
from pydantic import Field

class UserCreateRequest(FlextApiModels.BaseRequest):
    """Request model for user creation."""
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    age: Optional[int] = Field(None, ge=0, le=150)

class UserResponse(FlextApiModels.BaseResponse):
    """Response model for user data."""
    id: str
    name: str
    email: str
    created_at: str
    is_active: bool = True

# Usage in routes
@app.post("/users", response_model=UserResponse)
async def create_user(request: UserCreateRequest):
    # Validate and process request
    user = await user_service.create_user(request.name, request.email)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at.isoformat(),
        is_active=True
    )
```

### Error Response Models

Standardized error responses across the API.

```python
from flext_api.models import ErrorResponse

class ValidationErrorResponse(ErrorResponse):
    """Validation error response."""
    field_errors: dict[str, t.StringList]

class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response."""
    login_url: Optional[str] = None

# Usage in exception handlers
@app.exception_handler(ValidationException)
async def validation_exception_handler(request: Request, exc: ValidationException):
    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            field_errors=exc.field_errors
        ).dict()
    )
```

## HTTP Utilities

### FlextApiUtilities - Helper Functions

Collection of HTTP-related utility functions.

```python
from flext_api.utilities import FlextApiUtilities

# URL manipulation
base_url = "https://api.example.com/v1"
full_url = FlextApiUtilities.build_url(base_url, "/users", {"limit": 10})

# Header manipulation
headers = FlextApiUtilities.merge_headers(
    {"Content-Type": "application/json"},
    {"Authorization": "Bearer token123"}
)

# Request/response transformation
json_data = FlextApiUtilities.parse_json_response(response)
clean_data = FlextApiUtilities.sanitize_response_data(data)
```

**Key Functions:**

- `build_url()`: Construct URLs with query parameters
- `merge_headers()`: Combine header dictionaries
- `parse_json_response()`: Parse and validate JSON responses
- `sanitize_response_data()`: Remove sensitive data from responses
- `format_request_data()`: Prepare data for HTTP requests

## Quality Metrics

| Module         | Coverage | Status    | Description                 |
| -------------- | -------- | --------- | --------------------------- |
| `client.py`    | 95%      | ✅ Stable | HTTP client implementation  |
| `app.py`       | 90%      | ✅ Stable | FastAPI application factory |
| `models.py`    | 85%      | ✅ Good   | HTTP models and schemas     |
| `utilities.py` | 92%      | ✅ Stable | HTTP utility functions      |
| `config.py`    | 88%      | ✅ Good   | Configuration management    |

## Usage Examples

### Complete HTTP Client Example

```python
from flext_api import FlextApiClient, FlextApiSettings
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

class UserApiClient(FlextApiClient):
    """HTTP client for user management API."""

    def __init__(self):
        super().__init__(
            base_url="https://jsonplaceholder.typicode.com",
            timeout=10.0,
            headers={"User-Agent": "FLEXT-API-Example/0.9.9"}
        )

    def get_users(self, limit: int = 10) -> FlextResult[list]:
        """Get list of users with pagination."""
        return self.get("/users", params={"_limit": limit})

    def get_user(self, user_id: int) -> FlextResult[dict]:
        """Get single user by ID."""
        return self.get(f"/users/{user_id}")

    def create_user(self, user_data: dict) -> FlextResult[dict]:
        """Create new user."""
        return self.post("/users", json=user_data)

    def update_user(self, user_id: int, user_data: dict) -> FlextResult[dict]:
        """Update existing user."""
        return self.put(f"/users/{user_id}", json=user_data)

    def delete_user(self, user_id: int) -> FlextResult[bool]:
        """Delete user."""
        return self.delete(f"/users/{user_id}")

# Usage example
client = UserApiClient()

# Get users
users_result = client.get_users(limit=5)
if users_result.is_success:
    users = users_result.unwrap()
    print(f"Retrieved {len(users)} users")

# Create user
new_user = {"name": "John Doe", "email": "john@example.com"}
create_result = client.create_user(new_user)
if create_result.is_success:
    user = create_result.unwrap()
    print(f"Created user: {user['name']}")

# Error handling
error_result = client.get_user(99999)
if error_result.is_failure:
    print(f"User not found: {error_result.error}")
```

### FastAPI Application Example

```python
from flext_api import create_fastapi_app, FlextApiSettings
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
from fastapi import HTTPException, Depends

# Configuration
config = FlextApiSettings(
    title="User Management API",
    version="1.0.0",
    description="API for managing users in the system",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Create application
app = create_fastapi_app(config=config)

# Models
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

# Dependency injection
def get_user_service():
    return UserService()

# Routes
@app.get("/users", response_model=list[UserResponse])
async def list_users(
    limit: int = 10,
    offset: int = 0,
    user_service: UserService = Depends(get_user_service)
) -> list[UserResponse]:
    """List users with pagination."""
    result = user_service.get_users(limit=limit, offset=offset)

    if result.is_failure:
        raise HTTPException(status_code=500, detail=result.error)

    users = result.unwrap()
    return [
        UserResponse(id=user.id, name=user.name, email=user.email)
        for user in users
    ]

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create new user."""
    result = user_service.create_user(user_data.name, user_data.email)

    if result.is_failure:
        raise HTTPException(status_code=400, detail=result.error)

    user = result.unwrap()
    return UserResponse(id=user.id, name=user.name, email=user.email)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID."""
    result = user_service.get_user(user_id)

    if result.is_failure:
        raise HTTPException(status_code=404, detail="User not found")

    user = result.unwrap()
    return UserResponse(id=user.id, name=user.name, email=user.email)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Run application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

This core API provides a solid foundation for building HTTP-based applications with proper error handling, type safety, and clean architecture patterns.
