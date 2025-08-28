# Basic Usage Examples

**Fundamental FLEXT API usage patterns and examples**

> **Navigation**: [FLEXT Hub](../../../docs/NAVIGATION.md) > [flext-api](../../README.md) > [Examples](../) > Basic Usage

---

## 🎯 Basic Usage Overview

This guide provides practical examples for getting started with FLEXT API, covering the most common use cases and patterns. All examples follow FLEXT-Core compliance standards and enterprise best practices.

### **Prerequisites**

```bash
# Ensure proper installation
cd /workspace/flext/flext-api
poetry install --with dev,test
make check  # Verify installation
```

---

## 🚀 Quick Start Examples

### **Creating an API Instance**

```python
from flext_api import create_flext_api, FlextResult
from flext_core import get_logger

logger = get_logger(__name__)

def basic_api_creation():
    """Basic API instance creation example."""

    # Method 1: Factory function (recommended)
    api = create_flext_api()
    logger.info("API instance created via factory")

    # Verify API functionality
    assert hasattr(api, 'flext_api_create_client')
    assert hasattr(api, 'get_builder')

    return api

# Usage
api = basic_api_creation()
print("✅ API instance ready")
```

### **Creating HTTP Clients**

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

def create_http_client_example():
    """Example of creating HTTP clients with different configurations."""

    api = create_flext_api()

    # Basic HTTP client
    basic_client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 30
    })

    if basic_client_result.success:
        client = basic_client_result.data
        logger.info("Basic HTTP client created successfully")

        # Test the client
        response = client.get("/json")
        if response.success:
            logger.info("Test request successful", data_keys=list(response.data.keys()))
            return response.data
        else:
            logger.error("Test request failed", error=response.error)
            return None
    else:
        logger.error("Client creation failed", error=basic_client_result.error)
        return None

# Usage
result = create_http_client_example()
if result:
    print(f"✅ Client test successful: {result}")
else:
    print("❌ Client test failed")
```

### **HTTP Client with Custom Headers**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def client_with_headers_example():
    """Example of HTTP client with custom headers."""

    api = create_flext_api()

    # Client with authentication and custom headers
    client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 30,
        "headers": {
            "User-Agent": "FLEXT-API/0.9.0",
            "Accept": "application/json",
            "Authorization": "Bearer demo-token",
            "X-Custom-Header": "FLEXT-Example"
        }
    })

    if client_result.success:
        client = client_result.data
        logger.info("Client with headers created")

        # Test with headers
        response = client.get("/headers")
        if response.success:
            headers_received = response.data.get("headers", {})
            logger.info("Headers test successful",
                       user_agent=headers_received.get("User-Agent"),
                       custom_header=headers_received.get("X-Custom-Header"))
            return headers_received
        else:
            logger.error("Headers test failed", error=response.error)
    else:
        logger.error("Client creation failed", error=client_result.error)

    return None

# Usage
headers_result = client_with_headers_example()
if headers_result:
    print("✅ Custom headers working correctly")
```

---

## 🔧 HTTP Operations Examples

### **GET Requests**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def get_request_examples():
    """Examples of various GET request patterns."""

    api = create_flext_api()
    client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 15
    })

    if not client_result.success:
        logger.error("Client creation failed")
        return

    client = client_result.data

    # Simple GET request
    logger.info("Testing simple GET request")
    response = client.get("/json")
    if response.success:
        logger.info("Simple GET successful", data_type=type(response.data).__name__)

    # GET with query parameters
    logger.info("Testing GET with query parameters")
    response = client.get("/get", params={"param1": "value1", "param2": "value2"})
    if response.success:
        args = response.data.get("args", {})
        logger.info("GET with params successful", params=args)

    # GET with custom headers
    logger.info("Testing GET with custom headers")
    response = client.get("/get", headers={"X-Test-Header": "test-value"})
    if response.success:
        headers = response.data.get("headers", {})
        logger.info("GET with headers successful",
                   test_header=headers.get("X-Test-Header"))

# Usage
get_request_examples()
```

### **POST Requests**

```python
from flext_api import create_flext_api
from flext_core import get_logger
import json

logger = get_logger(__name__)

def post_request_examples():
    """Examples of various POST request patterns."""

    api = create_flext_api()
    client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 15
    })

    if not client_result.success:
        logger.error("Client creation failed")
        return

    client = client_result.data

    # POST with JSON data
    logger.info("Testing POST with JSON data")
    json_data = {
        "name": "FLEXT API Test",
        "version": "0.9.0",
        "features": ["http_client", "builders", "plugins"]
    }

    response = client.post("/post", json=json_data)
    if response.success:
        received_json = response.data.get("json", {})
        logger.info("POST JSON successful", name=received_json.get("name"))

    # POST with form data
    logger.info("Testing POST with form data")
    form_data = {
        "field1": "value1",
        "field2": "value2"
    }

    response = client.post("/post", data=form_data)
    if response.success:
        received_form = response.data.get("form", {})
        logger.info("POST form successful", fields=list(received_form.keys()))

    # POST with raw data
    logger.info("Testing POST with raw data")
    raw_data = "This is raw text data"

    response = client.post("/post",
                          data=raw_data,
                          headers={"Content-Type": "text/plain"})
    if response.success:
        received_data = response.data.get("data", "")
        logger.info("POST raw data successful", length=len(received_data))

# Usage
post_request_examples()
```

### **Error Handling Examples**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def error_handling_examples():
    """Examples of proper error handling with FlextResult pattern."""

    api = create_flext_api()

    # Test with invalid URL
    logger.info("Testing error handling with invalid URL")
    client_result = api.flext_api_create_client({
        "base_url": "https://invalid-domain-that-does-not-exist.com",
        "timeout": 5
    })

    if client_result.success:
        client = client_result.data
        response = client.get("/test")

        if response.success:
            logger.info("Request unexpectedly succeeded")
        else:
            logger.info("Request failed as expected", error=response.error)
            # Handle the error appropriately
            print(f"Handled error: {response.error}")
    else:
        logger.info("Client creation failed as expected", error=client_result.error)

    # Test with timeout
    logger.info("Testing timeout handling")
    client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 1  # Very short timeout
    })

    if client_result.success:
        client = client_result.data
        response = client.get("/delay/5")  # 5 second delay

        if response.is_failure:
            logger.info("Timeout handled correctly", error=response.error)
            # Handle timeout gracefully
            print("Request timed out - implementing fallback logic")

    # Test with HTTP error status
    logger.info("Testing HTTP error status handling")
    client_result = api.flext_api_create_client({
        "base_url": "https://httpbin.org",
        "timeout": 10
    })

    if client_result.success:
        client = client_result.data
        response = client.get("/status/404")  # Force 404 error

        if response.is_failure:
            logger.info("HTTP error handled correctly", error=response.error)
            # Handle HTTP errors
            print("Received HTTP error - checking status code")

# Usage
error_handling_examples()
```

---

## 🏗️ Builder Pattern Examples

### **Query Building**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def query_builder_examples():
    """Examples of using query builders."""

    api = create_flext_api()
    builder = api.get_builder()

    # Simple query building
    logger.info("Building simple query")
    query = (
        builder.for_query()
        .equals("status", "active")
        .equals("category", "api")
        .build()
    )

    query_dict = query.to_dict()
    logger.info("Simple query built", query=query_dict)
    print(f"Simple query: {query_dict}")

    # Complex query with sorting and pagination
    logger.info("Building complex query")
    complex_query = (
        builder.for_query()
        .equals("status", "active")
        .contains("name", "flext")
        .greater_than("created_at", "2024-01-01")
        .sort_desc("updated_at")
        .sort_asc("name")
        .page(1)
        .page_size(20)
        .build()
    )

    complex_dict = complex_query.to_dict()
    logger.info("Complex query built", query=complex_dict)
    print(f"Complex query: {complex_dict}")

    # Query with custom filters
    logger.info("Building query with custom filters")
    custom_query = (
        builder.for_query()
        .add_filter("custom_field", "custom_value")
        .add_filter("numeric_field", 42)
        .add_filter("boolean_field", True)
        .build()
    )

    custom_dict = custom_query.to_dict()
    logger.info("Custom query built", query=custom_dict)
    print(f"Custom query: {custom_dict}")

# Usage
query_builder_examples()
```

### **Response Building**

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def response_builder_examples():
    """Examples of using response builders."""

    api = create_flext_api()
    builder = api.get_builder()

    # Success response
    logger.info("Building success response")
    success_response = (
        builder.for_response()
        .success(
            data={"items": [1, 2, 3], "total": 3},
            message="Data retrieved successfully"
        )
        .build()
    )

    success_dict = success_response.to_dict()
    logger.info("Success response built", response=success_dict)
    print(f"Success response: {success_dict}")

    # Error response
    logger.info("Building error response")
    error_response = (
        builder.for_response()
        .error("Validation failed", 400)
        .add_error_detail("field", "name", "Name is required")
        .add_error_detail("field", "email", "Invalid email format")
        .build()
    )

    error_dict = error_response.to_dict()
    logger.info("Error response built", response=error_dict)
    print(f"Error response: {error_dict}")

    # Paginated response
    logger.info("Building paginated response")
    paginated_response = (
        builder.for_response()
        .paginated(
            data=[{"id": i, "name": f"Item {i}"} for i in range(1, 11)],
            page=1,
            page_size=10,
            total=100
        )
        .build()
    )

    paginated_dict = paginated_response.to_dict()
    logger.info("Paginated response built", response=paginated_dict)
    print(f"Paginated response: {paginated_dict}")

# Usage
response_builder_examples()
```

---

## 🔧 Configuration Examples

### **Basic Configuration**

```python
from flext_api import create_flext_api, FlextApiClientConfig
from flext_core import get_logger

logger = get_logger(__name__)

def basic_configuration_example():
    """Example of basic configuration patterns."""

    # Configuration with dictionary
    logger.info("Creating client with dictionary configuration")
    api = create_flext_api()

    dict_config = {
        "base_url": "https://httpbin.org",
        "timeout": 30,
        "max_retries": 3,
        "headers": {
            "User-Agent": "FLEXT-API-Example/0.9.0",
            "Accept": "application/json"
        }
    }

    client_result = api.flext_api_create_client(dict_config)
    if client_result.success:
        logger.info("Client created with dictionary config")
        client = client_result.data

        # Test the configured client
        response = client.get("/user-agent")
        if response.success:
            user_agent = response.data.get("user-agent", "")
            print(f"✅ User-Agent: {user_agent}")

    # Configuration with Pydantic model
    logger.info("Creating client with Pydantic configuration")
    pydantic_config = FlextApiClientConfig(
        base_url="https://httpbin.org",
        timeout=25.0,
        max_retries=2,
        headers={"X-Config-Type": "Pydantic"}
    )

    client_result = api.flext_api_create_client(pydantic_config.dict())
    if client_result.success:
        logger.info("Client created with Pydantic config")
        print("✅ Pydantic configuration successful")

# Usage
basic_configuration_example()
```

### **Environment-Based Configuration**

```python
import os
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def environment_configuration_example():
    """Example of environment-based configuration."""

    # Set environment variables for configuration
    os.environ.setdefault("FLEXT_API_BASE_URL", "https://httpbin.org")
    os.environ.setdefault("FLEXT_API_TIMEOUT", "30")
    os.environ.setdefault("FLEXT_API_MAX_RETRIES", "3")
    os.environ.setdefault("FLEXT_API_USER_AGENT", "FLEXT-API-Env/0.9.0")

    # Create configuration from environment
    config = {
        "base_url": os.getenv("FLEXT_API_BASE_URL"),
        "timeout": int(os.getenv("FLEXT_API_TIMEOUT", "30")),
        "max_retries": int(os.getenv("FLEXT_API_MAX_RETRIES", "3")),
        "headers": {
            "User-Agent": os.getenv("FLEXT_API_USER_AGENT", "FLEXT-API/0.9.0")
        }
    }

    logger.info("Creating client with environment configuration", config=config)

    api = create_flext_api()
    client_result = api.flext_api_create_client(config)

    if client_result.success:
        client = client_result.data
        logger.info("Environment-configured client created")

        # Test environment configuration
        response = client.get("/user-agent")
        if response.success:
            user_agent = response.data.get("user-agent", "")
            print(f"✅ Environment config working: {user_agent}")
    else:
        logger.error("Environment configuration failed", error=client_result.error)

# Usage
environment_configuration_example()
```

---

## 🧪 Testing Examples

### **Simple Test Example**

```python
import pytest
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

class TestBasicFlextApi:
    """Basic test examples for FLEXT API."""

    def test_api_creation(self):
        """Test API instance creation."""
        # Arrange & Act
        api = create_flext_api()

        # Assert
        assert api is not None
        assert hasattr(api, 'flext_api_create_client')
        assert hasattr(api, 'get_builder')
        logger.info("API creation test passed")

    def test_client_creation_success(self):
        """Test successful HTTP client creation."""
        # Arrange
        api = create_flext_api()
        config = {
            "base_url": "https://httpbin.org",
            "timeout": 10
        }

        # Act
        result = api.flext_api_create_client(config)

        # Assert
        assert result.success
        assert result.data is not None
        logger.info("Client creation test passed")

    def test_client_creation_failure(self):
        """Test client creation with invalid configuration."""
        # Arrange
        api = create_flext_api()
        invalid_config = {"base_url": ""}  # Invalid empty URL

        # Act
        result = api.flext_api_create_client(invalid_config)

        # Assert
        assert result.is_failure
        assert "base_url" in result.error.lower()
        logger.info("Client creation failure test passed")

    @pytest.mark.integration
    def test_http_request(self):
        """Integration test with real HTTP request."""
        # Arrange
        api = create_flext_api()
        client_result = api.flext_api_create_client({
            "base_url": "https://httpbin.org",
            "timeout": 15
        })

        assert client_result.success
        client = client_result.data

        # Act
        response = client.get("/json")

        # Assert
        assert response.success
        assert "slideshow" in response.data
        logger.info("HTTP request integration test passed")

# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 📚 Complete Example Application

### **Simple API Client Application**

```python
#!/usr/bin/env python3
"""
Complete example application demonstrating FLEXT API usage.
This example creates a simple CLI tool for making HTTP requests.
"""

import sys
import json
from typing import Optional, Dict, object
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class SimpleApiClient:
    """Simple API client using FLEXT API."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.api = create_flext_api()
        self.base_url = base_url
        self.timeout = timeout
        self.client = None

        # Initialize client
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize the HTTP client."""
        logger.info("Initializing HTTP client", base_url=self.base_url)

        client_result = self.api.flext_api_create_client({
            "base_url": self.base_url,
            "timeout": self.timeout,
            "headers": {
                "User-Agent": "SimpleApiClient/1.0",
                "Accept": "application/json"
            }
        })

        if client_result.success:
            self.client = client_result.data
            logger.info("HTTP client initialized successfully")
        else:
            logger.error("Failed to initialize HTTP client", error=client_result.error)
            raise RuntimeError(f"Client initialization failed: {client_result.error}")

    def get(self, path: str, params: Optional[Dict[str, object]] = None) -> FlextResult[Dict[str, object]]:
        """Make a GET request."""
        if not self.client:
            return FlextResult[None].fail("Client not initialized")

        logger.info("Making GET request", path=path, params=params)

        response = self.client.get(path, params=params)

        if response.success:
            logger.info("GET request successful", path=path)
            return FlextResult[None].ok(response.data)
        else:
            logger.error("GET request failed", path=path, error=response.error)
            return FlextResult[None].fail(response.error)

    def post(self, path: str, data: Optional[Dict[str, object]] = None) -> FlextResult[Dict[str, object]]:
        """Make a POST request."""
        if not self.client:
            return FlextResult[None].fail("Client not initialized")

        logger.info("Making POST request", path=path)

        response = self.client.post(path, json=data)

        if response.success:
            logger.info("POST request successful", path=path)
            return FlextResult[None].ok(response.data)
        else:
            logger.error("POST request failed", path=path, error=response.error)
            return FlextResult[None].fail(response.error)

def main():
    """Main application entry point."""
    # Configure logging
    import os
    os.environ.setdefault("LOG_LEVEL", "INFO")

    logger.info("Starting SimpleApiClient example")

    try:
        # Create client instance
        client = SimpleApiClient("https://httpbin.org")

        # Example 1: Simple GET request
        print("\n=== Example 1: Simple GET ===")
        get_result = client.get("/json")
        if get_result.success:
            print("✅ GET request successful")
            print(f"Data keys: {list(get_result.data.keys())}")
        else:
            print(f"❌ GET request failed: {get_result.error}")

        # Example 2: GET with parameters
        print("\n=== Example 2: GET with parameters ===")
        params_result = client.get("/get", params={"param1": "value1", "test": "data"})
        if params_result.success:
            args = params_result.data.get("args", {})
            print("✅ GET with params successful")
            print(f"Parameters received: {args}")
        else:
            print(f"❌ GET with params failed: {params_result.error}")

        # Example 3: POST request
        print("\n=== Example 3: POST request ===")
        post_data = {
            "message": "Hello from FLEXT API!",
            "timestamp": "2024-01-01T00:00:00Z",
            "client": "SimpleApiClient"
        }
        post_result = client.post("/post", data=post_data)
        if post_result.success:
            received_json = post_result.data.get("json", {})
            print("✅ POST request successful")
            print(f"Posted data: {received_json}")
        else:
            print(f"❌ POST request failed: {post_result.error}")

        print("\n✅ All examples completed successfully!")

    except Exception as e:
        logger.exception("Application failed")
        print(f"❌ Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

To run this example:

```bash
# Save as simple_client.py and run
python simple_client.py
```

---

## 📚 Next Steps

### **Advanced Topics**

After mastering these basic examples, explore:

- **[Advanced Patterns](advanced-patterns.md)** - Complex usage patterns and optimization
- **[Integration Examples](integration-examples.md)** - Service integration patterns
- **[Architecture Guide](../architecture.md)** - Understanding the underlying architecture
- **[Development Guide](../development.md)** - Contributing and development workflows

### **Related Documentation**

- **[Configuration](../configuration.md)** - Advanced configuration patterns
- **[Integration](../integration.md)** - Ecosystem integration guide
- **[Troubleshooting](../troubleshooting.md)** - Common issues and solutions

---

**Basic Usage Examples v0.9.0** - Fundamental usage patterns for FLEXT API HTTP foundation library.
