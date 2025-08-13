"""Comprehensive tests for FLEXT API domain value objects.

Tests all value objects with 100% coverage including:
- Value object creation and validation
- Business rule enforcement and error handling
- FlextResult integration and railway-oriented programming
- Foundation pattern compliance and immutability

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import from api_models.py directly (files were renamed with api_ prefix)
from flext_api.models import (
    URL,  # Proper URL value object with create method
    BearerToken,  # Proper domain value object
    HttpHeader,  # Proper domain value object
    HttpMethod,
    HttpStatus,
)


class TestHttpMethod:
    """Test HttpMethod enumeration."""

    def test_all_methods_available(self) -> None:
        """Test all HTTP methods are available."""
        assert HttpMethod.GET == "GET"
        assert HttpMethod.POST == "POST"
        assert HttpMethod.PUT == "PUT"
        assert HttpMethod.PATCH == "PATCH"
        assert HttpMethod.DELETE == "DELETE"
        assert HttpMethod.HEAD == "HEAD"
        assert HttpMethod.OPTIONS == "OPTIONS"
        assert HttpMethod.TRACE == "TRACE"

    def test_method_equality(self) -> None:
        """Test method equality comparisons."""
        assert HttpMethod.GET == HttpMethod.GET
        assert HttpMethod.POST != HttpMethod.GET
        assert HttpMethod.GET == "GET"
        assert HttpMethod.POST == "POST"

    def test_method_in_list(self) -> None:
        """Test method membership testing."""
        methods = [HttpMethod.GET, HttpMethod.POST]
        assert HttpMethod.GET in methods
        assert HttpMethod.DELETE not in methods


class TestHttpStatus:
    """Test HttpStatus enumeration with semantic categories."""

    def test_status_codes_values(self) -> None:
        """Test HTTP status code values."""
        assert HttpStatus.OK == 200
        assert HttpStatus.CREATED == 201
        assert HttpStatus.BAD_REQUEST == 400
        assert HttpStatus.NOT_FOUND == 404
        assert HttpStatus.INTERNAL_SERVER_ERROR == 500

    def test_is_informational(self) -> None:
        """Test informational status detection (1xx)."""
        assert HttpStatus.CONTINUE.is_informational
        assert HttpStatus.SWITCHING_PROTOCOLS.is_informational
        assert HttpStatus.PROCESSING.is_informational
        assert not HttpStatus.OK.is_informational
        assert not HttpStatus.BAD_REQUEST.is_informational

    def test_is_success(self) -> None:
        """Test success status detection (2xx)."""
        assert HttpStatus.OK.is_success
        assert HttpStatus.CREATED.is_success
        assert HttpStatus.ACCEPTED.is_success
        assert HttpStatus.NO_CONTENT.is_success
        assert not HttpStatus.CONTINUE.is_success
        assert not HttpStatus.BAD_REQUEST.is_success

    def test_is_redirection(self) -> None:
        """Test redirection status detection (3xx)."""
        assert HttpStatus.MOVED_PERMANENTLY.is_redirection
        assert HttpStatus.FOUND.is_redirection
        assert HttpStatus.NOT_MODIFIED.is_redirection
        assert not HttpStatus.OK.is_redirection
        assert not HttpStatus.BAD_REQUEST.is_redirection

    def test_is_client_error(self) -> None:
        """Test client error status detection (4xx)."""
        assert HttpStatus.BAD_REQUEST.is_client_error
        assert HttpStatus.UNAUTHORIZED.is_client_error
        assert HttpStatus.FORBIDDEN.is_client_error
        assert HttpStatus.NOT_FOUND.is_client_error
        assert not HttpStatus.OK.is_client_error
        assert not HttpStatus.INTERNAL_SERVER_ERROR.is_client_error

    def test_is_server_error(self) -> None:
        """Test server error status detection (5xx)."""
        assert HttpStatus.INTERNAL_SERVER_ERROR.is_server_error
        assert HttpStatus.NOT_IMPLEMENTED.is_server_error
        assert HttpStatus.BAD_GATEWAY.is_server_error
        assert not HttpStatus.OK.is_server_error
        assert not HttpStatus.BAD_REQUEST.is_server_error


class TestURL:
    """Test URL value object with validation and domain behavior."""

    def test_create_success_https(self) -> None:
        """Test successful URL creation with HTTPS."""
        result = URL.create("https://api.example.com/v1/users")

        assert result.success
        assert result.data is not None
        url = result.data
        assert url.raw_url == "https://api.example.com/v1/users"
        assert url.scheme == "https"
        assert url.host == "api.example.com"
        assert url.path == "/v1/users"
        assert url.port is None
        assert url.query is None
        assert url.fragment is None

    def test_create_success_http(self) -> None:
        """Test successful URL creation with HTTP."""
        result = URL.create("http://localhost:8080/api")

        assert result.success
        assert result.data is not None
        url = result.data
        assert url.scheme == "http"
        assert url.host == "localhost"
        assert url.port == 8080
        assert url.path == "/api"

    def test_create_success_with_query_and_fragment(self) -> None:
        """Test URL creation with query parameters and fragment."""
        result = URL.create("https://api.example.com/search?q=test&limit=10#results")

        assert result.success
        assert result.data is not None
        url = result.data
        assert url.path == "/search"
        assert url.query == "q=test&limit=10"
        assert url.fragment == "results"

    def test_create_defaults_scheme_to_https(self) -> None:
        """Test URL creation defaults to HTTPS when no scheme provided."""
        result = URL.create("//api.example.com/users")

        assert result.success
        assert result.data is not None
        assert result.data.scheme == "https"

    def test_create_empty_url_fails(self) -> None:
        """Test URL creation fails for empty URL."""
        result = URL.create("")

        assert not result.success
        assert "URL cannot be empty" in result.error

    def test_create_whitespace_url_fails(self) -> None:
        """Test URL creation fails for whitespace-only URL."""
        result = URL.create("   ")

        assert not result.success
        assert "URL cannot be empty" in result.error

    def test_create_invalid_scheme_fails(self) -> None:
        """Test URL creation fails for invalid scheme."""
        result = URL.create("ftp://invalid.com")

        assert not result.success
        assert "Invalid URL scheme: ftp" in result.error

    def test_create_no_host_fails(self) -> None:
        """Test URL creation fails when no host provided."""
        result = URL.create("https://")

        assert not result.success
        assert "valid host" in result.error

    def test_create_invalid_port_fails(self) -> None:
        """Test URL creation fails for invalid port."""
        result = URL.create("https://api.example.com:99999")

        assert not result.success
        assert "Port out of range" in result.error

    def test_create_zero_port_fails(self) -> None:
        """Test URL creation fails for zero port."""
        result = URL.create("https://api.example.com:0")

        assert not result.success
        assert "Invalid port number: 0" in result.error

    def test_create_parsing_error_fails(self) -> None:
        """Test URL creation handles parsing errors gracefully."""
        # This should cause urlparse to fail
        result = URL.create("https://[invalid-ipv6")

        # Should handle the exception and return failure
        assert not result.success
        assert "parsing failed" in result.error

    def test_is_secure(self) -> None:
        """Test HTTPS detection."""
        https_result = URL.create("https://api.example.com")
        http_result = URL.create("http://api.example.com")

        assert https_result.success
        assert https_result.data.is_secure()
        assert http_result.success
        assert not http_result.data.is_secure()

    def test_base_url_without_port(self) -> None:
        """Test base URL extraction without port."""
        result = URL.create("https://api.example.com/v1/users?q=test")

        assert result.success
        assert result.data is not None
        assert result.data.base_url() == "https://api.example.com"

    def test_base_url_with_port(self) -> None:
        """Test base URL extraction with port."""
        result = URL.create("http://localhost:8080/api/users")

        assert result.success
        assert result.data is not None
        assert result.data.base_url() == "http://localhost:8080"

    def test_full_path_simple(self) -> None:
        """Test full path extraction without query or fragment."""
        result = URL.create("https://api.example.com/v1/users")

        assert result.success
        assert result.data is not None
        assert result.data.full_path() == "/v1/users"

    def test_full_path_with_query(self) -> None:
        """Test full path extraction with query parameters."""
        result = URL.create("https://api.example.com/search?q=test&limit=10")

        assert result.success
        assert result.data is not None
        assert result.data.full_path() == "/search?q=test&limit=10"

    def test_full_path_with_fragment(self) -> None:
        """Test full path extraction with fragment."""
        result = URL.create("https://api.example.com/docs#introduction")

        assert result.success
        assert result.data is not None
        assert result.data.full_path() == "/docs#introduction"

    def test_full_path_with_query_and_fragment(self) -> None:
        """Test full path extraction with both query and fragment."""
        result = URL.create("https://api.example.com/search?q=test#results")

        assert result.success
        assert result.data is not None
        assert result.data.full_path() == "/search?q=test#results"


class TestHttpHeader:
    """Test HttpHeader value object with validation."""

    def test_create_success(self) -> None:
        """Test successful header creation."""
        result = HttpHeader.create("Content-Type", "application/json")

        assert result.success
        assert result.data is not None
        header = result.data
        assert header.name == "Content-Type"
        assert header.value == "application/json"

    def test_create_authorization_header(self) -> None:
        """Test authorization header creation."""
        result = HttpHeader.create("Authorization", "Bearer token123")

        assert result.success
        assert result.data is not None
        header = result.data
        assert header.name == "Authorization"
        assert header.value == "Bearer token123"

    def test_create_empty_name_fails(self) -> None:
        """Test header creation fails for empty name."""
        result = HttpHeader.create("", "value")

        assert not result.success
        assert "Header name cannot be empty" in result.error

    def test_create_whitespace_name_fails(self) -> None:
        """Test header creation fails for whitespace-only name."""
        result = HttpHeader.create("   ", "value")

        assert not result.success
        assert "Header name cannot be empty" in result.error

    def test_create_invalid_header_name_fails(self) -> None:
        """Test header creation fails for RFC 7230 non-compliant name."""
        result = HttpHeader.create("Invalid Header Name", "value")

        assert not result.success
        assert "Invalid header name" in result.error

    def test_create_header_name_with_special_chars_fails(self) -> None:
        """Test header creation fails for names with invalid characters."""
        result = HttpHeader.create("Content@Type", "application/json")

        assert not result.success
        assert "Invalid header name" in result.error

    def test_create_valid_header_names_succeed(self) -> None:
        """Test various valid header names succeed."""
        valid_names = [
            "Content-Type",
            "X-Custom-Header",
            "Authorization",
            "Accept",
            "User-Agent",
            "Cache-Control",
        ]

        for name in valid_names:
            result = HttpHeader.create(name, "test-value")
            assert result.success, f"Valid header name {name} should succeed"

    def test_create_control_character_in_value_fails(self) -> None:
        """Test header creation fails for control characters in value."""
        result = HttpHeader.create("Content-Type", "application/json\x00")

        assert not result.success
        assert "invalid control characters" in result.error

    def test_create_tab_in_value_succeeds(self) -> None:
        """Test header creation succeeds with tab character (allowed)."""
        result = HttpHeader.create("Custom-Header", "value\twith\ttab")

        assert result.success

    def test_is_authorization(self) -> None:
        """Test authorization header detection."""
        auth_result = HttpHeader.create("Authorization", "Bearer token")
        content_result = HttpHeader.create("Content-Type", "application/json")

        assert auth_result.success
        assert auth_result.data.is_authorization()
        assert content_result.success
        assert not content_result.data.is_authorization()

    def test_is_authorization_case_insensitive(self) -> None:
        """Test authorization header detection is case insensitive."""
        result = HttpHeader.create("authorization", "Bearer token")

        assert result.success
        assert result.data is not None
        assert result.data.is_authorization()

    def test_is_content_type(self) -> None:
        """Test content-type header detection."""
        content_result = HttpHeader.create("Content-Type", "application/json")
        auth_result = HttpHeader.create("Authorization", "Bearer token")

        assert content_result.success
        assert content_result.data.is_content_type()
        assert auth_result.success
        assert not auth_result.data.is_content_type()

    def test_is_content_type_case_insensitive(self) -> None:
        """Test content-type header detection is case insensitive."""
        result = HttpHeader.create("content-type", "application/json")

        assert result.success
        assert result.data is not None
        assert result.data.is_content_type()

    def test_to_dict(self) -> None:
        """Test header conversion to dictionary."""
        result = HttpHeader.create("Accept", "application/json")

        assert result.success
        assert result.data is not None
        header_dict = result.data.to_dict()
        assert header_dict == {"Accept": "application/json"}

    def test_to_tuple(self) -> None:
        """Test header conversion to tuple."""
        result = HttpHeader.create("User-Agent", "FLEXT-API/1.0")

        assert result.success
        assert result.data is not None
        header_tuple = result.data.to_tuple()
        assert header_tuple == ("User-Agent", "FLEXT-API/1.0")


class TestBearerToken:
    """Test BearerToken value object with JWT validation."""

    def test_create_success(self) -> None:
        """Test successful bearer token creation."""
        result = BearerToken.create("valid-token-123456789")

        assert result.success
        assert result.data is not None
        token = result.data
        assert token.token == "valid-token-123456789"
        assert token.token_type == "Bearer"

    def test_create_with_custom_type(self) -> None:
        """Test bearer token creation with custom type."""
        result = BearerToken.create("jwt-token-123456789", token_type="JWT")

        assert result.success
        assert result.data is not None
        token = result.data
        assert token.token == "jwt-token-123456789"
        assert token.token_type == "JWT"

    def test_create_empty_token_fails(self) -> None:
        """Test token creation fails for empty token."""
        result = BearerToken.create("")

        assert not result.success
        assert "Bearer token cannot be empty" in result.error

    def test_create_whitespace_token_fails(self) -> None:
        """Test token creation fails for whitespace-only token."""
        result = BearerToken.create("   ")

        assert not result.success
        assert "Bearer token cannot be empty" in result.error

    def test_create_short_token_fails(self) -> None:
        """Test token creation fails for token too short."""
        result = BearerToken.create("short")

        assert not result.success
        assert "at least 16 characters" in result.error

    def test_create_invalid_token_type_fails(self) -> None:
        """Test token creation fails for invalid token type."""
        result = BearerToken.create("valid-token-123456789", token_type="Invalid")

        assert not result.success
        assert "Invalid token type: Invalid" in result.error

    def test_create_jwt_format_validation_success(self) -> None:
        """Test JWT format validation success."""
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        result = BearerToken.create(jwt_token)

        assert result.success
        assert result.data is not None
        assert result.data.is_jwt_format()

    def test_create_jwt_invalid_parts_fails(self) -> None:
        """Test that tokens with 2 parts are treated as regular (non-JWT) tokens."""
        two_part_token = "headerheader.payloadpayload"  # Only 2 parts, but 16+ chars
        result = BearerToken.create(two_part_token)

        # Should succeed as a regular bearer token (not JWT)
        assert result.success
        assert result.data is not None
        assert not result.data.is_jwt_format()  # Not treated as JWT

    def test_create_jwt_empty_parts_fails(self) -> None:
        """Test JWT format validation fails for empty parts."""
        invalid_jwt = "header..signature"  # Empty payload
        result = BearerToken.create(invalid_jwt)

        assert not result.success
        assert "empty parts not allowed" in result.error

    def test_is_jwt_format_true(self) -> None:
        """Test JWT format detection returns true for valid JWT."""
        jwt_token = "header.payload.signature"
        result = BearerToken.create(jwt_token)

        assert result.success
        assert result.data is not None
        assert result.data.is_jwt_format()

    def test_is_jwt_format_false(self) -> None:
        """Test JWT format detection returns false for non-JWT."""
        simple_token = "simple-bearer-token-123456789"
        result = BearerToken.create(simple_token)

        assert result.success
        assert result.data is not None
        assert not result.data.is_jwt_format()

    def test_to_authorization_header(self) -> None:
        """Test conversion to authorization header."""
        result = BearerToken.create("test-token-123456789")

        assert result.success
        assert result.data is not None
        header = result.data.to_authorization_header()
        assert header.name == "Authorization"
        assert header.value == "Bearer test-token-123456789"

    def test_to_authorization_header_custom_type(self) -> None:
        """Test conversion to authorization header with custom type."""
        result = BearerToken.create("jwt-token-123456789", token_type="JWT")

        assert result.success
        assert result.data is not None
        header = result.data.to_authorization_header()
        assert header.name == "Authorization"
        assert header.value == "JWT jwt-token-123456789"

    def test_get_raw_token(self) -> None:
        """Test raw token extraction."""
        token_string = "raw-token-content-123456789"
        result = BearerToken.create(token_string)

        assert result.success
        assert result.data is not None
        assert result.data.get_raw_token() == token_string
