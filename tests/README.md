# Test Suite

**Test organization for FLEXT API library**

## Directory Structure

```
tests/
├── conftest.py                     # Shared test configuration
├── fixtures/                       # Test data and fixtures
├── test_helpers/                   # Test utilities
├── unit/                           # Unit tests with mocks
├── integration/                    # Integration tests with real services
├── e2e/                           # End-to-end workflow tests
└── benchmarks/                    # Performance benchmarks
```

## Test Categories

### Unit Tests (unit/)

Fast isolated tests with mocks for core functionality:

- API service classes
- HTTP client operations
- Query/response builders
- Configuration management
- Exception handling

### Integration Tests (integration/)

Tests with real external services:

- HTTP client with live endpoints
- Database connections
- Cache integration

### End-to-End Tests (e2e/)

Complete workflow validation:

- Full API request/response cycles
- Multi-component integration
- Real-world usage scenarios

### Performance Tests (benchmarks/)

Performance and scalability validation:

- Execution time benchmarks
- Memory usage profiling
- Load testing scenarios

## Running Tests

```bash
# All tests
make test

# By category
make test-unit          # Unit tests only
make test-integration   # Integration tests
make test-e2e          # End-to-end tests

# With markers
pytest -m "not slow"    # Exclude slow tests
pytest -m api          # API tests only
pytest -m client       # Client tests only
```

## Coverage

```bash
make coverage-html     # HTML coverage report
make coverage-xml      # XML coverage for CI
```

## Development

See project documentation for testing patterns, fixture usage, and development guidelines.
