"""HTTP protocol adapter for flext-api using SOLID principles.

Generic protocol adaptation following flext-core patterns.
Single responsibility: HTTP to WebSocket protocol adaptation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import cbor2
import msgpack
from flext_core import r

from flext_api.models import FlextApiModels
from flext_api.typings import t


class FlextApiAdapters:
    """Adapters factory implementing API system protocols."""

    class HttpProtocol:
        """HTTP protocol adapter following SOLID principles.

        Single responsibility: HTTP to WebSocket protocol adaptation.
        Uses flext-core patterns for type safety and error handling.
        """

        @staticmethod
        def adapt_http_request_to_websocket(
            request: FlextApiModels.HttpRequest,
        ) -> r[t.JsonObject | FlextApiModels.HttpRequest]:
            """Convert HTTP request to WebSocket message format."""
            try:
                # Convert body to string if bytes, otherwise use as-is
                body_value: str | t.JsonObject | None = None
                if request.body:
                    if isinstance(request.body, bytes):
                        try:
                            body_value = request.body.decode("utf-8")
                        except UnicodeDecodeError:
                            body_value = "<binary data>"
                    elif isinstance(request.body, (str, dict)):
                        body_value = request.body

                message: t.JsonObject = {
                    "type": "request",
                    "method": request.method,
                    "url": str(request.url),
                    "headers": (
                        dict(request.headers) if request.headers is not None else {}
                    ),
                    "body": body_value,
                }

                return r[t.JsonObject | FlextApiModels.HttpRequest].ok(
                    message,
                )

            except Exception as e:
                return r[t.JsonObject | FlextApiModels.HttpRequest].fail(
                    f"HTTP to WebSocket adaptation failed: {e}",
                )

        @staticmethod
        def adapt_websocket_message_to_http_response(
            message: t.JsonObject,
        ) -> r[FlextApiModels.HttpResponse]:
            """Adapt WebSocket message to HTTP response.

            Uses Pydantic 2 model_validate() for dict-to-Model conversion.
            Model validators handle type coercion automatically.
            """
            try:
                # Extract headers with proper type narrowing
                headers_raw = message.get("headers")
                headers = (
                    {str(k): str(v) for k, v in headers_raw.items()}
                    if isinstance(headers_raw, dict)
                    else {}
                )

                # Pydantic 2 model_validate for dict→Model conversion
                response = FlextApiModels.HttpResponse.model_validate({
                    "status_code": message.get("status", 200),
                    "headers": headers,
                    "body": message.get("body"),
                })
                return r[FlextApiModels.HttpResponse].ok(response)

            except Exception as e:
                return r[FlextApiModels.HttpResponse].fail(
                    f"WebSocket to HTTP adaptation failed: {e}",
                )

    class Schema:
        """Schema adaptation following SOLID principles.

        Single responsibility: Schema format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def adapt_openapi_to_graphql_schema(
            _openapi_spec: t.JsonObject,
        ) -> r[t.JsonObject]:
            """Convert OpenAPI specification to GraphQL schema."""
            try:
                # Simplified OpenAPI to GraphQL conversion
                graphql_schema: t.JsonObject = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }

                return r[t.JsonObject].ok(graphql_schema)

            except Exception as e:
                return r[t.JsonObject].fail(
                    f"OpenAPI to GraphQL conversion failed: {e}",
                )

    class FormatConverter:
        """Format conversion following SOLID principles.

        Single responsibility: Data format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def convert_json_to_messagepack(
            data: t.JsonObject,
        ) -> r[bytes]:
            """Convert JSON data to MessagePack format."""
            try:
                # msgpack.packb returns bytes for valid input
                packed_data = msgpack.packb(data)
                if not isinstance(packed_data, bytes):
                    return r[bytes].fail("msgpack.packb did not return bytes")
                # msgpack.packb always returns bytes for valid input
                return r[bytes].ok(packed_data)

            except Exception as e:
                return r[bytes].fail(f"JSON to MessagePack conversion failed: {e}")

        @staticmethod
        def convert_json_to_cbor(data: t.JsonObject) -> r[bytes]:
            """Convert JSON data to CBOR format."""
            try:
                packed: bytes = cbor2.dumps(data)
                return r[bytes].ok(packed)

            except Exception as e:
                return r[bytes].fail(f"JSON to CBOR conversion failed: {e}")

    class RequestTransformer:
        """Request/response transformation following SOLID principles.

        Single responsibility: HTTP request/response transformation.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def transform_request_for_protocol(
            request: FlextApiModels.HttpRequest,
            target_protocol: str,
        ) -> r[t.JsonObject | FlextApiModels.HttpRequest]:
            """Transform request for specific protocol."""
            try:
                if target_protocol == "websocket":
                    result = (
                        FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(
                            request,
                        )
                    )
                    if result.is_success:
                        return result
                    return r[t.JsonObject | FlextApiModels.HttpRequest].fail(
                        result.error or "Adaptation failed",
                    )
                return r[t.JsonObject | FlextApiModels.HttpRequest].ok(
                    request,
                )

            except Exception as e:
                return r[t.JsonObject | FlextApiModels.HttpRequest].fail(
                    f"Request transformation failed: {e}",
                )

        @staticmethod
        def transform_response_for_protocol(
            response: t.JsonObject | FlextApiModels.HttpResponse,
            source_protocol: str,
        ) -> r[FlextApiModels.HttpResponse]:
            """Transform response for specific protocol.

            Returns HttpResponse Model for all protocols - consistent return type.
            """
            try:
                if source_protocol == "websocket" and isinstance(response, dict):
                    return FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
                        response,
                    )
                if isinstance(response, FlextApiModels.HttpResponse):
                    return r[FlextApiModels.HttpResponse].ok(response)

                return r[FlextApiModels.HttpResponse].fail("Invalid response type")

            except Exception as e:
                return r[FlextApiModels.HttpResponse].fail(
                    f"Response transformation failed: {e}",
                )


__all__ = [
    "FlextApiAdapters",
]
