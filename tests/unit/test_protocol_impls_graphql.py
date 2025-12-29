"""Comprehensive tests for GraphQLProtocolPlugin.

Tests validate GraphQL protocol functionality using real implementation.
No mocks - uses actual GraphQLProtocolPlugin.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api.protocol_impls.graphql import GraphQLProtocolPlugin


class TestGraphQLProtocolPlugin:
    """Test GraphQL protocol plugin."""

    def test_initialization(self) -> None:
        """Test GraphQL protocol plugin can be initialized."""
        plugin = GraphQLProtocolPlugin()
        assert plugin is not None
        assert plugin.name == "graphql"
        assert plugin.version == "1.0.0"
        assert plugin.description == "GraphQL protocol plugin (stub)"

    def test_supports_protocol_graphql(self) -> None:
        """Test supports_protocol for GraphQL."""
        plugin = GraphQLProtocolPlugin()
        assert plugin.supports_protocol("graphql")
        assert plugin.supports_protocol("GraphQL")  # Case insensitive
        assert plugin.supports_protocol("GRAPHQL")

    def test_supports_protocol_gql(self) -> None:
        """Test supports_protocol for GQL."""
        plugin = GraphQLProtocolPlugin()
        assert plugin.supports_protocol("gql")
        assert plugin.supports_protocol("GQL")

    def test_supports_protocol_unsupported(self) -> None:
        """Test supports_protocol for unsupported protocols."""
        plugin = GraphQLProtocolPlugin()
        assert not plugin.supports_protocol("http")
        assert not plugin.supports_protocol("websocket")
        assert not plugin.supports_protocol("")

    def test_get_supported_protocols(self) -> None:
        """Test get_supported_protocols method."""
        plugin = GraphQLProtocolPlugin()
        protocols = plugin.get_supported_protocols()
        assert isinstance(protocols, list)
        assert "graphql" in protocols
        assert "gql" in protocols
        assert len(protocols) == 2

    def test_send_request_stub(self) -> None:
        """Test send_request returns not implemented error."""
        plugin = GraphQLProtocolPlugin()
        result = plugin.send_request({"query": "test"})
        assert result.is_failure
        assert result.error is not None and "not yet implemented" in result.error

    def test_send_request_invalid_request(self) -> None:
        """Test send_request with invalid request."""
        plugin = GraphQLProtocolPlugin()
        result = plugin.send_request({})  # Empty dict
        assert result.is_failure
        assert result.error is not None and "cannot be empty" in result.error

    def test_send_request_non_dict_request(self) -> None:
        """Test send_request with non-dict request."""
        plugin = GraphQLProtocolPlugin()
        result = plugin.send_request("not a dict")  # type: ignore[arg-type]
        assert result.is_failure
        assert result.error is not None and "must be a dictionary" in result.error
