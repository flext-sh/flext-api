"""Generic HTTP client facade."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, override

from flext_api._utilities.client_request import FlextApiClientRequestMixin
from flext_api.base import FlextApiServiceBase
from flext_api.settings import FlextApiSettings
from flext_core.result import r

if TYPE_CHECKING:
    from flext_api import p, t


class FlextApiClient(FlextApiClientRequestMixin, FlextApiServiceBase[bool]):
    """Generic HTTP client using FLEXT patterns."""

    config_type: ClassVar[type[FlextApiSettings]] = FlextApiSettings

    def __init__(self, *, settings: FlextApiSettings | None = None) -> None:
        """Public bootstrap surface using the canonical ``settings=`` call form."""
        super().__init__(runtime_settings=settings)

    @property
    def base_url(self) -> str:
        """Access base_url from configuration."""
        return self.settings.base_url

    @property
    def timeout(self) -> float:
        """Access timeout from configuration."""
        timeout: float = self.settings.timeout
        return timeout

    @override
    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute service lifecycle parity after validating configured settings."""
        if kwargs:
            self.logger.info(f"Execute called with kwargs keys: {list(kwargs.keys())}")
        _ = self.settings
        return r[bool].ok(True)


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]
