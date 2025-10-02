"""Simple unit tests for GraphQL protocol plugin.

Focused tests for GraphQL protocol implementation validation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_api.models import FlextApiModels
from flext_api.protocol_impls.graphql import GraphQLProtocolPlugin


class TestGraphQLProtocolPluginSimple:
    """Simple test suite for GraphQLProtocolPlugin."""

    def test_plugin_initialization(self) -> None:
        """Test GraphQL plugin initialization."""
        plugin = GraphQLProtocolPlugin(
            endpoint="https://api.example.com/graphql",
            timeout=30.0,
            introspection=True,
        )

        assert plugin is not None
        assert plugin.name == "graphql"
        assert plugin._endpoint == "https://api.example.com/graphql"
        assert plugin._timeout == 30.0
        assert plugin._introspection is True

    def test_plugin_supports_protocol(self) -> None:
        """Test protocol support checking."""
        plugin = GraphQLProtocolPlugin()

        assert plugin.supports_protocol("graphql") is True
        assert plugin.supports_protocol("gql") is True
        assert plugin.supports_protocol("http") is False

    def test_plugin_get_supported_protocols(self) -> None:
        """Test getting list of supported protocols."""
        plugin = GraphQLProtocolPlugin()

        protocols = plugin.get_supported_protocols()

        assert "graphql" in protocols
        assert "gql" in protocols

    def test_plugin_initialization_lifecycle(self) -> None:
        """Test plugin initialization and shutdown lifecycle."""
        plugin = GraphQLProtocolPlugin()

        # Test initialization
        init_result = plugin.initialize()
        assert init_result.is_success
        assert plugin.is_initialized

        # Test double initialization fails
        init_result_2 = plugin.initialize()
        assert init_result_2.is_failure

        # Test shutdown
        shutdown_result = plugin.shutdown()
        assert shutdown_result.is_success
        assert not plugin.is_initialized

        # Test double shutdown fails
        shutdown_result_2 = plugin.shutdown()
        assert shutdown_result_2.is_failure

    def test_plugin_metadata(self) -> None:
        """Test plugin metadata retrieval."""
        plugin = GraphQLProtocolPlugin()

        metadata = plugin.get_metadata()

        assert metadata["name"] == "graphql"
        assert "version" in metadata
        assert "description" in metadata
        assert "initialized" in metadata

    def test_plugin_configuration(self) -> None:
        """Test GraphQL plugin configuration."""
        plugin = GraphQLProtocolPlugin(
            endpoint="https://graphql.example.com",
            headers={"Authorization": "Bearer token123"},
            verify_ssl=True,
            fetch_schema_from_transport=True,
        )

        assert plugin._endpoint == "https://graphql.example.com"
        assert "Authorization" in plugin._headers
        assert plugin._verify_ssl is True
        assert plugin._fetch_schema_from_transport is True


class TestGraphQLModelsSimple:
    """Simple test suite for GraphQL models."""

    def test_graphql_query_creation(self) -> None:
        """Test GraphQLQuery creation."""
        query = FlextApiModels.GraphQLQuery(
            query="query GetUser($id: ID!) { user(id: $id) { name } }",
            variables={"id": "123"},
            operation_name="GetUser",
        )

        assert query.query is not None
        assert query.has_variables is True
        assert query.operation_name == "GetUser"
        assert query.query_length > 0

    def test_graphql_query_without_variables(self) -> None:
        """Test GraphQLQuery without variables."""
        query = FlextApiModels.GraphQLQuery(
            query="query { users { name } }",
        )

        assert query.has_variables is False
        assert query.operation_name is None

    def test_graphql_query_with_fragments(self) -> None:
        """Test GraphQLQuery with fragments."""
        query = FlextApiModels.GraphQLQuery(
            query="query { user { ...UserFields } }",
            fragments=["fragment UserFields on User { name email }"],
        )

        assert query.has_fragments is True
        assert len(query.fragments) == 1

    def test_graphql_response_success(self) -> None:
        """Test GraphQLResponse for successful query."""
        response = FlextApiModels.GraphQLResponse(
            data={"user": {"name": "John", "email": "john@example.com"}},
            errors=[],
        )

        assert response.has_data is True
        assert response.has_errors is False
        assert response.is_success is True
        assert response.error_count == 0

    def test_graphql_response_with_errors(self) -> None:
        """Test GraphQLResponse with errors."""
        response = FlextApiModels.GraphQLResponse(
            data=None,
            errors=[
                {"message": "User not found", "path": ["user"]},
            ],
        )

        assert response.has_errors is True
        assert response.is_success is False
        assert response.error_count == 1

    def test_graphql_response_partial_data(self) -> None:
        """Test GraphQLResponse with partial data and errors."""
        response = FlextApiModels.GraphQLResponse(
            data={"user": {"name": "John", "email": None}},
            errors=[
                {"message": "Email field error", "path": ["user", "email"]},
            ],
        )

        assert response.has_data is True
        assert response.has_errors is True
        assert response.is_success is False

    def test_graphql_schema_creation(self) -> None:
        """Test GraphQLSchema creation."""
        schema = FlextApiModels.GraphQLSchema(
            schema_string="type Query { user(id: ID!): User }",
            types=["Query", "User"],
            queries=["user"],
            mutations=[],
            subscriptions=[],
        )

        assert schema.has_queries is True
        assert schema.has_mutations is False
        assert schema.has_subscriptions is False
        assert schema.operation_count == 1

    def test_graphql_schema_with_all_operations(self) -> None:
        """Test GraphQLSchema with all operation types."""
        schema = FlextApiModels.GraphQLSchema(
            schema_string="type Query { users: [User] }",
            types=["Query", "Mutation", "Subscription", "User"],
            queries=["users", "user"],
            mutations=["createUser", "updateUser"],
            subscriptions=["userAdded"],
        )

        assert schema.has_queries is True
        assert schema.has_mutations is True
        assert schema.has_subscriptions is True
        assert schema.operation_count == 5

    def test_graphql_subscription_creation(self) -> None:
        """Test GraphQLSubscription creation."""
        subscription = FlextApiModels.GraphQLSubscription(
            subscription="subscription { messageAdded { id text } }",
            state="active",
        )

        assert subscription.subscription is not None
        assert subscription.is_active is True
        assert subscription.has_variables is False

    def test_graphql_subscription_with_variables(self) -> None:
        """Test GraphQLSubscription with variables."""
        subscription = FlextApiModels.GraphQLSubscription(
            subscription="subscription OnMessage($channelId: ID!) { messageAdded(channelId: $channelId) { id } }",
            variables={"channelId": "channel123"},
            operation_name="OnMessage",
            state="active",
        )

        assert subscription.has_variables is True
        assert subscription.operation_name == "OnMessage"
        assert subscription.is_active is True

    def test_graphql_subscription_invalid_state(self) -> None:
        """Test GraphQLSubscription with invalid state."""
        with pytest.raises(ValueError):
            FlextApiModels.GraphQLSubscription(
                subscription="subscription { test }",
                state="invalid_state",
            )

    def test_graphql_subscription_states(self) -> None:
        """Test GraphQLSubscription different states."""
        states = ["pending", "active", "completed", "error", "cancelled"]

        for state in states:
            subscription = FlextApiModels.GraphQLSubscription(
                subscription="subscription { test }",
                state=state,
            )
            assert subscription.state == state

    def test_graphql_subscription_event_tracking(self) -> None:
        """Test GraphQLSubscription event tracking."""
        subscription = FlextApiModels.GraphQLSubscription(
            subscription="subscription { test }",
            state="active",
            events_received=42,
        )

        assert subscription.events_received == 42
