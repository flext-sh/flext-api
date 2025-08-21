"""Comprehensive tests for FLEXT API domain entities.

Tests all domain entities with 100% coverage including:
- Business logic validation and rules
- State transitions and lifecycle management
- FlextResult integration and error handling
- Foundation pattern compliance

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from flext_api import (
    ApiEndpoint,
    ApiRequest,
    ApiResponse,
    ApiSession,
    HttpMethod,
    HttpStatus,
    RequestState,
    ResponseState,
)


class TestApiRequest:
    """Test ApiRequest domain entity."""

    def test_basic_creation(self) -> None:
        """Test basic ApiRequest creation with validation."""
        request = ApiRequest(
            id="test-request-123",
            method=HttpMethod.GET,
            url="https://api.example.com/users",
        )

        assert request.method == HttpMethod.GET
        assert request.url == "https://api.example.com/users"
        assert request.headers == {}
        assert request.body is None
        assert request.query_params == {}
        assert request.state == RequestState.CREATED
        assert request.id is not None
        assert request.created_at is not None

    def test_validation_success(self) -> None:
        """Test successful business rule validation."""
        request = ApiRequest(
            id="test-request-124",
            method=HttpMethod.POST,
            url="/api/users",
            headers={"Content-Type": "application/json"},
            body={"name": "John Doe"},
        )

        result = request.validate_business_rules()
        assert result.success
        assert result.value is None

    def test_validation_empty_url_fails(self) -> None:
        """Test validation fails for empty URL."""
        request = ApiRequest(id="test-request-125", method=HttpMethod.GET, url="")

        result = request.validate_business_rules()
        assert not result.success
        assert "URL cannot be empty" in result.error

    def test_validation_whitespace_url_fails(self) -> None:
        """Test validation fails for whitespace-only URL."""
        request = ApiRequest(id="test-request-126", method=HttpMethod.GET, url="   ")

        result = request.validate_business_rules()
        assert not result.success
        assert "URL cannot be empty" in result.error

    def test_validation_invalid_url_scheme_fails(self) -> None:
        """Test validation fails for invalid URL scheme."""
        request = ApiRequest(
            id="test-request-127",
            method=HttpMethod.GET,
            url="ftp://invalid.com",
        )

        result = request.validate_business_rules()
        assert not result.success
        assert "valid HTTP URL or path" in result.error

    def test_validation_relative_path_succeeds(self) -> None:
        """Test validation succeeds for relative paths."""
        request = ApiRequest(
            id="test-request-128",
            method=HttpMethod.GET,
            url="/api/users",
        )

        result = request.validate_business_rules()
        assert result.success

    def test_validation_empty_header_key_fails(self) -> None:
        """Test validation fails for empty header key."""
        request = ApiRequest(
            id="test-request-129",
            method=HttpMethod.GET,
            url="https://api.example.com",
            headers={"": "value"},
        )

        result = request.validate_business_rules()
        assert not result.success
        assert "Header keys must be non-empty" in result.error

    def test_validation_empty_header_value_fails(self) -> None:
        """Test validation fails for empty header value."""
        request = ApiRequest(
            id="test-request-130",
            method=HttpMethod.GET,
            url="https://api.example.com",
            headers={"Content-Type": ""},
        )

        result = request.validate_business_rules()
        assert not result.success
        assert "Header values cannot be empty" in result.error

    def test_start_processing_success(self) -> None:
        """Test successful start processing state transition."""
        request = ApiRequest(
            id="test-request-131",
            method=HttpMethod.GET,
            url="https://api.example.com",
            state=RequestState.VALIDATED,
        )

        result = request.start_processing()
        assert result.success
        assert result.value is not None
        assert result.value.state == RequestState.PROCESSING
        assert result.value.updated_at > request.updated_at

    def test_start_processing_invalid_state_fails(self) -> None:
        """Test start processing fails from invalid state."""
        request = ApiRequest(
            id="test-request-132",
            method=HttpMethod.GET,
            url="https://api.example.com",
            state=RequestState.CREATED,
        )

        result = request.start_processing()
        assert not result.success
        assert "Cannot start processing from state: created" in result.error

    def test_complete_processing_success(self) -> None:
        """Test successful complete processing state transition."""
        request = ApiRequest(
            id="test-request-133",
            method=HttpMethod.GET,
            url="https://api.example.com",
            state=RequestState.PROCESSING,
        )

        result = request.complete_processing()
        assert result.success
        assert result.value is not None
        assert result.value.state == RequestState.COMPLETED
        assert result.value.updated_at > request.updated_at

    def test_complete_processing_invalid_state_fails(self) -> None:
        """Test complete processing fails from invalid state."""
        request = ApiRequest(
            id="test-request-134",
            method=HttpMethod.GET,
            url="https://api.example.com",
            state=RequestState.CREATED,
        )

        result = request.complete_processing()
        assert not result.success
        assert "Cannot complete from state: created" in result.error


class TestApiResponse:
    """Test ApiResponse domain entity."""

    def test_basic_creation(self) -> None:
        """Test basic ApiResponse creation."""
        response = ApiResponse(id="test-response-200", status_code=HttpStatus.OK.value)

        assert response.status_code == HttpStatus.OK.value
        assert response.headers == {}
        assert response.body is None
        assert response.state == ResponseState.PENDING
        assert response.request_id is None
        assert response.id is not None
        assert response.created_at is not None

    def test_creation_with_context(self) -> None:
        """Test ApiResponse creation with full context."""
        response = ApiResponse(
            id="test-response-201",
            status_code=HttpStatus.CREATED.value,
            headers={"Content-Type": "application/json"},
            body={"id": 123, "name": "John Doe"},
            request_id="req-123",
        )

        assert response.status_code == HttpStatus.CREATED.value
        assert response.headers["Content-Type"] == "application/json"
        assert response.body == {"id": 123, "name": "John Doe"}
        assert response.request_id == "req-123"

    def test_validation_success(self) -> None:
        """Test successful business rule validation."""
        response = ApiResponse(
            id="test-response-202",
            status_code=HttpStatus.OK.value,
            headers={"Content-Type": "application/json"},
        )

        result = response.validate_business_rules()
        assert result.success

    def test_validation_invalid_status_code_fails(self) -> None:
        """Test validation fails for invalid status code."""
        response = ApiResponse(id="test-response-203", status_code=99)  # Below minimum

        result = response.validate_business_rules()
        assert not result.success
        assert "Invalid HTTP status code: 99" in result.error

    def test_validation_high_status_code_fails(self) -> None:
        """Test validation fails for status code too high."""
        response = ApiResponse(id="test-response-204", status_code=600)  # Above maximum

        result = response.validate_business_rules()
        assert not result.success
        assert "Invalid HTTP status code: 600" in result.error

    def test_validation_empty_header_key_fails(self) -> None:
        """Test validation fails for empty header key."""
        response = ApiResponse(
            id="test-response-205",
            status_code=HttpStatus.OK.value,
            headers={"": "value"},
        )

        result = response.validate_business_rules()
        assert not result.success
        assert "header keys must be non-empty" in result.error

    def test_validation_empty_header_value_fails(self) -> None:
        """Test validation fails for empty header value."""
        response = ApiResponse(
            id="test-response-206",
            status_code=HttpStatus.OK.value,
            headers={"Content-Type": ""},
        )

        result = response.validate_business_rules()
        assert not result.success
        assert "header values cannot be empty" in result.error

    def test_mark_success(self) -> None:
        """Test marking response as successful."""
        response = ApiResponse(id="test-response-207", status_code=HttpStatus.OK.value)

        result = response.mark_success()
        assert result.success
        assert result.value is not None
        assert result.value.state == ResponseState.SUCCESS
        assert result.value.updated_at > response.updated_at

    def test_mark_error(self) -> None:
        """Test marking response as error."""
        response = ApiResponse(
            id="test-response-208",
            status_code=HttpStatus.INTERNAL_SERVER_ERROR.value,
        )
        error_message = "Internal server error occurred"

        result = response.mark_error(error_message)
        assert result.success
        assert result.value is not None
        assert result.value.state == ResponseState.ERROR
        assert result.value.body is not None
        assert result.value.body["error"] == error_message
        assert result.value.body["response_id"] == response.id
        assert "timestamp" in result.value.body


class TestApiEndpoint:
    """Test ApiEndpoint domain entity."""

    def test_basic_creation(self) -> None:
        """Test basic ApiEndpoint creation."""
        endpoint = ApiEndpoint(
            id="test-endpoint-300",
            path="/api/users",
            methods=[HttpMethod.GET, HttpMethod.POST],
        )

        assert endpoint.path == "/api/users"
        assert endpoint.methods == [HttpMethod.GET, HttpMethod.POST]
        assert endpoint.description is None
        assert endpoint.auth_required is True
        assert endpoint.rate_limit is None
        assert endpoint.id is not None

    def test_creation_with_full_context(self) -> None:
        """Test ApiEndpoint creation with full context."""
        endpoint = ApiEndpoint(
            id="test-endpoint-301",
            path="/api/public/health",
            methods=[HttpMethod.GET],
            description="Health check endpoint",
            auth_required=False,
            rate_limit=100,
        )

        assert endpoint.path == "/api/public/health"
        assert endpoint.methods == [HttpMethod.GET]
        assert endpoint.description == "Health check endpoint"
        assert endpoint.auth_required is False
        assert endpoint.rate_limit == 100

    def test_validation_success(self) -> None:
        """Test successful business rule validation."""
        endpoint = ApiEndpoint(
            id="test-endpoint-302",
            path="/api/users",
            methods=[HttpMethod.GET, HttpMethod.POST],
        )

        result = endpoint.validate_business_rules()
        assert result.success

    def test_validation_empty_path_fails(self) -> None:
        """Test validation fails for empty path."""
        endpoint = ApiEndpoint(
            id="test-endpoint-303",
            path="",
            methods=[HttpMethod.GET],
        )

        result = endpoint.validate_business_rules()
        assert not result.success
        assert "path cannot be empty" in result.error

    def test_validation_path_without_slash_fails(self) -> None:
        """Test validation fails for path not starting with slash."""
        endpoint = ApiEndpoint(
            id="test-endpoint-304",
            path="api/users",
            methods=[HttpMethod.GET],
        )

        result = endpoint.validate_business_rules()
        assert not result.success
        assert "path must start with '/'" in result.error

    def test_validation_empty_methods_fails(self) -> None:
        """Test validation fails for empty methods list."""
        endpoint = ApiEndpoint(id="test-endpoint-305", path="/api/users", methods=[])

        result = endpoint.validate_business_rules()
        assert not result.success
        assert "at least one HTTP method" in result.error

    def test_validation_negative_rate_limit_fails(self) -> None:
        """Test validation fails for negative rate limit."""
        endpoint = ApiEndpoint(
            id="test-endpoint-306",
            path="/api/users",
            methods=[HttpMethod.GET],
            rate_limit=-1,
        )

        result = endpoint.validate_business_rules()
        assert not result.success
        assert "Rate limit must be positive" in result.error

    def test_validation_zero_rate_limit_fails(self) -> None:
        """Test validation fails for zero rate limit."""
        endpoint = ApiEndpoint(
            id="test-endpoint-307",
            path="/api/users",
            methods=[HttpMethod.GET],
            rate_limit=0,
        )

        result = endpoint.validate_business_rules()
        assert not result.success
        assert "Rate limit must be positive" in result.error

    def test_supports_method(self) -> None:
        """Test method support checking."""
        endpoint = ApiEndpoint(
            id="test-endpoint-308",
            path="/api/users",
            methods=[HttpMethod.GET, HttpMethod.POST],
        )

        assert endpoint.supports_method(HttpMethod.GET)
        assert endpoint.supports_method(HttpMethod.POST)
        assert not endpoint.supports_method(HttpMethod.DELETE)
        assert not endpoint.supports_method(HttpMethod.PUT)

    def test_requires_authentication(self) -> None:
        """Test authentication requirement checking."""
        auth_endpoint = ApiEndpoint(
            id="test-endpoint-309",
            path="/api/users",
            methods=[HttpMethod.GET],
            auth_required=True,
        )

        public_endpoint = ApiEndpoint(
            id="test-endpoint-310",
            path="/api/health",
            methods=[HttpMethod.GET],
            auth_required=False,
        )

        assert auth_endpoint.requires_authentication()
        assert not public_endpoint.requires_authentication()


class TestApiSession:
    """Test ApiSession domain entity."""

    def test_basic_creation(self) -> None:
        """Test basic ApiSession creation."""
        session = ApiSession(id="test-session-400")

        assert session.user_id is None
        assert session.token is None
        assert session.expires_at is None
        assert session.last_activity is None
        assert session.is_active is True
        assert session.id is not None

    def test_creation_with_context(self) -> None:
        """Test ApiSession creation with full context."""
        expires_at = datetime.now(UTC) + timedelta(hours=1)
        last_activity = datetime.now(UTC)

        session = ApiSession(
            id="test-session-401",
            user_id="user-123",
            token="session-token-456",
            expires_at=expires_at,
            last_activity=last_activity,
        )

        assert session.user_id == "user-123"
        assert session.token == "session-token-456"
        assert session.expires_at == expires_at
        assert session.last_activity == last_activity
        assert session.is_active is True

    def test_validation_success(self) -> None:
        """Test successful business rule validation."""
        session = ApiSession(
            id="test-session-402",
            token="valid-token-123456789",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

        result = session.validate_business_rules()
        assert result.success

    def test_validation_short_token_fails(self) -> None:
        """Test validation fails for token too short."""
        session = ApiSession(id="test-session-403", token="short")

        result = session.validate_business_rules()
        assert not result.success
        assert "at least 16 characters" in result.error

    def test_validation_past_expiration_fails(self) -> None:
        """Test validation fails for past expiration time."""
        session = ApiSession(
            id="test-session-404",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )

        result = session.validate_business_rules()
        assert not result.success
        assert "past expiration" in result.error

    def test_is_expired_no_expiration(self) -> None:
        """Test session is not expired when no expiration set."""
        session = ApiSession(id="test-session-405", expires_at=None)
        assert not session.is_expired()

    def test_is_expired_future_expiration(self) -> None:
        """Test session is not expired when expiration in future."""
        session = ApiSession(
            id="test-session-406",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert not session.is_expired()

    def test_is_expired_past_expiration(self) -> None:
        """Test session is expired when expiration in past."""
        session = ApiSession(
            id="test-session-407",
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )
        assert session.is_expired()

    def test_extend_session_success(self) -> None:
        """Test successful session extension."""
        session = ApiSession(id="test-session-408", is_active=True)

        result = session.extend_session(duration_minutes=30)
        assert result.success
        assert result.value is not None
        assert result.value.expires_at is not None
        assert result.value.last_activity is not None
        assert result.value.updated_at > session.updated_at

    def test_extend_session_custom_duration(self) -> None:
        """Test session extension with custom duration."""
        session = ApiSession(id="test-session-409", is_active=True)

        result = session.extend_session(duration_minutes=120)
        assert result.success
        assert result.value is not None
        # Verify duration is approximately correct (within 5 seconds)
        expected_expiry = datetime.now(UTC) + timedelta(minutes=120)
        actual_expiry = result.value.expires_at
        assert actual_expiry is not None
        assert abs((actual_expiry - expected_expiry).total_seconds()) < 5

    def test_extend_inactive_session_fails(self) -> None:
        """Test extending inactive session fails."""
        session = ApiSession(id="test-session-410", is_active=False)

        result = session.extend_session()
        assert not result.success
        assert "Cannot extend inactive session" in result.error

    def test_deactivate_session(self) -> None:
        """Test session deactivation."""
        session = ApiSession(id="test-session-411", is_active=True)

        result = session.deactivate()
        assert result.success
        assert result.value is not None
        assert result.value.is_active is False
        assert result.value.updated_at > session.updated_at
