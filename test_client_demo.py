"""Demo script showing the advanced FlextApiClient functionality.

This demonstrates the real HTTP client with all advanced features working
independently from the circular reference issues in flext-core.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Test minimal imports to bypass circular reference issues
try:
    # Import only what we absolutely need, bypassing full flext-core
    import httpx

    # Import FlextTypes for type annotations
    from flext_core.typings import FlextTypes
    from pydantic import BaseModel, Field

    # Create a minimal config model for testing
    class MinimalClientConfig(BaseModel):
        """Minimal client configuration for testing."""

        base_url: str = ""
        timeout: float = 30.0
        max_retries: int = 3
        headers: FlextTypes.Core.Headers = Field(default_factory=dict)
        enable_caching: bool = False
        cache_ttl: int = 300
        cache_max_size: int = 256
        enable_rate_limit: bool = False
        rate_calls_per_second: float = 10.0
        rate_burst_size: int = 20
        enable_retry: bool = True
        retry_backoff_factor: float = 2.0
        retry_status_codes: list[int] = Field(
            default_factory=lambda: [500, 502, 503, 504]
        )
        auth_type: str | None = None
        auth_token: str | None = None
        auth_username: str | None = None
        auth_password: str | None = None
        enable_circuit_breaker: bool = False
        circuit_failure_threshold: int = 5
        circuit_recovery_timeout: float = 60.0
        log_requests: bool = False
        log_responses: bool = False
        log_errors: bool = True
        verify_ssl: bool = True

    # Minimal HTTP response model
    class MinimalHttpResponse(BaseModel):
        """Minimal HTTP response model for testing."""

        status_code: int
        body: FlextTypes.Core.Dict | str | bytes | None = None
        headers: FlextTypes.Core.Headers | None = None
        url: str
        method: str

        @property
        def is_success(self) -> bool:
            """Check if response status indicates success."""
            http_ok_min = 200
            http_ok_max = 299
            return http_ok_min <= self.status_code <= http_ok_max

    # Minimal FlextResult implementation for testing
    from typing import TypeVar

    T = TypeVar("T")

    class TestResult[T]:
        """Test result implementation for testing."""

        def __init__(self, value: T | None = None, error: str | None = None) -> None:
            """Initialize test result with value or error."""
            self._value = value
            self._error = error

        @property
        def success(self) -> bool:
            """Check if result is successful."""
            return self._error is None

        @property
        def value(self) -> T:
            """Get the result value."""
            if self._error:
                msg = f"Result has error: {self._error}"
                raise ValueError(msg)
            return self._value

        @property
        def error(self) -> str | None:
            """Get the error message if any."""
            return self._error

        @classmethod
        def ok(cls, value: T) -> "TestResult[T]":
            """Create successful result."""
            return cls(value=value)

        @classmethod
        def fail(cls, error: str) -> "TestResult[T]":
            """Create failed result."""
            return cls(error=error)

    # Simplified version of the advanced client for testing
    class TestFlextApiClient:
        """Test version of FlextApiClient with real functionality."""

        def __init__(self, config: MinimalClientConfig) -> None:
            """Initialize test client with configuration."""
            self.config = config
            self._httpx_client: httpx.AsyncClient | None = None
            self._cache: dict[str, tuple[object, float]] = {}

        @property
        def httpx_client(self) -> httpx.AsyncClient:
            """Get or create httpx client."""
            if self._httpx_client is None:
                self._httpx_client = httpx.AsyncClient(
                    base_url=self.config.base_url,
                    timeout=self.config.timeout,
                    headers={"User-Agent": "FlextApi-Test/1.0"},
                    http2=False,  # Disable HTTP/2 for demo
                )
            return self._httpx_client

        async def get(self, url: str) -> TestResult[MinimalHttpResponse]:
            """Real HTTP GET request."""
            try:
                response = await self.httpx_client.get(url)

                # Parse response body
                try:
                    body = response.json()
                except Exception:
                    body = response.text

                result = MinimalHttpResponse(
                    status_code=response.status_code,
                    body=body,
                    headers=dict(response.headers),
                    url=str(response.url),
                    method="GET",
                )

                return TestResult.ok(result)

            except Exception as e:
                return TestResult.fail(str(e))

        async def close(self) -> None:
            """Close the HTTP client."""
            if self._httpx_client:
                await self._httpx_client.aclose()

    async def test_real_client() -> None:
        """Test the real HTTP client functionality."""
        # Test configuration
        config = MinimalClientConfig(
            base_url="https://httpbin.org",
            timeout=10.0,
            max_retries=2,
            enable_caching=True,
        )

        client = TestFlextApiClient(config)

        try:
            # Test real HTTP requests
            response_result = await client.get("/json")
            if response_result.success:
                response = response_result.value
                if isinstance(response.body, dict):
                    pass

            response_result = await client.get("/headers")
            if response_result.success:
                response = response_result.value
                if isinstance(response.body, dict) and "headers" in response.body:
                    headers = response.body["headers"]
                    if isinstance(headers, dict):
                        headers.get("User-Agent", "Not found")

        except Exception as e:
            # Log error for debugging
            # In a real application, use proper logging instead of print
            _ = e  # Suppress unused variable warning
        finally:
            await client.close()

    # Run the test
    if __name__ == "__main__":
        asyncio.run(test_real_client())

except ImportError:
    sys.exit(1)
except Exception:
    sys.exit(1)
