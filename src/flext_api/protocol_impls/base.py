"""Base Protocol Implementation for flext-api.

Defines the base class and patterns that all protocol implementations must follow.
All protocol implementations extend this base class to ensure consistent behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)

from flext_api import c, p, r, t, u


class FlextApiBaseProtocolImplementation:
    """Base class for all protocol implementations.

    Defines the standard interface and patterns that all protocol implementations
    must follow. All protocol implementations extend this class.

    This class structurally implements FlextApiProtocolPlugins.Protocol without explicit
    inheritance to avoid MRO conflicts with s[bool]. All required
    Protocol methods are implemented here.

    Responsibilities:
    - Standardize initialization patterns
    - Provide common error handling
    - Define required method signatures
    - Ensure consistent logging
    - Enforce r patterns

    All protocol implementations must:
    1. Extend this class
    2. Implement send_request() method
    3. Implement supports_protocol() method
    4. Use r for all return values
    5. Use FlextApiConstants for all constants
    6. Follow railway-oriented error handling

    """

    name: str
    version: str
    description: str
    _initialized: bool

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        **kwargs: t.Scalar,
    ) -> None:
        """Initialize base protocol implementation.

        Args:
        name: Protocol name (e.g., "http", "websocket", "sse")
        version: Protocol version
        description: Protocol description
        **kwargs: Additional configuration parameters

        """
        self.logger = u.fetch_logger(__name__)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "_initialized", False)

    @property
    def initialized(self) -> bool:
        """Check if protocol is initialized."""
        return self._initialized

    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute protocol - return success if initialized."""
        if not self._initialized:
            return r[bool].fail("Protocol not initialized")
        if kwargs:
            self.logger.debug(
                f"Protocol.execute received kwargs: {list(kwargs.keys())}",
            )
        return r[bool].ok(value=True)

    def protocol_info(self) -> Mapping[str, t.JsonValue | t.StrSequence]:
        """Get protocol configuration information.

        Returns:
        Dictionary with protocol metadata and configuration

        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "initialized": self._initialized,
            "supported_protocols": self.supported_protocols(),
        }

    def supported_protocols(self) -> t.StrSequence:
        """Get list of supported protocols.

        Returns:
        List of supported protocol identifiers

        """
        return []

    def initialize(self) -> p.Result[bool]:
        """Initialize protocol resources."""
        if self._initialized:
            return r[bool].fail(f"Protocol '{self.name}' already initialized")
        self.logger.debug(f"Initializing protocol: {self.name}")
        self._initialized = True
        return r[bool].ok(value=True)

    def send_request(
        self,
        request: t.JsonMapping,
        **kwargs: t.Scalar,
    ) -> p.Result[t.Api.HttpResponseDict]:
        """Send request using this protocol.

        This method must be implemented by subclasses. Base implementation
        returns an error indicating the method must be overridden.

        Args:
        request: Request dictionary with protocol-specific fields
        **kwargs: Additional protocol-specific parameters

        Returns:
        r containing response dictionary or error

        """
        _ = request
        _ = kwargs
        return r[t.Api.HttpResponseDict].fail(
            f"send_request() must be implemented by {self.__class__.__name__}",
        )

    def shutdown(self) -> p.Result[bool]:
        """Shutdown protocol and release resources."""
        if not self._initialized:
            return r[bool].fail(f"Protocol '{self.name}' not initialized")
        self.logger.debug(f"Shutting down protocol: {self.name}")
        self._initialized = False
        return r[bool].ok(value=True)

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this protocol implementation supports the given protocol.

        This method must be implemented by subclasses.

        Args:
        protocol: Protocol identifier (e.g., "http", "https", "websocket")

        Returns:
        True if protocol is supported, False otherwise

        """
        _ = protocol
        return False

    def _build_error_response(
        self,
        error: str,
        status_code: int = 500,
    ) -> t.JsonMapping:
        """Build error response dictionary.

        Args:
        error: Error message
        status_code: HTTP status code (if applicable)

        Returns:
        Error response dictionary

        """
        return {
            "status": c.Api.Status.ERROR.value,
            "status_code": status_code,
            "error": error,
            "timestamp": None,
        }

    def _build_success_response(
        self,
        data: t.JsonValue | None = None,
        status_code: int = 200,
    ) -> t.JsonMapping:
        """Build success response dictionary.

        Args:
        data: Response data
        status_code: HTTP status code (if applicable)

        Returns:
        Success response dictionary

        """
        response: t.MutableJsonMapping = {
            "status": c.Api.Status.SUCCESS.value,
            "status_code": status_code,
        }
        if data is not None:
            response["data"] = data
        return response

    def _validate_request(
        self,
        request: t.JsonMapping,
    ) -> p.Result[t.JsonMapping]:
        """Validate request dictionary.

        Args:
            request: Request dictionary to validate

        Returns:
            r with validated request or error

        """
        if not request:
            return r[t.JsonMapping].fail("Request cannot be empty")
        return r[t.JsonMapping].ok(request)


__all__: list[str] = ["FlextApiBaseProtocolImplementation"]
