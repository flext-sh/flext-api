# Troubleshooting Guide

Comprehensive guide for diagnosing and resolving common issues with FLEXT-API applications, HTTP clients, and FastAPI integrations.

## HTTP Client Issues

### Connection Problems

**1. Connection Timeouts**

```python
# Symptom: Requests timeout after 30 seconds
# Solution: Increase timeout or check network connectivity

# Check network connectivity
import socket
try:
    socket.create_connection(("api.example.com", 443), timeout=5)
    print("✅ Network connection OK")
except OSError as e:
    print(f"❌ Network connection failed: {e}")

# Increase timeout for slow APIs
client = FlextApiClient(
    base_url="https://slow-api.com",
    timeout=60.0  # Increased from default 30s
)

# Check if API endpoint is reachable
result = client.get("/health")
if result.is_failure:
    print(f"API health check failed: {result.error}")
```

**2. SSL Certificate Errors**

```python
# Symptom: SSL certificate verification failed
# Solution: Check certificates or use custom SSL context

# Disable SSL verification (NOT recommended for production)
client = FlextApiClient(
    base_url="https://api.example.com",
    verify_ssl=False
)

# Use custom SSL context for self-signed certificates
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

client = FlextApiClient(
    base_url="https://internal-api.company.com",
    ssl_context=ssl_context
)

# Check certificate details
import requests
try:
    response = requests.get("https://api.example.com", timeout=5)
    print(f"Certificate: {response.url}")
except requests.exceptions.SSLError as e:
    print(f"SSL Error: {e}")
```

### Request/Response Issues

**1. 400 Bad Request Errors**

```python
# Symptom: Server returns 400 errors
# Solution: Check request format and validation

# Validate request data before sending
user_data = {"name": "Test User", "email": "test@example.com"}

# Check data types
if not isinstance(user_data["name"], str):
    print("Name must be a string")

if "@" not in user_data["email"]:
    print("Invalid email format")

# Check request size limits
import json
request_size = len(json.dumps(user_data).encode('utf-8'))
max_size = 1024 * 1024  # 1MB

if request_size > max_size:
    print(f"Request too large: {request_size} bytes")

# Try request with detailed error logging
result = client.post("/users", json=user_data)
if result.is_failure:
    error = result.error
    print(f"Request failed: {error.message}")
    print(f"Status code: {error.status_code}")
    print(f"Response body: {error.response_text}")
```

**2. 404 Not Found Errors**

```python
# Symptom: API endpoints return 404
# Solution: Check URL construction and API documentation

# Verify base URL
print(f"Base URL: {client.base_url}")

# Check endpoint exists
result = client.get("/health")
if result.is_success:
    print("✅ API is reachable")
else:
    print(f"❌ API not reachable: {result.error}")

# Check URL construction
base_url = "https://api.example.com/v1"
endpoint = "/users/123"
full_url = f"{base_url.rstrip('/')}{endpoint}"

print(f"Full URL: {full_url}")

# List available endpoints (if API supports it)
result = client.get("/")
if result.is_success:
    print("Available endpoints:", result.unwrap().json())
```

**3. 429 Rate Limit Errors**

```python
# Symptom: Rate limit exceeded errors
# Solution: Implement backoff strategy and rate limiting

import time
from flext_api import FlextApiClient

class RateLimitedClient(FlextApiClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0
        self.last_request_time = 0
        self.rate_limit = kwargs.get("rate_limit", 60)  # requests per minute

    def get(self, url, **kwargs):
        # Simple rate limiting
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        # Wait if needed to respect rate limit
        min_interval = 60.0 / self.rate_limit
        if time_since_last_request < min_interval:
            sleep_time = min_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()
        self.request_count += 1

        return super().get(url, **kwargs)

# Handle rate limit responses
result = client.get("/api/data")
if result.is_failure and result.error.status_code == 429:
    retry_after = result.error.headers.get("Retry-After")
    if retry_after:
        wait_time = int(retry_after)
        print(f"Rate limited. Retry after {wait_time} seconds")
        time.sleep(wait_time)
        # Retry request
        result = client.get("/api/data")
```

## FastAPI Application Issues

### Startup Problems

**1. Port Already in Use**

```bash
# Symptom: "Address already in use" error
# Solution: Check what's using the port and choose different port

# Check what's using port 8000
lsof -i :8000

# Or use different port
uvicorn main:app --port 8001 --host 0.0.0.0

# Check available ports
netstat -tulpn | grep LISTEN
```

**2. Import Errors**

```python
# Symptom: ImportError when starting application
# Solution: Check dependencies and Python path

# Check if flext-core is installed
python -c "import flext_core; print('✅ flext-core available')"

# Check if flext-api is installed
python -c "import flext_api; print('✅ flext-api available')"

# Check Python path
import sys
print("Python path:", sys.path)

# Install missing dependencies
pip install -r requirements.txt

# Or install from source
pip install -e .
```

### Runtime Issues

**1. CORS Errors**

```python
# Symptom: CORS policy errors in browser
# Solution: Configure CORS properly

from flext_api import FlextApiConfig

# Configure CORS in application
config = FlextApiConfig(
    cors_origins=[
        "http://localhost:3000",      # React dev server
        "http://localhost:8080",     # Vue dev server
        "https://myapp.company.com"  # Production frontend
    ],
    cors_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    cors_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With"
    ],
    cors_credentials=True
)

# Test CORS configuration
@app.options("/users")
async def cors_preflight():
    return {"message": "CORS OK"}
```

**2. Authentication Issues**

```python
# Symptom: Authentication fails unexpectedly
# Solution: Debug JWT tokens and authentication flow

import jwt
from flext_api.middleware import JwtAuthenticationMiddleware

# Debug JWT token
def debug_jwt_token(token: str):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        print(f"Token payload: {payload}")
        print(f"Expiration: {payload.get('exp')}")
        print(f"Issuer: {payload.get('iss')}")
        print(f"Subject: {payload.get('sub')}")
    except Exception as e:
        print(f"Invalid token: {e}")

# Check authentication middleware configuration
auth_middleware = JwtAuthenticationMiddleware(
    secret_key="your-secret-key",
    algorithm="HS256"
)

# Test authentication manually
test_request = type('Request', (), {
    'headers': {'Authorization': 'Bearer your-token'}
})()

result = await auth_middleware.authenticate_request(test_request)
if result.is_failure:
    print(f"Authentication failed: {result.error}")
```

## Configuration Issues

### Environment Variables

**1. Missing Environment Variables**

```python
# Symptom: Application fails to start due to missing config
# Solution: Check environment variables and provide defaults

import os
from flext_api import FlextApiConfig

# Check required environment variables
required_vars = [
    "DATABASE_URL",
    "JWT_SECRET",
    "API_KEY"
]

missing_vars = []
for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")

# Provide sensible defaults
config = FlextApiConfig(
    database_url=os.getenv("DATABASE_URL", "sqlite:///app.db"),
    jwt_secret=os.getenv("JWT_SECRET", "development-secret"),
    debug=os.getenv("DEBUG", "false").lower() == "true"
)
```

## Database Issues

### Connection Problems

**1. Database Connection Failures**

```python
# Symptom: Database connection fails
# Solution: Check connection parameters and database status

from flext_core import FlextCore

# Check database service registration
container = FlextCore.Container.get_global()
db_result = container.get("database")

if db_result.is_failure:
    print(f"Database service not registered: {db_result.error}")
else:
    db = db_result.unwrap()

    # Test database connection
    try:
        # This depends on your database service implementation
        connection_test = db.test_connection()
        if connection_test.is_success:
            print("✅ Database connection OK")
        else:
            print(f"❌ Database connection failed: {connection_test.error}")
    except Exception as e:
        print(f"❌ Database connection error: {e}")

# Check database URL format
database_url = os.getenv("DATABASE_URL")
if database_url:
    print(f"Database URL: {database_url}")
    if not database_url.startswith(("postgresql://", "mysql://", "sqlite://")):
        print("❌ Invalid database URL format")
```

**2. Migration Issues**

```python
# Symptom: Database migrations fail
# Solution: Check migration status and database state

# Check if migrations table exists
try:
    # This depends on your migration system
    migration_status = db.check_migration_status()
    print(f"Migration status: {migration_status}")
except Exception as e:
    print(f"Migration check failed: {e}")

# Manual migration check
try:
    # Check if key tables exist
    tables = db.list_tables()
    expected_tables = ["users", "posts", "comments"]

    for table in expected_tables:
        if table not in tables:
            print(f"❌ Missing table: {table}")
        else:
            print(f"✅ Table exists: {table}")
except Exception as e:
    print(f"Table check failed: {e}")
```

## Logging Issues

### Log Configuration Problems

**1. Logs Not Appearing**

```python
# Symptom: Application logs don't appear
# Solution: Check logging configuration

from flext_core import FlextCore
import logging

# Check logger configuration
logger = FlextCore.Logger(__name__)
logger.info("Test log message")

# Check if logging is configured
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Python logging test")

# Check log file permissions
import os
log_file = "/var/log/flext-api/app.log"
if os.path.exists(log_file):
    # Check file permissions
    stat = os.stat(log_file)
    print(f"Log file permissions: {oct(stat.st_mode)}")
else:
    print(f"Log file does not exist: {log_file}")
```

**2. Log Format Issues**

```python
# Symptom: Logs are not in expected format
# Solution: Check logging configuration

# Configure structured logging
logger = FlextCore.Logger(__name__, format="json")

# Test structured logging
logger.info("User action", extra={
    "user_id": "user_123",
    "action": "login",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
})

# Check if JSON format is working
import json
test_log = logger._format_log("INFO", "Test message", {"key": "value"})
try:
    parsed = json.loads(test_log)
    print("✅ JSON logging format OK")
except json.JSONDecodeError as e:
    print(f"❌ JSON logging format error: {e}")
```

## Performance Issues

### Slow Response Times

**1. Database Query Performance**

```python
# Symptom: API responses are slow
# Solution: Check database queries and indexes

import time

# Measure database query time
start_time = time.time()
users = db.get_all_users()
query_time = time.time() - start_time

print(f"Database query took: {query_time:.2f}s")

if query_time > 1.0:
    print("❌ Slow database query detected")
    print("Consider adding database indexes")
    print("Check query execution plan")

# Check for N+1 query problems
def get_users_with_posts():
    users = db.get_all_users()  # 1 query

    for user in users:
        posts = db.get_user_posts(user.id)  # N queries - BAD!
        user.posts = posts

    return users

# Fix N+1 problem
def get_users_with_posts_fixed():
    # Single query with JOIN or use ORM relationships
    return db.get_users_with_posts()  # 1 query - GOOD!
```

**2. Memory Usage Issues**

```python
# Symptom: High memory usage
# Solution: Check for memory leaks and large data structures

import psutil
import os

def check_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024

    print(f"Memory usage: {memory_mb:.1f} MB")

    if memory_mb > 500:  # 500MB threshold
        print("⚠️ High memory usage detected")

    return memory_mb

# Monitor memory during request processing
@app.middleware("http")
async def memory_monitor(request, call_next):
    initial_memory = check_memory_usage()

    response = await call_next(request)

    final_memory = check_memory_usage()
    memory_delta = final_memory - initial_memory

    if memory_delta > 10:  # 10MB increase
        print(f"⚠️ Memory increased by {memory_delta:.1f} MB during request")

    return response
```

## Testing Issues

### Test Failures

**1. Flaky Tests**

```python
# Symptom: Tests pass sometimes but fail randomly
# Solution: Identify and fix race conditions

import time
import random

def test_flaky_endpoint():
    """Test that sometimes fails due to timing issues."""

    # Add small delay to reduce flakiness
    time.sleep(0.1)

    # Or use retry mechanism
    max_retries = 3
    for attempt in range(max_retries):
        result = client.get("/unstable-endpoint")

        if result.is_success:
            break

        if attempt < max_retries - 1:
            time.sleep(random.uniform(0.1, 0.5))  # Random delay

    assert result.is_success, f"Test failed after {max_retries} attempts"
```

**2. Mock Setup Issues**

```python
# Symptom: Mocks not working as expected
# Solution: Check mock configuration and usage

from unittest.mock import Mock, patch

# Test with proper mock setup
@patch('flext_api.client.httpx.Client')
def test_http_client_with_mock(mock_http_client):
    """Test HTTP client with mocked httpx.Client."""

    # Setup mock response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Test User"}
    mock_response.headers = {"Content-Type": "application/json"}

    # Configure mock to return response
    mock_http_client.return_value.request.return_value = mock_response

    # Test client behavior
    client = FlextApiClient(base_url="https://api.example.com")
    result = client.get("/users/1")

    # Verify mock was called correctly
    mock_http_client.return_value.request.assert_called_once()
    call_args = mock_http_client.return_value.request.call_args

    assert result.is_success
    user = result.unwrap()
    assert user["name"] == "Test User"
```

## Deployment Issues

### Docker Issues

**1. Container Build Failures**

```bash
# Symptom: Docker build fails
# Solution: Check Dockerfile and dependencies

# Check if Python version matches
python --version  # Should match Dockerfile

# Check if all dependencies are available
pip list | grep -E "(fastapi|uvicorn|pydantic)"

# Check if Docker can access files
ls -la Dockerfile
ls -la requirements.txt

# Test build locally
docker build -t flext-api:test .
```

**2. Container Runtime Issues**

```python
# Symptom: Application fails in container
# Solution: Check environment and configuration

# Check environment variables in container
import os
print(f"Environment: {os.environ.get('ENVIRONMENT', 'not set')}")
print(f"Database URL: {os.environ.get('DATABASE_URL', 'not set')}")

# Check if all required files are present
required_files = [
    "/app/config.toml",
    "/app/.env",
    "/app/database/migrations"
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"✅ {file_path} exists")
    else:
        print(f"❌ {file_path} missing")
```

## Monitoring and Debugging

### Application Monitoring

```python
# Add health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""

    # Check database connectivity
    db_healthy = await check_database_health()

    # Check external service connectivity
    api_healthy = await check_external_api_health()

    # Check disk space
    disk_healthy = check_disk_space()

    if all([db_healthy, api_healthy, disk_healthy]):
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        }
    else:
        raise HTTPException(status_code=503, detail="Service unhealthy")

async def check_database_health() -> bool:
    """Check database connectivity."""
    try:
        # Test database query
        result = db.execute("SELECT 1")
        return result.is_success
    except Exception:
        return False

async def check_external_api_health() -> bool:
    """Check external API connectivity."""
    try:
        result = client.get("/external-api/health")
        return result.is_success
    except Exception:
        return False

def check_disk_space() -> bool:
    """Check available disk space."""
    import shutil
    total, used, free = shutil.disk_usage("/")
    free_gb = free / (1024**3)
    return free_gb > 1.0  # Require at least 1GB free
```

### Debug Logging

```python
# Enable debug logging for troubleshooting
import logging

# Set logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)

# Create debug logger
logger = FlextCore.Logger(__name__)
logger.setLevel(logging.DEBUG)

# Add debug information to requests
@app.middleware("http")
async def debug_middleware(request, call_next):
    logger.debug("Incoming request", extra={
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else "unknown"
    })

    response = await call_next(request)

    logger.debug("Outgoing response", extra={
        "status_code": response.status_code,
        "response_headers": dict(response.headers)
    })

    return response
```

This troubleshooting guide provides comprehensive solutions for common issues encountered when developing and deploying FLEXT-API applications.
