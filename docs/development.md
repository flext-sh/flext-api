# Development Guide - flext-api

**Development Workflow and Contribution Guidelines**

**Version**: 0.9.9 RC | **Updated**: September 17, 2025

This guide covers the complete development workflow for contributing to flext-api, including setup, testing, quality gates, and contribution standards based on the actual implementation.

---

## 🚀 Quick Development Setup

### **Prerequisites**

- **Python 3.13+**: Required for advanced type features
- **Poetry**: Dependency management and virtual environment
- **Git**: Version control and contribution workflow
- **Make**: Build automation (optional but recommended)

### **Setup Steps**

```bash
# 1. Clone the repository (if not already in FLEXT workspace)
git clone https://github.com/flext-sh/flext-api.git
cd flext-api

# 2. Install dependencies with development tools
poetry install --with dev,test,typings,security

# 3. Set up pre-commit hooks (optional)
poetry run pre-commit install

# 4. Verify installation
make validate
```

---

## 🔧 Development Environment

### **Essential Commands**

| Command           | Purpose            | Description                            |
| ----------------- | ------------------ | -------------------------------------- |
| `make setup`      | Initial setup      | Complete development environment setup |
| `make dev`        | Development server | Start FastAPI development server       |
| `make test`       | Run tests          | Execute complete test suite            |
| `make lint`       | Code linting       | Run Ruff linting checks                |
| `make type-check` | Type checking      | Run MyPy type validation               |
| `make format`     | Code formatting    | Auto-format with Black and isort       |
| `make security`   | Security scan      | Run Bandit security analysis           |
| `make validate`   | Quality gates      | Complete validation pipeline           |
| `make clean`      | Cleanup            | Remove build artifacts                 |

### **Development Server**

```bash
# Start development server with auto-reload
make dev

# Or manually with uvicorn
poetry run uvicorn flext_api.app:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

### **Code Quality Tools**

```bash
# Linting with Ruff
make lint
# Or: poetry run ruff check src/ tests/

# Type checking with MyPy
make type-check
# Or: poetry run mypy src/

# Code formatting
make format
# Or: poetry run black src/ tests/ && poetry run isort src/ tests/

# Security scanning
make security
# Or: poetry run bandit -r src/
```

---

## 🧪 Testing Strategy

### **Test Structure**

```
tests/
├── unit/                    # Unit tests for individual modules
│   ├── test_client.py       # HTTP client tests
│   ├── test_models.py       # Data model tests
│   ├── test_config.py       # Configuration tests
│   └── test_utilities.py    # Utility function tests
├── integration/             # Integration tests with real HTTP
│   ├── test_http_server.py  # FastAPI server integration
│   ├── test_client_auth.py  # Authentication integration
│   └── test_storage.py      # Storage backend tests
├── e2e/                     # End-to-end workflow tests
│   └── test_api_workflows.py
└── conftest.py              # Test configuration and fixtures
```

### **Running Tests**

```bash
# Run all tests
make test

# Run specific test categories
pytest -m unit               # Unit tests only
pytest -m integration        # Integration tests only
pytest -m e2e                # End-to-end tests only

# Run with coverage
pytest --cov=src/flext_api --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py -v

# Run with debugging
pytest tests/unit/test_client.py::test_http_request -v -s
```

### **Test Coverage Goals**

- **Current Coverage**: 73% (target: 95%+)
- **Test Pass Rate**: 78% (261/334 tests passing)
- **Priority Modules**: client.py, models.py, app.py
- **Coverage Target**: 100% for critical HTTP operations

### **Writing Tests**

```python
import pytest
import asyncio
from flext_api import FlextApiClient, FlextApiModels
from flext_core import FlextResult

class TestFlextApiClient:
    """Test HTTP client functionality."""

    @pytest.mark.asyncio
    async def test_basic_http_request(self):
        """Test basic HTTP request functionality."""

        client = FlextApiClient(base_url="https://httpbin.org")

        request = FlextApiModels.HttpRequest(
            method="GET",
            url="/get",
            headers={"Accept": "application/json"}
        )

        try:
            result = await client.request(request)

            assert result.is_success, f"Request failed: {result.error}"

            response = result.unwrap()
            assert response.status_code == 200
            assert isinstance(response.body, (dict, str))

        finally:
            await client.close()

    def test_http_request_model_validation(self):
        """Test HTTP request model validation."""

        # Valid request
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="/test",
            headers={"User-Agent": "test"}
        )
        assert request.method == "GET"
        assert request.url == "/test"

        # Invalid method should raise validation error
        with pytest.raises(ValueError):
            FlextApiModels.HttpRequest(
                method="INVALID",
                url="/test"
            )
```

---

## 🏗️ Architecture Guidelines

### **FLEXT Integration Requirements**

All code MUST follow FLEXT ecosystem patterns:

```python
# ✅ CORRECT: Use FlextResult for error handling
from flext_core import FlextResult, FlextService

class MyHttpService(FlextService):
    async def process_request(self, data: dict) -> FlextResult[dict]:
        if not data:
            return FlextResult[dict].fail("Data cannot be empty")

        # Process data...
        return FlextResult[dict].ok(processed_data)

# ❌ INCORRECT: Don't use try/except fallbacks
def bad_function(data):
    try:
        return process_data(data)
    except Exception:
        return None  # NEVER do this
```

### **Code Organization**

```python
# ✅ CORRECT: Single unified class per module
class FlextApiClient(FlextService):
    """Single responsibility class with nested helpers."""

    class _RequestHelper:
        """Nested helper class - no loose functions."""
        @staticmethod
        def validate_request(request: HttpRequest) -> FlextResult[None]:
            pass

    def __init__(self, **kwargs):
        super().__init__()
        self._logger = FlextLogger(__name__)

    async def request(self, request: HttpRequest) -> FlextResult[HttpResponse]:
        # Use nested helper
        validation_result = self._RequestHelper.validate_request(request)
        if validation_result.is_failure:
            return FlextResult[HttpResponse].fail(validation_result.error)

        # Main logic here
        pass

# ❌ INCORRECT: Multiple classes or loose functions
class HttpClient:  # Don't split into multiple classes
    pass

class RequestHelper:  # Don't create separate helper classes
    pass

def validate_request():  # Don't create loose functions
    pass
```

### **Import Standards**

```python
# ✅ CORRECT: Root-level imports only
from flext_core import FlextResult, FlextLogger, FlextService
from flext_api.models import FlextApiModels
from flext_api.config import FlextApiConfig

# ❌ INCORRECT: Internal imports
from flext_core.result import FlextResult  # Don't use internal imports
from flext_api.models.http import HttpRequest  # Don't access internal modules
```

---

## 🔍 Code Review Guidelines

### **Pre-Submission Checklist**

Before submitting code:

- [ ] All tests pass (`make test`)
- [ ] Code passes linting (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Security scan passes (`make security`)
- [ ] Code coverage maintained or improved
- [ ] Documentation updated for new features
- [ ] FLEXT patterns followed consistently

### **Code Review Standards**

**Must Have**:

- FlextResult error handling for all operations
- Proper type annotations with Python 3.13+ features
- Single unified class per module
- Comprehensive test coverage
- Clear, descriptive docstrings

**Must Not Have**:

- Try/except fallback mechanisms
- Multiple classes per module
- Loose helper functions outside classes
- Direct imports from internal modules
- Hardcoded configuration values

### **Review Process**

1. **Automated Checks**: All quality gates must pass
2. **Architecture Review**: Verify FLEXT pattern compliance
3. **Security Review**: Check for security vulnerabilities
4. **Performance Review**: Ensure efficient HTTP operations
5. **Documentation Review**: Verify documentation accuracy

---

## 🚀 Release Process

### **Version Management**

flext-api follows semantic versioning:

- **Major (1.0.0)**: Breaking changes
- **Minor (0.9.9)**: New features, backward compatible
- **Patch (0.9.1)**: Bug fixes, no new features

### **Release Checklist**

- [ ] All tests pass with 100% success rate
- [ ] Documentation updated and accurate
- [ ] CHANGELOG.md updated with changes
- [ ] Version numbers updated in:
  - `pyproject.toml`
  - `src/flext_api/__version__.py`
  - Documentation files
- [ ] Security scan passes
- [ ] Performance benchmarks maintained
- [ ] Integration tests with FLEXT ecosystem pass

### **Release Commands**

```bash
# 1. Update version
poetry version minor  # or major/patch

# 2. Run complete validation
make validate

# 3. Update documentation
# Update README.md, docs/, and CHANGELOG.md

# 4. Commit and tag
git add .
git commit -m "Release v0.9.9"
git tag v0.9.9

# 5. Push release
git push origin main --tags
```

---

## 🐛 Debugging and Troubleshooting

### **Common Development Issues**

#### **Import Errors**

```python
# Problem: ModuleNotFoundError
# Solution: Install in development mode
poetry install --with dev

# Problem: Circular imports
# Solution: Use TYPE_CHECKING pattern
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from flext_api.models import HttpRequest
```

#### **Test Failures**

```bash
# Problem: Field name mismatches in tests
# Current issue: Tests expect .page but model has current_page with alias

# Debug specific test
pytest tests/unit/test_models.py::test_pagination -v -s

# Check model definition
python -c "from flext_api.models import FlextApiModels; print(FlextApiModels.PaginationConfig.model_fields)"
```

#### **Type Checking Issues**

```bash
# Problem: MyPy errors
# Run with verbose output
poetry run mypy src/ --show-error-codes --no-error-summary

# Problem: Missing stubs
# Install type stubs
poetry add --group typings types-requests
```

### **Development Tools**

#### **Interactive Development**

```python
# Use IPython for interactive development
poetry run ipython

# Test HTTP client interactively
from flext_api import FlextApiClient
client = FlextApiClient(base_url="https://httpbin.org")

# Use async in IPython
import asyncio
result = await client.get("/json")
print(result.unwrap().body if result.is_success else result.error)
```

#### **Debugging HTTP Requests**

```python
# Enable HTTP logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use httpx logging
import httpx
httpx.logger.setLevel(logging.DEBUG)

# Debug specific request
from flext_api import FlextApiClient
client = FlextApiClient(base_url="https://httpbin.org")
result = await client.get("/get")
```

### **Performance Profiling**

```bash
# Profile test execution
poetry run pytest tests/ --profile

# Memory profiling
poetry run python -m memory_profiler scripts/profile_client.py

# HTTP performance testing
poetry run python -m pytest tests/performance/ -v
```

---

## 📚 Contributing Guidelines

### **Getting Started with Contributions**

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** following coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### **Commit Message Standards**

```bash
# Good commit messages
git commit -m "feat: add retry logic to HTTP client"
git commit -m "fix: resolve field name mismatch in pagination model"
git commit -m "docs: update API reference with new methods"
git commit -m "test: add integration tests for authentication"

# Commit types: feat, fix, docs, test, refactor, perf, chore
```

### **Pull Request Process**

1. **Quality Gates**: All automated checks must pass
2. **Review**: Code review from maintainers
3. **Testing**: Integration tests with FLEXT ecosystem
4. **Documentation**: Updated documentation if needed
5. **Merge**: Squash merge to main branch

### **Community Guidelines**

- **Be respectful** in all interactions
- **Follow coding standards** consistently
- **Write clear documentation** for new features
- **Provide comprehensive tests** for changes
- **Respond to feedback** constructively

---

## 🎯 Development Roadmap

### **Current Development Focus (v0.9.9)**

1. **Fix Test Suite**: Resolve 59 failing tests
2. **Improve Coverage**: Increase from 73% to 95%+
3. **Field Alignment**: Fix model/test field name mismatches
4. **HTTP Methods**: Ensure consistent HttpMethods enum usage

### **Next Version (v1.0.0) - Production Features**

1. **Retry Logic**: Implement actual retry functionality
2. **Connection Pooling**: Optimize httpx client configuration
3. **Plugin System**: Implement authentication and logging plugins
4. **Circuit Breaker**: Add fault tolerance patterns
5. **HTTP/2 Support**: Enable HTTP/2 by default
6. **Performance Optimization**: Connection pool tuning

### **Future Versions (v1.1.0+)**

1. **Advanced Authentication**: OAuth, JWT, session handling
2. **Streaming Responses**: Large response handling
3. **Metrics Integration**: Advanced monitoring and tracing
4. **Load Balancing**: Client-side load balancing
5. **Advanced Security**: Rate limiting, security headers

---

## 🆘 Getting Help

### **Development Support**

- **Documentation**: [docs/](.) - Complete development guides
- **Issues**: [GitHub Issues](https://github.com/flext-sh/flext-api/issues) - Report bugs or request features
- **Discussions**: GitHub Discussions - Ask questions or share ideas
- **FLEXT Workspace**: Integration with broader FLEXT ecosystem

### **Quick Reference Links**

- [Getting Started](getting-started.md) - Installation and basic usage
- [Architecture](architecture.md) - Design patterns and structure
- [API Reference](api-reference.md) - Complete API documentation
- [Configuration](configuration.md) - Settings and environment management

---

**Development Summary**: flext-api follows strict quality standards with comprehensive testing, type safety, and FLEXT ecosystem integration. All contributions must maintain these standards while advancing the HTTP foundation for the entire FLEXT platform.
