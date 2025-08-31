# FLEXT API Tests - REAL Classes Only

**Reorganized test structure using ONLY REAL classes**

## Test Organization

### Unit Tests Structure: `tests/unit/test_[módulo].py`

Each module has its own dedicated test file testing only REAL functionality:

- **test_api.py** - Tests FlextApi REAL class
- **test_app.py** - Tests FlextApiApp REAL class  
- **test_client.py** - Tests FlextApiClient REAL class
- **test_config.py** - Tests FlextApiConfig REAL class
- **test_constants.py** - Tests FlextApiConstants REAL class
- **test_errors.py** - Tests FlextErrors REAL class
- **test_models.py** - Tests FlextApiModels REAL class and nested classes
- **test_plugins.py** - Tests FlextApiPlugins REAL class
- **test_storage.py** - Tests FlextApiStorage REAL class
- **test_types.py** - Tests FlextApiTypes REAL class
- **test_utils.py** - Tests FlextUtils REAL class

## Key Testing Principles

### REAL Classes Only
- **No helpers** - Only test actual functionality
- **No aliases** - Import REAL classes directly
- **No compatibility layers** - Test actual implementation
- **Direct imports**: `from flext_api import FlextApi, FlextApiClient, ...`

### FlextResult Pattern Testing
- All operations that return FlextResult are tested for both success and failure paths
- Error handling validation with proper FlextResult.success/error checking
- Type-safe result data validation

### Test Examples

```python
from flext_api import FlextApi, FlextApiClient

def test_real_functionality():
    """Test using only REAL classes."""
    # Create API using REAL class
    api = FlextApi()
    
    # Test REAL method that returns FlextResult
    result = api.create_client({"base_url": "https://httpbin.org"})
    
    # Test REAL FlextResult pattern
    assert result.success
    assert result.data is not None
    
    # Get REAL client instance
    client = result.data
    assert isinstance(client, FlextApiClient)
```

## Running Tests

### Run Module-Specific Tests
```bash
# Test specific module
PYTHONPATH=src python -m pytest tests_new/unit/test_api.py -v
PYTHONPATH=src python -m pytest tests_new/unit/test_client.py -v
PYTHONPATH=src python -m pytest tests_new/unit/test_storage.py -v

# Run all unit tests
PYTHONPATH=src python -m pytest tests_new/unit/ -v

# Run with coverage
PYTHONPATH=src python -m pytest tests_new/unit/ --cov=src --cov-report=term-missing
```

### Test Markers Available
```bash
# Run by marker
python -m pytest -m unit -v           # All unit tests
python -m pytest -m real_classes -v   # All tests using REAL classes  
python -m pytest -m api -v            # API-related tests
python -m pytest -m client -v         # Client-related tests
python -m pytest -m storage -v        # Storage-related tests
```

## Test Structure Benefits

### Organized by Module
- Each src/flext_api/[module].py has corresponding tests/unit/test_[module].py
- Clear mapping between implementation and tests
- Easy to locate and maintain tests

### REAL Functionality Focus
- Tests validate actual working code, not compatibility layers
- Direct testing of FlextResult patterns and error handling
- Validates integration with flext-core base classes

### Comprehensive Coverage
- Each REAL class is thoroughly tested
- Both success and failure paths validated
- Type safety and validation testing
- Async functionality testing where applicable

## Migration from Old Structure

This reorganized structure replaces the complex nested directory structure with:
- **Simple flat structure** - One test file per module
- **Clear naming** - test_[module].py matches src/flext_api/[module].py  
- **REAL classes only** - No testing of helpers, aliases, or compatibility layers
- **Focused testing** - Each file tests only its corresponding module

The reorganized tests provide better maintainability, clearer organization, and focus on testing the actual REAL functionality that users will use.