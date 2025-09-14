"""FLEXT API - Unifying high-level API class.

Provides a single, typed entry point that composes existing flext-api
components (client, models, app factory) without duplicating logic.

Rules compliance:
- One class per module (FlextApi)
- Pydantic v2 used by dependencies (models/config)
- No Any; use precise types from flext-core/flext-api
- Direct use of flext-core primitives; no extra wrappers
"""

from __future__ import annotations

from collections.abc import Mapping

from flext_core import FlextDomainService, FlextResult

from flext_api.app import create_fastapi_app
from flext_api.client import FlextApiClient
from flext_api.config import FlextApiConfig
from flext_api.models import FlextApiModels


class FlextApi(FlextDomainService[object]):
    """Unifying API facade for flext-api.

    Encapsulates client creation and common operations while delegating
    behavior to existing components (client/app/models). This class does
    not introduce new logic; it orchestrates the public surface.
    """

    def __init__(
        self,
        config: (
            FlextApiModels.ClientConfig
            | FlextApiConfig
            | Mapping[str, object]
            | str
            | None
        ) = None,
        **kwargs: object,
    ) -> None:
        """Initialize the unifying API with a concrete client.

        Accepts the same inputs supported by `FlextApiClient.create_client`.
        Raises ValueError if the client cannot be created.
        """
        super().__init__()
        # Normalize to a FlextApiClient via its own factory
        if isinstance(config, Mapping):
            client_res = FlextApiClient.create_client(config, **kwargs)
        else:
            client_res = FlextApiClient.create_client(config, **kwargs)

        if client_res.is_failure:
            # Raise early to ensure invariant (FlextApi must have a client)
            msg = client_res.error or "Failed to create FlextApiClient"
            raise ValueError(msg)
        self._client = client_res.value

    # Core surface ---------------------------------------------------------

    @property
    def client(self) -> FlextApiClient:
        """Access the underlying client (read-only)."""
        return self._client

    # Client lifecycle -----------------------------------------------------

    async def start(self) -> FlextResult[None]:  # Delegate to client
        """Start the underlying HTTP client session."""
        return await self._client.start()

    async def stop(self) -> FlextResult[None]:  # Delegate to client
        """Stop the underlying HTTP client session."""
        return await self._client.stop()

    async def close(self) -> FlextResult[None]:  # Alias
        """Close the underlying HTTP client session (alias for stop)."""
        return await self._client.close()

    # Requests -------------------------------------------------------------

    async def get(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform a GET request via the underlying client."""
        return await self._client.get(url, **kwargs)

    async def post(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform a POST request via the underlying client."""
        return await self._client.post(url, **kwargs)

    async def put(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform a PUT request via the underlying client."""
        return await self._client.put(url, **kwargs)

    async def delete(
        self, url: str, **kwargs: object
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Perform a DELETE request via the underlying client."""
        return await self._client.delete(url, **kwargs)

    # Configuration --------------------------------------------------------

    def configure(self, config: Mapping[str, object]) -> FlextResult[None]:
        """Update client configuration using provided mapping."""
        return self._client.configure(dict(config))

    def get_config(self) -> dict[str, object]:
        """Return current client configuration as a dictionary."""
        return self._client.get_config()

    def health(self) -> dict[str, object]:
        """Return health information from the underlying client."""
        return self._client.health_check()

    # Factories ------------------------------------------------------------

    @staticmethod
    def create_app(config: FlextApiModels.AppConfig) -> FlextResult[object]:
        """Create a FastAPI application using the provided app config."""
        try:
            app = create_fastapi_app(config)
            return FlextResult[object].ok(app)
        except Exception as e:
            return FlextResult[object].fail(f"Failed to create app: {e}")


__all__ = ["FlextApi"]
