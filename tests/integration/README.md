# Integration Tests

**Tests with real external services and dependencies**

## Test Files

### HTTP Client Integration
- **test_http_client_integration.py** - HTTP client with real services
  - External API connectivity
  - Network request/response validation
  - Timeout and retry behavior
  - Error handling with real services

## Test Scope

### External Dependencies
- HTTP services (httpbin.org for testing)
- Database connections (when available)
- Cache services (Redis)
- Authentication services

### Test Scenarios
- Successful HTTP requests with various methods
- Network timeout handling
- Service unavailability response
- Authentication flow testing

## Running Tests

```bash
# All integration tests
make test-integration

# With specific markers
pytest tests/integration/ -m integration -v

# With timeout protection
pytest tests/integration/ --timeout=30 -v

# Specific test file
pytest tests/integration/test_http_client_integration.py -v
```

## Environment Requirements

- Internet connectivity for external service testing
- Access to test endpoints (httpbin.org)
- Service dependencies (PostgreSQL, Redis if testing)

## Test Characteristics

- Execution time: 5-30 seconds per test
- External dependencies: Real services and networks
- Test isolation: Limited (shares external resources)
- Reliability: Dependent on external service availability

## Development

See parent directory documentation for test patterns, debugging guidelines, and best practices for integration testing.
