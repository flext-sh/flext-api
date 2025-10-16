# Testing Plan & Strategy

## Overview

**Current Status**: 23 tests passing, 76 failing (28% pass rate) · Target: 75%+ coverage with real HTTP functionality

**Testing Philosophy**: Comprehensive testing strategy ensuring reliability, maintainability, and confidence in HTTP foundation deployments across the FLEXT ecosystem.

## Test Categories & Structure

### 1. Unit Tests (Primary Focus)

**Status**: 23 passing, 76 failing - Major improvements needed
**Coverage Target**: 80%+ unit test coverage

#### HTTP Client Testing (`tests/unit/test_client.py`)

**Current Issues**:

- ❌ Client creation fails due to missing `FlextModels.create_validated_http_url()`
- ❌ Protocol plugin interface inconsistencies
- ❌ Configuration API test failures

**Required Fixes**:

```python
# Missing method causing failures
@classmethod
def create_validated_http_url(cls, url: str) -> FlextResult[str]:
    """Validate and normalize HTTP URL."""
    # Implementation needed
```

#### Model Validation Testing (`tests/unit/test_models.py`)

**Current Issues**:

- ❌ 3 test failures due to missing URL validation method
- ❌ HttpResponse 204 No Content validation errors
- ❌ Configuration factory test failures

**Test Coverage Requirements**:

- ✅ HttpRequest model validation
- ✅ HttpResponse model validation
- ✅ ClientConfig creation and validation
- ✅ URL validation and normalization
- ✅ Error response handling

#### Configuration Testing (`tests/unit/test_config.py`)

**Current Issues**:

- ❌ Missing `to_dict()` serialization method
- ❌ Negative timeout validation not raising ValueError
- ❌ API base URL attribute access failures

**Configuration Test Matrix**:

```python
# Required test scenarios
def test_config_defaults():
def test_config_validation():
def test_config_serialization():  # to_dict() method needed
def test_config_negative_timeout():
def test_api_config_creation():
```

#### Storage Testing (`tests/unit/test_storage.py`)

**Current Issues**:

- ❌ Logger property setter missing
- ❌ Storage initialization failures
- ❌ Size and clear operations failing

**Storage Test Requirements**:

- ✅ Basic CRUD operations
- ✅ TTL functionality
- ✅ Performance scenarios
- ✅ Error recovery patterns

### 2. Integration Tests (Secondary Priority)

**Status**: Not implemented - Planned for Phase 1 completion
**Target**: Real HTTP server integration testing

#### HTTP Operations Integration (`tests/integration/test_http_operations.py`)

**Planned Tests**:

- ✅ Real HTTP GET/POST operations with httpbin.org
- ✅ Error handling with various HTTP status codes
- ✅ Timeout and connection handling
- ✅ Request/response header validation
- ✅ JSON data serialization/deserialization

#### FastAPI Application Testing (`tests/integration/test_fastapi_app.py`)

**Planned Tests**:

- ✅ Application factory creation
- ✅ Health endpoint responses
- ✅ Middleware integration
- ✅ Error handling middleware
- ✅ Request/response logging

### 3. End-to-End Tests (Future Phase)

**Status**: Not implemented
**Target**: Complete HTTP workflows

#### HTTP Workflow Testing (`tests/e2e/test_http_workflows.py`)

**Future Tests**:

- ✅ User registration and authentication flows
- ✅ Data submission and retrieval workflows
- ✅ Error recovery and retry scenarios
- ✅ Performance under load testing

## Critical Test Failures (Priority Fixes)

### High Priority (Blocking Phase 1 Completion)

#### 1. Model Validation Failures (4 tests failing)

**Error**: `AttributeError: type object 'FlextModels' has no attribute 'create_validated_http_url'`

**Impact**: Prevents model creation and validation testing
**Solution**: Implement missing URL validation method in models.py

#### 2. Configuration API Failures (4 tests failing)

**Error**: `AttributeError: 'FlextApiConfig' object has no attribute 'to_dict'`

**Impact**: Configuration serialization not working
**Solution**: Add to_dict() method to configuration classes

#### 3. HTTP Response Validation Failures (1 test failing)

**Error**: `ValidationError: HTTP 204 No Content responses should not have a body`

**Impact**: Response validation too strict for No Content responses
**Solution**: Adjust validation logic for 204 responses

#### 4. Storage Implementation Failures (6 tests failing)

**Error**: `AttributeError: property 'logger' of 'FlextApiStorage' object has no setter`

**Impact**: Storage abstraction cannot be properly initialized
**Solution**: Implement logger property setter

### Medium Priority (Quality Improvements)

#### 5. Constants API Issues (3 tests failing)

**Error**: Various attribute access failures in constants
**Impact**: Status code and constant access problems
**Solution**: Fix constants module exports

#### 6. Utility Function Failures (16 tests failing)

**Error**: Missing methods in utility classes
**Impact**: HTTP utility functions not available
**Solution**: Implement missing utility methods

## Test Infrastructure Requirements

### Test Fixtures & Setup

#### HTTP Client Fixtures

```python
@pytest.fixture
def http_client():
    """Provide configured HTTP client for tests."""
    return FlextApiClient(
        base_url="https://httpbin.org",
        timeout=5.0
    )

@pytest.fixture
def mock_http_server():
    """Provide mock HTTP server for testing."""
    # httpx mock server implementation
```

#### Model Fixtures

```python
@pytest.fixture
def valid_http_request():
    """Provide valid HTTP request model."""
    return FlextApiModels.HttpRequest(
        method="GET",
        url="https://httpbin.org/get"
    )

@pytest.fixture
def valid_client_config():
    """Provide valid client configuration."""
    return FlextApiModels.ClientConfig(
        base_url="https://api.example.com"
    )
```

### Test Data Factories

#### Request/Response Factories

```python
class TestDataFactory:
    @staticmethod
    def create_http_request(overrides=None):
        """Create test HTTP request."""
        base = {
            "method": "GET",
            "url": "https://httpbin.org/get",
            "headers": {"Accept": "application/json"}
        }
        if overrides:
            base.update(overrides)
        return FlextApiModels.HttpRequest(**base)

    @staticmethod
    def create_http_response(overrides=None):
        """Create test HTTP response."""
        base = {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": {"status": "ok"}
        }
        if overrides:
            base.update(overrides)
        return FlextApiModels.HttpResponse(**base)
```

## Testing Strategy by Component

### HTTP Client Testing Strategy

#### Unit Testing Approach

```python
class TestFlextApiClient:
    def test_successful_get_request(self, http_client, mock_response):
        """Test successful GET request."""
        # Mock httpx response
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        result = http_client.get("/test")

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200
        assert response.body["data"] == "test"

    def test_error_handling(self, http_client, mock_response):
        """Test error response handling."""
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=mock_request, response=mock_response
        )

        result = http_client.get("/not-found")

        assert result.is_failure
        error = result.error
        assert error.status_code == 404
```

#### Integration Testing Approach

```python
class TestHTTPIntegration:
    def test_real_http_get(self, http_client):
        """Test real HTTP GET with httpbin.org."""
        result = http_client.get("/get")

        assert result.is_success
        response = result.unwrap()
        assert response.status_code == 200
        assert "url" in response.body

    def test_timeout_handling(self, http_client):
        """Test timeout behavior."""
        # Configure slow endpoint
        result = http_client.get("/delay/10", timeout=1.0)

        assert result.is_failure
        assert isinstance(result.error, TimeoutError)
```

### Model Testing Strategy

#### Validation Testing

```python
class TestModelValidation:
    def test_url_validation(self):
        """Test URL validation patterns."""
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://localhost:8080/api",
            "https://api.example.com/v1/users"
        ]

        for url in valid_urls:
            result = FlextModels.create_validated_http_url(url)
            assert result.is_success

        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            ""
        ]

        for url in invalid_urls:
            result = FlextModels.create_validated_http_url(url)
            assert result.is_failure
```

#### Serialization Testing

```python
class TestModelSerialization:
    def test_request_serialization(self, valid_http_request):
        """Test HTTP request JSON serialization."""
        json_data = valid_http_request.model_dump_json()
        assert json_data is not None

        # Test deserialization
        deserialized = FlextApiModels.HttpRequest.model_validate_json(json_data)
        assert deserialized.method == valid_http_request.method
        assert deserialized.url == valid_http_request.url
```

## Test Execution Strategy

### Development Testing Workflow

#### Quick Test Execution

```bash
# Run all tests with coverage
make test                    # 23/99 passing (28%)

# Run specific test categories
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests
pytest -m e2e              # End-to-end tests

# Run specific test files
pytest tests/unit/test_client.py -v
pytest tests/unit/test_models.py -v

# Run with debugging
pytest --pdb -x            # Stop on first failure
pytest --lf                # Run last failed tests
```

#### Test Coverage Analysis

```bash
# Coverage report
pytest --cov=src/flext_api --cov-report=html --cov-report=term-missing

# Coverage by module
pytest --cov=src/flext_api --cov-report=term-missing:skip-covered

# Target coverage enforcement
pytest --cov=src/flext_api --cov-fail-under=75
```

### CI/CD Testing Integration

#### Quality Gates

```bash
# Phase 1 quality gates (current status)
make lint                    # ✅ PASSING
make type-check             # ❌ 295 ERRORS (CRITICAL)
make security               # ✅ PASSING
make test                   # ❌ 28% PASS RATE (CRITICAL)

# Target quality gates (Phase 1 completion)
make validate               # All gates passing
pytest --cov-fail-under=75  # 75%+ coverage
```

## Performance & Load Testing

### HTTP Performance Benchmarks

#### Response Time Testing

```python
def test_response_time_performance(http_client):
    """Test response time requirements."""
    import time
    import statistics

    response_times = []

    # Measure 10 requests
    for _ in range(10):
        start_time = time.time()
        result = http_client.get("/get")
        end_time = time.time()

        if result.is_success:
            response_times.append((end_time - start_time) * 1000)  # ms

    # Performance assertions
    avg_time = statistics.mean(response_times)
    max_time = max(response_times)

    assert avg_time < 500, f"Average response time too slow: {avg_time}ms"
    assert max_time < 2000, f"Max response time too slow: {max_time}ms"
```

#### Concurrent Request Testing

```python
import asyncio

async def test_concurrent_requests(http_client):
    """Test concurrent request handling."""
    async def make_request(i):
        return await http_client.get(f"/get?request_id={i}")

    # Make 50 concurrent requests
    tasks = [make_request(i) for i in range(50)]
    results = await asyncio.gather(*tasks)

    successful = [r for r in results if r.is_success]
    success_rate = len(successful) / len(results)

    assert success_rate > 0.95, f"Success rate too low: {success_rate}"
```

## Test Maintenance & Evolution

### Test Organization Principles

#### Test File Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_client.py      # HTTP client tests
│   ├── test_models.py      # Model validation tests
│   ├── test_config.py      # Configuration tests
│   └── test_storage.py     # Storage abstraction tests
├── integration/            # Integration tests
│   ├── test_http_operations.py
│   └── test_fastapi_app.py
├── e2e/                    # End-to-end tests
│   └── test_http_workflows.py
├── conftest.py            # Shared fixtures
└── test_utils.py          # Test utilities
```

#### Test Naming Conventions

```python
# Unit tests
def test_successful_operation():
def test_error_handling():
def test_validation_scenarios():
def test_edge_cases():

# Integration tests
def test_real_http_integration():
def test_end_to_end_workflow():
def test_system_interaction():
```

### Test Data Management

#### Test Data Patterns

```python
# Test data constants
TEST_BASE_URL = "https://httpbin.org"
TEST_TIMEOUT = 5.0

# Test data factories
def create_test_user_data(**overrides):
    """Create test user data with defaults."""
    base = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30
    }
    base.update(overrides)
    return base

# Parameterized test data
VALID_HTTP_METHODS = ["GET", "POST", "PUT", "DELETE"]
INVALID_URLS = ["", "not-a-url", "ftp://invalid"]
HTTP_STATUS_CODES = [200, 201, 400, 401, 404, 500]
```

## Testing Roadmap

### Phase 1: Foundation (Current - 28% → 75%)

**Timeline**: October - November 2025

1. **Week 1-2**: Fix critical test failures
   - Implement missing methods
   - Fix type safety issues
   - Resolve import errors

2. **Week 3-4**: Improve unit test coverage
   - Add comprehensive model tests
   - Implement configuration tests
   - Add storage abstraction tests

3. **Week 5-6**: Integration testing
   - Real HTTP server tests
   - FastAPI application tests
   - Error handling validation

### Phase 2: Advanced Testing (Future)

**Timeline**: December 2025 - January 2026

1. **Performance Testing**: Load and stress testing
2. **Security Testing**: Authentication and authorization
3. **End-to-End Testing**: Complete workflow validation
4. **Cross-Platform Testing**: Multiple environments

## Success Metrics

### Quantitative Metrics

- **Test Pass Rate**: 95%+ (current: 23%)
- **Coverage**: 75%+ (current: 28%)
- **Performance**: <500ms average response time
- **Reliability**: 99%+ success rate under normal conditions

### Qualitative Metrics

- **Test Quality**: Tests validate real functionality, not mocks
- **Error Coverage**: All error paths tested
- **Maintainability**: Tests easy to understand and modify
- **Documentation**: Test scenarios well-documented

## Risk Mitigation

### Test Reliability Risks

1. **Flaky Tests**: Implement retry logic for network-dependent tests
2. **Environment Dependencies**: Use Docker for consistent test environments
3. **External Service Dependencies**: Mock external services where possible

### Coverage Gaps

1. **Error Path Coverage**: Explicit testing of error conditions
2. **Edge Case Coverage**: Boundary value and edge case testing
3. **Integration Coverage**: Real system interaction testing

### Maintenance Overhead

1. **Test Data Management**: Centralized test data factories
2. **Fixture Optimization**: Shared fixtures to reduce duplication
3. **Test Organization**: Clear test categorization and naming

---

**Current Status**: 23/99 tests passing (28% pass rate)
**Critical Issues**: 4 major failure categories blocking progress
**Target**: 75%+ coverage with real HTTP functionality by Phase 1 completion
**Next Priority**: Implement missing methods and fix type safety issues
