"""HTTP protocol adapter for flext-api using SOLID principles.

Generic protocol adaptation following flext-core patterns.
Single responsibility: HTTP to WebSocket protocol adaptation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Any

import cbor2
import msgpack
from flext_core import FlextResult

from flext_api.models import FlextApiModels


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
        ) -> FlextResult[dict[str, Any] | FlextApiModels.HttpRequest]:
            """Convert HTTP request to WebSocket message format."""
            try:
                # Convert body to string if bytes, otherwise use as-is
                body_value: str | dict[str, Any] | list[Any] | None = None
                if request.body:
                    if isinstance(request.body, bytes):
                        try:
                            body_value = request.body.decode("utf-8")
                        except UnicodeDecodeError:
                            body_value = "<binary data>"
                    elif isinstance(request.body, (str, dict, list)):
                        body_value = request.body

                message: dict[str, Any] = {
                    "type": "request",
                    "method": request.method,
                    "url": str(request.url),
                    "headers": (
                        dict(request.headers) if request.headers is not None else {}
                    ),
                    "body": body_value,
                }

                return FlextResult[dict[str, Any]].ok(message)

            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"HTTP to WebSocket adaptation failed: {e}"
                )

        @staticmethod
        def adapt_websocket_message_to_http_response(
            message: dict[str, Any],
        ) -> FlextResult[FlextApiModels.HttpResponse | dict[str, Any]]:
            """Adapt WebSocket message to HTTP response."""
            try:
                # Convert WebSocket message to HTTP response
                status_code_value: int = 200
                if "status" in message:
                    status_raw = message["status"]
                    if isinstance(status_raw, int):
                        status_code_value = status_raw

                body: dict[str, Any] = {}
                if "body" in message:
                    body_value = message["body"]
                    if isinstance(body_value, dict):
                        body = body_value

                headers: dict[str, str] = {}
                if "headers" in message:
                    headers_value = message["headers"]
                    if isinstance(headers_value, dict):
                        headers = headers_value

                return FlextResult[FlextApiModels.HttpResponse].ok(
                    FlextApiModels.create_response(
                        status_code=status_code_value,
                        body=body,
                        headers=headers,
                    )
                )

            except Exception as e:
                return FlextResult[FlextApiModels.HttpResponse].fail(
                    f"WebSocket to HTTP adaptation failed: {e}"
                )

    class Schema:
        """Schema adaptation following SOLID principles.

        Single responsibility: Schema format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def adapt_openapi_to_graphql_schema(
            _openapi_spec: dict[str, Any],
        ) -> FlextResult[dict[str, Any]]:
            """Convert OpenAPI specification to GraphQL schema."""
            try:
                # Simplified OpenAPI to GraphQL conversion
                graphql_schema: dict[str, Any] = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }

                return FlextResult[dict[str, Any]].ok(graphql_schema)

            except Exception as e:
                return FlextResult[dict[str, Any]].fail(
                    f"OpenAPI to GraphQL conversion failed: {e}"
                )

    class FormatConverter:
        """Format conversion following SOLID principles.

        Single responsibility: Data format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def convert_json_to_messagepack(data: dict[str, Any]) -> FlextResult[bytes]:
            """Convert JSON data to MessagePack format."""
            try:
                # msgpack.packb returns bytes for valid input
                packed_data = msgpack.packb(data)
                if not isinstance(packed_data, bytes):
                    return FlextResult[bytes].fail("msgpack.packb did not return bytes")
                # msgpack.packb always returns bytes for valid input
                return FlextResult[bytes].ok(packed_data)

            except Exception as e:
                return FlextResult[bytes].fail(
                    f"JSON to MessagePack conversion failed: {e}"
                )

        @staticmethod
        def convert_json_to_cbor(data: dict[str, Any]) -> FlextResult[bytes]:
            """Convert JSON data to CBOR format."""
            try:
                packed: bytes = cbor2.dumps(data)
                return FlextResult[bytes].ok(packed)

            except Exception as e:
                return FlextResult[bytes].fail(f"JSON to CBOR conversion failed: {e}")

    class RequestTransformer:
        """Request/response transformation following SOLID principles.

        Single responsibility: HTTP request/response transformation.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def transform_request_for_protocol(
            request: FlextApiModels.HttpRequest, target_protocol: str
        ) -> FlextResult[dict[str, Any] | FlextApiModels.HttpRequest]:
            """Transform request for specific protocol."""
            try:
                if target_protocol == "websocket":
                    result = (
                        FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(
                            request
                        )
                    )
                    if result.is_success:
                        return result
                    return FlextResult[
                        dict[str, Any] | FlextApiModels.HttpRequest
                    ].fail(result.error or "Adaptation failed")
                return FlextResult[dict[str, Any] | FlextApiModels.HttpRequest].ok(
                    request
                )

            except Exception as e:
                return FlextResult[dict[str, Any] | FlextApiModels.HttpRequest].fail(
                    f"Request transformation failed: {e}"
                )

        @staticmethod
        def transform_response_for_protocol(
            response: dict[str, Any] | FlextApiModels.HttpResponse, source_protocol: str
        ) -> FlextResult[FlextApiModels.HttpResponse | dict[str, Any]]:
            """Transform response for specific protocol."""
            try:
                if source_protocol == "websocket" and isinstance(response, dict):
                    result = FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
                        response
                    )
                    if result.is_success:
                        return result
                    return FlextResult[
                        FlextApiModels.HttpResponse | dict[str, Any]
                    ].fail(result.error or "Adaptation failed")
                if isinstance(response, FlextApiModels.HttpResponse):
                    return FlextResult[FlextApiModels.HttpResponse | dict[str, Any]].ok(
                        response
                    )
                return FlextResult[FlextApiModels.HttpResponse | dict[str, Any]].fail(
                    "Invalid response type"
                )

            except Exception as e:
                return FlextResult[FlextApiModels.HttpResponse | dict[str, Any]].fail(
                    f"Response transformation failed: {e}"
                )


__all__ = [
    "FlextApiAdapters",
]
