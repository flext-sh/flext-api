# Schema API Reference


<!-- TOC START -->
- [OpenAPI Schema Generation](#openapi-schema-generation)
  - [OpenApiSchema - OpenAPI 3.0 Specification](#openapischema-openapi-30-specification)
  - [Schema Customization](#schema-customization)
- [AsyncAPI Schema Generation](#asyncapi-schema-generation)
  - [AsyncApiSchema - AsyncAPI 2.0 Specification](#asyncapischema-asyncapi-20-specification)
- [JSON Schema Generation](#json-schema-generation)
  - [JsonSchema - JSON Schema Draft 2020-12](#jsonschema-json-schema-draft-2020-12)
  - [Schema Validation](#schema-validation)
- [Schema Integration](#schema-integration)
  - [FastAPI Integration](#fastapi-integration)
  - [Custom Schema Extensions](#custom-schema-extensions)
- [Quality Metrics](#quality-metrics)
- [Usage Examples](#usage-examples)
  - [Complete Schema Generation Workflow](#complete-schema-generation-workflow)
  - [Schema Validation in Production](#schema-validation-in-production)
<!-- TOC END -->

This section covers the schema generation and validation capabilities for OpenAPI, AsyncAPI, and JSON Schema specifications.

## OpenAPI Schema Generation

### OpenApiSchema - OpenAPI 3.0 Specification

Generate OpenAPI 3.0 specifications from FastAPI applications and FLEXT models.

```python
from flext_api.schemas.openapi import OpenApiSchema
from flext_api import create_fastapi_app

# Create FastAPI application
app = create_fastapi_app(title="My API", version="1.0.0")

# Generate OpenAPI schema
schema_generator = OpenApiSchema(app)
openapi_spec = schema_generator.generate()

# Access schema components
info = openapi_spec.info
paths = openapi_spec.paths
components = openapi_spec.components

# Export to file
schema_generator.export_to_file("openapi.json")
schema_generator.export_to_file("openapi.yaml")
```

**Key Features:**

- Automatic schema generation from FastAPI routes
- Pydantic model integration
- Security scheme support
- Custom field descriptions and examples
- Multiple output formats (JSON, YAML)

### Schema Customization

```python
# Custom OpenAPI configuration
from flext_api.schemas.openapi import OpenApiConfig

config = OpenApiConfig(
    title="Enterprise API",
    version="2.0.0",
    description="Enterprise-grade REST API with comprehensive documentation",
    contact={"name": "API Team", "email": "api@company.com"},
    license={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    servers=[
        {"url": "https://api.company.com", "description": "Production server"},
        {"url": "https://staging-api.company.com", "description": "Staging server"}
    ]
)

schema = OpenApiSchema(app, config=config)
```

## AsyncAPI Schema Generation

### AsyncApiSchema - AsyncAPI 2.0 Specification

Generate AsyncAPI 2.0 specifications for event-driven architectures and WebSocket APIs.

```python
from flext_api.schemas.asyncapi import AsyncApiSchema

# Define AsyncAPI configuration
asyncapi_config = {
    "info": {
        "title": "User Events API",
        "version": "1.0.0",
        "description": "Real-time user event streaming"
    },
    "servers": {
        "production": {
            "url": "wss://api.company.com/events",
            "protocol": "wss"
        }
    },
    "channels": {
        "user/created": {
            "subscribe": {
                "message": {
                    "$ref": "#/components/messages/UserCreated"
                }
            }
        }
    }
}

# Generate AsyncAPI schema
schema_generator = AsyncApiSchema(asyncapi_config)
asyncapi_spec = schema_generator.generate()

# Export specification
schema_generator.export_to_file("asyncapi.yaml")
```

## JSON Schema Generation

### JsonSchema - JSON Schema Draft 2020-12

Generate JSON Schema specifications for data validation and API contracts.

```python
from flext_api.schemas.jsonschema import JsonSchema
from flext_api.models import FlextApiModels
from typing import Optional

class UserCreateRequest(FlextApiModels.BaseRequest):
    """Request model for user creation."""
    name: str
    email: str
    age: Optional[int] = None

# Generate JSON Schema
schema_generator = JsonSchema()
json_schema = schema_generator.generate_from_model(UserCreateRequest)

# Schema includes validation rules
print(f"Required fields: {json_schema.required}")
print(f"Properties: {list(json_schema.properties.keys())}")
```

**Key Features:**

- Automatic schema generation from Pydantic models
- Support for all JSON Schema data types
- Validation constraint inclusion
- Nested object support
- Array and enum handling

### Schema Validation

```python
from flext_api.schemas.jsonschema import JsonSchemaValidator

# Create validator
validator = JsonSchemaValidator(json_schema)

# Validate data
test_data = {"name": "Alice", "email": "alice@example.com", "age": 30}
is_valid = validator.validate(test_data)

if not is_valid:
    errors = validator.get_validation_errors()
    print(f"Validation errors: {errors}")

# Validate with custom context
validation_result = validator.validate_with_context(
    test_data,
    context={"strict": True, "allow_extra": False}
)
```

## Schema Integration

### FastAPI Integration

Automatic schema generation for FastAPI applications with OpenAPI integration.

```python
from flext_api.schemas.openapi import FastApiOpenApiIntegration

# Integrate with FastAPI application
integration = FastApiOpenApiIntegration(app)

# Configure response schemas
@integration.response_schema(UserResponse)
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Implementation
    pass

# Configure request schemas
@integration.request_schema(UserCreateRequest)
@app.post("/users")
async def create_user(request: UserCreateRequest):
    # Implementation
    pass

# Generate complete OpenAPI spec
openapi_spec = integration.generate_complete_spec()
```

### Custom Schema Extensions

Extend schemas with custom fields and metadata.

```python
from flext_api.schemas.jsonschema import JsonSchemaExtension

# Add custom extensions
extension = JsonSchemaExtension()

# Add example data
extension.add_example("user_example", {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
})

# Add custom metadata
extension.add_metadata("deprecated", False)
extension.add_metadata("since", "1.0.0")

# Apply to schema
extended_schema = extension.apply_to_schema(json_schema)
```

## Quality Metrics

| Module                  | Coverage | Status  | Description             |
| ----------------------- | -------- | ------- | ----------------------- |
| `schemas/openapi.py`    | 85%      | ✅ Good | OpenAPI 3.0 generation  |
| `schemas/asyncapi.py`   | 80%      | ✅ Good | AsyncAPI 2.0 generation |
| `schemas/jsonschema.py` | 88%      | ✅ Good | JSON Schema generation  |

## Usage Examples

### Complete Schema Generation Workflow

```python
from flext_api.schemas.openapi import OpenApiSchema, OpenApiConfig
from flext_api.schemas.jsonschema import JsonSchema
from flext_api import create_fastapi_app

# 1. Create FastAPI application
app = create_fastapi_app(title="User Management API", version="1.0.0")

# 2. Define models
class UserCreateRequest(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str

# 3. Generate OpenAPI schema
openapi_config = OpenApiConfig(
    title="User Management API",
    version="1.0.0",
    description="API for managing users",
    servers=[
        {"url": "https://api.company.com", "description": "Production"},
        {"url": "https://staging-api.company.com", "description": "Staging"}
    ]
)

openapi_schema = OpenApiSchema(app, config=openapi_config)
openapi_spec = openapi_schema.generate()

# 4. Generate JSON Schema for models
json_schema_generator = JsonSchema()
user_request_schema = json_schema_generator.generate_from_model(UserCreateRequest)
user_response_schema = json_schema_generator.generate_from_model(UserResponse)

# 5. Export schemas
openapi_schema.export_to_file("user_api_openapi.yaml")
json_schema_generator.export_to_file(user_request_schema, "user_request_schema.json")
json_schema_generator.export_to_file(user_response_schema, "user_response_schema.json")

print("✅ Schema generation complete!")
print(f"OpenAPI paths: {len(openapi_spec.paths)}")
print(f"JSON Schema properties: {len(user_request_schema.properties)}")
```

### Schema Validation in Production

```python
from flext_api.schemas.jsonschema import JsonSchemaValidator, SchemaValidationError

def validate_user_request(data: dict) -> tuple[bool, t.StringList]:
    """Validate user creation request data."""
    try:
        validator = JsonSchemaValidator(user_request_schema)
        is_valid = validator.validate(data)

        if is_valid:
            return True, []
        else:
            return False, validator.get_validation_errors()

    except SchemaValidationError as e:
        return False, [str(e)]

# Usage in API endpoint
@app.post("/users")
async def create_user(request: dict):
    # Validate request schema
    is_valid, errors = validate_user_request(request)

    if not is_valid:
        raise HTTPException(
            status_code=422,
            detail={"message": "Validation failed", "errors": errors}
        )

    # Process valid request
    user = await user_service.create_user(request)
    return UserResponse(**user.dict())
```

This schema system provides comprehensive API documentation generation and validation capabilities for building robust, well-documented HTTP APIs.
