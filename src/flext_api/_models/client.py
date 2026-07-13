"""API client configuration models."""

from __future__ import annotations

from types import MappingProxyType
from typing import Annotated, ClassVar

from flext_api import c, t
from flext_web import m, u


class FlextApiModelsClient:
    """Client configuration model shard for ``m.Api``."""

    class ClientConfig(m.Value):
        """HTTP client configuration model."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        base_url: Annotated[
            str,
            u.Field(
                default=c.Api.DEFAULT_BASE_URL,
                max_length=c.Api.MAX_URL_LENGTH,
                description="Base URL for all requests",
            ),
        ]
        timeout: Annotated[
            t.PositiveTimeout,
            u.Field(
                default=float(c.Api.DEFAULT_TIMEOUT),
                description="Request timeout in seconds",
            ),
        ]
        max_retries: Annotated[
            t.RetryCount,
            u.Field(default=c.MAX_RETRY_ATTEMPTS, description="Maximum retry attempts"),
        ]
        headers: Annotated[
            t.StrMapping, u.Field(description="Default headers for all requests")
        ] = u.Field(default_factory=lambda: MappingProxyType({}))
        verify_ssl: Annotated[
            bool, u.Field(default=True, description="Verify SSL certificates")
        ]

        @u.computed_field(return_type=bool)
        @property
        def configured(self) -> bool:
            """Whether the configuration is usable."""
            return bool(self.base_url) and self.timeout > 0


__all__: t.MutableSequenceOf[str] = ["FlextApiModelsClient"]
