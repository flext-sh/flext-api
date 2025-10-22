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
            request: object,
        ) -> FlextResult[dict[str, Any]]:
            """Convert HTTP request to WebSocket message format."""
            try:
                # Convert body to string if bytes, otherwise use as-is
                body_value: str | dict[str, Any] | list[Any] | None = None
                if hasattr(request, "body"):
                    body = getattr(request, "body", None)
                    if body is not None:
                        try:
                            body_value = body.decode("utf-8")  # type: ignore[union-attr]
                        except (UnicodeDecodeError, AttributeError):
                            body_value = "<binary data>"

                message: dict[str, Any] = {
                    "type": "request",
                    "method": getattr(request, "method", "GET"),
                    "url": str(getattr(request, "url", "")),
                    "headers": dict(getattr(request, "headers", {})),
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
        ) -> FlextResult[FlextApiModels.HttpResponse]:
            """Adapt WebSocket message to HTTP response."""
            try:
                # Convert WebSocket message to HTTP response
                status_code = message.get("status", 200)
                body = message.get("body", {})

                return FlextResult[FlextApiModels.HttpResponse].ok(
                    FlextApiModels.create_response(
                        status_code=status_code,
                        body=body,
                        headers=message.get("headers", {}),
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
                graphql_schema = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }

                return FlextResult.ok(graphql_schema)

            except Exception as e:
                return FlextResult.fail(f"OpenAPI to GraphQL conversion failed: {e}")

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
                packed = msgpack.packb(data)
                return FlextResult.ok(packed)

            except Exception as e:
                return FlextResult.fail(f"JSON to MessagePack conversion failed: {e}")

        @staticmethod
        def convert_json_to_cbor(data: dict[str, Any]) -> FlextResult[bytes]:
            """Convert JSON data to CBOR format."""
            try:
                packed = cbor2.dumps(data)
                return FlextResult.ok(packed)

            except Exception as e:
                return FlextResult.fail(f"JSON to CBOR conversion failed: {e}")

    class RequestTransformer:
        """Request/response transformation following SOLID principles.

        Single responsibility: HTTP request/response transformation.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def transform_request_for_protocol(
            request: object, target_protocol: str
        ) -> FlextResult[object]:
            """Transform request for specific protocol."""
            try:
                if target_protocol == "websocket":
                    result = (
                        FlextApiAdapters.HttpProtocol.adapt_http_request_to_websocket(
                            request
                        )
                    )
                    if result.is_success:
                        return FlextResult[object].ok(result.value)
                    return FlextResult[object].fail(result.error or "Adaptation failed")
                return FlextResult[object].ok(request)

            except Exception as e:
                return FlextResult[object].fail(f"Request transformation failed: {e}")

        @staticmethod
        def transform_response_for_protocol(
            response: object, source_protocol: str
        ) -> FlextResult[object]:
            """Transform response for specific protocol."""
            try:
                if source_protocol == "websocket" and isinstance(response, dict):
                    result = FlextApiAdapters.HttpProtocol.adapt_websocket_message_to_http_response(
                        response
                    )
                    if result.is_success:
                        return FlextResult[object].ok(result.value)
                    return FlextResult[object].fail(result.error or "Adaptation failed")
                return FlextResult[object].ok(response)

            except Exception as e:
                return FlextResult[object].fail(f"Response transformation failed: {e}")


__all__ = [
    "FlextApiAdapters",
]
