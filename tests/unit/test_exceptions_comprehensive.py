"""Comprehensive tests for FlextApiExceptions module."""

from flext_api.exceptions import FlextApiExceptions


class TestFlextApiExceptionsComprehensive:
    """Comprehensive test suite for FlextApiExceptions."""

    def test_authentication_error(self):
        """Test authentication error."""
        exc = FlextApiExceptions.AuthenticationError("Auth failed")
        assert str(exc) == "Auth failed"
        assert isinstance(exc, Exception)

    def test_authorization_error(self):
        """Test authorization error."""
        exc = FlextApiExceptions.AuthorizationError("Not authorized")
        assert str(exc) == "Not authorized"
        assert isinstance(exc, Exception)

    def test_validation_error(self):
        """Test validation error."""
        exc = FlextApiExceptions.ValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert isinstance(exc, Exception)

    def test_not_found_error(self):
        """Test not found error."""
        exc = FlextApiExceptions.NotFoundError("Resource not found")
        assert str(exc) == "Resource not found"
        assert isinstance(exc, Exception)

    def test_conflict_error(self):
        """Test conflict error."""
        exc = FlextApiExceptions.ConflictError("Resource conflict")
        assert str(exc) == "Resource conflict"
        assert isinstance(exc, Exception)

    def test_rate_limit_error(self):
        """Test rate limit error."""
        exc = FlextApiExceptions.RateLimitError("Rate limit exceeded")
        assert str(exc) == "Rate limit exceeded"
        assert isinstance(exc, Exception)

    def test_server_error(self):
        """Test server error."""
        exc = FlextApiExceptions.ServerError("Server error")
        assert str(exc) == "Server error"
        assert isinstance(exc, Exception)

    def test_client_error(self):
        """Test client error."""
        exc = FlextApiExceptions.ClientError("Client error")
        assert str(exc) == "Client error"
        assert isinstance(exc, Exception)

    def test_http_error(self):
        """Test HTTP error."""
        exc = FlextApiExceptions.HttpError("HTTP error")
        assert str(exc) == "HTTP error"
        assert isinstance(exc, Exception)

    def test_http_timeout_error(self):
        """Test HTTP timeout error."""
        exc = FlextApiExceptions.HttpTimeoutError("HTTP timeout")
        assert str(exc) == "HTTP timeout"
        assert isinstance(exc, Exception)

    def test_bad_request_error(self):
        """Test bad request error."""
        exc = FlextApiExceptions.BadRequestError("Bad request")
        assert str(exc) == "Bad request"
        assert isinstance(exc, Exception)

    def test_unauthorized_error(self):
        """Test unauthorized error."""
        exc = FlextApiExceptions.UnauthorizedError("Unauthorized")
        assert str(exc) == "Unauthorized"
        assert isinstance(exc, Exception)

    def test_forbidden_error(self):
        """Test forbidden error."""
        exc = FlextApiExceptions.ForbiddenError("Forbidden")
        assert str(exc) == "Forbidden"
        assert isinstance(exc, Exception)

    def test_method_not_allowed_error(self):
        """Test method not allowed error."""
        exc = FlextApiExceptions.MethodNotAllowedError("Method not allowed")
        assert str(exc) == "Method not allowed"
        assert isinstance(exc, Exception)

    def test_too_many_requests_error(self):
        """Test too many requests error."""
        exc = FlextApiExceptions.TooManyRequestsError("Too many requests")
        assert str(exc) == "Too many requests"
        assert isinstance(exc, Exception)

    def test_internal_server_error(self):
        """Test internal server error."""
        exc = FlextApiExceptions.InternalServerError("Internal server error")
        assert str(exc) == "Internal server error"
        assert isinstance(exc, Exception)

    def test_bad_gateway_error(self):
        """Test bad gateway error."""
        exc = FlextApiExceptions.BadGatewayError("Bad gateway")
        assert str(exc) == "Bad gateway"
        assert isinstance(exc, Exception)

    def test_service_unavailable_error(self):
        """Test service unavailable error."""
        exc = FlextApiExceptions.ServiceUnavailableError("Service unavailable")
        assert str(exc) == "Service unavailable"
        assert isinstance(exc, Exception)

    def test_gateway_timeout_error(self):
        """Test gateway timeout error."""
        exc = FlextApiExceptions.GatewayTimeoutError("Gateway timeout")
        assert str(exc) == "Gateway timeout"
        assert isinstance(exc, Exception)

    def test_request_timeout_error(self):
        """Test request timeout error."""
        exc = FlextApiExceptions.RequestTimeoutError("Request timeout")
        assert str(exc) == "Request timeout"
        assert isinstance(exc, Exception)

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from Exception."""
        exceptions = [
            FlextApiExceptions.AuthenticationError,
            FlextApiExceptions.AuthorizationError,
            FlextApiExceptions.ValidationError,
            FlextApiExceptions.NotFoundError,
            FlextApiExceptions.ConflictError,
            FlextApiExceptions.RateLimitError,
            FlextApiExceptions.ServerError,
            FlextApiExceptions.ClientError,
            FlextApiExceptions.HttpError,
            FlextApiExceptions.HttpTimeoutError,
            FlextApiExceptions.BadRequestError,
            FlextApiExceptions.UnauthorizedError,
            FlextApiExceptions.ForbiddenError,
            FlextApiExceptions.MethodNotAllowedError,
            FlextApiExceptions.TooManyRequestsError,
            FlextApiExceptions.InternalServerError,
            FlextApiExceptions.BadGatewayError,
            FlextApiExceptions.ServiceUnavailableError,
            FlextApiExceptions.GatewayTimeoutError,
            FlextApiExceptions.RequestTimeoutError,
        ]

        for exc_class in exceptions:
            exc = exc_class("Test message")
            assert isinstance(exc, Exception)
            assert str(exc) == "Test message"

    def test_exception_with_custom_message(self):
        """Test exceptions with custom messages."""
        custom_message = "Custom error message with details"
        exc = FlextApiExceptions.ValidationError(custom_message)
        assert str(exc) == custom_message

    def test_exception_with_empty_message(self):
        """Test exceptions with empty message."""
        exc = FlextApiExceptions.HttpError("")
        assert str(exc) == ""

    def test_exception_with_none_message(self):
        """Test exceptions with None message."""
        exc = FlextApiExceptions.ServerError(None)
        assert str(exc) == "None"
