# flext-api - HTTP Foundation Library

**Type**: Library | **Status**: Development | **Dependencies**: flext-core

HTTP client and FastAPI integration library for the FLEXT ecosystem.

> **⚠️ Development Status**: Basic HTTP functionality working, flext-core integration partial (35%)

## Quick Start

```bash
# Install dependencies
poetry install

# Run basic HTTP client
python -c "from flext_api import FlextApi; api = FlextApi(); print('✅ Working')"

# Start FastAPI dev server
poetry run uvicorn flext_api.main:app --reload
```

## Current Reality

**What Actually Works:**

- Basic HTTP client (`flext_api.client`)
- Query builders (`flext_api.builder`)
- FastAPI app (`flext_api.main`)
- Configuration system (`flext_api.config`)

**What Needs Work:**

- FlextResult integration (35% complete)
- Plugin architecture (exists but needs flext-core integration)
- Error handling standardization

## Integration

- **flext-core**: Foundation patterns, FlextResult error handling
- **FLEXT ecosystem**: HTTP communication layer

## Documentation

- [Complete Documentation](../docs/projects/flext-api/)
- [Main FLEXT Documentation](../docs/)
