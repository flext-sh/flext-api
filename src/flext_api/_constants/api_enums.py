"""API enum constants."""

from __future__ import annotations

from enum import StrEnum, unique


class FlextApiConstantsEnums:
    """API enum constants mixed into ``c.Api``."""

    @unique
    class Method(StrEnum):
        """HTTP method enumeration."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        CONNECT = "CONNECT"
        TRACE = "TRACE"

    @unique
    class ProtocolMethod(StrEnum):
        """Protocol route method enumeration for special handlers."""

        SSE = "SSE"

    @unique
    class Status(StrEnum):
        """HTTP operation status enumeration."""

        IDLE = "idle"
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        ERROR = "error"
        SUCCESS = "success"

    @unique
    class WebhookDeliveryStatus(StrEnum):
        """Webhook delivery status enumeration."""

        FAILED = "failed"

    @unique
    class WebhookAlgorithm(StrEnum):
        """HMAC algorithm enumeration for webhook signature verification."""

        SHA256 = "sha256"

    @unique
    class ContentType(StrEnum):
        """Content type enumeration."""

        JSON = "application/json"
        XML = "application/xml"
        TEXT = "text/plain"
        HTML = "text/html"

    @unique
    class OpenApiSecuritySchemeType(StrEnum):
        """OpenAPI security scheme type enumeration."""

        API_KEY = "apiKey"
        HTTP = "http"
        OAUTH2 = "oauth2"

    @unique
    class HttpProtocol(StrEnum):
        """HTTP protocol enumeration."""

        HTTP = "http"
        HTTPS = "https"


__all__: list[str] = ["FlextApiConstantsEnums"]
