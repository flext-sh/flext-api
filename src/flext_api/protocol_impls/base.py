"""Base Protocol Implementation for flext-api.

Defines the base class and patterns that all protocol implementations must follow.
All protocol implementations extend this base class to ensure consistent behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

from flext_api import c, p, r, t, u


class FlextApiBaseProtocolImplementation:
    """Base class for concrete flext-api protocol implementations.

    This surface keeps the protocol implementation contract centralized: it
    carries shared metadata, lifecycle state, canonical result helpers, and the
    default failure behavior for operations subclasses must implement.
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
    ) -> None:
        """Initialize the common protocol implementation metadata."""
        self.logger = u.fetch_logger(__name__)
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "_initialized", False)

    @property
    def initialized(self) -> bool:
        """Return whether this protocol implementation is initialized."""
        return self._initialized

    def execute(self, **kwargs: t.Scalar) -> p.Result[bool]:
        """Execute the protocol surface after initialization."""
        if not self._initialized:
            return r[bool].fail("Protocol not initialized")
        if kwargs:
            self.logger.debug(
                f"Protocol.execute received kwargs: {list(kwargs.keys())}",
            )
        return r[bool].ok(value=True)

    def protocol_info(self) -> Mapping[str, t.JsonValue | t.StrSequence]:
        """Return protocol metadata and supported protocol names."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "initialized": self._initialized,
            "supported_protocols": self.supported_protocols(),
        }

    def supported_protocols(self) -> t.StrSequence:
        """Return the protocols supported by this implementation."""
        protocols: t.MutableSequenceOf[str] = []
        return protocols

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
        """Send a request using the concrete protocol implementation."""
        _ = request
        _ = kwargs
        return r[t.Api.HttpResponseDict].fail(
            f"send_request() must be implemented by {self.__class__.__name__}",
        )

    def shutdown(self) -> p.Result[bool]:
        """Shutdown the protocol and release any tracked resources."""
        if not self._initialized:
            return r[bool].fail(f"Protocol '{self.name}' not initialized")
        self.logger.debug(f"Shutting down protocol: {self.name}")
        self._initialized = False
        return r[bool].ok(value=True)

    def supports_protocol(self, protocol: str) -> bool:
        """Return whether this implementation supports the given protocol."""
        _ = protocol
        return False

    def _build_error_response(
        self,
        error: str,
        status_code: int = 500,
    ) -> t.JsonMapping:
        """Build a normalized error response payload."""
        response: t.MutableJsonMapping = {
            "status": c.Api.Status.ERROR.value,
            "status_code": status_code,
            "error": error,
            "timestamp": None,
        }
        return response

    def _build_success_response(
        self,
        data: t.JsonValue | None = None,
        status_code: int = 200,
    ) -> t.JsonMapping:
        """Build a normalized success response payload."""
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
        """Validate that the request payload is non-empty."""
        if not request:
            return r[t.JsonMapping].fail("Request cannot be empty")
        return r[t.JsonMapping].ok(request)


__all__: t.MutableSequenceOf[str] = ["FlextApiBaseProtocolImplementation"]
