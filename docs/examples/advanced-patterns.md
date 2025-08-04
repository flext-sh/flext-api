# Advanced Patterns

**Advanced usage patterns and enterprise implementations for FLEXT API**

> **Navigation**: [FLEXT Hub](../../../docs/NAVIGATION.md) > [flext-api](../../README.md) > [Examples](../) > Advanced Patterns

---

## 🎯 Advanced Patterns Overview

This guide covers sophisticated FLEXT API usage patterns for enterprise applications, including plugin systems, advanced error handling, performance optimization, and complex integration scenarios.

### **Prerequisites**

- Understanding of [Basic Usage](basic-usage.md) patterns
- Familiarity with FLEXT-Core patterns and FlextResult
- Knowledge of async/await patterns in Python

---

## 🔌 Plugin System Patterns

### **Custom Plugin Development**

```python
from flext_api import FlextApiPlugin, create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any, Optional
import time
import hashlib

logger = get_logger(__name__)

class RequestLoggingPlugin(FlextApiPlugin):
    """Advanced logging plugin with request/response tracking."""

    def __init__(self, log_level: str = "INFO", include_body: bool = False):
        self.log_level = log_level
        self.include_body = include_body
        self.request_times = {}

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Log and track request before execution."""
        request_id = self._generate_request_id(request_config)
        self.request_times[request_id] = time.time()

        log_data = {
            "request_id": request_id,
            "method": request_config.get("method", "GET"),
            "url": request_config.get("url", ""),
            "headers": request_config.get("headers", {})
        }

        if self.include_body and "json" in request_config:
            log_data["body"] = request_config["json"]

        logger.info("HTTP request starting", **log_data)
        request_config["_request_id"] = request_id

        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Log response and calculate request duration."""
        request_id = response.get("_request_id")
        if request_id and request_id in self.request_times:
            duration = time.time() - self.request_times[request_id]
            del self.request_times[request_id]

            log_data = {
                "request_id": request_id,
                "status_code": response.get("status_code", 0),
                "duration_ms": round(duration * 1000, 2),
                "response_size": len(str(response.get("content", "")))
            }

            if self.include_body and "data" in response:
                log_data["response_data"] = response["data"]

            logger.info("HTTP request completed", **log_data)

        return FlextResult.ok(response)

    def _generate_request_id(self, request_config: Dict[str, Any]) -> str:
        """Generate unique request ID."""
        content = f"{request_config.get('method', 'GET')}{request_config.get('url', '')}{time.time()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]

class RequestThrottlingPlugin(FlextApiPlugin):
    """Advanced throttling plugin with sliding window rate limiting."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times = []

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Check rate limit before request."""
        current_time = time.time()

        # Remove old requests outside the window
        self.request_times = [
            req_time for req_time in self.request_times
            if current_time - req_time < self.window_seconds
        ]

        # Check if we're over the limit
        if len(self.request_times) >= self.max_requests:
            oldest_request = min(self.request_times)
            wait_time = self.window_seconds - (current_time - oldest_request)
            logger.warning("Rate limit exceeded",
                          requests_in_window=len(self.request_times),
                          wait_time_seconds=wait_time)
            return FlextResult.fail(f"Rate limit exceeded. Wait {wait_time:.1f} seconds")

        # Add current request to tracking
        self.request_times.append(current_time)
        logger.debug("Request allowed",
                    requests_in_window=len(self.request_times),
                    max_requests=self.max_requests)

        return FlextResult.ok(request_config)

def advanced_plugin_example():
    """Example using advanced custom plugins."""

    api = create_flext_api()

    # Create plugins
    logging_plugin = RequestLoggingPlugin(log_level="INFO", include_body=True)
    throttling_plugin = RequestThrottlingPlugin(max_requests=10, window_seconds=60)

    plugins = [logging_plugin, throttling_plugin]

    # Create client with plugins
    client_result = api.flext_api_create_client_with_plugins(
        {
            "base_url": "https://httpbin.org",
            "timeout": 30
        },
        plugins
    )

    if client_result.success:
        client = client_result.data
        logger.info("Client with advanced plugins created")

        # Make requests to test plugins
        for i in range(5):
            response = client.get(f"/get?request={i}")
            if response.success:
                logger.info(f"Request {i+1} completed successfully")
            else:
                logger.error(f"Request {i+1} failed", error=response.error)

            time.sleep(0.1)  # Small delay between requests

    return client_result

# Usage
plugin_result = advanced_plugin_example()
```

### **Circuit Breaker Implementation**

```python
from flext_api import FlextApiPlugin, create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any
import time
from enum import Enum

logger = get_logger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class AdvancedCircuitBreakerPlugin(FlextApiPlugin):
    """Advanced circuit breaker with exponential backoff and health checking."""

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 half_open_max_calls: int = 3):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.state = CircuitState.CLOSED
        self.half_open_calls = 0

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Check circuit state before request."""
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            if current_time - self.last_failure_time > self.recovery_timeout:
                self._transition_to_half_open()
            else:
                remaining_time = self.recovery_timeout - (current_time - self.last_failure_time)
                logger.warning("Circuit breaker is OPEN",
                              remaining_time=remaining_time,
                              failure_count=self.failure_count)
                return FlextResult.fail(f"Circuit breaker OPEN. Retry in {remaining_time:.1f}s")

        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                logger.warning("Half-open call limit reached")
                return FlextResult.fail("Circuit breaker half-open call limit reached")

            self.half_open_calls += 1
            logger.info("Half-open request allowed", calls=self.half_open_calls)

        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Update circuit state based on response."""
        status_code = response.get("status_code", 0)
        success = 200 <= status_code < 300

        if success:
            self._handle_success()
        else:
            self._handle_failure()

        return FlextResult.ok(response)

    def _handle_success(self):
        """Handle successful response."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                self._transition_to_closed()
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)
                logger.debug("Failure count decremented", count=self.failure_count)

    def _handle_failure(self):
        """Handle failed response."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
        elif self.state == CircuitState.CLOSED and self.failure_count >= self.failure_threshold:
            self._transition_to_open()

        logger.warning("Request failure recorded",
                      failure_count=self.failure_count,
                      state=self.state.value)

    def _transition_to_open(self):
        """Transition circuit to OPEN state."""
        self.state = CircuitState.OPEN
        self.half_open_calls = 0
        logger.error("Circuit breaker OPENED",
                    failure_count=self.failure_count,
                    recovery_timeout=self.recovery_timeout)

    def _transition_to_half_open(self):
        """Transition circuit to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self.half_open_calls = 0
        self.success_count = 0
        logger.info("Circuit breaker transitioned to HALF_OPEN")

    def _transition_to_closed(self):
        """Transition circuit to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        logger.info("Circuit breaker CLOSED - service recovered")

def circuit_breaker_example():
    """Example using advanced circuit breaker."""

    api = create_flext_api()
    circuit_breaker = AdvancedCircuitBreakerPlugin(
        failure_threshold=3,
        recovery_timeout=10,
        half_open_max_calls=2
    )

    client_result = api.flext_api_create_client_with_plugins(
        {
            "base_url": "https://httpbin.org",
            "timeout": 5
        },
        [circuit_breaker]
    )

    if client_result.success:
        client = client_result.data

        # Test circuit breaker with failing requests
        logger.info("Testing circuit breaker with failing requests")
        for i in range(10):
            # Use status endpoint to simulate failures
            status_code = 500 if i < 5 else 200
            response = client.get(f"/status/{status_code}")

            logger.info(f"Request {i+1}: Status {status_code}",
                       success=response.success,
                       circuit_state=circuit_breaker.state.value)

            time.sleep(1)  # Allow time for recovery testing

    return client_result

# Usage
circuit_result = circuit_breaker_example()
```

---

## 🚀 Async and Concurrency Patterns

### **Async HTTP Client Pattern**

```python
import asyncio
from typing import List, Dict, Any
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class AsyncFlextApiWrapper:
    """Async wrapper for FLEXT API operations."""

    def __init__(self, base_url: str):
        self.api = create_flext_api()
        self.base_url = base_url
        self.client = None

    async def initialize(self) -> FlextResult[bool]:
        """Initialize the async client."""
        loop = asyncio.get_event_loop()

        # Run client creation in thread pool to avoid blocking
        client_result = await loop.run_in_executor(None, self._create_client)

        if client_result.success:
            self.client = client_result.data
            logger.info("Async client initialized")
            return FlextResult.ok(data=True)
        else:
            logger.error("Async client initialization failed", error=client_result.error)
            return FlextResult.fail(client_result.error)

    def _create_client(self):
        """Create client (runs in thread pool)."""
        return self.api.flext_api_create_client({
            "base_url": self.base_url,
            "timeout": 30
        })

    async def get_async(self, path: str, **kwargs) -> FlextResult[Dict[str, Any]]:
        """Async GET request."""
        if not self.client:
            return FlextResult.fail("Client not initialized")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.client.get, path, kwargs)

        return response

    async def post_async(self, path: str, **kwargs) -> FlextResult[Dict[str, Any]]:
        """Async POST request."""
        if not self.client:
            return FlextResult.fail("Client not initialized")

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, self.client.post, path, kwargs)

        return response

async def concurrent_requests_example():
    """Example of concurrent HTTP requests."""

    client = AsyncFlextApiWrapper("https://httpbin.org")
    init_result = await client.initialize()

    if not init_result.success:
        logger.error("Failed to initialize async client")
        return

    # Create multiple concurrent requests
    tasks = []
    urls = ["/get", "/json", "/headers", "/user-agent", "/ip"]

    for url in urls:
        task = client.get_async(url)
        tasks.append(task)

    logger.info(f"Starting {len(tasks)} concurrent requests")

    # Execute all requests concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful_requests = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Request {i+1} failed with exception", error=str(result))
        elif result.success:
            successful_requests += 1
            logger.info(f"Request {i+1} successful", url=urls[i])
        else:
            logger.error(f"Request {i+1} failed", url=urls[i], error=result.error)

    logger.info(f"Concurrent requests completed: {successful_requests}/{len(tasks)} successful")

# Usage
# asyncio.run(concurrent_requests_example())
```

### **Batch Processing Pattern**

```python
import asyncio
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

@dataclass
class BatchRequest:
    """Request item for batch processing."""
    id: str
    method: str
    path: str
    data: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None

@dataclass
class BatchResult:
    """Result item from batch processing."""
    request_id: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration_ms: float = 0.0

class BatchProcessor:
    """Advanced batch processing for HTTP requests."""

    def __init__(self, base_url: str, max_concurrent: int = 10, timeout: int = 30):
        self.api = create_flext_api()
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.client = None

        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0

    def initialize(self) -> FlextResult[bool]:
        """Initialize the batch processor."""
        client_result = self.api.flext_api_create_client({
            "base_url": self.base_url,
            "timeout": self.timeout,
            "headers": {
                "User-Agent": "FLEXT-BatchProcessor/0.9.0"
            }
        })

        if client_result.success:
            self.client = client_result.data
            logger.info("Batch processor initialized",
                       base_url=self.base_url,
                       max_concurrent=self.max_concurrent)
            return FlextResult.ok(data=True)
        else:
            logger.error("Batch processor initialization failed", error=client_result.error)
            return FlextResult.fail(client_result.error)

    async def process_batch(self, requests: List[BatchRequest],
                          progress_callback: Optional[Callable[[int, int], None]] = None) -> List[BatchResult]:
        """Process a batch of requests with concurrency control."""

        if not self.client:
            raise RuntimeError("Batch processor not initialized")

        logger.info(f"Processing batch of {len(requests)} requests")

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Create tasks for all requests
        tasks = [
            self._process_single_request(semaphore, request, i, len(requests), progress_callback)
            for i, request in enumerate(requests)
        ]

        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        batch_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                batch_results.append(BatchResult(
                    request_id=requests[i].id,
                    success=False,
                    error=f"Exception: {str(result)}"
                ))
                self.failed_requests += 1
            else:
                batch_results.append(result)
                if result.success:
                    self.successful_requests += 1
                else:
                    self.failed_requests += 1

        self.total_requests += len(requests)

        logger.info("Batch processing completed",
                   total=self.total_requests,
                   successful=self.successful_requests,
                   failed=self.failed_requests,
                   success_rate=f"{(self.successful_requests/self.total_requests)*100:.1f}%")

        return batch_results

    async def _process_single_request(self, semaphore: asyncio.Semaphore,
                                    request: BatchRequest,
                                    index: int,
                                    total: int,
                                    progress_callback: Optional[Callable[[int, int], None]]) -> BatchResult:
        """Process a single request with semaphore control."""

        async with semaphore:
            start_time = asyncio.get_event_loop().time()

            try:
                # Execute request in thread pool
                loop = asyncio.get_event_loop()

                if request.method.upper() == "GET":
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.client.get(request.path, params=request.params)
                    )
                elif request.method.upper() == "POST":
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.client.post(request.path, json=request.data, params=request.params)
                    )
                else:
                    return BatchResult(
                        request_id=request.id,
                        success=False,
                        error=f"Unsupported method: {request.method}"
                    )

                duration = (asyncio.get_event_loop().time() - start_time) * 1000

                # Update progress
                if progress_callback:
                    progress_callback(index + 1, total)

                if response.success:
                    return BatchResult(
                        request_id=request.id,
                        success=True,
                        data=response.data,
                        duration_ms=duration
                    )
                else:
                    return BatchResult(
                        request_id=request.id,
                        success=False,
                        error=response.error,
                        duration_ms=duration
                    )

            except Exception as e:
                duration = (asyncio.get_event_loop().time() - start_time) * 1000
                logger.exception(f"Request {request.id} failed")
                return BatchResult(
                    request_id=request.id,
                    success=False,
                    error=str(e),
                    duration_ms=duration
                )

async def batch_processing_example():
    """Example of advanced batch processing."""

    processor = BatchProcessor("https://httpbin.org", max_concurrent=5)
    init_result = processor.initialize()

    if not init_result.success:
        logger.error("Failed to initialize batch processor")
        return

    # Create batch requests
    requests = [
        BatchRequest(id=f"req_{i}", method="GET", path="/get", params={"index": i})
        for i in range(20)
    ]

    # Add some POST requests
    requests.extend([
        BatchRequest(
            id=f"post_{i}",
            method="POST",
            path="/post",
            data={"message": f"Batch message {i}", "timestamp": f"2024-01-{i:02d}"}
        )
        for i in range(1, 6)
    ])

    # Progress callback
    def progress_callback(completed: int, total: int):
        percentage = (completed / total) * 100
        logger.info(f"Progress: {completed}/{total} ({percentage:.1f}%)")

    # Process batch
    results = await processor.process_batch(requests, progress_callback)

    # Analyze results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    if successful:
        avg_duration = sum(r.duration_ms for r in successful) / len(successful)
        logger.info(f"Successful requests: {len(successful)}, avg duration: {avg_duration:.1f}ms")

    if failed:
        logger.warning(f"Failed requests: {len(failed)}")
        for failure in failed[:5]:  # Show first 5 failures
            logger.error(f"Failed request {failure.request_id}: {failure.error}")

# Usage
# asyncio.run(batch_processing_example())
```

---

## 🔄 Advanced Error Handling and Retry Patterns

### **Exponential Backoff with Jitter**

```python
import random
import time
from typing import List, Callable, Any
from flext_api import create_flext_api, FlextApiPlugin
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class AdvancedRetryPlugin(FlextApiPlugin):
    """Advanced retry plugin with exponential backoff and jitter."""

    def __init__(self,
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 jitter: bool = True,
                 retry_conditions: List[Callable[[Any], bool]] = None):

        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retry_conditions = retry_conditions or [
            lambda r: r.get("status_code", 0) in [408, 429, 500, 502, 503, 504],
            lambda r: "timeout" in str(r.get("error", "")).lower(),
            lambda r: "connection" in str(r.get("error", "")).lower()
        ]

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Handle response with advanced retry logic."""

        # Check if retry is needed
        should_retry = any(condition(response) for condition in self.retry_conditions)

        if not should_retry:
            return FlextResult.ok(response)

        # Get retry count from response metadata
        retry_count = response.get("_retry_count", 0)

        if retry_count >= self.max_retries:
            logger.warning("Max retries exceeded",
                          retry_count=retry_count,
                          max_retries=self.max_retries)
            return FlextResult.ok(response)

        # Calculate delay with exponential backoff and jitter
        delay = self._calculate_delay(retry_count)

        logger.info("Retrying request",
                   retry_count=retry_count + 1,
                   max_retries=self.max_retries,
                   delay_seconds=delay)

        # Sleep before retry (in real implementation, this would be handled by the client)
        time.sleep(delay)

        # Mark response for retry
        response["_should_retry"] = True
        response["_retry_count"] = retry_count + 1
        response["_retry_delay"] = delay

        return FlextResult.ok(response)

    def _calculate_delay(self, retry_count: int) -> float:
        """Calculate delay with exponential backoff and optional jitter."""

        # Exponential backoff
        delay = self.base_delay * (self.exponential_base ** retry_count)

        # Apply maximum delay limit
        delay = min(delay, self.max_delay)

        # Add jitter to avoid thundering herd
        if self.jitter:
            # Full jitter: random delay between 0 and calculated delay
            delay = random.uniform(0, delay)

        return delay

class ResilientHttpClient:
    """HTTP client with advanced resilience patterns."""

    def __init__(self, base_url: str):
        self.api = create_flext_api()
        self.base_url = base_url
        self.client = None

        # Resilience plugins
        self.retry_plugin = AdvancedRetryPlugin(
            max_retries=5,
            base_delay=1.0,
            max_delay=30.0,
            exponential_base=2.0,
            jitter=True
        )

        self._initialize_client()

    def _initialize_client(self):
        """Initialize resilient client."""
        client_result = self.api.flext_api_create_client_with_plugins(
            {
                "base_url": self.base_url,
                "timeout": 30,
                "headers": {"User-Agent": "ResilientClient/0.9.0"}
            },
            [self.retry_plugin]
        )

        if client_result.success:
            self.client = client_result.data
            logger.info("Resilient client initialized")
        else:
            logger.error("Client initialization failed", error=client_result.error)
            raise RuntimeError(f"Client initialization failed: {client_result.error}")

    def resilient_request(self, method: str, path: str, **kwargs) -> FlextResult[Dict[str, Any]]:
        """Make resilient request with advanced error handling."""

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                if method.upper() == "GET":
                    response = self.client.get(path, **kwargs)
                elif method.upper() == "POST":
                    response = self.client.post(path, **kwargs)
                else:
                    return FlextResult.fail(f"Unsupported method: {method}")

                if response.success:
                    logger.info("Resilient request successful",
                               method=method,
                               path=path,
                               attempt=attempt + 1)
                    return response

                # Handle specific error cases
                if "timeout" in response.error.lower():
                    logger.warning("Request timeout", attempt=attempt + 1)
                    if attempt < max_attempts - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue

                return response

            except Exception as e:
                logger.exception("Request attempt failed", attempt=attempt + 1)
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    continue
                return FlextResult.fail(f"All attempts failed: {e}")

        return FlextResult.fail("All resilience attempts exhausted")

def resilient_client_example():
    """Example of resilient HTTP client usage."""

    client = ResilientHttpClient("https://httpbin.org")

    # Test with various scenarios
    test_cases = [
        ("GET", "/get", {}),
        ("GET", "/status/500", {}),  # Should trigger retry
        ("GET", "/delay/2", {}),     # Should work with timeout handling
        ("POST", "/post", {"json": {"test": "data"}}),
    ]

    for method, path, kwargs in test_cases:
        logger.info(f"Testing {method} {path}")
        response = client.resilient_request(method, path, **kwargs)

        if response.success:
            logger.info(f"✅ {method} {path} successful")
        else:
            logger.error(f"❌ {method} {path} failed", error=response.error)

# Usage
resilient_client_example()
```

---

## 🎯 Performance Optimization Patterns

### **Connection Pooling and Reuse**

```python
from typing import Dict, Any, Optional
import threading
import time
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class ConnectionPoolManager:
    """Advanced connection pool management."""

    def __init__(self, max_connections: int = 10, connection_timeout: int = 30):
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.pools: Dict[str, Dict[str, Any]] = {}
        self.pool_lock = threading.Lock()
        self.api = create_flext_api()

    def get_client(self, base_url: str, config: Optional[Dict[str, Any]] = None) -> FlextResult[Any]:
        """Get or create HTTP client with connection pooling."""

        with self.pool_lock:
            pool_key = self._generate_pool_key(base_url, config)

            # Check if pool exists and is valid
            if pool_key in self.pools:
                pool_info = self.pools[pool_key]

                # Check if pool is still valid (not expired)
                if time.time() - pool_info["created_at"] < self.connection_timeout:
                    pool_info["last_used"] = time.time()
                    pool_info["usage_count"] += 1

                    logger.debug("Reusing connection from pool",
                               pool_key=pool_key,
                               usage_count=pool_info["usage_count"])

                    return FlextResult.ok(pool_info["client"])
                else:
                    # Pool expired, remove it
                    logger.info("Connection pool expired, creating new", pool_key=pool_key)
                    del self.pools[pool_key]

            # Create new client and add to pool
            client_config = {
                "base_url": base_url,
                "timeout": 30,
                **(config or {})
            }

            client_result = self.api.flext_api_create_client(client_config)

            if client_result.success:
                self.pools[pool_key] = {
                    "client": client_result.data,
                    "created_at": time.time(),
                    "last_used": time.time(),
                    "usage_count": 1,
                    "base_url": base_url,
                    "config": config
                }

                logger.info("New connection pool created",
                           pool_key=pool_key,
                           total_pools=len(self.pools))

                return client_result
            else:
                logger.error("Failed to create pooled client", error=client_result.error)
                return client_result

    def _generate_pool_key(self, base_url: str, config: Optional[Dict[str, Any]]) -> str:
        """Generate unique key for connection pool."""
        config_str = str(sorted((config or {}).items()))
        return f"{base_url}:{hash(config_str)}"

    def cleanup_expired_pools(self):
        """Clean up expired connection pools."""
        with self.pool_lock:
            current_time = time.time()
            expired_keys = [
                key for key, pool_info in self.pools.items()
                if current_time - pool_info["last_used"] > self.connection_timeout
            ]

            for key in expired_keys:
                logger.info("Cleaning up expired pool", pool_key=key)
                del self.pools[key]

            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired pools")

    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        with self.pool_lock:
            stats = {
                "total_pools": len(self.pools),
                "pools": {}
            }

            for key, pool_info in self.pools.items():
                stats["pools"][key] = {
                    "base_url": pool_info["base_url"],
                    "usage_count": pool_info["usage_count"],
                    "age_seconds": time.time() - pool_info["created_at"],
                    "idle_seconds": time.time() - pool_info["last_used"]
                }

            return stats

def connection_pooling_example():
    """Example of connection pooling usage."""

    pool_manager = ConnectionPoolManager(max_connections=5, connection_timeout=60)

    # Make multiple requests to the same base URL
    base_url = "https://httpbin.org"

    for i in range(10):
        client_result = pool_manager.get_client(base_url)

        if client_result.success:
            client = client_result.data
            response = client.get(f"/get?request={i}")

            if response.success:
                logger.info(f"Request {i+1} successful via pooled connection")
            else:
                logger.error(f"Request {i+1} failed", error=response.error)

        # Simulate some delay
        time.sleep(0.1)

    # Show pool statistics
    stats = pool_manager.get_pool_stats()
    logger.info("Connection pool statistics", stats=stats)

    # Cleanup expired pools
    pool_manager.cleanup_expired_pools()

# Usage
connection_pooling_example()
```

### **Request Caching with TTL**

```python
import time
import hashlib
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from flext_api import create_flext_api, FlextApiPlugin
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata."""
    data: Dict[str, Any]
    created_at: float
    ttl: int
    hit_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.ttl

    def access(self) -> Dict[str, Any]:
        self.hit_count += 1
        self.last_accessed = time.time()
        return self.data

class AdvancedCachingPlugin(FlextApiPlugin):
    """Advanced caching plugin with TTL, LRU, and statistics."""

    def __init__(self,
                 ttl: int = 300,
                 max_entries: int = 1000,
                 cache_get: bool = True,
                 cache_post: bool = False):

        self.ttl = ttl
        self.max_entries = max_entries
        self.cache_get = cache_get
        self.cache_post = cache_post
        self.cache: Dict[str, CacheEntry] = {}

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "expired": 0,
            "evictions": 0
        }

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Check cache before making request."""

        method = request_config.get("method", "GET").upper()

        # Only cache GET requests by default
        if method == "GET" and not self.cache_get:
            return FlextResult.ok(request_config)
        if method == "POST" and not self.cache_post:
            return FlextResult.ok(request_config)

        cache_key = self._generate_cache_key(request_config)

        # Check if cached response exists
        if cache_key in self.cache:
            entry = self.cache[cache_key]

            if entry.is_expired():
                logger.debug("Cache entry expired", cache_key=cache_key[:16])
                del self.cache[cache_key]
                self.stats["expired"] += 1
            else:
                # Cache hit
                cached_data = entry.access()
                self.stats["hits"] += 1

                logger.info("Cache hit",
                           cache_key=cache_key[:16],
                           hit_count=entry.hit_count,
                           age_seconds=time.time() - entry.created_at)

                # Return cached response (mark as cached)
                cached_response = {
                    **cached_data,
                    "_from_cache": True,
                    "_cache_key": cache_key,
                    "_cache_age": time.time() - entry.created_at
                }

                # Skip actual request by setting special flag
                request_config["_skip_request"] = True
                request_config["_cached_response"] = cached_response

        self.stats["misses"] += 1
        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Cache successful responses."""

        # Don't cache if request was skipped (cache hit)
        if response.get("_from_cache"):
            return FlextResult.ok(response)

        # Only cache successful responses
        status_code = response.get("status_code", 0)
        if not (200 <= status_code < 300):
            return FlextResult.ok(response)

        # Get original request config from response metadata
        request_config = response.get("_request_config", {})
        method = request_config.get("method", "GET").upper()

        if method == "GET" and self.cache_get:
            self._cache_response(request_config, response)
        elif method == "POST" and self.cache_post:
            self._cache_response(request_config, response)

        return FlextResult.ok(response)

    def _cache_response(self, request_config: Dict[str, Any], response: Dict[str, Any]):
        """Cache the response."""

        cache_key = self._generate_cache_key(request_config)

        # Check if we need to evict entries
        if len(self.cache) >= self.max_entries:
            self._evict_lru_entry()

        # Create cache entry
        cache_data = {
            "status_code": response.get("status_code"),
            "data": response.get("data"),
            "headers": response.get("headers", {})
        }

        entry = CacheEntry(
            data=cache_data,
            created_at=time.time(),
            ttl=self.ttl
        )

        self.cache[cache_key] = entry

        logger.debug("Response cached",
                    cache_key=cache_key[:16],
                    cache_size=len(self.cache),
                    ttl=self.ttl)

    def _generate_cache_key(self, request_config: Dict[str, Any]) -> str:
        """Generate cache key from request configuration."""

        # Create normalized key from method, URL, and parameters
        key_data = {
            "method": request_config.get("method", "GET"),
            "url": request_config.get("url", ""),
            "params": request_config.get("params", {}),
            "headers": {k: v for k, v in request_config.get("headers", {}).items()
                       if k.lower() not in ["authorization", "cookie"]}  # Exclude auth headers
        }

        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _evict_lru_entry(self):
        """Evict least recently used cache entry."""

        if not self.cache:
            return

        # Find LRU entry
        lru_key = min(self.cache.keys(),
                     key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at)

        logger.debug("Evicting LRU cache entry", cache_key=lru_key[:16])
        del self.cache[lru_key]
        self.stats["evictions"] += 1

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""

        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        return {
            **self.stats,
            "cache_size": len(self.cache),
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }

    def clear_cache(self):
        """Clear all cache entries."""
        self.cache.clear()
        logger.info("Cache cleared")

def advanced_caching_example():
    """Example of advanced caching usage."""

    # Create caching plugin
    caching_plugin = AdvancedCachingPlugin(
        ttl=60,  # 60 second TTL
        max_entries=100,
        cache_get=True,
        cache_post=False
    )

    # Create API with caching
    api = create_flext_api()
    client_result = api.flext_api_create_client_with_plugins(
        {
            "base_url": "https://httpbin.org",
            "timeout": 10
        },
        [caching_plugin]
    )

    if not client_result.success:
        logger.error("Failed to create cached client")
        return

    client = client_result.data

    # Make requests to test caching
    test_urls = ["/get", "/json", "/headers", "/get", "/json"]  # Repeat some URLs

    for i, url in enumerate(test_urls):
        logger.info(f"Request {i+1}: {url}")
        response = client.get(url, params={"request": i})

        if response.success:
            is_cached = response.data.get("_from_cache", False)
            cache_age = response.data.get("_cache_age", 0)

            logger.info(f"✅ Request successful",
                       cached=is_cached,
                       cache_age=f"{cache_age:.2f}s" if is_cached else "N/A")
        else:
            logger.error(f"❌ Request failed", error=response.error)

        time.sleep(0.5)  # Small delay between requests

    # Show cache statistics
    stats = caching_plugin.get_cache_stats()
    logger.info("Cache statistics", **stats)

# Usage
advanced_caching_example()
```

---

## 📚 Related Documentation

### **Next Steps**

- **[Integration Examples](integration-examples.md)** - Service integration patterns
- **[API Reference](../api-reference.md)** - Complete API documentation
- **[Architecture Guide](../architecture.md)** - Understanding the system design
- **[Development Guide](../development.md)** - Contributing to the project

### **Advanced Topics**

- **[Configuration](../configuration.md)** - Advanced configuration patterns
- **[Integration](../integration.md)** - Ecosystem integration guide
- **[Troubleshooting](../troubleshooting.md)** - Advanced debugging techniques

---

**Advanced Patterns v0.9.0** - Enterprise usage patterns for FLEXT API HTTP foundation library.
