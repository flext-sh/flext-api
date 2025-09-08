# Unit Tests

**Fast isolated tests with mocks for FLEXT API components**

## Test Files

### Core Component Tests

- **test_api_core.py** - FlextApi service functionality
- **test_app_core.py** - FastAPI application factory
- **test_builder_core.py** - Query/response builders
- **test_client_core.py** - HTTP client operations
- **test_config_comprehensive.py** - Configuration management
- **test_constants_core.py** - Project constants
- **test_exceptions_comprehensive.py** - Exception handling
- **test_fields_core.py** - Field definitions
- **test_main_core.py** - Application entry point
- **test_storage_core.py** - Storage implementation
- **test_types_core.py** - Type definitions

### Coverage Tests

- **test\_\*\_coverage.py** - Coverage validation tests
- **test_missing_coverage.py** - Uncovered code paths
- **test_init_coverage.py** - Module initialization tests
- **test_version.py** - Version information

### Disabled Tests

- **test\_\*.py.disabled** - Tests requiring fixes

## Running Tests

```bash
# All unit tests
make test-unit

# Without coverage (fastest)
make test-unit-fast

# Specific files
pytest tests/unit/test_api_core.py -v
pytest tests/unit/test_client_core.py -v

# By markers
pytest tests/unit/ -m "not slow" -v
pytest tests/unit/ -k "api" -v
```

## Test Standards

- Fast execution (<100ms per test)
- Isolated with proper mocking
- Clear naming conventions
- Comprehensive assertions
- AAA pattern (Arrange, Act, Assert)

## Development

See parent directory documentation for detailed testing patterns, fixture usage, and debugging guidelines.
