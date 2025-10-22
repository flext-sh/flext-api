"""GraphQL Protocol Plugin for flext-api (stub implementation).

Minimal GraphQL protocol plugin for Phase 2+ development.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import FlextResult

from flext_api.plugins import ProtocolPlugin


class GraphQLProtocolPlugin(ProtocolPlugin):
    """GraphQL protocol plugin stub (to be implemented in Phase 2+)."""

    def __init__(self) -> None:
        """Initialize GraphQL protocol plugin stub."""
        super().__init__(
            name="graphql",
            version="1.0.0",
            description="GraphQL protocol plugin (stub)",
        )

    def send_request(
        self,
        request: dict[str, object],  # noqa: ARG002
        **kwargs: object,  # noqa: ARG002
    ) -> FlextResult[dict[str, object]]:
        """Send GraphQL request (stub - not implemented).

        Args:
        request: GraphQL request dictionary
        **kwargs: Additional parameters

        Returns:
        FlextResult with error indicating not implemented

        """
        return FlextResult[dict[str, object]].fail(
            "GraphQL protocol not yet implemented (Phase 2+)"
        )

    def supports_protocol(self, protocol: str) -> bool:
        """Check if this plugin supports the given protocol.

        Args:
        protocol: Protocol identifier

        Returns:
        True if protocol is supported

        """
        return protocol.lower() in {"graphql", "gql"}

    def get_supported_protocols(self) -> list[str]:
        """Get list of supported protocols.

        Returns:
        List of supported protocol identifiers

        """
        return ["graphql", "gql"]


__all__ = ["GraphQLProtocolPlugin"]
