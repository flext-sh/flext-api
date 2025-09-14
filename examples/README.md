# FLEXT API Examples

**Usage examples demonstrating REAL classes and functionality**

## Example Files (REAL Classes Only)

### Basic Usage

- **01_basic_usage.py** - Basic API usage patterns using REAL classes
  - FlextApiClient creation and configuration
  - HTTP client creation and setup
  - Model instantiation and validation
  - Error handling with FlextResult

### Advanced Features

- **02_advanced.py** - Advanced usage patterns using REAL classes
  - Plugin system demonstration
  - Storage backends usage
  - Query builder with filters
  - Response builder patterns
  - Model validation examples
  - Async patterns with HTTP client

## Key Patterns Demonstrated

### REAL Classes Usage

- **FlextApiClient** - Core API service class
- **FlextApiClient** - HTTP client with async support
- **FlextApiModels** - Domain models and data structures
- **FlextApiStorage** - Storage backends (Memory, File)
- **FlextApiPlugins** - Extensible plugin system
- **create_flext_api()** - Factory function
- **create_flext_api_app()** - FastAPI application factory

### No Aliases or Helpers

All examples use REAL classes directly from their modules:

```python
from flext_api import FlextApiClient, FlextApiClient, FlextApiModels
# NOT helpers, NOT aliases, ONLY real functionality
```

## Running Examples

```bash
# Run basic usage example
python examples/01_basic_usage.py

# Run advanced features example
python examples/02_advanced.py

# Run from project root
cd /home/marlonsc/flext/flext-api
PYTHONPATH=src python examples/01_basic_usage.py
PYTHONPATH=src python examples/02_advanced.py
```

## Example Patterns

### FlextResult Usage (REAL Pattern)

```python
# Always check success/failure using REAL FlextResult methods
result = api_operation()
if result.success:
    data = result.data
    logger.info("Operation successful", data=data)
else:
    logger.error("Operation failed", error=result.error)
    return result  # Return the failure result
```

### REAL Classes Import Pattern

```python
# CORRECT: Import REAL classes directly
from flext_api import FlextApiClient, FlextApiClient, FlextApiModels

# INCORRECT: Don't use aliases or helpers
# from flext_api import create_client  # This is a helper, not a REAL class
```

### Error Handling with REAL Classes

```python
# Create API using REAL class
api = FlextApiClient()

# Create client using REAL method that returns FlextResult
client_result = api.create_client({"base_url": "https://api.example.com"})

if client_result.success:
    client = client_result.data
    # Use REAL client instance
else:
    print(f"Failed: {client_result.error}")
```

### Model Validation using REAL Classes

```python
# Use REAL nested model classes
request = FlextApiModels.ApiRequest(
    method=FlextApiModels.HttpMethod.GET,
    url="https://api.example.com/data"
)

# Use REAL nested storage classes
storage = FlextApiStorage.MemoryBackend()
result = storage.set("key", {"data": "value"})
```

## Development Guidelines

- **Use ONLY REAL classes** - No helpers, no aliases, no compatibility layers
- **Import from root level** - Always `from flext_api import ClassName`
- **Check FlextResult patterns** - Always handle `.success` and `.error`
- **Use REAL nested classes** - Access via `ParentClass.NestedClass`
- **Test examples regularly** - Ensure they work with actual implementation
- **No placeholder code** - All examples must use working functionality

See project documentation for complete API reference and architectural patterns.
