"""WebSocket connection manager for real-time communication.

This module implements WebSocket connection management functionality
for real-time pipeline monitoring and system event broadcasting.

Module provides:
- Connection lifecycle management
- Subscription management
- Broadcast capabilities

Note:
----
    Supports real-time pipeline updates and system monitoring events.

"""

from fastapi import WebSocket
from websockets.exceptions import ConnectionClosed

# ZERO TOLERANCE - Use high-performance msgspec instead of standard library JSON
from flext_core.serialization.msgspec_adapters import get_serializer
from flext_observability.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    """ConnectionManager - Resource Manager.

    Gerencia recursos e lifecycle de componentes específicos.
    Implementa padrões de gestão de recursos enterprise.

    Arquitetura: Enterprise Patterns
    Padrões: SOLID principles, clean code

    Attributes:
    ----------
    Sem atributos públicos documentados.

    Methods:
    -------
    startup(): Inicia operação
    shutdown(): Método específico da classe
    connect(): Método específico da classe
    disconnect(): Método específico da classe
    send_personal_message(): Método específico da classe
    broadcast(): Método específico da classe
    broadcast_to_subscribers(): Método específico da classe
    subscribe(): Método específico da classe
    unsubscribe(): Método específico da classe
    get_connection_count(): Obtém dados
    get_subscriber_count(): Obtém dados

    Examples:
    --------
    Uso típico da classe:

    ```python
    instance = ConnectionManager()
    result = instance.method()
    ```

    See Also:
    --------
    - [Documentação da Arquitetura](../../docs/architecture/index.md)
    - [Padrões de Design](../../docs/architecture/001-clean-architecture-ddd.md)

    Note:
    ----
    Esta classe segue os padrões Enterprise Patterns estabelecidos no projeto.

    """

    def __init__(self) -> None:
        """Initialize the ConnectionManager."""
        self._active_connections: dict[str, WebSocket] = {}
        self._subscriptions: dict[str, set[str]] = {}
        self.logger = logger.bind(component="ws_manager")
        # High-performance serializer for WebSocket messages
        self._serializer = get_serializer()

    async def startup(self) -> None:
        """Start the WebSocket manager."""
        self.logger.info("WebSocket manager starting up")

    async def shutdown(self) -> None:
        """Shutdown the WebSocket manager."""
        self.logger.info("WebSocket manager shutting down")

        # Close all connections
        for client_id in list(self._active_connections.keys()):
            await self.disconnect(client_id)

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        """Connect a new WebSocket client."""
        await websocket.accept()
        self._active_connections[client_id] = websocket
        self.logger.info("Client connected", client_id=client_id)

        # Send welcome message using high-performance msgspec serialization
        welcome_msg = {
            "type": "connected",
            "message": "Welcome to FLEXT WebSocket",
            "client_id": client_id,
        }
        await self.send_personal_message(
            self._serializer.encode_json_str(welcome_msg),
            client_id,
        )

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a WebSocket client."""
        if client_id in self._active_connections:
            del self._active_connections[client_id]

            # Remove all subscriptions
            self._subscriptions.pop(client_id, None)

            self.logger.info("Client disconnected", client_id=client_id)

    async def send_personal_message(self, message: str, client_id: str) -> None:
        """Send a message to a specific client."""
        if client_id in self._active_connections:
            websocket = self._active_connections[client_id]
            try:
                await websocket.send_text(message)
            except (ConnectionClosed, RuntimeError, OSError) as e:
                self.logger.exception(
                    "Failed to send message",
                    client_id=client_id,
                    error=str(e),
                )
                await self.disconnect(client_id)

    async def broadcast(self, message: str) -> None:
        """Broadcast a message to all connected clients."""
        disconnected: list[str] = []

        for client_id, websocket in self._active_connections.items():
            try:
                await websocket.send_text(message)
            except (ConnectionClosed, RuntimeError, OSError) as e:
                self.logger.exception(
                    "Failed to broadcast message",
                    client_id=client_id,
                    error=str(e),
                )
                disconnected.append(client_id)

        # Remove disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def broadcast_to_subscribers(self, event_type: str, message: str) -> None:
        """Broadcast a message to subscribers of a specific event type."""
        disconnected: list[str] = []

        for client_id, subscriptions in self._subscriptions.items():
            if event_type in subscriptions or "*" in subscriptions:
                try:
                    await self.send_personal_message(message, client_id)
                except (ConnectionClosed, RuntimeError, OSError) as e:
                    self.logger.exception(
                        "Failed to send message to subscriber",
                        client_id=client_id,
                        event_type=event_type,
                        error=str(e),
                    )
                    disconnected.append(client_id)

        # Remove disconnected clients
        for client_id in disconnected:
            await self.disconnect(client_id)

    async def subscribe(self, client_id: str, event_type: str) -> None:
        """Subscribe a client to an event type."""
        if client_id not in self._subscriptions:
            self._subscriptions[client_id] = set()

        self._subscriptions[client_id].add(event_type)

        self.logger.info(
            "Client subscribed",
            client_id=client_id,
            event_type=event_type,
        )

        # Send confirmation - using high-performance msgspec
        serializer = get_serializer()
        await self.send_personal_message(
            serializer.encode_json_str(
                {
                    "type": "subscribed",
                    "event": event_type,
                },
            ),
            client_id,
        )

    async def unsubscribe(self, client_id: str, event_type: str) -> None:
        """Unsubscribe a client from an event type."""
        if client_id in self._subscriptions:
            self._subscriptions[client_id].discard(event_type)

            self.logger.info(
                "Client unsubscribed",
                client_id=client_id,
                event_type=event_type,
            )

            # Send confirmation - using high-performance msgspec
            serializer = get_serializer()
            await self.send_personal_message(
                serializer.encode_json_str(
                    {
                        "type": "unsubscribed",
                        "event": event_type,
                    },
                ),
                client_id,
            )

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self._active_connections)

    def get_subscriber_count(self, event_type: str) -> int:
        """Get the number of subscribers for an event type."""
        count = 0
        for subscriptions in self._subscriptions.values():
            if event_type in subscriptions:
                count += 1
        return count
