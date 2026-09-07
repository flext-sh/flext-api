"""Generic HTTP client facade."""

from __future__ import annotations

from typing import override

from flext_api._settings import FlextApiSettings
from flext_api.base import FlextApiServiceBase
from flext_api.protocols import FlextApiProtocols
from flext_api.typings import FlextApiTypes
from flext_api.utilities import u
from flext_core import r

from .client_request import FlextApiClientRequestMixin

p = FlextApiProtocols
t = FlextApiTypes
_LOGGER = u.fetch_logger(__name__)


class FlextApiClient(FlextApiClientRequestMixin, FlextApiServiceBase[bool]):
    """Generic HTTP client using FLEXT patterns."""

    def __init__(self, settings: FlextApiSettings | None = None) -> None:
        """Bind the client to explicit settings or the global singleton."""
        resolved = settings if settings is not None else FlextApiSettings.fetch_global()
        FlextApiServiceBase.__init__(self, runtime_settings=resolved)

    @property
    def base_url(self) -> str:
        """The configured API base URL."""
        return self.settings.Api.base_url

    @property
    def timeout(self) -> float:
        """The configured request timeout in seconds."""
        return self.settings.Api.timeout

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute service lifecycle parity."""
        if kwargs:
            _LOGGER.info("Execute called with kwargs keys: %s", list(kwargs.keys()))
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]
