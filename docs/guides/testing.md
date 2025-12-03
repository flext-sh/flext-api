# Testing Guide

Comprehensive guide for testing FLEXT-API applications with unit tests, integration tests, and end-to-end testing strategies.

## Testing Philosophy

FLEXT-API follows a comprehensive testing strategy that ensures reliability, maintainability, and confidence in deployments.

### Test Categories

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Performance Tests** - Validate performance requirements
5. **Security Tests** - Validate security measures

## Unit Testing

### HTTP Client Testing

```python
import pytest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
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

class TestFlextApiClient:
    def setup_method(self):
        self.client = FlextApiClient(
            base_url="https://jsonplaceholder.typicode.com"
        )

    def test_get_request_success(self):
        """Test successful GET request."""
        result = self.client.get("/users/1")

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200

        user = response.json()
        assert "id" in user
        assert "name" in user

    def test_get_request_not_found(self):
        """Test 404 error handling."""
        result = self.client.get("/users/99999")

        assert result.is_failure
        error = result.error
        assert error.status_code == 404

    def test_post_request_with_data(self):
        """Test POST request with JSON data."""
        user_data = {"name": "Test User", "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 201

    @pytest.mark.parametrize("invalid_data", [
        {"name": ""},  # Empty name
        {"email": "invalid-email"},  # Invalid email
        {},  # Empty data
    ])
    def test_post_request_validation(self, invalid_data):
        """Test POST request validation."""
        result = self.client.post("/users", json=invalid_data)

        # Should handle validation errors gracefully
        assert isinstance(result, FlextResult)
```

### Middleware Testing

```python
import pytest
from flext_api.middleware import LoggingMiddleware, AuthenticationMiddleware
from flext_core import FlextBus
from flext_core import FlextConfig
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

class TestLoggingMiddleware:
    def setup_method(self):
        self.logger = FlextLogger("test")
        self.middleware = LoggingMiddleware(self.logger)

    def test_request_logging(self, mock_request):
        """Test that requests are logged."""
        # Mock request object
        mock_request.method = "GET"
        mock_request.path = "/users"
        mock_request.headers = {"User-Agent": "test"}

        result = await self.middleware.process_request(mock_request)

        assert result.is_success
        # Verify logging was called (mock verification)

    def test_response_logging(self, mock_request, mock_response):
        """Test that responses are logged."""
        mock_response.status_code = 200
        mock_response.duration_ms = 150

        result = await self.middleware.process_response(mock_request, mock_response)

        assert result.is_success
        # Verify logging was called (mock verification)
```

## Integration Testing

### FastAPI Application Testing

```python
import pytest
from fastapi.testclient import TestClient
from flext_api import create_fastapi_app, FlextApiConfig

class TestUserAPI:
    def setup_method(self):
        config = FlextApiConfig(
            title="Test API",
            version="1.0.0",
            debug=True
        )
        self.app = create_fastapi_app(config=config)
        self.client = TestClient(self.app)

    def test_get_users_endpoint(self):
        """Test GET /users endpoint."""
        response = self.client.get("/users")

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data

    def test_create_user_endpoint(self):
        """Test POST /users endpoint."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com"
        }

        response = self.client.post("/users", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert "id" in data

    def test_user_not_found(self):
        """Test 404 error handling."""
        response = self.client.get("/users/99999")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
```

### Database Integration Testing

```python
import pytest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
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

class TestDatabaseIntegration:
    def setup_method(self):
        # Setup test database
        self.container = FlextContainer.get_global()
        self.db_service = self.container.get("database").unwrap()

        # Clear test data
        self.db_service.clear_test_data()

        # Create test client
        self.client = FlextApiClient(
            base_url="http://localhost:8000"
        )

    def teardown_method(self):
        # Cleanup test data
        self.db_service.clear_test_data()

    def test_user_creation_flow(self):
        """Test complete user creation workflow."""

        # 1. Create user via API
        user_data = {"name": "Integration Test User", "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.is_success
        user_response = result.unwrap().json()
        user_id = user_response["id"]

        # 2. Verify user exists in database
        db_user = self.db_service.get_user_by_id(user_id)
        assert db_user is not None
        assert db_user.name == "Integration Test User"

        # 3. Retrieve user via API
        result = self.client.get(f"/users/{user_id}")
        assert result.is_success
        retrieved_user = result.unwrap().json()
        assert retrieved_user["name"] == "Integration Test User"
```

## End-to-End Testing

### Complete Workflow Testing

```python
import pytest
from playwright.sync_api import Page, expect

class TestE2EUserWorkflow:
    def setup_method(self):
        self.client = FlextApiClient(
            base_url="http://localhost:8000"
        )

    def test_complete_user_journey(self):
        """Test complete user registration and profile update journey."""

        # 1. Register new user
        user_data = {
            "name": "E2E Test User",
            "email": "e2e@example.com",
            "password": "secure_password"
        }

        result = self.client.post("/auth/register", json=user_data)
        assert result.is_success

        # 2. Login
        login_data = {
            "email": "e2e@example.com",
            "password": "secure_password"
        }

        result = self.client.post("/auth/login", json=login_data)
        assert result.is_success

        # Extract token
        login_response = result.unwrap().json()
        token = login_response["access_token"]

        # 3. Update profile (authenticated request)
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"name": "Updated E2E User"}

        result = self.client.put("/users/profile", json=update_data, headers=headers)
        assert result.is_success

        # 4. Verify update
        result = self.client.get("/users/profile", headers=headers)
        assert result.is_success

        profile = result.unwrap().json()
        assert profile["name"] == "Updated E2E User"
```

## Performance Testing

### Load Testing

```python
import asyncio
import time
from statistics import mean, median
from flext_api import FlextApiClient

async def load_test_endpoint(endpoint: str, requests: int = 100):
    """Perform load testing on an endpoint."""
    client = FlextApiClient(base_url="http://localhost:8000")

    start_time = time.time()
    results = []

    # Execute requests concurrently
    async def make_request(i: int):
        request_start = time.time()
        result = client.get(f"{endpoint}?request_id={i}")
        request_time = time.time() - request_start

        return {
            "request_id": i,
            "success": result.is_success,
            "status_code": result.unwrap().status_code if result.is_success else None,
            "duration_ms": request_time * 1000,
            "error": str(result.error) if result.is_failure else None
        }

    # Run all requests
    tasks = [make_request(i) for i in range(requests)]
    results = await asyncio.gather(*tasks)

    total_time = time.time() - start_time

    # Calculate metrics
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]

    durations = [r["duration_ms"] for r in successful_requests]

    return {
        "total_requests": requests,
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "success_rate": len(successful_requests) / requests * 100,
        "total_time": total_time,
        "requests_per_second": requests / total_time,
        "average_response_time": mean(durations) if durations else 0,
        "median_response_time": median(durations) if durations else 0,
        "min_response_time": min(durations) if durations else 0,
        "max_response_time": max(durations) if durations else 0
    }

# Usage
results = asyncio.run(load_test_endpoint("/users", 100))
print(f"Success rate: {results['success_rate']:.2f}%")
print(f"Average response time: {results['average_response_time']:.2f}ms")
print(f"Requests per second: {results['requests_per_second']:.2f}")
```

## Security Testing

### Authentication Testing

```python
import pytest
from flext_api import FlextApiClient

class TestAuthentication:
    def setup_method(self):
        self.client = FlextApiClient(base_url="http://localhost:8000")

    def test_unauthorized_access(self):
        """Test that unauthorized requests are rejected."""
        result = self.client.get("/REDACTED_LDAP_BIND_PASSWORD/users")

        assert result.is_failure
        error = result.error
        assert error.status_code == 401

    def test_invalid_token(self):
        """Test invalid JWT token handling."""
        headers = {"Authorization": "Bearer invalid_token"}
        result = self.client.get("/users/profile", headers=headers)

        assert result.is_failure
        error = result.error
        assert error.status_code == 401

    def test_authorized_access(self):
        """Test successful authentication."""
        # Login first
        login_data = {"email": "test@example.com", "password": "password"}
        login_result = self.client.post("/auth/login", json=login_data)

        assert login_result.is_success
        token = login_result.unwrap().json()["access_token"]

        # Use token for authenticated request
        headers = {"Authorization": f"Bearer {token}"}
        result = self.client.get("/users/profile", headers=headers)

        assert result.is_success
        assert result.unwrap().status_code == 200
```

### Input Validation Testing

```python
import pytest

class TestInputValidation:
    def setup_method(self):
        self.client = FlextApiClient(base_url="http://localhost:8000")

    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@example.com",
        "user@",
        "user@.com",
        ""
    ])
    def test_invalid_email_validation(self, invalid_email):
        """Test email validation."""
        user_data = {"name": "Test User", "email": invalid_email}
        result = self.client.post("/users", json=user_data)

        assert result.is_failure
        error = result.error
        assert error.status_code == 422  # Validation error

    @pytest.mark.parametrize("invalid_name", [
        "",  # Empty name
        "a" * 101,  # Too long name
        None,  # Missing field
    ])
    def test_name_validation(self, invalid_name):
        """Test name validation."""
        user_data = {"name": invalid_name, "email": "test@example.com"}
        result = self.client.post("/users", json=user_data)

        assert result.is_failure
        error = result.error
        assert error.status_code == 422

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        malicious_data = {
            "name": "'; DROP TABLE users; --",
            "email": "hacker@example.com"
        }

        result = self.client.post("/users", json=malicious_data)

        # Should either reject the input or sanitize it
        assert result.is_failure or result.unwrap().status_code in [201, 422]
```

## Test Infrastructure

### Test Fixtures

```python
import pytest
from flext_api import FlextApiClient
from flext_core import FlextBus
from flext_core import FlextConfig
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

@pytest.fixture
def api_client():
    """Provide configured API client for tests."""
    return FlextApiClient(
        base_url="http://localhost:8000",
        timeout=5.0  # Shorter timeout for tests
    )

@pytest.fixture
def test_database():
    """Provide test database with cleanup."""
    container = FlextContainer.get_global()
    db = container.get("test_database").unwrap()

    # Setup test data
    db.seed_test_data()

    yield db

    # Cleanup
    db.clear_test_data()

@pytest.fixture
def authenticated_client():
    """Provide authenticated API client."""
    client = FlextApiClient(base_url="http://localhost:8000")

    # Login and get token
    login_result = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "test_password"
    })

    if login_result.is_success:
        token = login_result.unwrap().json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {token}"})

    return client
```

### Test Utilities

```python
from flext_api.testing import TestUtilities

class TestHelpers:
    """Helper methods for testing."""

    @staticmethod
    def assert_success_response(result: FlextResult, expected_status: int = 200):
        """Assert that result is successful."""
        assert result.is_success, f"Expected success but got error: {result.error}"
        response = result.unwrap()
        assert response.status_code == expected_status

    @staticmethod
    def assert_error_response(result: FlextResult, expected_status: int):
        """Assert that result is an error."""
        assert result.is_failure, "Expected error but got success"
        error = result.error
        assert error.status_code == expected_status

    @staticmethod
    def create_test_user_data(overrides: dict[str, object] = None) -> dict[str, object]:
        """Create test user data."""
        base_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "test_password"
        }

        if overrides:
            base_data.update(overrides)

        return base_data

# Usage in tests
def test_user_creation(api_client):
    user_data = TestHelpers.create_test_user_data({"name": "Custom User"})
    result = api_client.post("/users", json=user_data)

    TestHelpers.assert_success_response(result, 201)
    response_data = result.unwrap().json()
    assert response_data["name"] == "Custom User"
```

## Running Tests

### Test Execution

```bash
# Run all tests
make test

# Run specific test categories
make test-unit         # Unit tests only
make test-integration  # Integration tests only
make test-e2e         # End-to-end tests only

# Run with coverage
make test-coverage

# Run specific test files
pytest tests/unit/test_client.py -v
pytest tests/integration/test_user_api.py -v

# Run with parallel execution
pytest -n auto tests/

# Run with verbose output
pytest -v --tb=short tests/
```

### Test Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests",
    "security: Security tests"
]
```

## Best Practices

### Test Organization

1. **Test Structure**: Group related tests in classes
2. **Test Naming**: Use descriptive names starting with `test_`
3. **Test Isolation**: Each test should be independent
4. **Setup/Teardown**: Use fixtures for common setup
5. **Assertions**: Use specific assertions over generic ones

### Error Handling in Tests

```python
def test_error_scenarios(api_client):
    """Test various error scenarios."""

    # Test 404 Not Found
    result = api_client.get("/users/99999")
    assert result.is_failure
    assert result.error.status_code == 404

    # Test 400 Bad Request
    invalid_data = {"name": ""}  # Invalid data
    result = api_client.post("/users", json=invalid_data)
    assert result.is_failure
    assert result.error.status_code == 422

    # Test 500 Server Error
    # This would require mocking a server error
    # Implementation depends on your error simulation approach
```

### Performance Testing

```python
import time
import statistics

def test_api_performance(api_client):
    """Test API performance requirements."""

    # Measure response time for multiple requests
    response_times = []

    for i in range(10):
        start_time = time.time()
        result = api_client.get("/users")
        end_time = time.time()

        if result.is_success:
            response_time = (end_time - start_time) * 1000  # Convert to ms
            response_times.append(response_time)

    # Assert performance requirements
    avg_response_time = statistics.mean(response_times)
    max_response_time = max(response_times)

    assert avg_response_time < 500, f"Average response time too slow: {avg_response_time}ms"
    assert max_response_time < 1000, f"Max response time too slow: {max_response_time}ms"
    assert all(t < 1000 for t in response_times), "All requests should be under 1s"
```

This testing guide provides comprehensive coverage of testing strategies for FLEXT-API applications, ensuring reliability and maintainability.
