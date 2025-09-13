# Simplified Patterns Documentation

**FLEXT API Simplified Architecture Patterns and Implementation Guide**

> **Navigation**: [FLEXT Hub](../../../docs/NAVIGATION.md) > [flext-api](../../README.md) > [Examples](../) > Simplified Patterns

---

## 🎯 Overview

This document outlines the simplified patterns implemented in FLEXT API that provide clean, maintainable, and enterprise-ready HTTP functionality using flext-core extensively.

## 📦 Core Architectural Patterns

### 1. FlextResult Pattern (Railway Pattern)

**Problem**: Exception handling creates unpredictable code paths and makes error handling inconsistent.

**Solution**: Use `FlextResult[T]` for all operations that can fail.

```python
from flext_core import FlextResult
from flext_api import FlextApiClient, FlextApiModels

async def make_http_request(url: str) -> FlextResult[dict]:
    """Example of proper FlextResult usage."""
    # Input validation with early return
    if not url or not url.startswith(('http://', 'https://')):
        return FlextResult[dict].fail("Invalid URL provided")
    
    # HTTP operation through flext-api
    client = FlextApiClient(base_url=url)
    
    try:
        response_result = await client.get("/api/data")
        if response_result.is_success:
            response = response_result.unwrap()
            if response.status_code == 200:
                return FlextResult[dict].ok({"data": response.body})
            else:
                return FlextResult[dict].fail(f"HTTP {response.status_code}: {response.body}")
        else:
            return FlextResult[dict].fail(f"Request failed: {response_result.error}")
    except Exception as e:
        return FlextResult[dict].fail(f"Unexpected error: {e}")

# Usage
result = await make_http_request("https://api.example.com")
if result.is_success:
    data = result.unwrap()
    print(f"Success: {data}")
else:
    print(f"Error: {result.error}")
```

### 2. Unified Class Pattern

**Problem**: Multiple classes per module create complexity and violate single responsibility.

**Solution**: One main class per module with nested helper classes.

```python
from flext_core import FlextDomainService, FlextResult, FlextLogger
from flext_api import FlextApiClient, FlextApiModels

class HttpService(FlextDomainService):
    """Single unified HTTP service class."""
    
    def __init__(self) -> None:
        super().__init__()
        self._logger = FlextLogger(__name__)
        
    class _RequestValidator:
        """Nested helper for request validation."""
        
        @staticmethod
        def validate_url(url: str) -> FlextResult[str]:
            if not url or not url.startswith(('http://', 'https://')):
                return FlextResult[str].fail("Invalid URL format")
            return FlextResult[str].ok(url)
    
    class _ResponseProcessor:
        """Nested helper for response processing."""
        
        @staticmethod
        def process_response(response: FlextApiModels.HttpResponse) -> FlextResult[dict]:
            if response.status_code >= 400:
                return FlextResult[dict].fail(f"HTTP {response.status_code}")
            
            try:
                # Assume JSON response
                import json
                data = json.loads(response.body) if response.body else {}
                return FlextResult[dict].ok(data)
            except json.JSONDecodeError:
                return FlextResult[dict].fail("Invalid JSON response")
    
    async def fetch_data(self, url: str) -> FlextResult[dict]:
        """Main service method using nested helpers."""
        # Validate using nested helper
        url_result = self._RequestValidator.validate_url(url)
        if url_result.is_failure:
            return FlextResult[dict].fail(url_result.error)
        
        # Make request
        client = FlextApiClient(base_url=url_result.unwrap())
        response_result = await client.get("/")
        
        if response_result.is_failure:
            return FlextResult[dict].fail(response_result.error)
        
        # Process using nested helper
        return self._ResponseProcessor.process_response(response_result.unwrap())
```

### 3. FLEXT-Core Integration Pattern

**Problem**: Duplication of common functionality across projects.

**Solution**: Use flext-core extensively for all common operations.

```python
from flext_core import (
    FlextContainer,
    FlextLogger, 
    FlextModels,
    FlextResult,
    FlextTypes,
    FlextUtilities,
)
from flext_api import FlextApiClient

class EnterpriseHttpService:
    """HTTP service using flext-core extensively."""
    
    def __init__(self) -> None:
        # Use flext-core dependency injection
        self._container = FlextContainer.get_global()
        self._logger = FlextLogger(__name__)
        
        # Generate ID using flext-core utilities
        self._service_id = FlextUtilities.Generators.generate_entity_id()
    
    def create_http_config(self, base_url: str) -> FlextResult[FlextModels.Http.HttpRequestConfig]:
        """Create HTTP configuration using flext-core models."""
        try:
            config = FlextModels.Http.HttpRequestConfig(
                url=base_url,
                method="GET",
                timeout=30.0,
                retries=3,
                headers={"User-Agent": "flext-api/1.0"}
            )
            return FlextResult[FlextModels.Http.HttpRequestConfig].ok(config)
        except Exception as e:
            return FlextResult[FlextModels.Http.HttpRequestConfig].fail(f"Config creation failed: {e}")
    
    async def make_authenticated_request(
        self, 
        base_url: str, 
        token: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Make authenticated HTTP request using flext-core patterns."""
        
        # Create config using flext-core
        config_result = self.create_http_config(base_url)
        if config_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(config_result.error)
        
        config = config_result.unwrap()
        
        # Create client with authentication
        client = FlextApiClient(
            base_url=config.url,
            timeout=config.timeout,
            max_retries=config.retries,
            headers={**config.headers, "Authorization": f"Bearer {token}"}
        )
        
        # Make request
        response_result = await client.get("/api/data")
        if response_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(response_result.error)
        
        response = response_result.unwrap()
        
        # Return flext-core compatible dict
        result_data: FlextTypes.Core.Dict = {
            "status_code": response.status_code,
            "body": response.body,
            "headers": response.headers,
            "timestamp": FlextUtilities.Generators.generate_iso_timestamp()
        }
        
        return FlextResult[FlextTypes.Core.Dict].ok(result_data)
```

### 4. Clean Architecture Service Pattern

**Problem**: Business logic mixed with infrastructure concerns.

**Solution**: Domain services that use flext-api as infrastructure layer.

```python
from flext_core import FlextDomainService, FlextResult
from flext_api import FlextApiClient, FlextApiModels

class UserDataService(FlextDomainService):
    """Domain service for user data operations."""
    
    def __init__(self, api_base_url: str) -> None:
        super().__init__()
        # Infrastructure dependency (flext-api client)
        self._client = FlextApiClient(base_url=api_base_url)
    
    async def get_user_profile(self, user_id: str) -> FlextResult[UserProfile]:
        """Business logic: get user profile."""
        # Validate business rules
        if not user_id or len(user_id) < 3:
            return FlextResult[UserProfile].fail("Invalid user ID")
        
        # Use infrastructure (HTTP call)
        response_result = await self._client.get(f"/users/{user_id}")
        if response_result.is_failure:
            return FlextResult[UserProfile].fail(f"API error: {response_result.error}")
        
        response = response_result.unwrap()
        if response.status_code != 200:
            return FlextResult[UserProfile].fail(f"User not found: {response.status_code}")
        
        # Transform to domain model
        try:
            import json
            user_data = json.loads(response.body)
            profile = UserProfile(
                id=user_data["id"],
                name=user_data["name"], 
                email=user_data["email"]
            )
            return FlextResult[UserProfile].ok(profile)
        except (json.JSONDecodeError, KeyError) as e:
            return FlextResult[UserProfile].fail(f"Invalid user data: {e}")

# Domain model
class UserProfile:
    def __init__(self, id: str, name: str, email: str) -> None:
        self.id = id
        self.name = name
        self.email = email
```

## 🚀 Benefits of Simplified Patterns

### 1. **Predictable Error Handling**
- All operations return `FlextResult[T]` 
- No exceptions for business logic errors
- Consistent error propagation

### 2. **Single Responsibility**
- One main class per module
- Nested helpers for specific concerns
- Clear separation of responsibilities

### 3. **Zero Duplication**
- All common functionality from flext-core
- HTTP operations through flext-api only
- Consistent patterns across ecosystem

### 4. **Type Safety**
- Full MyPy compatibility
- Generic types for FlextResult
- Proper type annotations

### 5. **Testing Simplicity**
- Easy to mock FlextResult returns
- Clear success/failure paths
- Isolated business logic

## 📋 Implementation Checklist

When implementing these patterns:

- [ ] Use `FlextResult[T]` for all operations that can fail
- [ ] Import common functionality from flext-core only
- [ ] One main class per module with nested helpers
- [ ] HTTP operations only through FlextApiClient
- [ ] Proper type annotations with MyPy validation
- [ ] Business logic separate from infrastructure
- [ ] Consistent error messages and handling

## 🔗 Related Documentation

- [FLEXT Architecture](../architecture.md)
- [Basic Usage Examples](basic-usage.md)
- [Advanced Patterns](advanced-patterns.md)
- [Integration Guide](../integration.md)

---

**Last Updated**: 2025-01-08
**Status**: ✅ Implemented and Validated
