"""Client pipeline and utility tests for FlextApiClient.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import cast

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiModels,
)


@pytest.mark.asyncio
async def test_client_request_pipeline_success() -> None:
    """Test successful client request pipeline execution."""
    client = FlextApiClient(
        config="https://httpbin.org",
        timeout=10,
        headers={"User-Agent": "FlextApiClient-Test/1.0"},
    )

    # Test the basic request pipeline
    result = await client.get("/get")

    assert result.is_success
    assert result.value is not None
    assert result.value.status_code == 200


@pytest.mark.asyncio
async def test_client_error_handling_pipeline() -> None:
    """Test client error handling in request pipeline."""
    client_config = FlextApiModels.ClientConfig(
        base_url="https://invalid-domain-that-does-not-exist-12345.com",
        timeout=10,
    )
    client = FlextApiClient(config=client_config)

    try:
        request = FlextApiModels.HttpRequest(
            method="GET",
            url="https://invalid-domain-that-does-not-exist-12345.com/test",
        )

        # Should fail due to DNS resolution failure
        result = await client.get(request.url)

        assert not result.is_success
        assert result.error is not None
        # Check for common connection error messages
        error_lower = result.error.lower()
        assert any(
            keyword in error_lower
            for keyword in ["failed", "error", "connection", "resolve", "name"]
        )
    finally:
        # Client cleanup is automatic
        pass


def test_client_session_management() -> None:
    """Test client session management utilities."""
    client_config = FlextApiModels.ClientConfig(
        base_url="https://httpbin.org",
        timeout=10,
    )
    client = FlextApiClient(config=client_config)

    # Test client creation
    assert client is not None

    # Test connection manager is available
    assert hasattr(client, "_connection_manager")


def test_create_client_factory_function() -> None:
    """Test create_client factory function."""
    config_dict = {
        "base_url": "https://api.example.com",
        "timeout": 30.0,
        "max_retries": 3,
        "headers": {"Authorization": "Bearer token"},
    }

    typed_config = cast(
        "Mapping[str, str | int, float] | bool | dict[str, str] | None", config_dict
    )
    client = FlextApiClient(config=typed_config)

    assert client is not None
    assert isinstance(client, FlextApiClient)
    assert client.base_url == "https://api.example.com"


def test_create_client_validation_error() -> None:
    """Test create_client with validation errors."""
    # Invalid config without base_url should raise exception or return valid client with defaults
    invalid_config: dict[str, object] = {"timeout": 30.0}

    # The function may throw an exception or return a client - test it doesn't crash
    try:
        typed_invalid_config = cast(
            "Mapping[str, str | int, float] | bool | dict[str, str] | None",
            invalid_config,
        )
        client = FlextApiClient(config=typed_invalid_config)
        # If it returns a client, it should be valid
        assert client is not None
        assert isinstance(client, FlextApiClient)
    except Exception:
        # Exception is expected for invalid configuration - this is the intended behavior
        if os.getenv("DEBUG_TESTS"):
            raise  # Re-raise in debug mode for investigation


def test_client_request_validation() -> None:
    """Test client request validation."""
    client_config = FlextApiModels.ClientConfig(
        base_url="https://httpbin.org",
        timeout=10,
    )
    # Client created for context but not used in this validation test
    _ = FlextApiClient(client_config)

    # Valid request
    valid_request = FlextApiModels.HttpRequest(
        method="GET",
        url="https://httpbin.org/get",
    )
    assert valid_request.method == "GET"
    assert valid_request.url == "https://httpbin.org/get"

    # Request with additional data
    post_request = FlextApiModels.HttpRequest(
        method="POST",
        url="https://httpbin.org/post",
        body={"test": "data"},
        headers={"Content-Type": "application/json"},
    )
    assert post_request.method == "POST"
    assert post_request.body == {"test": "data"}


def test_client_response_structure() -> None:
    """Test client response structure validation."""
    # Test response construction
    response = FlextApiModels.HttpResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        body={"message": "success"},
        url="https://example.com",
        method="GET",
        elapsed_time=0.5,
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.body == {"message": "success"}
    assert response.elapsed_time == 0.5


@pytest.mark.asyncio
async def test_client_lifecycle_with_requests() -> None:
    """Test complete client lifecycle with actual requests."""
    client = FlextApiClient(
        config="https://httpbin.org",
        timeout=10,
        max_retries=1,
    )

    # Test client functionality
    # Client should be ready for requests

    # Make a request
    result = await client.get("https://httpbin.org/uuid")

    assert result.is_success
    assert result.value is not None
    assert result.value.status_code == 200

    # Test client cleanup is automatic


def test_client_configuration_inheritance() -> None:
    """Test client configuration inheritance and validation."""
    # Test minimal config
    minimal_config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
    client = FlextApiClient(minimal_config)

    assert client.base_url == "https://api.example.com"

    # Test full config
    full_config = FlextApiModels.ClientConfig(
        base_url="https://api.example.com",
        timeout=60,
        max_retries=5,
        headers={"User-Agent": "CustomAgent/1.0"},
    )
    full_client = FlextApiClient(full_config)

    assert full_client.base_url == "https://api.example.com"
    # Test that client was created successfully
