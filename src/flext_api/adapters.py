"""HTTP protocol adapter for flext-api using SOLID principles.

Generic protocol adaptation following flext-core patterns.
Single responsibility: HTTP to WebSocket protocol adaptation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import cast

import cbor2
import msgpack
from flext_core import r

from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


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
        ) -> r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest]:
            """Convert HTTP request to WebSocket message format."""
            try:
                # Convert body to string if bytes, otherwise use as-is
                body_value: str | FlextApiTypes.JsonObject | None = None
                if request.body:
                    if isinstance(request.body, bytes):
                        try:
                            body_value = request.body.decode("utf-8")
                        except UnicodeDecodeError:
                            body_value = "<binary data>"
                    elif isinstance(request.body, (str, dict)):
                        body_value = request.body

                message: FlextApiTypes.JsonObject = {
                    "type": "request",
                    "method": request.method,
                    "url": str(request.url),
                    "headers": (
                        dict(request.headers) if request.headers is not None else {}
                    ),
                    "body": body_value,
                }

                return r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest].ok(
                    message,
                )

            except Exception as e:
                return r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest].fail(
                    f"HTTP to WebSocket adaptation failed: {e}",
                )

        @staticmethod
        def adapt_websocket_message_to_http_response(
            message: FlextApiTypes.JsonObject,
        ) -> r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject]:
            """Adapt WebSocket message to HTTP response."""
            try:
                # Convert WebSocket message to HTTP response
                status_code_value: int = 200
                if "status" in message:
                    status_raw = message["status"]
                    if isinstance(status_raw, int):
                        status_code_value = status_raw

                body: FlextApiTypes.JsonObject = {}
                if "body" in message:
                    body_value = message["body"]
                    if isinstance(body_value, dict):
                        # Type narrowing: build dict with proper iteration
                        for k, v in body_value.items():
                            # Cast to JsonValue to match dict value type
                            body[k] = cast("FlextApiTypes.JsonValue", v)

                headers: dict[str, str] = {}
                if "headers" in message:
                    headers_value = message["headers"]
                    if isinstance(headers_value, dict):
                        # Type narrowing: convert dict values to str
                        headers = {
                            k: str(v) if not isinstance(v, str) else v
                            for k, v in headers_value.items()
                        }

                return r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject].ok(
                    FlextApiModels.create_response(
                        status_code=status_code_value,
                        body=body,
                        headers=headers,
                    ),
                )

            except Exception as e:
                return r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject].fail(
                    f"WebSocket to HTTP adaptation failed: {e}",
                )

    class Schema:
        """Schema adaptation following SOLID principles.

        Single responsibility: Schema format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def adapt_openapi_to_graphql_schema(
            _openapi_spec: FlextApiTypes.JsonObject,
        ) -> r[FlextApiTypes.JsonObject]:
            """Convert OpenAPI specification to GraphQL schema."""
            try:
                # Simplified OpenAPI to GraphQL conversion
                graphql_schema: FlextApiTypes.JsonObject = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }

                return r[FlextApiTypes.JsonObject].ok(graphql_schema)

            except Exception as e:
                return r[FlextApiTypes.JsonObject].fail(
                    f"OpenAPI to GraphQL conversion failed: {e}",
                )

    class FormatConverter:
        """Format conversion following SOLID principles.

        Single responsibility: Data format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def convert_json_to_messagepack(
            data: FlextApiTypes.JsonObject,
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
        def convert_json_to_cbor(data: FlextApiTypes.JsonObject) -> r[bytes]:
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
        ) -> r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest]:
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
                    return r[
                        FlextApiTypes.JsonObject | FlextApiModels.HttpRequest
                    ].fail(result.error or "Adaptation failed")
                return r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest].ok(
                    request,
                )

            except Exception as e:
                return r[FlextApiTypes.JsonObject | FlextApiModels.HttpRequest].fail(
                    f"Request transformation failed: {e}",
                )

        @staticmethod
        def transform_response_for_protocol(
            response: FlextApiTypes.JsonObject | FlextApiModels.HttpResponse,
            source_protocol: str,
        ) -> r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject]:
            """Transform response for specific protocol."""
            try:
                if source_protocol == "websocket" and isinstance(response, dict):
                    result = FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
                        response,
                    )
                    if result.is_success:
                        return result
                    return r[
                        FlextApiModels.HttpResponse | FlextApiTypes.JsonObject
                    ].fail(result.error or "Adaptation failed")
                if isinstance(response, FlextApiModels.HttpResponse):
                    return r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject].ok(
                        response,
                    )
                return r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject].fail(
                    "Invalid response type",
                )

            except Exception as e:
                return r[FlextApiModels.HttpResponse | FlextApiTypes.JsonObject].fail(
                    f"Response transformation failed: {e}",
                )


__all__ = [
    "FlextApiAdapters",
]
