from _typeshed import Incomplete

from flext_api.api_client import (
    FlextApiBuilder as FlextApiBuilder,
    FlextApiCachingPlugin as FlextApiCachingPlugin,
    FlextApiClient as FlextApiClient,
    FlextApiClientConfig as FlextApiClientConfig,
    FlextApiClientMethod as FlextApiClientMethod,
    FlextApiClientRequest as FlextApiClientRequest,
    FlextApiClientResponse as FlextApiClientResponse,
    FlextApiClientStatus as FlextApiClientStatus,
    FlextApiPlugin as FlextApiPlugin,
    FlextApiQueryBuilder as FlextApiQueryBuilder,
    FlextApiResponseBuilder as FlextApiResponseBuilder,
    FlextApiRetryPlugin as FlextApiRetryPlugin,
    create_client as create_client,
)

__all__ = [
    "FlextApiBuilder",
    "FlextApiCachingPlugin",
    "FlextApiClient",
    "FlextApiClientConfig",
    "FlextApiClientMethod",
    "FlextApiClientRequest",
    "FlextApiClientResponse",
    "FlextApiClientStatus",
    "FlextApiPlugin",
    "FlextApiQueryBuilder",
    "FlextApiResponseBuilder",
    "FlextApiRetryPlugin",
    "create_client",
    "create_client_with_plugins",
]

def create_client_with_plugins(
    config: object = None, plugins: object = None
) -> object: ...

class FlextApiCircuitBreakerPlugin(FlextApiPlugin):
    failure_threshold: Incomplete
    recovery_timeout: Incomplete
    def __init__(
        self, failure_threshold: int = 5, recovery_timeout: int = 60
    ) -> None: ...
