# Troubleshooting Guide

**Common issues, solutions, and debugging strategies for FLEXT API**

> **Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [flext-api](../README.md) > Troubleshooting

---

## 🎯 Troubleshooting Overview

This guide covers common issues encountered when developing with FLEXT API, their root causes, and proven solutions. All troubleshooting approaches follow FLEXT-Core patterns and enterprise debugging standards.

### **Diagnostic Philosophy**

1. **Investigate Deep** - Verify actual state before assuming causes
2. **Use Tools First** - Leverage debugging tools before guessing
3. **Follow Patterns** - Apply FlextResult error handling consistently
4. **Log Structured** - Use get_logger() with context information
5. **Test Systematically** - Isolate issues with targeted tests

---

## 🔧 Development Environment Issues

### **Installation and Setup Problems**

#### **Poetry Installation Failures**

**Symptoms**:

```bash
Poetry command not found
Failed to install dependencies
Lock file conflicts
```

**Diagnosis**:

```bash
# Check Poetry installation
poetry --version

# Check Python version compatibility
python --version  # Should be 3.13+

# Verify virtual environment
poetry env info
```

**Solutions**:

```bash
# Reinstall Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clean and reinstall dependencies
poetry env remove python
poetry install --with dev,test,docs

# Fix lock file issues
poetry lock --no-update
poetry install
```

#### **flext-core Dependency Issues**

**Symptoms**:

```python
ImportError: No module named 'flext_core'
AttributeError: module 'flext_core' has no attribute 'FlextResult'
```

**Diagnosis**:

```bash
# Check flext-core installation
python -c "import flext_core; print(flext_core.__version__)"

# Verify FLEXT workspace structure
ls -la ../flext-core/  # Should exist in workspace

# Check Poetry dependency resolution
poetry show flext-core
```

**Solutions**:

```bash
# Install from workspace (development)
cd ../flext-core && poetry install
cd ../flext-api && poetry install

# Or install specific version
poetry add flext-core@^0.9.0

# Verify installation
python -c "from flext_core import FlextResult, get_logger; print('✅ OK')"
```

### **Development Server Issues**

#### **FastAPI Server Won't Start**

**Symptoms**:

```bash
make dev fails
Port already in use
ModuleNotFoundError in main.py
```

**Diagnosis**:

```bash
# Check port availability
lsof -i :8000

# Test module imports
python -c "from flext_api.main import app; print('✅ Import OK')"

# Check FastAPI installation
python -c "import fastapi; print(fastapi.__version__)"
```

**Solutions**:

```bash
# Kill process using port
lsof -ti:8000 | xargs kill -9

# Use different port
API_PORT=8001 make dev

# Fix import issues
poetry install --with dev
python -c "from flext_api import create_flext_api; print('✅ Fixed')"

# Start server manually with debugging
poetry run uvicorn flext_api.main:app --reload --port 8000 --log-level debug
```

#### **Hot Reload Not Working**

**Symptoms**:

```bash
Changes not reflected in development server
Server doesn't restart on file changes
```

**Solutions**:

```bash
# Use aggressive reload mode
make dev-reload

# Start with uvicorn directly
poetry run uvicorn flext_api.main:app --reload --reload-dir src/

# Check file permissions
ls -la src/flext_api/

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

---

## 🧪 Testing Issues

### **Test Execution Failures**

#### **Import Errors in Tests**

**Symptoms**:

```bash
ModuleNotFoundError: No module named 'flext_api'
ImportError: attempted relative import with no known parent package
```

**Diagnosis**:

```bash
# Check Python path in test environment
python -c "import sys; print('\n'.join(sys.path))"

# Verify test configuration
cat pyproject.toml | grep -A 10 "\[tool.pytest\]"

# Test import manually
python -c "from flext_api import create_flext_api; print('✅ OK')"
```

**Solutions**:

```bash
# Install in development mode
poetry install -e .

# Set PYTHONPATH explicitly
PYTHONPATH=src pytest tests/

# Use pytest with src layout
pytest --import-mode=importlib tests/

# Fix pyproject.toml configuration
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

#### **Async Test Issues**

**Symptoms**:

```bash
RuntimeError: This event loop is already running
TypeError: object generator can't be used in 'await' expression
```

**Diagnosis**:

```bash
# Check pytest-asyncio installation
poetry show pytest-asyncio

# Verify async test markers
grep -r "@pytest.mark.asyncio" tests/

# Check asyncio mode configuration
cat pyproject.toml | grep asyncio
```

**Solutions**:

```bash
# Install pytest-asyncio
poetry add --group test pytest-asyncio

# Configure asyncio mode in pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"

# Fix async test patterns
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_operation()
    assert result.success

# Use proper async fixtures
@pytest.fixture
async def async_client():
    async with AsyncClient() as client:
        yield client
```

#### **Coverage Issues**

**Symptoms**:

```bash
Coverage below 90% requirement
Missing coverage for specific modules
Coverage report showing incorrect paths
```

**Diagnosis**:

```bash
# Run coverage with details
poetry run pytest --cov=flext_api --cov-report=term-missing

# Check which files are missing coverage
poetry run coverage report --show-missing

# Verify coverage configuration
cat pyproject.toml | grep -A 10 "\[tool.coverage"
```

**Solutions**:

```bash
# Configure coverage properly
[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]

# Run specific coverage
poetry run pytest tests/unit/ --cov=flext_api --cov-report=html

# Generate detailed report
make coverage-html
open htmlcov/index.html
```

### **Test Performance Issues**

#### **Slow Test Execution**

**Symptoms**:

```bash
Tests taking too long to complete
Timeout errors in integration tests
Memory usage growing during tests
```

**Diagnosis**:

```bash
# Profile test execution
pytest --durations=10 tests/

# Check for slow tests
pytest -m "not slow" tests/

# Monitor memory usage
python -m memory_profiler pytest tests/unit/
```

**Solutions**:

```bash
# Use parallel execution
poetry add --group test pytest-xdist
pytest -n auto tests/

# Skip slow tests in development
pytest -m "not slow" tests/

# Optimize fixtures
@pytest.fixture(scope="session")
def expensive_setup():
    # Setup once per session
    return setup_expensive_resource()

# Use mocking for external dependencies
@patch('flext_api.client.httpx.Client')
def test_with_mock(self, mock_client):
    # Fast test with mocks
    pass
```

---

## 🔗 HTTP Client Issues

### **Connection Problems**

#### **Connection Refused Errors**

**Symptoms**:

```python
FlextResult[None].fail("Connection refused")
ConnectionError: [Errno 61] Connection refused
```

**Diagnosis**:

```bash
# Test connectivity manually
curl -I http://localhost:8000/health

# Check if service is running
ps aux | grep uvicorn

# Verify port availability
netstat -an | grep 8000

# Test with different URL
python -c "
import requests
try:
    r = requests.get('http://httpbin.org/get', timeout=5)
    print(f'✅ External OK: {r.status_code}')
except Exception as e:
    print(f'❌ Network issue: {e}')
"
```

**Solutions**:

```python
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

# Add connection retry logic
api = create_flext_api()
client_result = api.flext_api_create_client({
    "base_url": "http://localhost:8000",
    "timeout": 10,
    "max_retries": 3,
    "retry_backoff_factor": 2.0
})

if not client_result.success:
    logger.error("Client creation failed", error=client_result.error)
    # Fallback to alternative endpoint
    fallback_result = api.flext_api_create_client({
        "base_url": "http://httpbin.org",
        "timeout": 5
    })
```

#### **Timeout Issues**

**Symptoms**:

```python
FlextResult[None].fail("Request timeout")
TimeoutError: Request timed out after 30 seconds
```

**Diagnosis**:

```python
from flext_api import create_flext_api
import time

# Test with different timeout values
api = create_flext_api()
client_result = api.flext_api_create_client({
    "base_url": "https://httpbin.org",
    "timeout": 1  # Very short for testing
})

if client_result.success:
    client = client_result.data
    start_time = time.time()
    response = client.get("/delay/5")  # 5 second delay
    elapsed = time.time() - start_time
    print(f"Request took {elapsed:.2f} seconds")
```

**Solutions**:

```python
from flext_api import create_flext_api, FlextApiRetryPlugin
from flext_core import get_logger

logger = get_logger(__name__)

# Configure appropriate timeouts
api = create_flext_api()
client_result = api.flext_api_create_client({
    "base_url": "https://api.slow-service.com",
    "timeout": 60,  # Longer timeout for slow services
    "max_retries": 2,
    "headers": {"User-Agent": "FLEXT-API/0.9.0"}
})

# Use retry plugin with exponential backoff
plugins = [FlextApiRetryPlugin(
    max_retries=3,
    backoff_factor=2.0,
    retry_status_codes=[408, 429, 500, 502, 503, 504]
)]

client_result = api.flext_api_create_client_with_plugins(
    {"base_url": "https://api.unreliable.com", "timeout": 30},
    plugins
)
```

### **Authentication Issues**

#### **Authentication Failures**

**Symptoms**:

```python
HTTP 401 Unauthorized
Authentication token expired
Invalid credentials
```

**Diagnosis**:

```python
from flext_api import create_flext_api
import base64

# Test authentication manually
api = create_flext_api()
client_result = api.flext_api_create_client({
    "base_url": "https://api.example.com",
    "headers": {"Authorization": "Bearer your-token-here"}
})

if client_result.success:
    client = client_result.data
    response = client.get("/user/profile")
    print(f"Auth test: {response.success}")
    if response.is_failure:
        print(f"Error: {response.error}")
```

**Solutions**:

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
import os

logger = get_logger(__name__)

class AuthenticatedClient:
    def __init__(self):
        self.api = create_flext_api()
        self.token = None

    def authenticate(self, username: str, password: str) -> FlextResult[str]:
        """Authenticate and get token."""
        auth_client_result = self.api.flext_api_create_client({
            "base_url": "https://auth.example.com"
        })

        if not auth_client_result.success:
            return FlextResult[None].fail("Auth client creation failed")

        auth_client = auth_client_result.data
        response = auth_client.post("/auth/token", json={
            "username": username,
            "password": password
        })

        if response.success:
            self.token = response.data.get("access_token")
            logger.info("Authentication successful")
            return FlextResult[None].ok(self.token)
        else:
            logger.error("Authentication failed", error=response.error)
            return FlextResult[None].fail(f"Auth failed: {response.error}")

    def create_authenticated_client(self, base_url: str) -> FlextResult[object]:
        """Create client with authentication."""
        if not self.token:
            return FlextResult[None].fail("Not authenticated")

        return self.api.flext_api_create_client({
            "base_url": base_url,
            "headers": {"Authorization": f"Bearer {self.token}"}
        })

# Usage
auth_client = AuthenticatedClient()
auth_result = auth_client.authenticate("user", "pass")
if auth_result.success:
    client_result = auth_client.create_authenticated_client("https://api.example.com")
```

---

## 🏗️ Architecture and Pattern Issues

### **FlextResult Pattern Violations**

#### **Exception Handling Instead of FlextResult**

**Symptoms**:

```python
# ❌ Incorrect pattern
def bad_operation():
    if error_condition:
        raise ValueError("Something went wrong")
    return result

# Results in unhandled exceptions
```

**Solutions**:

```python
from flext_core import FlextResult, get_logger

logger = get_logger(__name__)

# ✅ Correct pattern
def good_operation() -> FlextResult[dict]:
    """Operation following FlextResult pattern."""
    try:
        if error_condition:
            logger.warning("Operation condition not met")
            return FlextResult[None].fail("Invalid operation state")

        result = perform_operation()
        logger.info("Operation completed successfully")
        return FlextResult[None].ok(result)

    except Exception as e:
        logger.exception("Operation failed unexpectedly")
        return FlextResult[None].fail(f"Operation failed: {e}")

# Usage
result = good_operation()
if result.success:
    data = result.data
    # Process successful result
else:
    # Handle failure case
    logger.error("Operation failed", error=result.error)
```

#### **Logging Pattern Violations**

**Symptoms**:

```python
# ❌ Incorrect logging
import structlog
log = structlog.get_logger()

# ❌ Standard logging
import logging
logger = logging.getLogger(__name__)
```

**Solutions**:

```python
from flext_core import get_logger

# ✅ Correct pattern
logger = get_logger(__name__)

def service_operation():
    logger.info("Starting operation", operation="service_operation")

    try:
        result = perform_work()
        logger.info("Operation completed",
                   operation="service_operation",
                   records_processed=len(result))
        return FlextResult[None].ok(result)
    except Exception as e:
        logger.exception("Operation failed",
                        operation="service_operation",
                        error_type=type(e).__name__)
        return FlextResult[None].fail(f"Operation failed: {e}")
```

### **Dependency Injection Issues**

#### **Local Container Instead of Global**

**Symptoms**:

```python
# ❌ Incorrect pattern
from dependency_injector import containers

class LocalContainer(containers.DeclarativeContainer):
    # Local DI container
    pass

container = LocalContainer()
```

**Solutions**:

```python
from flext_core import get_flext_container, FlextService

# ✅ Correct pattern
container = FlextContainer.get_global()

class FlextApiService(FlextService):
    """Service using global DI container."""

    def __init__(self):
        super().__init__()
        self.container = FlextContainer.get_global()

    def get_dependency(self, dependency_type):
        """Get dependency from global container."""
        return self.container.get(dependency_type)
```

---

## 🔍 Debugging Strategies

### **Systematic Debugging Approach**

#### **Environment Diagnosis**

```bash
# Complete environment check
echo "=== FLEXT API Environment Diagnosis ==="
echo "Python version: $(python --version)"
echo "Poetry version: $(poetry --version)"
echo "Virtual env: $(poetry env info --path)"

echo -e "\n=== Dependencies ==="
poetry show flext-core flext-observability fastapi pydantic

echo -e "\n=== Service Health ==="
curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API OK" || echo "❌ API Down"
curl -f http://localhost:8080/health 2>/dev/null && echo "✅ FlexCore OK" || echo "❌ FlexCore Down"

echo -e "\n=== Import Tests ==="
python -c "from flext_api import create_flext_api; print('✅ flext_api OK')" 2>/dev/null || echo "❌ flext_api Import Failed"
python -c "from flext_core import FlextResult; print('✅ flext_core OK')" 2>/dev/null || echo "❌ flext_core Import Failed"
```

#### **Runtime Debugging**

```python
from flext_api import create_flext_api
from flext_core import get_logger
import traceback

logger = get_logger(__name__)

def debug_api_operation():
    """Debug API operation with comprehensive logging."""

    logger.debug("Starting API operation debug")

    try:
        # Step 1: Create API instance
        logger.debug("Creating API instance")
        api = create_flext_api()
        logger.debug("API instance created successfully")

        # Step 2: Create HTTP client
        logger.debug("Creating HTTP client")
        client_result = api.flext_api_create_client({
            "base_url": "https://httpbin.org",
            "timeout": 10
        })

        if not client_result.success:
            logger.error("Client creation failed", error=client_result.error)
            return

        logger.debug("HTTP client created successfully")
        client = client_result.data

        # Step 3: Make test request
        logger.debug("Making test HTTP request")
        response = client.get("/json")

        if response.success:
            logger.debug("Request successful",
                        status="success",
                        data_type=type(response.data).__name__)
        else:
            logger.error("Request failed", error=response.error)

    except Exception as e:
        logger.exception("Debug operation failed")
        traceback.print_exc()

# Enable debug logging
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
debug_api_operation()
```

### **Performance Debugging**

#### **Profiling HTTP Operations**

```python
import time
import cProfile
import pstats
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def profile_http_operations():
    """Profile HTTP client operations."""

    def perform_operations():
        api = create_flext_api()
        client_result = api.flext_api_create_client({
            "base_url": "https://httpbin.org"
        })

        if client_result.success:
            client = client_result.data

            # Perform multiple operations
            for i in range(10):
                response = client.get(f"/delay/0.1")
                if response.success:
                    logger.debug(f"Request {i+1} completed")

    # Profile the operations
    profiler = cProfile.Profile()
    profiler.enable()

    start_time = time.time()
    perform_operations()
    end_time = time.time()

    profiler.disable()

    # Print results
    print(f"Total time: {end_time - start_time:.2f} seconds")

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Run profiling
profile_http_operations()
```

#### **Memory Usage Analysis**

```python
import tracemalloc
from flext_api import create_flext_api
from flext_core import get_logger

logger = get_logger(__name__)

def analyze_memory_usage():
    """Analyze memory usage of API operations."""

    # Start memory tracing
    tracemalloc.start()

    # Initial snapshot
    snapshot1 = tracemalloc.take_snapshot()

    # Perform operations
    api = create_flext_api()
    clients = []

    for i in range(100):
        client_result = api.flext_api_create_client({
            "base_url": f"https://api-{i}.example.com"
        })
        if client_result.success:
            clients.append(client_result.data)

    # Final snapshot
    snapshot2 = tracemalloc.take_snapshot()

    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("Top 10 memory allocations:")
    for stat in top_stats[:10]:
        print(stat)

    # Stop tracing
    tracemalloc.stop()

# Run memory analysis
analyze_memory_usage()
```

---

## 📊 Quality Gate Failures

### **Lint Failures**

#### **Ruff Linting Errors**

**Common Issues**:

```bash
E501 line too long (87 > 88 characters)
F401 'module' imported but unused
W291 trailing whitespace
```

**Solutions**:

```bash
# Auto-fix most issues
make format

# Run specific ruff fixes
poetry run ruff --fix src/

# Check specific rules
poetry run ruff check src/ --select E501

# Configure line length in pyproject.toml
[tool.ruff]
extend = "../.ruff-shared.toml"
lint.isort.known-first-party = ["flext_api"]
```

### **Type Checking Failures**

#### **MyPy Type Errors**

**Common Issues**:

```bash
error: Function is missing a return type annotation
error: Argument 1 has incompatible type "str"; expected "int"
error: "None" has no attribute "data"
```

**Solutions**:

```python
from typing import Optional, Dict, Any
from flext_core import FlextResult

# ✅ Add proper type annotations
def typed_function(name: str, age: int) -> FlextResult[Dict[str, Any]]:
    """Function with proper type annotations."""
    if not name:
        return FlextResult[None].fail("Name is required")

    result = {"name": name, "age": age}
    return FlextResult[None].ok(result)

# ✅ Handle Optional types properly
def handle_optional(value: Optional[str]) -> str:
    """Handle optional values correctly."""
    if value is None:
        return "default"
    return value.upper()

# ✅ Use proper generic types
from typing import List, Union

def process_items(items: List[Union[str, int]]) -> FlextResult[List[str]]:
    """Process items with proper typing."""
    try:
        result = [str(item) for item in items]
        return FlextResult[None].ok(result)
    except Exception as e:
        return FlextResult[None].fail(f"Processing failed: {e}")
```

---

## 🆘 Emergency Procedures

### **Service Recovery**

#### **Complete Service Reset**

```bash
#!/bin/bash
# emergency-reset.sh - Complete FLEXT API service reset

echo "🚨 Emergency FLEXT API Reset"

# 1. Stop all services
echo "Stopping services..."
pkill -f uvicorn
pkill -f flext-api

# 2. Clean environment
echo "Cleaning environment..."
cd /workspace/flext/flext-api
make clean-all

# 3. Reset dependencies
echo "Resetting dependencies..."
poetry env remove python
poetry install --with dev,test,docs

# 4. Verify core dependencies
echo "Verifying dependencies..."
python -c "from flext_core import FlextResult; print('✅ flext-core OK')" || exit 1
python -c "from flext_api import create_flext_api; print('✅ flext-api OK')" || exit 1

# 5. Run quality gates
echo "Running quality checks..."
make validate || echo "⚠️  Quality gates failed - check logs"

# 6. Restart service
echo "Restarting service..."
make dev &

# 7. Health check
sleep 5
curl -f http://localhost:8000/health && echo "✅ Service recovered" || echo "❌ Recovery failed"
```

#### **Quick Diagnostic Script**

```bash
#!/bin/bash
# quick-diagnosis.sh - Rapid issue identification

echo "🔍 FLEXT API Quick Diagnosis"

# Check Python environment
echo "Python: $(python --version)"
echo "Poetry: $(poetry --version)"
echo "Virtual env: $(poetry env info --path 2>/dev/null || echo 'Not found')"

# Check key imports
echo -e "\n📦 Import Tests:"
python -c "import flext_api; print('✅ flext_api')" 2>/dev/null || echo "❌ flext_api import failed"
python -c "import flext_core; print('✅ flext_core')" 2>/dev/null || echo "❌ flext_core import failed"
python -c "import fastapi; print('✅ fastapi')" 2>/dev/null || echo "❌ fastapi import failed"

# Check services
echo -e "\n🌐 Service Health:"
curl -f http://localhost:8000/health 2>/dev/null && echo "✅ API (8000)" || echo "❌ API down"
curl -f http://localhost:8080/health 2>/dev/null && echo "✅ FlexCore (8080)" || echo "❌ FlexCore down"

# Check ports
echo -e "\n🔌 Port Usage:"
lsof -i :8000 | head -2
lsof -i :8080 | head -2

# Check logs
echo -e "\n📋 Recent Errors:"
grep -i error logs/*.log 2>/dev/null | tail -5 || echo "No error logs found"

echo -e "\n✅ Diagnosis complete"
```

---

## 📚 Additional Resources

### **Documentation Links**

- **[Architecture](architecture.md)** - System design and troubleshooting context
- **[Development](development.md)** - Development workflows and debugging
- **[Configuration](configuration.md)** - Settings and environment issues
- **[Integration](integration.md)** - Service integration troubleshooting
- **[Main Documentation Hub](../../docs/NAVIGATION.md)** - Complete FLEXT ecosystem

### **External Resources**

- **[FastAPI Troubleshooting](https://fastapi.tiangolo.com/tutorial/debugging/)** - Web framework debugging
- **[Poetry Troubleshooting](https://python-poetry.org/docs/troubleshooting/)** - Dependency management issues
- **[Python Debugging](https://docs.python.org/3/library/pdb.html)** - Python debugger reference
- **[HTTP Client Debugging](https://httpx.readthedocs.io/en/latest/logging/)** - HTTP debugging strategies

### **Community Support**

- **GitHub Issues**: [flext-api/issues](https://github.com/flext-sh/flext-api/issues)
- **GitHub Discussions**: [flext/discussions](https://github.com/flext-sh/flext/discussions)
- **Documentation Issues**: Report via pull requests to improve this guide

---

**Troubleshooting Guide v0.9.0** - Comprehensive issue resolution for FLEXT API HTTP foundation library.
