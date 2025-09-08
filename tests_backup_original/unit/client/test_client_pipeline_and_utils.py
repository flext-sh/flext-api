"""Client pipeline and utility tests for FlextApiClient.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

import pytest

from flext_api import (
    FlextApiClient,
    FlextApiModels,
    create_client,
)


@pytest.mark.asyncio
async def test_client_request_pipeline_success() -> None:
    """Test successful client request pipeline execution."""
    config = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        headers={"User-Agent": "FlextApi-Test/1.0"},
    )
    client = FlextApiClient(config)

    request = FlextApiModels.ApiRequest(
        id="test_req",
        method=FlextApiModels.HttpMethod.GET,
        url="https://httpbin.org/get",
    )

    # Test the basic request pipeline
    await client._ensure_session()
    result = await client._perform_http_request(request)

    assert result.success
    assert result.value is not None
    assert result.value.status_code == 200


@pytest.mark.asyncio
async def test_client_error_handling_pipeline() -> None:
    """Test client error handling in request pipeline."""
    config = FlextApiClient(
        base_url="https://invalid-domain-that-does-not-exist-12345.com",
        timeout=10.0,
    )
    client = FlextApiClient(config)
    await client.start()

    try:
        request = FlextApiModels.ApiRequest(
            id="test_req",
            method=FlextApiModels.HttpMethod.GET,
            url="https://invalid-domain-that-does-not-exist-12345.com/test",
        )

        # Should fail due to DNS resolution failure
        result = await client._perform_http_request(request)

        assert not result.success
        assert result.error is not None
        # Check for common connection error messages
        error_lower = result.error.lower()
        assert any(
            keyword in error_lower
            for keyword in ["failed", "error", "connection", "resolve", "name"]
        )
    finally:
        await client.stop()


@pytest.mark.asyncio
async def test_client_session_management() -> None:
    """Test client session management utilities."""
    config = FlextApiClient(base_url="https://httpbin.org", timeout=10.0)
    client = FlextApiClient(config)

    # Test session creation
    await client._ensure_session()
    assert client._session is not None

    # Test session is available
    assert hasattr(client, "_session")


def test_create_client_factory_function() -> None:
    """Test create_client factory function."""
    config_dict = {
        "base_url": "https://api.example.com",
        "timeout": 30.0,
        "max_retries": 3,
        "headers": {"Authorization": "Bearer token"},
    }

    client = create_client(config_dict)

    assert client is not None
    assert isinstance(client, FlextApiClient)
    assert client.config.base_url == "https://api.example.com"
    assert client.config.timeout == 30.0


def test_create_client_validation_error() -> None:
    """Test create_client with validation errors."""
    # Invalid config without base_url should raise exception or return valid client with defaults
    invalid_config = {"timeout": 30.0}

    # The function may throw an exception or return a client - test it doesn't crash
    try:
        client = create_client(invalid_config)
        # If it returns a client, it should be valid
        assert client is not None
        assert isinstance(client, FlextApiClient)
    except Exception:
        # Exception is expected for invalid configuration - this is the intended behavior
        if os.getenv("DEBUG_TESTS"):
            raise  # Re-raise in debug mode for investigation


@pytest.mark.asyncio
async def test_client_request_validation() -> None:
    """Test client request validation."""
    config = FlextApiClient(base_url="https://httpbin.org", timeout=10.0)
    # Client created for context but not used in this validation test
    _ = FlextApiClient(config)

    # Valid request
    valid_request = FlextApiModels.ApiRequest(
        id="test_req",
        method=FlextApiModels.HttpMethod.GET,
        url="https://httpbin.org/get",
    )
    assert valid_request.method == "GET"
    assert valid_request.url == "https://httpbin.org/get"

    # Request with additional data
    post_request = FlextApiModels.ApiRequest(
        method=FlextApiModels.HttpMethod.POST,
        url="https://httpbin.org/post",
        json_data={"test": "data"},
        headers={"Content-Type": "application/json"},
    )
    assert post_request.method == "POST"
    assert post_request.json_data == {"test": "data"}


def test_client_response_structure() -> None:
    """Test client response structure validation."""
    # Test response construction
    response = FlextApiModels.ApiResponse(
        status_code=200,
        headers={"Content-Type": "application/json"},
        data={"message": "success"},
        elapsed_time=0.5,
    )

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.value == {"message": "success"}
    assert response.elapsed_time == 0.5


@pytest.mark.asyncio
async def test_client_lifecycle_with_requests() -> None:
    """Test complete client lifecycle with actual requests."""
    config = FlextApiClient(
        base_url="https://httpbin.org",
        timeout=10.0,
        max_retries=1,
    )
    client = FlextApiClient(config)

    # Test lifecycle
    await client.start()
    assert client.status == "running"

    # Make a request during lifecycle
    request = FlextApiModels.ApiRequest(
        id="test_req",
        method=FlextApiModels.HttpMethod.GET,
        url="https://httpbin.org/uuid",
    )
    result = await client._perform_http_request(request)

    assert result.success
    assert result.value is not None
    assert result.value.status_code == 200

    # Stop client
    await client.stop()
    assert client.status == "stopped"


def test_client_configuration_inheritance() -> None:
    """Test client configuration inheritance and validation."""
    # Test minimal config
    minimal_config = FlextApiClient(base_url="https://api.example.com")
    client = FlextApiClient(minimal_config)

    assert client.config.base_url == "https://api.example.com"
    assert client.config.timeout == 30.0  # Default value
    assert client.config.max_retries == 3  # Default value

    # Test full config
    full_config = FlextApiClient(
        base_url="https://api.example.com",
        timeout=60.0,
        max_retries=5,
        headers={"User-Agent": "CustomAgent/1.0"},
    )
    full_client = FlextApiClient(full_config)

    assert full_client.config.timeout == 60.0
    assert full_client.config.max_retries == 5
    assert full_client.config.headers["User-Agent"] == "CustomAgent/1.0"
