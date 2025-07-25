"""FlextApi Universal API Client.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Universal API client with async/await, HTTP/2, GraphQL, WebSockets, streaming,
validation, observability, circuit breaker, caching and plugin system.
"""

from __future__ import annotations

from flext_api.client.core import (
    FlextApiClient,
    FlextApiClientBuilder,
    FlextApiClientConfig,
    FlextApiClientMethod,
    FlextApiClientProtocol,
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiClientStatus,
    flext_api_client_context,
    flext_api_create_client,
)
from flext_api.client.plugins import (
    FlextApiCachingPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiLoggingPlugin,
    FlextApiMetricsPlugin,
    FlextApiPlugin,
    FlextApiRetryPlugin,
)
from flext_api.client.protocols import (
    FlextApiGraphQLClient,
    FlextApiGraphQLQuery,
    FlextApiGraphQLResponse,
    FlextApiStreamingClient,
    FlextApiWebSocketClient,
    FlextApiWebSocketMessage,
)
from flext_api.client.validation import (
    FlextApiRequestValidator,
    FlextApiResponseValidator,
    FlextApiValidationManager,
    FlextApiValidationRule,
    FlextApiValidationRuleset,
    FlextApiValidators,
)

__all__ = [
    # Plugins
    "FlextApiCachingPlugin",
    "FlextApiCircuitBreakerPlugin",
    # Core client
    "FlextApiClient",
    "FlextApiClientBuilder",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientProtocol",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    # Protocol clients
    "FlextApiGraphQLClient",
    "FlextApiGraphQLQuery",
    "FlextApiGraphQLResponse",
    "FlextApiLoggingPlugin",
    "FlextApiMetricsPlugin",
    "FlextApiPlugin",
    # Validation
    "FlextApiRequestValidator",
    "FlextApiResponseValidator",
    "FlextApiRetryPlugin",
    "FlextApiStreamingClient",
    "FlextApiValidationManager",
    "FlextApiValidationRule",
    "FlextApiValidationRuleset",
    "FlextApiValidators",
    "FlextApiWebSocketClient",
    "FlextApiWebSocketMessage",
    "flext_api_client_context",
    "flext_api_create_client",
]
