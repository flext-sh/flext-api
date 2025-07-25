#!/usr/bin/env python3
"""FlextApi Basic Client Usage Examples.

This example demonstrates the massive code reduction achieved with FlextApi Universal Client
compared to traditional approaches.
"""

import asyncio
import contextlib
from typing import Any

from flext_api import (
    FlextApiClient,
    FlextApiClientBuilder,
    flext_api_client_context,
    flext_api_create_client,
)

# ==============================================================================
# EXAMPLE 1: TRADITIONAL APPROACH VS FLEXT-API (90% CODE REDUCTION)
# ==============================================================================

async def traditional_approach_example():
    """Traditional HTTP client code - verbose and error-prone."""
    import asyncio
    import json
    import time
    from typing import Optional

    import aiohttp

    # Traditional approach requires ~50 lines for basic functionality
    session: aiohttp.ClientSession | None = None
    retries = 3
    timeout = 30.0
    base_url = "https://api.example.com"

    try:
        # Manual session management
        connector = aiohttp.TCPConnector(limit=100, enable_cleanup_closed=True)
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        session = aiohttp.ClientSession(connector=connector, timeout=timeout_config)

        # Manual retry logic with exponential backoff
        for attempt in range(retries):
            try:
                start_time = time.time()
                async with session.get(f"{base_url}/users/123") as response:
                    if response.status == 200:
                        data = await response.json()
                        (time.time() - start_time) * 1000
                        return data
                    if response.status in [408, 429, 500, 502, 503, 504] and attempt < retries - 1:
                        delay = 2 ** attempt  # Exponential backoff
                        await asyncio.sleep(delay)
                        continue
                    error_text = await response.text()
                    raise Exception(f"HTTP {response.status}: {error_text}")

            except (TimeoutError, aiohttp.ClientError) as e:
                if attempt < retries - 1:
                    delay = 2 ** attempt
                    await asyncio.sleep(delay)
                    continue
                raise Exception(f"Request failed after {retries} attempts: {e}")

    finally:
        if session:
            await session.close()


async def flext_api_approach_example():
    """FlextApi approach - clean, concise, and robust."""
    # FlextApi approach requires only ~5 lines for same functionality + more features!
    async with flext_api_client_context("https://api.example.com") as client:
        result = await client.get("/users/123")
        if result.success:
            return result.data.json_data
    return None


# ==============================================================================
# EXAMPLE 2: ENTERPRISE FEATURES WITH ZERO BOILERPLATE
# ==============================================================================

async def enterprise_features_example() -> None:
    """Demonstrate enterprise features with minimal code."""
    # Single builder call enables ALL enterprise features
    client = (FlextApiClientBuilder()
              .with_base_url("https://api.example.com")
              .with_auth_token("bearer-token-123")
              .with_caching(enabled=True, ttl=600)
              .with_circuit_breaker(enabled=True, failure_threshold=3)
              .with_retries(max_retries=5, delay=1.0)
              .with_http2(enabled=True)
              .with_observability(metrics=True, tracing=True)
              .build())

    async with client:
        # All requests automatically get:
        # - Authentication (Bearer token)
        # - Caching (10 minutes TTL)
        # - Circuit breaker protection
        # - Intelligent retries with exponential backoff
        # - HTTP/2 support
        # - Comprehensive metrics and tracing
        # - Request/response validation
        # - Structured logging

        # Multiple parallel requests with automatic connection pooling
        tasks = [
            client.get("/users/1"),
            client.get("/users/2"),
            client.post("/orders", json={"item": "laptop", "quantity": 1}),
            client.get("/products?category=electronics"),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for _i, result in enumerate(results):
            if isinstance(result, Exception) or result.success:
                pass
            else:
                pass

        # Get comprehensive health and metrics
        client.get_health()
        client.get_metrics()



# ==============================================================================
# EXAMPLE 3: PROTOCOL-SPECIFIC CLIENTS
# ==============================================================================

async def protocol_clients_example() -> None:
    """Demonstrate GraphQL, WebSocket, and Streaming clients."""
    client = flext_api_create_client("https://api.example.com")

    async with client:
        # GraphQL client with zero additional setup
        from flext_api import FlextApiGraphQLClient

        graphql = FlextApiGraphQLClient(client)
        await graphql.connect()  # Auto-introspection

        # Execute GraphQL query
        query_result = await graphql.query("""
            query GetUser($id: ID!) {
                user(id: $id) {
                    name
                    email
                    posts {
                        title
                        content
                    }
                }
            }
        """, variables={"id": "123"})

        if query_result.success:
            pass

        # WebSocket client with auto-reconnect
        from flext_api import FlextApiWebSocketClient

        websocket = FlextApiWebSocketClient(client)
        await websocket.connect()

        # Add message handlers
        def handle_notification(message) -> None:
            pass

        websocket.add_message_handler("notification", handle_notification)

        # Send message
        await websocket.send_message({
            "type": "subscribe",
            "channel": "user_updates",
            "user_id": "123"
        })

        # Streaming client for large data
        from flext_api import FlextApiStreamingClient

        streaming = FlextApiStreamingClient(client)

        def process_chunk(chunk: bytes) -> None:
            pass

        # Stream large file download
        download_result = await streaming.stream_download(
            "/large-dataset.json",
            callback=process_chunk
        )

        if download_result.success:
            pass


# ==============================================================================
# EXAMPLE 4: PLUGIN SYSTEM FOR CUSTOM FUNCTIONALITY
# ==============================================================================

async def plugin_system_example() -> None:
    """Demonstrate extensible plugin system."""
    from flext_api import (
        FlextApiCachingPlugin,
        FlextApiLoggingPlugin,
        FlextApiMetricsPlugin,
        FlextApiPlugin,
        FlextApiRetryPlugin,
    )

    # Custom plugin example
    class CustomValidationPlugin(FlextApiPlugin):
        async def before_request(self, request) -> None:
            # Add custom validation logic
            if "api_key" not in request.headers:
                request.headers["api_key"] = "default-key"

        async def after_request(self, request, response) -> None:
            # Log successful responses to custom system
            pass

        async def on_error(self, request, response) -> None:
            # Custom error handling
            pass

    # Build client with multiple plugins
    client = (FlextApiClientBuilder()
              .with_base_url("https://api.example.com")
              .with_plugin(FlextApiLoggingPlugin())  # Comprehensive logging
              .with_plugin(FlextApiRetryPlugin())    # Intelligent retries
              .with_plugin(FlextApiCachingPlugin())  # Response caching
              .with_plugin(FlextApiMetricsPlugin())  # Performance metrics
              .with_plugin(CustomValidationPlugin()) # Custom logic
              .build())

    async with client:
        # All plugins automatically execute in order
        await client.get("/protected-endpoint")

        # Get plugin-specific metrics
        for plugin in client._plugins:
            plugin.get_metrics()


# ==============================================================================
# MAIN DEMO
# ==============================================================================

async def main() -> None:
    """Run all examples to demonstrate code reduction."""
    with contextlib.suppress(Exception):
        await flext_api_approach_example()


    with contextlib.suppress(Exception):
        await enterprise_features_example()


    with contextlib.suppress(Exception):
        await protocol_clients_example()


    with contextlib.suppress(Exception):
        await plugin_system_example()



if __name__ == "__main__":
    asyncio.run(main())
