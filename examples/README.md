# Examples

**Usage examples and demonstrations for FLEXT API library**

## Example Files

### Basic Usage

- **01_basic_usage.py** - Basic API usage patterns
- **01_basic_usage_corrected.py** - Corrected version with fixes

### Advanced Features

- **02_advanced_features.py** - Advanced features demonstration

## Coverage

### Basic Usage Examples

- FlextApi service creation and initialization
- HTTP client configuration
- Query building patterns
- Error handling demonstration

### Advanced Examples

- Plugin architecture usage
- Advanced HTTP client features
- Complex query building
- Integration patterns

## Running Examples

```bash
# Run basic usage example
python examples/01_basic_usage_corrected.py

# Run advanced features example
python examples/02_advanced_features.py

# Run all examples
python -m examples
```

## Development Testing

```bash
# Test examples against current implementation
pytest tests/unit/test_functional_examples.py

# Validate example accuracy
make test-examples

# Check example compliance
make validate-examples
```

## Example Patterns

### FlextResult Usage

```python
# Always check success/failure
result = api_operation()
if result.is_failure:
    logger.error("Operation failed", error=result.error)
    return

# Use the data
data = result.data
```

### Structured Logging

```python
from flext_core import get_logger

logger = get_logger(__name__)
logger.info("Operation completed", count=len(results))
```

## Development Guidelines

- Test examples against actual code
- Use only implemented features
- Handle all failure cases with FlextResult
- Include comprehensive error handling
- Use structured logging patterns
- Provide context and comments

See project documentation for development patterns, testing procedures, and API usage guidelines.
