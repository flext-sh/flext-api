"""Plugin protocol type shard.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from flext_web import u

from flext_api import r, t

if TYPE_CHECKING:
    from flext_web import p


class FlextApiProtocolPluginTypes:
    """Plugin type shard for ``p.Api``."""

    class _FlextApiPluginBase:
        """Base class for flext-api plugin implementations."""

        name: str
        version: str
        description: str
        logger: p.Logger

        def __init__(
            self,
            name: str = "plugin",
            version: str = "0.0.0",
            description: str = "",
        ) -> None:
            self.name = name
            self.version = version
            self.description = description
            self.logger = u.fetch_logger(__name__)

        def initialize(self) -> p.Result[bool]:
            """Initialize plugin resources.

            Returns:
                The resulting ``p.Result[bool]``.
            """
            return r[bool].ok(value=True)

        def shutdown(self) -> p.Result[bool]:
            """Shutdown plugin resources.

            Returns:
                The resulting ``p.Result[bool]``.
            """
            return r[bool].ok(value=True)

    class Plugin(_FlextApiPluginBase, ABC):
        """Base plugin type used by manager APIs."""

    class Protocol(_FlextApiPluginBase, ABC):
        """Abstract protocol plugin for API protocol implementations."""

        def supported_protocols(self) -> t.StrSequence:
            """Get list of supported protocols.

            Returns:
                The resulting ``t.StrSequence``.
            """
            return []

        @abstractmethod
        def send_request(
            self,
            request: t.JsonMapping,
            **kwargs: t.Scalar,
        ) -> p.Result[t.JsonMapping]:
            """Send request using this protocol."""
            ...

        @abstractmethod
        def supports_protocol(self, protocol: str) -> bool:
            """Check if this plugin supports the given protocol."""
            ...

    class Schema(_FlextApiPluginBase, ABC):
        """Abstract schema plugin for schema validation and introspection."""

        def schema_version(self) -> str:
            """Get schema specification version.

            Returns:
                The resulting ``str``.
            """
            return "unknown"

        @abstractmethod
        def load_schema(self, schema_source: str) -> p.Result[t.JsonValue]:
            """Load schema from source."""
            ...

        def supports_schema_type(self) -> bool:
            """Check if this plugin supports the given schema type.

            Returns:
                The resulting ``bool``.
            """
            return False

        @abstractmethod
        def validate_request(
            self,
            request: t.JsonMapping,
            schema: t.JsonMapping,
        ) -> p.Result[bool]:
            """Validate request against schema."""
            ...

        @abstractmethod
        def validate_response(
            self,
            response: t.JsonMapping,
            schema: t.JsonMapping,
        ) -> p.Result[bool]:
            """Validate response against schema."""
            ...

    class Transport(_FlextApiPluginBase, ABC):
        """Abstract transport plugin for network communication."""

        @abstractmethod
        def connect(self, url: str, **options: t.Scalar) -> p.Result[bool]:
            """Establish connection to endpoint."""
            ...

        @abstractmethod
        def disconnect(self, connection: t.JsonValue) -> p.Result[bool]:
            """Close connection."""
            ...

        def connection_info(self) -> t.JsonMapping:
            """Get connection information.

            Returns:
                The resulting ``t.JsonMapping``.
            """
            return {}

        @abstractmethod
        def receive(
            self,
            connection: t.JsonValue,
            **options: t.Scalar,
        ) -> p.Result[t.JsonMapping | str | bytes]:
            """Receive data from connection."""
            ...

        @abstractmethod
        def send(
            self,
            connection: t.JsonValue,
            data: t.JsonMapping | str | bytes,
            **options: t.Scalar,
        ) -> p.Result[bool]:
            """Send data through connection."""
            ...

        def supports_streaming(self) -> bool:
            """Check if transport supports streaming.

            Returns:
                The resulting ``bool``.
            """
            return False

    class Authentication(_FlextApiPluginBase, ABC):
        """Abstract authentication plugin for credential management."""

        @abstractmethod
        def authenticate(
            self,
            request: t.JsonMapping,
            credentials: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Add authentication to request."""
            ...

        def auth_scheme(self) -> str:
            """Get authentication scheme name.

            Returns:
                The resulting ``str``.
            """
            return "Unknown"

        def refresh_credentials(
            self,
            credentials: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Refresh authentication credentials.

            Returns:
                The resulting ``p.Result[t.JsonMapping]``.
            """
            _ = credentials
            return r[t.JsonMapping].fail("Refresh not supported by this plugin")

        def requires_refresh(self) -> bool:
            """Check if credentials need refresh.

            Returns:
                The resulting ``bool``.
            """
            return False

        @abstractmethod
        def validate_credentials(self, credentials: t.JsonMapping) -> p.Result[bool]:
            """Validate authentication credentials."""
            ...


__all__: list[str] = ["FlextApiProtocolPluginTypes"]
