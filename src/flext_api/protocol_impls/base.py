"""Base Protocol Implementation for flext-api.

Defines the base class and patterns that all protocol implementations must follow.
All protocol implementations extend this base class to ensure consistent behavior.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextLogger, r

from flext_api.typings import t


class BaseProtocolImplementation:
    """Base class for all protocol implementations.

    Defines the standard interface and patterns that all protocol implementations
    must follow. All protocol implementations extend this class.

    This class structurally implements FlextApiPlugins.Protocol without explicit
    inheritance to avoid MRO conflicts with FlextService[bool]. All required
    Protocol methods are implemented here.

    Responsibilities:
    - Standardize initialization patterns
    - Provide common error handling
    - Define required method signatures
    - Ensure consistent logging
    - Enforce FlextResult patterns

    All protocol implementations must:
    1. Extend this class
    2. Implement send_request() method
    3. Implement supports_protocol() method
    4. Use FlextResult for all return values
    5. Use FlextApiConstants for all constants
    6. Follow railway-oriented error handling

    """

    # Protocol metadata fields (set via object.__setattr__ in __init__)
    name: str
    version: str
    description: str
    _initialized: bool

    def __init__(
        self,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        **_kwargs: t.GeneralValueType,
    ) -> None:
        """Initialize base protocol implementation.

        Args:
        name: Protocol name (e.g., "http", "websocket", "sse")
        version: Protocol version
        description: Protocol description
        **kwargs: Additional configuration parameters

        """
        # Initialize basic object - no FlextService dependency to avoid Pydantic validation conflicts
        self.logger = FlextLogger(__name__)

        # Store protocol metadata as instance attributes
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "description", description)

        # Protocol state
        object.__setattr__(self, "_initialized", False)

    def execute(self, **kwargs: object) -> r[bool]:
        """Execute protocol - return success if initialized."""
        if not self._initialized:
            return r[bool].fail("Protocol not initialized")
        if kwargs:
            self.logger.debug(
                f"Protocol.execute received kwargs: {list(kwargs.keys())}",
            )
        return r[bool].ok(True)

    def initialize(self) -> r[bool]:
        """Initialize protocol resources."""
        if self._initialized:
            return r[bool].fail(f"Protocol '{self.name}' already initialized")

        self.logger.debug(f"Initializing protocol: {self.name}")
        self._initialized = True
        return r[bool].ok(True)

    def shutdown(self) -> r[bool]:
        """Shutdown protocol and release resources."""
        if not self._initialized:
            return r[bool].fail(f"Protocol '{self.name}' not initialized")

        self.logger.debug(f"Shutting down protocol: {self.name}")
        self._initialized = False
        return r[bool].ok(True)

    @property
    def is_initialized(self) -> bool:
        """Check if protocol is initialized."""
        return self._initialized

    def send_request(
        self,
        request: dict[str, t.GeneralValueType],
        **kwargs: object,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Send request using this protocol.

        This method must be implemented by subclasses. Base implementation
        returns an error indicating the method must be overridden.

        Args:
        request: Request dictionary with protocol-specific fields
        **kwargs: Additional protocol-specific parameters

        Returns:
        FlextResult containing response dictionary or error

        """
        # Acknowledge parameters to avoid linting warnings
        _ = request
        _ = kwargs
        return r[dict[str, t.GeneralValueType]].fail(
            f"send_request() must be implemented by {self.__class__.__name__}",
        )

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this protocol implementation supports the given protocol.

        This method must be implemented by subclasses.

        Args:
        protocol: Protocol identifier (e.g., "http", "https", "websocket")

        Returns:
        True if protocol is supported, False otherwise

        """
        # Acknowledge parameter to avoid linting warnings
        _ = protocol
        return False

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols.

        Returns:
        List of supported protocol identifiers

        """
        return []

    def get_protocol_info(self) -> t.JsonObject:
        """Get protocol configuration information.

        Returns:
        Dictionary with protocol metadata and configuration

        """
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "initialized": self._initialized,
            "supported_protocols": self.get_supported_protocols(),
        }

    def _validate_request(
        self, request: dict[str, t.GeneralValueType]
    ) -> r[dict[str, t.GeneralValueType]]:
        """Validate request dictionary.

        Args:
            request: Request dictionary to validate

        Returns:
            FlextResult with validated request or error

        """
        if not isinstance(request, dict):
            return r[dict[str, t.GeneralValueType]].fail("Request must be a dictionary")

        if not request:
            return r[dict[str, t.GeneralValueType]].fail("Request cannot be empty")

        return r[dict[str, t.GeneralValueType]].ok(request)

    def _build_error_response(
        self,
        error: str,
        status_code: int = 500,
    ) -> dict[str, t.GeneralValueType]:
        """Build error response dictionary.

        Args:
        error: Error message
        status_code: HTTP status code (if applicable)

        Returns:
        Error response dictionary

        """
        return {
            "status": "error",
            "status_code": status_code,
            "error": error,
            "timestamp": None,  # Will be set by subclasses if needed
        }

    def _build_success_response(
        self,
        data: dict[str, t.GeneralValueType] | None = None,
        status_code: int = 200,
    ) -> dict[str, t.GeneralValueType]:
        """Build success response dictionary.

        Args:
        data: Response data
        status_code: HTTP status code (if applicable)

        Returns:
        Success response dictionary

        """
        response: dict[str, t.GeneralValueType] = {
            "status": "success",
            "status_code": status_code,
        }

        if data is not None:
            response["data"] = data

        return response


__all__ = ["BaseProtocolImplementation"]
