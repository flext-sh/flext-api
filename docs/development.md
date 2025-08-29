# Development Guide

**Development workflow and contribution guidelines for FLEXT API**

> **Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [flext-api](../README.md) > Development

---

## 🎯 Development Overview

FLEXT API follows **Clean Architecture** principles with **Domain-Driven Design (DDD)** patterns, emphasizing **FLEXT-Core compliance** and **enterprise-grade quality standards**. All development must align with the broader FLEXT ecosystem patterns.

### **Development Philosophy**

1. **Quality First** - Zero tolerance for lint/type/test failures
2. **FLEXT-Core Compliance** - Railway-oriented programming with FlextResult[T]
3. **Test-Driven Development** - 90% minimum test coverage requirement
4. **Documentation-Driven** - All public APIs must be documented
5. **Ecosystem Integration** - Seamless integration with all 33 FLEXT projects

---

## 🚀 Quick Development Setup

### **Prerequisites**

```bash
# Required tools
- Python 3.13+
- Poetry 1.8+
- Make
- Git
- Docker (for integration tests)

# Verify installations
python --version    # Should show 3.13+
poetry --version    # Should show 1.8+
make --version      # object recent version
```

### **Initial Setup**

```bash
# Clone FLEXT ecosystem workspace
git clone https://github.com/flext-sh/flext.git
cd flext/flext-api

# Complete development setup
make setup          # Install tools, dependencies, pre-commit hooks
make dev           # Start development server

# Verify setup
make check         # Should pass all quality gates
curl http://localhost:8000/health  # Should return {"status": "healthy"}
```

---

## 🔧 Development Commands

### **Essential Quality Gates (Mandatory)**

```bash
# Pre-commit validation (must pass before commits)
make validate       # Complete validation pipeline (lint + type + security + test)
make check          # Quick validation (lint + type check)
make test           # Run all tests with 90% coverage requirement
make security-scan  # Security vulnerability analysis

# Individual quality checks
make lint           # Ruff linting (zero errors tolerance)
make type-check     # MyPy strict mode type checking
make format         # Auto-format code with ruff
make test-unit      # Fast unit tests with mocks
```

### **Development Server**

```bash
# Development server options
make dev            # FastAPI on localhost:8000 (recommended)
make dev-reload     # Aggressive reload mode for rapid development
make serve          # Alias for dev

# Health and status checks
curl http://localhost:8000/health       # Basic health check
curl http://localhost:8000/docs         # Interactive API documentation
curl http://localhost:8000/redoc        # Alternative API documentation
```

### **Testing Commands**

```bash
# Test execution
make test                    # All tests with coverage reporting
make test-unit              # Unit tests with parallel execution
make test-integration       # Integration tests with external services
make test-e2e              # End-to-end workflow validation
make test-benchmark        # Performance benchmarks

# Test categories and markers
pytest -m unit -v           # Unit tests only
pytest -m integration -v   # Integration tests only
pytest -m "not slow" -v    # Fast tests for quick feedback
pytest -m benchmark -v     # Performance tests

# Advanced testing
make test-watch            # Continuous testing (if available)
pytest --lf -v            # Re-run last failed tests
pytest --co               # Show test collection
make coverage-html         # Generate HTML coverage report
```

### **Build and Maintenance**

```bash
# Build operations
make build          # Build distribution packages
make clean          # Clean build artifacts and cache
make clean-all      # Deep clean including virtual environment
make reset          # Reset project to clean state

# Dependency management
make install        # Install project dependencies
make install-dev    # Install development dependencies
make deps-update    # Update all dependencies
make deps-audit     # Security audit of dependencies
```

---

## 🏗️ Architecture and Patterns

### **FLEXT-Core Compliance Requirements**

**Current Status: 35% → Target: 95%**

#### **Mandatory Patterns**

1. **FlextResult[T] Pattern** (Currently 70% compliant)

   ```python
   from flext_core import FlextResult, FlextLogger

   logger = FlextLogger(__name__)

   def service_operation() -> FlextResult[DataType]:
       try:
           result = perform_operation()
           return FlextResult[None].ok(result)
       except Exception as e:
           logger.exception("Operation failed", operation="service_operation")
           return FlextResult[None].fail(f"Operation failed: {e}")
   ```

2. **Structured Logging** (Currently 25% compliant)

   ```python
   from flext_core import FlextLogger

   # ✅ Correct pattern
   logger = FlextLogger(__name__)
   logger.info("Operation completed", user_id=123, operation="create_client")

   # ❌ Avoid - structlog direct usage
   import structlog  # Use FlextLogger() instead
   ```

3. **Dependency Injection** (Currently 40% compliant)

   ```python
   from flext_core import get_flext_container

   # ✅ Use global container
   container = FlextContainer.get_global()
   service = container.get(SomeService)

   # ❌ Avoid - local containers
   local_container = SomeLocalContainer()  # Use global instead
   ```

### **Clean Architecture Boundaries**

```
src/flext_api/
├── api.py              # Application Layer - FlextApi service composition
├── client.py           # Application Layer - HTTP client operations
├── builder.py          # Application Layer - Query/response building
├── config.py           # Infrastructure Layer - Configuration management
├── constants.py        # Domain Layer - Domain constants and enums
├── exceptions.py       # Domain Layer - Business exceptions
├── fields.py           # Domain Layer - Domain field definitions
└── main.py            # Interface Layer - FastAPI application entry
```

### **Domain-Driven Design Implementation**

**Current Gap: Domain entities and value objects are minimal (10% compliance)**

```python
# Required domain entity pattern
from flext_core import FlextModels.Entity
from pydantic import Field
from typing import Optional

class HttpRequest(FlextModels.Entity):
    """Domain entity representing an HTTP request."""

    method: str = Field(..., description="HTTP method")
    url: str = Field(..., description="Request URL")
    headers: dict = Field(default_factory=dict, description="Request headers")
    body: Optional[str] = Field(default=None, description="Request body")

    def is_valid(self) -> bool:
        """Business rule validation."""
        return self.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]
```

---

## 📋 Development Workflow

### **Git Workflow**

```bash
# Feature development workflow
git checkout main
git pull origin main
git checkout -b feature/enhance-plugin-system

# Make changes following patterns
# ... implement feature ...

# Quality validation before commit
make validate       # Must pass completely

# Commit with conventional commits
git add .
git commit -m "feat: enhance plugin system with circuit breaker support

- Add FlextApiCircuitBreakerPlugin with configurable thresholds
- Implement failure tracking with exponential backoff
- Add comprehensive tests for failure scenarios
- Update documentation with usage examples

Resolves: #123"

# Push and create pull request
git push origin feature/enhance-plugin-system
```

### **Code Review Checklist**

#### **FLEXT-Core Compliance**

- [ ] All operations return `FlextResult[T]`
- [ ] Uses `FlextLogger(__name__)` for logging
- [ ] Uses global dependency injection container
- [ ] Follows Clean Architecture boundaries
- [ ] Domain entities implement business rules

#### **Quality Standards**

- [ ] 90%+ test coverage with meaningful tests
- [ ] Zero lint errors (ruff)
- [ ] Zero type errors (mypy strict mode)
- [ ] All public APIs documented
- [ ] Security scan passes (bandit, pip-audit)

#### **Integration Requirements**

- [ ] Integrates properly with flext-core patterns
- [ ] Compatible with existing ecosystem projects
- [ ] Plugin system properly implemented
- [ ] Configuration follows ecosystem standards

### **Pull Request Template**

```markdown
## Description

Brief description of changes and their purpose.

## FLEXT-Core Compliance

- [ ] FlextResult pattern implemented
- [ ] Structured logging with FlextLogger()
- [ ] Global dependency injection used
- [ ] Clean Architecture boundaries respected

## Type of Change

- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass (`make test`)
- [ ] Coverage requirement met (90%+)

## Quality Gates

- [ ] `make validate` passes completely
- [ ] No lint errors (`make lint`)
- [ ] No type errors (`make type-check`)
- [ ] Security scan passes (`make security-scan`)

## Documentation

- [ ] Code comments updated
- [ ] API documentation updated
- [ ] README updated if needed
- [ ] CHANGELOG updated
```

---

## 🧪 Testing Standards

### **Testing Philosophy**

1. **Test-Driven Development** - Write tests before implementation
2. **Test Pyramid** - Many unit tests, fewer integration tests, minimal e2e tests
3. **Test Isolation** - Each test should be independent and repeatable
4. **Test Coverage** - 90% minimum with meaningful assertions
5. **Test Performance** - Unit tests <100ms, integration tests <5s

### **Test Organization**

```
tests/
├── unit/              # Fast tests with mocks (45+ active tests)
│   ├── test_api_core.py
│   ├── test_client_core.py
│   ├── test_builder_core.py
│   └── test_*_coverage.py
├── integration/       # Tests with real external services
│   ├── test_http_client_integration.py
│   └── test_plugin_integration.py
├── e2e/              # Complete workflow tests
│   └── test_api_workflow_e2e.py
├── benchmarks/       # Performance tests
│   └── test_performance_benchmarks.py
└── fixtures/         # Shared test data
    ├── sample_responses.json
    └── test_configurations.yaml
```

### **Writing Tests**

#### **Unit Test Pattern**

```python
import pytest
from unittest.mock import Mock, patch
from flext_api import create_flext_api, FlextResult
from flext_core import FlextLogger

logger = FlextLogger(__name__)

class TestFlextApiCore:
    """Unit tests for FlextApi core functionality."""

    def test_api_creation_success(self):
        """Test successful API instance creation."""
        # Arrange
        # Act
        api = create_flext_api()

        # Assert
        assert api is not None
        assert hasattr(api, 'flext_api_create_client')
        assert hasattr(api, 'get_builder')

    def test_client_creation_with_valid_config(self):
        """Test HTTP client creation with valid configuration."""
        # Arrange
        api = create_flext_api()
        config = {"base_url": "https://api.example.com", "timeout": 30}

        # Act
        result = api.flext_api_create_client(config)

        # Assert
        assert result.success
        assert result.data is not None
        logger.info("Client creation test passed")

    @patch('flext_api.client.httpx.Client')
    def test_http_request_with_mock(self, mock_client):
        """Test HTTP request with mocked client."""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_client.return_value.get.return_value = mock_response

        api = create_flext_api()
        client_result = api.flext_api_create_client({"base_url": "https://test.com"})

        # Act
        assert client_result.success
        client = client_result.data
        response = client.get("/test")

        # Assert
        assert response.success
        assert response.data["status"] == "ok"
```

#### **Integration Test Pattern**

```python
import pytest
from flext_api import create_flext_api
from flext_core import FlextLogger

logger = FlextLogger(__name__)

class TestHttpClientIntegration:
    """Integration tests with real HTTP services."""

    @pytest.mark.integration
    def test_real_http_request(self):
        """Test HTTP request to real service (httpbin.org)."""
        # Arrange
        api = create_flext_api()
        client_result = api.flext_api_create_client({
            "base_url": "https://httpbin.org",
            "timeout": 10
        })

        assert client_result.success
        client = client_result.data

        # Act
        response = client.get("/json")

        # Assert
        assert response.success
        data = response.data
        assert "slideshow" in data
        logger.info("Integration test completed successfully")

    @pytest.mark.integration
    def test_timeout_handling(self):
        """Test client timeout with slow endpoint."""
        # Arrange
        api = create_flext_api()
        client_result = api.flext_api_create_client({
            "base_url": "https://httpbin.org",
            "timeout": 1  # Very short timeout
        })

        assert client_result.success
        client = client_result.data

        # Act
        response = client.get("/delay/5")  # 5 second delay

        # Assert
        assert response.is_failure
        assert "timeout" in response.error.lower()
```

---

## 🔍 Debugging and Troubleshooting

### **Development Debugging**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
make dev

# Run with Python debugger
python -m pdb src/flext_api/main.py

# Profile performance
python -m cProfile -o profile.prof src/flext_api/main.py
python -m pstats profile.prof

# Memory profiling
pip install memory-profiler
python -m memory_profiler src/flext_api/main.py
```

### **Test Debugging**

```bash
# Run tests with debugging
pytest tests/unit/test_api_core.py -v -s --pdb

# Show test output
pytest tests/unit/test_api_core.py -v -s --capture=no

# Run specific test with debugging
pytest tests/unit/test_client_core.py::TestFlextApiClient::test_creation -vvv --pdb
```

### **Common Development Issues**

1. **Import Errors**

   ```bash
   # Check Python path
   python -c "import sys; print('\n'.join(sys.path))"

   # Verify flext-core installation
   python -c "from flext_core import FlextResult; print('✅ flext-core OK')"

   # Reinstall dependencies
   poetry install --with dev,test
   ```

2. **Type Checking Errors**

   ```bash
   # Run mypy with detailed output
   poetry run mypy src/flext_api --show-error-codes --show-traceback

   # Check specific file
   poetry run mypy src/flext_api/api.py -v
   ```

3. **Test Failures**

   ```bash
   # Run failed tests only
   pytest --lf -v

   # Show test durations
   pytest --durations=10

   # Run with coverage to identify untested code
   pytest --cov=flext_api --cov-report=html
   ```

---

## 📚 Development Resources

### **Code Examples**

- **[examples/](../examples/)** - Working code examples
- **[docs/examples/](examples/)** - Documentation examples
- **[tests/](../tests/)** - Test examples for all patterns

### **Documentation**

- **[Architecture](architecture.md)** - System design and patterns
- **[API Reference](api-reference.md)** - Complete API documentation
- **[Configuration](configuration.md)** - Settings and environment management
- **[Integration](integration.md)** - Ecosystem integration patterns

### **External Resources**

- **[Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)** - Architectural principles
- **[Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)** - DDD patterns
- **[FastAPI Documentation](https://fastapi.tiangolo.com/)** - Web framework reference
- **[Pydantic Documentation](https://docs.pydantic.dev/)** - Data validation patterns

---

## 🤝 Contributing Guidelines

### **Contribution Process**

1. **Fork & Clone** - Fork repository and clone locally
2. **Create Feature Branch** - Use descriptive branch names
3. **Implement Changes** - Follow FLEXT-Core patterns
4. **Run Quality Gates** - `make validate` must pass
5. **Write Tests** - Achieve 90%+ coverage
6. **Update Documentation** - Keep docs current
7. **Submit Pull Request** - Use provided template

### **Community Standards**

- **Be Respectful** - Professional and inclusive communication
- **Follow Patterns** - Adhere to established architectural patterns
- **Quality First** - No shortcuts on quality standards
- **Document Everything** - Code should be self-documenting
- **Test Thoroughly** - Comprehensive test coverage required

---

**Development Guide v0.9.0** - Comprehensive development workflow for FLEXT API HTTP foundation library.
