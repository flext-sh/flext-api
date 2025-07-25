#!/usr/bin/env python3
"""FlextApi Universal API Client - Protocol Implementations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Specialized protocol clients for GraphQL, WebSocket, and streaming.
"""

from __future__ import annotations

import asyncio
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import aiohttp
from flext_core import FlextResult, get_logger
from pydantic import BaseModel, Field

from flext_api.client.core import FlextApiClientResponse

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Callable

    from flext_api.client.core import FlextApiClient

logger = get_logger(__name__)


# ==============================================================================
# BASE PROTOCOL CLIENT
# ==============================================================================


class FlextApiProtocolClient(ABC):
    """Abstract base class for protocol-specific clients."""

    def __init__(self, client: FlextApiClient) -> None:
        self.client = client
        self._protocol_metrics: dict[str, Any] = {}

    @abstractmethod
    async def connect(self) -> FlextResult[bool]:
        """Establish protocol-specific connection."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close protocol-specific connection."""

    def get_metrics(self) -> dict[str, Any]:
        """Get protocol metrics."""
        return self._protocol_metrics.copy()


# ==============================================================================
# GRAPHQL CLIENT
# ==============================================================================


class FlextApiGraphQLVariable(BaseModel):
    """GraphQL variable with type information."""

    name: str
    type: str
    value: Any
    required: bool = False


class FlextApiGraphQLQuery(BaseModel):
    """GraphQL query model."""

    query: str
    variables: dict[str, Any] = Field(default_factory=dict)
    operation_name: str | None = None


class FlextApiGraphQLResponse(BaseModel):
    """GraphQL response model."""

    data: dict[str, Any] | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
    extensions: dict[str, Any] = Field(default_factory=dict)

    @property
    def has_errors(self) -> bool:
        """Check if response has errors."""
        return len(self.errors) > 0


@dataclass
class FlextApiGraphQLConfig:
    """Configuration for GraphQL client."""

    endpoint: str = "/graphql"
    introspection_enabled: bool = True
    query_validation: bool = True
    operation_timeout: float = 30.0
    max_query_depth: int = 10
    enable_subscriptions: bool = True
    subscription_endpoint: str = "/graphql/ws"


class FlextApiGraphQLClient(FlextApiProtocolClient):
    """GraphQL client with introspection and subscription support."""

    def __init__(
        self, client: FlextApiClient, config: FlextApiGraphQLConfig | None = None
    ) -> None:
        super().__init__(client)
        self.config = config or FlextApiGraphQLConfig()
        self._schema: dict[str, Any] | None = None
        self._subscription_ws: aiohttp.ClientWebSocketResponse | None = None
        self._subscription_callbacks: dict[str, Callable[[dict[str, Any]], None]] = {}

    async def connect(self) -> FlextResult[bool]:
        """Connect and optionally fetch schema."""
        if self.config.introspection_enabled:
            schema_result = await self.introspect()
            if not schema_result.success:
                logger.warning(
                    f"Failed to introspect GraphQL schema: {schema_result.message}"
                )

        return FlextResult.ok(True)

    async def disconnect(self) -> None:
        """Disconnect GraphQL client."""
        if self._subscription_ws and not self._subscription_ws.closed:
            await self._subscription_ws.close()

    async def query(
        self,
        query: str | FlextApiGraphQLQuery,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> FlextResult[FlextApiGraphQLResponse]:
        """Execute GraphQL query."""
        start_time = time.time()

        try:
            # Prepare query payload
            if isinstance(query, str):
                query_obj = FlextApiGraphQLQuery(
                    query=query,
                    variables=variables or {},
                    operation_name=operation_name,
                )
            else:
                query_obj = query

            # Validate query if enabled
            if self.config.query_validation and self._schema:
                validation_result = self._validate_query(query_obj)
                if not validation_result.success:
                    return FlextResult.fail(
                        f"Query validation failed: {validation_result.message}"
                    )

            # Prepare request payload
            payload = {
                "query": query_obj.query,
                "variables": query_obj.variables,
            }

            if query_obj.operation_name:
                payload["operationName"] = query_obj.operation_name

            # Execute HTTP request
            response = await self.client.post(
                self.config.endpoint,
                json=payload,
                timeout=self.config.operation_timeout,
            )

            if not response.success:
                return FlextResult.fail(
                    f"GraphQL request failed: {response.message}", response.data
                )

            # Parse GraphQL response
            http_response = response.data

            try:
                if http_response.json_data:
                    graphql_response = FlextApiGraphQLResponse(
                        **http_response.json_data
                    )
                else:
                    return FlextResult.fail("Invalid GraphQL response: no JSON data")
            except Exception as e:
                return FlextResult.fail(f"Failed to parse GraphQL response: {e}")

            # Update metrics
            execution_time = (time.time() - start_time) * 1000
            self._protocol_metrics["total_queries"] = (
                self._protocol_metrics.get("total_queries", 0) + 1
            )

            if graphql_response.has_errors:
                self._protocol_metrics["failed_queries"] = (
                    self._protocol_metrics.get("failed_queries", 0) + 1
                )
                return FlextResult.fail(
                    "GraphQL query returned errors", graphql_response
                )
            self._protocol_metrics["successful_queries"] = (
                self._protocol_metrics.get("successful_queries", 0) + 1
            )

            self._protocol_metrics["average_query_time"] = (
                self._protocol_metrics.get("total_query_time", 0) + execution_time
            ) / self._protocol_metrics["total_queries"]

            return FlextResult.ok(graphql_response)

        except Exception as e:
            logger.exception(f"GraphQL query error: {e}")
            self._protocol_metrics["query_exceptions"] = (
                self._protocol_metrics.get("query_exceptions", 0) + 1
            )
            return FlextResult.fail(f"GraphQL query exception: {e}")

    async def mutation(
        self,
        mutation: str | FlextApiGraphQLQuery,
        variables: dict[str, Any] | None = None,
    ) -> FlextResult[FlextApiGraphQLResponse]:
        """Execute GraphQL mutation."""
        if isinstance(mutation, str):
            mutation_obj = FlextApiGraphQLQuery(
                query=mutation, variables=variables or {}
            )
        else:
            mutation_obj = mutation

        return await self.query(mutation_obj)

    async def subscription(
        self,
        subscription: str | FlextApiGraphQLQuery,
        callback: Callable[[FlextApiGraphQLResponse], None],
        variables: dict[str, Any] | None = None,
    ) -> FlextResult[str]:
        """Start GraphQL subscription."""
        if not self.config.enable_subscriptions:
            return FlextResult.fail("Subscriptions are disabled")

        try:
            # Initialize WebSocket connection if needed
            if not self._subscription_ws or self._subscription_ws.closed:
                await self._init_subscription_ws()

            if isinstance(subscription, str):
                sub_obj = FlextApiGraphQLQuery(
                    query=subscription, variables=variables or {}
                )
            else:
                sub_obj = subscription

            # Generate subscription ID
            sub_id = f"sub_{len(self._subscription_callbacks)}_{int(time.time())}"

            # Send subscription start message
            start_message = {
                "id": sub_id,
                "type": "start",
                "payload": {
                    "query": sub_obj.query,
                    "variables": sub_obj.variables,
                },
            }

            await self._subscription_ws.send_str(json.dumps(start_message))

            # Store callback
            self._subscription_callbacks[sub_id] = callback

            # Start message handler if not already running
            if len(self._subscription_callbacks) == 1:
                self._message_handler_task = asyncio.create_task(
                    self._handle_subscription_messages()
                )

            self._protocol_metrics["active_subscriptions"] = len(
                self._subscription_callbacks
            )

            return FlextResult.ok(sub_id)

        except Exception as e:
            logger.exception(f"Subscription error: {e}")
            return FlextResult.fail(f"Failed to start subscription: {e}")

    async def unsubscribe(self, subscription_id: str) -> FlextResult[bool]:
        """Stop GraphQL subscription."""
        if subscription_id not in self._subscription_callbacks:
            return FlextResult.fail(f"Subscription {subscription_id} not found")

        try:
            # Send stop message
            if self._subscription_ws and not self._subscription_ws.closed:
                stop_message = {"id": subscription_id, "type": "stop"}
                await self._subscription_ws.send_str(json.dumps(stop_message))

            # Remove callback
            del self._subscription_callbacks[subscription_id]
            self._protocol_metrics["active_subscriptions"] = len(
                self._subscription_callbacks
            )

            return FlextResult.ok(True)

        except Exception as e:
            logger.exception(f"Unsubscribe error: {e}")
            return FlextResult.fail(f"Failed to unsubscribe: {e}")

    async def introspect(self) -> FlextResult[dict[str, Any]]:
        """Perform GraphQL introspection."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
                subscriptionType { name }
                types {
                    ...FullType
                }
                directives {
                    name
                    description
                    locations
                    args {
                        ...InputValue
                    }
                }
            }
        }

        fragment FullType on __Type {
            kind
            name
            description
            fields(includeDeprecated: true) {
                name
                description
                args {
                    ...InputValue
                }
                type {
                    ...TypeRef
                }
                isDeprecated
                deprecationReason
            }
            inputFields {
                ...InputValue
            }
            interfaces {
                ...TypeRef
            }
            enumValues(includeDeprecated: true) {
                name
                description
                isDeprecated
                deprecationReason
            }
            possibleTypes {
                ...TypeRef
            }
        }

        fragment InputValue on __InputValue {
            name
            description
            type { ...TypeRef }
            defaultValue
        }

        fragment TypeRef on __Type {
            kind
            name
            ofType {
                kind
                name
                ofType {
                    kind
                    name
                    ofType {
                        kind
                        name
                    }
                }
            }
        }
        """

        result = await self.query(introspection_query)

        if result.success:
            self._schema = result.data.data
            logger.info("GraphQL schema introspection completed")

        return result

    async def _init_subscription_ws(self) -> None:
        """Initialize WebSocket connection for subscriptions."""
        if not self.client.get_session():
            await self.client.ensure_session()

        ws_url = f"{self.client.config.base_url}{self.config.subscription_endpoint}"
        session = self.client.get_session()
        if not session:
            raise RuntimeError("Client session not available")
        self._subscription_ws = await session.ws_connect(
            ws_url, protocols=["graphql-ws"]
        )

        # Send connection init message
        init_message = {"type": "connection_init"}
        await self._subscription_ws.send_str(json.dumps(init_message))

        # Wait for connection ack
        ack_msg = await self._subscription_ws.receive()
        if ack_msg.type == aiohttp.WSMsgType.TEXT:
            ack_data = json.loads(ack_msg.data)
            if ack_data.get("type") != "connection_ack":
                raise ConnectionError(f"WebSocket connection failed: {ack_data}")

    async def _handle_subscription_messages(self) -> None:
        """Handle incoming WebSocket messages for subscriptions."""
        try:
            while self._subscription_ws and not self._subscription_ws.closed:
                msg = await self._subscription_ws.receive()

                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        msg_type = data.get("type")
                        msg_id = data.get("id")

                        if (
                            msg_type == "data"
                            and msg_id in self._subscription_callbacks
                        ):
                            # Create GraphQL response
                            graphql_response = FlextApiGraphQLResponse(
                                **data.get("payload", {})
                            )

                            # Call callback
                            callback = self._subscription_callbacks[msg_id]
                            callback(graphql_response)

                        elif msg_type == "error":
                            logger.error(f"Subscription error: {data}")

                        elif msg_type == "complete":
                            # Subscription completed
                            if msg_id in self._subscription_callbacks:
                                del self._subscription_callbacks[msg_id]

                    except json.JSONDecodeError:
                        logger.exception(
                            f"Invalid JSON in WebSocket message: {msg.data}"
                        )

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(
                        f"WebSocket error: {self._subscription_ws.exception()}"
                    )
                    break

                elif msg.type == aiohttp.WSMsgType.CLOSE:
                    logger.info("WebSocket connection closed")
                    break

        except Exception as e:
            logger.exception(f"Subscription message handler error: {e}")
        finally:
            # Clean up callbacks
            self._subscription_callbacks.clear()

    def _validate_query(self, query: FlextApiGraphQLQuery) -> FlextResult[bool]:
        """Validate GraphQL query against schema."""
        # Basic query depth validation
        query_depth = self._calculate_query_depth(query.query)
        if query_depth > self.config.max_query_depth:
            return FlextResult.fail(
                f"Query depth {query_depth} exceeds maximum {self.config.max_query_depth}"
            )

        # Additional validation could be added here
        return FlextResult.ok(True)

    def _calculate_query_depth(self, query: str) -> int:
        """Calculate approximate query depth."""
        # Simple depth calculation based on nested braces
        max_depth = 0
        current_depth = 0

        for char in query:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        return max_depth


# ==============================================================================
# WEBSOCKET CLIENT
# ==============================================================================


@dataclass
class FlextApiWebSocketConfig:
    """Configuration for WebSocket client."""

    endpoint: str = "/ws"
    protocols: list[str] = field(default_factory=list)
    heartbeat_interval: float = 30.0
    max_message_size: int = 1024 * 1024  # 1MB
    compression: bool = True
    auto_reconnect: bool = True
    max_reconnect_attempts: int = 5
    reconnect_delay: float = 2.0


class FlextApiWebSocketMessage(BaseModel):
    """WebSocket message model."""

    type: str
    data: Any = None
    timestamp: float = Field(default_factory=time.time)
    message_id: str | None = None


class FlextApiWebSocketClient(FlextApiProtocolClient):
    """WebSocket client with auto-reconnect and message handling."""

    def __init__(
        self, client: FlextApiClient, config: FlextApiWebSocketConfig | None = None
    ) -> None:
        super().__init__(client)
        self.config = config or FlextApiWebSocketConfig()
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._message_handlers: dict[
            str, Callable[[FlextApiWebSocketMessage], None]
        ] = {}
        self._heartbeat_task: asyncio.Task | None = None
        self._message_handler_task: asyncio.Task | None = None
        self._reconnect_attempts = 0
        self._connected = False

    async def connect(self) -> FlextResult[bool]:
        """Connect to WebSocket endpoint."""
        try:
            if not self.client.get_session():
                await self.client.ensure_session()

            ws_url = f"{self.client.config.base_url}{self.config.endpoint}"

            session = self.client.get_session()
            if not session:
                raise RuntimeError("Client session not available")
            self._ws = await session.ws_connect(
                ws_url,
                protocols=self.config.protocols,
                max_msg_size=self.config.max_message_size,
                compress=self.config.compression,
            )

            self._connected = True
            self._reconnect_attempts = 0

            # Start message handler
            self._message_handler_task = asyncio.create_task(self._handle_messages())

            # Start heartbeat if configured
            if self.config.heartbeat_interval > 0:
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            self._protocol_metrics["connections"] = (
                self._protocol_metrics.get("connections", 0) + 1
            )
            logger.info(f"WebSocket connected to {ws_url}")

            return FlextResult.ok(True)

        except Exception as e:
            logger.exception(f"WebSocket connection error: {e}")
            return FlextResult.fail(f"Failed to connect: {e}")

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        self._connected = False

        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        if self._message_handler_task:
            self._message_handler_task.cancel()

        if self._ws and not self._ws.closed:
            await self._ws.close()

        logger.info("WebSocket disconnected")

    async def send_message(
        self, message: FlextApiWebSocketMessage | dict[str, Any] | str
    ) -> FlextResult[bool]:
        """Send message through WebSocket."""
        if not self._connected or not self._ws or self._ws.closed:
            return FlextResult.fail("WebSocket not connected")

        try:
            if isinstance(message, FlextApiWebSocketMessage):
                data = message.model_dump()
            elif isinstance(message, dict):
                data = message
            else:
                data = {"type": "text", "data": message}

            await self._ws.send_str(json.dumps(data))

            self._protocol_metrics["messages_sent"] = (
                self._protocol_metrics.get("messages_sent", 0) + 1
            )

            return FlextResult.ok(True)

        except Exception as e:
            logger.exception(f"Send message error: {e}")
            return FlextResult.fail(f"Failed to send message: {e}")

    def add_message_handler(
        self, message_type: str, handler: Callable[[FlextApiWebSocketMessage], None]
    ) -> None:
        """Add message handler for specific message type."""
        self._message_handlers[message_type] = handler
        logger.debug(f"Added message handler for type: {message_type}")

    def remove_message_handler(self, message_type: str) -> None:
        """Remove message handler."""
        if message_type in self._message_handlers:
            del self._message_handlers[message_type]
            logger.debug(f"Removed message handler for type: {message_type}")

    async def _handle_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        try:
            while self._connected and self._ws and not self._ws.closed:
                msg = await self._ws.receive()

                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        ws_message = FlextApiWebSocketMessage(**data)

                        # Call appropriate handler
                        handler = self._message_handlers.get(ws_message.type)
                        if handler:
                            handler(ws_message)
                        else:
                            logger.debug(
                                f"No handler for message type: {ws_message.type}"
                            )

                        self._protocol_metrics["messages_received"] = (
                            self._protocol_metrics.get("messages_received", 0) + 1
                        )

                    except (json.JSONDecodeError, ValueError) as e:
                        logger.exception(f"Invalid message format: {e}")

                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {self._ws.exception()}")
                    break

                elif msg.type == aiohttp.WSMsgType.CLOSE:
                    logger.info("WebSocket connection closed by server")
                    break

        except Exception as e:
            logger.exception(f"Message handler error: {e}")

        # Handle reconnection if enabled
        if self.config.auto_reconnect and self._connected:
            await self._attempt_reconnect()

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeat messages."""
        try:
            while self._connected:
                await asyncio.sleep(self.config.heartbeat_interval)

                if self._connected and self._ws and not self._ws.closed:
                    heartbeat_msg = FlextApiWebSocketMessage(
                        type="heartbeat", data={"timestamp": time.time()}
                    )
                    await self.send_message(heartbeat_msg)

        except asyncio.CancelledError:
            logger.debug("Heartbeat loop cancelled")
        except Exception as e:
            logger.exception(f"Heartbeat error: {e}")

    async def _attempt_reconnect(self) -> None:
        """Attempt to reconnect WebSocket."""
        if self._reconnect_attempts >= self.config.max_reconnect_attempts:
            logger.error(
                f"Max reconnect attempts ({self.config.max_reconnect_attempts}) reached"
            )
            return

        self._reconnect_attempts += 1
        delay = self.config.reconnect_delay * self._reconnect_attempts

        logger.info(
            f"Attempting reconnect {self._reconnect_attempts}/{self.config.max_reconnect_attempts} in {delay}s"
        )

        await asyncio.sleep(delay)

        result = await self.connect()
        if not result.success:
            logger.error(
                f"Reconnect attempt {self._reconnect_attempts} failed: {result.message}"
            )


# ==============================================================================
# STREAMING CLIENT
# ==============================================================================


@dataclass
class FlextApiStreamingConfig:
    """Configuration for streaming client."""

    chunk_size: int = 8192
    buffer_size: int = 1024 * 1024  # 1MB
    timeout: float = 60.0
    content_types: list[str] = field(
        default_factory=lambda: [
            "application/json",
            "text/plain",
            "application/x-ndjson",
        ]
    )


class FlextApiStreamingClient(FlextApiProtocolClient):
    """Streaming client for large data transfers."""

    def __init__(
        self, client: FlextApiClient, config: FlextApiStreamingConfig | None = None
    ) -> None:
        super().__init__(client)
        self.config = config or FlextApiStreamingConfig()

    async def connect(self) -> FlextResult[bool]:
        """Streaming client doesn't need persistent connection."""
        return FlextResult.ok(True)

    async def disconnect(self) -> None:
        """Streaming client cleanup."""

    async def stream_download(
        self, url: str, callback: Callable[[bytes], None], **kwargs: object
    ) -> FlextResult[int]:
        """Stream download with callback for each chunk."""
        start_time = time.time()
        total_bytes = 0

        try:
            if not self.client.get_session():
                await self.client.ensure_session()

            session_kwargs = {
                "method": "GET",
                "url": self.client.build_full_url(url),
                "timeout": aiohttp.ClientTimeout(total=self.config.timeout),
                **kwargs,
            }

            session = self.client.get_session()
            if not session:
                raise RuntimeError("Client session not available")
            async with session.request(**session_kwargs) as response:
                if response.status != 200:
                    return FlextResult.fail(
                        f"HTTP {response.status}: {await response.text()}"
                    )

                async for chunk in response.content.iter_chunked(
                    self.config.chunk_size
                ):
                    callback(chunk)
                    total_bytes += len(chunk)

                    # Update metrics
                    self._protocol_metrics["bytes_downloaded"] = (
                        self._protocol_metrics.get("bytes_downloaded", 0) + len(chunk)
                    )

            # Update final metrics
            execution_time = (time.time() - start_time) * 1000
            self._protocol_metrics["download_requests"] = (
                self._protocol_metrics.get("download_requests", 0) + 1
            )
            self._protocol_metrics["average_download_time"] = (
                self._protocol_metrics.get("total_download_time", 0) + execution_time
            ) / self._protocol_metrics["download_requests"]

            logger.info(
                f"Stream download completed: {total_bytes} bytes in {execution_time:.2f}ms"
            )

            return FlextResult.ok(total_bytes)

        except Exception as e:
            logger.exception(f"Stream download error: {e}")
            return FlextResult.fail(f"Download failed: {e}")

    async def stream_upload(
        self,
        url: str,
        data_stream: AsyncIterator[bytes],
        content_type: str = "application/octet-stream",
        **kwargs: object,
    ) -> FlextResult[FlextApiClientResponse]:
        """Stream upload from async iterator."""
        start_time = time.time()
        total_bytes = 0

        try:
            if not self.client.get_session():
                await self.client.ensure_session()

            # Collect chunks into buffer
            chunks = []
            async for chunk in data_stream:
                chunks.append(chunk)
                total_bytes += len(chunk)

            data = b"".join(chunks)

            session_kwargs = {
                "method": "POST",
                "url": self.client.build_full_url(url),
                "data": data,
                "headers": {"Content-Type": content_type},
                "timeout": aiohttp.ClientTimeout(total=self.config.timeout),
                **kwargs,
            }

            session = self.client.get_session()
            if not session:
                raise RuntimeError("Client session not available")
            async with session.request(**session_kwargs) as response:
                # Build response
                result_response = FlextApiClientResponse(
                    status_code=response.status,
                    headers=dict(response.headers),
                    text=await response.text(),
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

                # Try to parse JSON
                try:
                    result_response.json_data = await response.json()
                    result_response.data = result_response.json_data
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    result_response.data = result_response.text

                # Update metrics
                self._protocol_metrics["bytes_uploaded"] = (
                    self._protocol_metrics.get("bytes_uploaded", 0) + total_bytes
                )
                self._protocol_metrics["upload_requests"] = (
                    self._protocol_metrics.get("upload_requests", 0) + 1
                )

                if 200 <= response.status < 300:
                    logger.info(f"Stream upload completed: {total_bytes} bytes")
                    return FlextResult.ok(result_response)
                return FlextResult.fail(
                    f"Upload failed: HTTP {response.status}", result_response
                )

        except Exception as e:
            logger.exception(f"Stream upload error: {e}")
            return FlextResult.fail(f"Upload failed: {e}")

    async def stream_json_lines(
        self, url: str, callback: Callable[[dict[str, Any]], None], **kwargs: object
    ) -> FlextResult[int]:
        """Stream JSON lines format (NDJSON)."""
        lines_processed = 0
        buffer = ""

        def process_chunk(chunk: bytes) -> None:
            nonlocal buffer, lines_processed

            # Decode chunk and add to buffer
            text = chunk.decode("utf-8")
            buffer += text

            # Process complete lines
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()

                if line:
                    try:
                        json_obj = json.loads(line)
                        callback(json_obj)
                        lines_processed += 1
                    except json.JSONDecodeError as e:
                        logger.exception(
                            f"Invalid JSON line: {line[:100]}... Error: {e}"
                        )

        result = await self.stream_download(url, process_chunk, **kwargs)

        if result.success:
            # Process any remaining buffer
            if buffer.strip():
                try:
                    json_obj = json.loads(buffer.strip())
                    callback(json_obj)
                    lines_processed += 1
                except json.JSONDecodeError:
                    logger.exception(f"Invalid JSON in final buffer: {buffer[:100]}...")

            self._protocol_metrics["json_lines_processed"] = (
                self._protocol_metrics.get("json_lines_processed", 0) + lines_processed
            )

            return FlextResult.ok(lines_processed)

        return result
