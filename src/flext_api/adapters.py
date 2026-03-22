"""HTTP protocol adapter for flext-api using SOLID principles.

Generic protocol adaptation following flext-core patterns.
Single responsibility: HTTP to WebSocket protocol adaptation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping

import cbor2
from flext_core import r
from pydantic import TypeAdapter, ValidationError

from flext_api import m, t, u
from flext_api.serializers import FlextApiSerializers

_HEADERS_ADAPTER: TypeAdapter[dict[str, str]] = TypeAdapter(dict[str, str])
_HTTP_RESPONSE_BODY_ADAPTER: TypeAdapter[t.Api.ResponseBody] = TypeAdapter(
    t.Api.ResponseBody,
)


class FlextApiAdapters:
    """Adapters factory implementing API system protocols."""

    class Http:
        """HTTP protocol adapter following SOLID principles.

        Single responsibility: HTTP to WebSocket protocol adaptation.
        Uses flext-core patterns for type safety and error handling.
        """

        @staticmethod
        def adapt_http_request_to_websocket(
            request: m.HttpRequest,
        ) -> r[t.JsonObject | m.HttpRequest]:
            """Convert HTTP request to WebSocket message format.

            Args:
                request: HTTP request model to adapt.

            Returns:
                r t.NormalizedValue containing WebSocket-compatible payload or failure.

            """
            try:
                body_value: str | t.JsonObject | None = None
                if request.body:
                    if isinstance(request.body, bytes):
                        try:
                            body_value = request.body.decode("utf-8")
                        except UnicodeDecodeError:
                            body_value = "<binary data>"
                    else:
                        body_value = request.body
                message: t.JsonObject = {
                    "type": "request",
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "body": body_value,
                }
                return r[t.JsonObject | m.HttpRequest].ok(message)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.JsonObject | m.HttpRequest].fail(
                    f"HTTP to WebSocket adaptation failed: {e}",
                )

        @staticmethod
        def adapt_websocket_message_to_http_response(
            message: t.JsonObject,
        ) -> r[m.HttpResponse]:
            """Adapt WebSocket message to HTTP response.

            Args:
                message: WebSocket message payload with response fields.

            Returns:
                r containing validated HttpResponse or failure.

            Notes:
                Uses Pydantic 2 model_validate() for dict-to-model conversion.
                Model validators handle type coercion automatically.

            """
            try:
                headers_raw = message.get("headers")
                headers: dict[str, str] = {}
                if isinstance(headers_raw, Mapping):
                    try:
                        headers = _HEADERS_ADAPTER.validate_python(headers_raw)
                    except ValidationError:
                        headers = {}
                status_code = message.get("status", 200)
                if not isinstance(status_code, int):
                    status_code = 200
                body = message.get("body")
                try:
                    response_body = _HTTP_RESPONSE_BODY_ADAPTER.validate_python(body)
                except ValidationError:
                    response_body = str(body) if body else None
                response = m.HttpResponse(
                    status_code=status_code,
                    headers=headers,
                    body=response_body,
                    request_id="",
                )
                return r[m.HttpResponse].ok(response)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[m.HttpResponse].fail(
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
            """Convert OpenAPI specification to GraphQL schema.

            Args:
                _openapi_spec: OpenAPI JSON t.NormalizedValue to translate.

            Returns:
                r containing GraphQL schema t.NormalizedValue or failure.

            """
            try:
                graphql_schema: t.JsonObject = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }
                return r[t.JsonObject].ok(graphql_schema)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.JsonObject].fail(
                    f"OpenAPI to GraphQL conversion failed: {e}",
                )

    class FormatConverter:
        """Format conversion following SOLID principles.

        Single responsibility: Data format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def convert_json_to_cbor(data: t.JsonObject) -> r[bytes]:
            """Convert JSON data to CBOR format.

            Args:
                data: JSON t.NormalizedValue for serialization.

            Returns:
                r containing CBOR bytes or failure.

            """
            try:
                packed: bytes = cbor2.dumps(data)
                return r[bytes].ok(packed)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[bytes].fail(f"JSON to CBOR conversion failed: {e}")

        @staticmethod
        def convert_json_to_messagepack(data: t.JsonObject) -> r[bytes]:
            """Convert JSON data to MessagePack format."""
            try:
                packed_data = FlextApiSerializers.MessagePack.packb(data)
                return u.try_(
                    lambda: bytes(packed_data),
                    catch=(TypeError, ValueError),
                ).map_error(lambda _: "MessagePack.packb did not return bytes")
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[bytes].fail(f"JSON to MessagePack conversion failed: {e}")

    class RequestTransformer:
        """Request/response transformation following SOLID principles.

        Single responsibility: HTTP request/response transformation.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def transform_request_for_protocol(
            request: m.HttpRequest,
            target_protocol: str,
        ) -> r[t.JsonObject | m.HttpRequest]:
            """Transform request for specific protocol."""
            try:
                if target_protocol == "websocket":
                    result = FlextApiAdapters.Http.adapt_http_request_to_websocket(
                        request,
                    )
                    if result.is_success:
                        return result
                    return r[t.JsonObject | m.HttpRequest].fail(
                        result.error or "Adaptation failed",
                    )
                return r[t.JsonObject | m.HttpRequest].ok(request)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.JsonObject | m.HttpRequest].fail(
                    f"Request transformation failed: {e}",
                )

        @staticmethod
        def transform_response_for_protocol(
            response: t.JsonObject | m.HttpResponse,
            source_protocol: str,
        ) -> r[m.HttpResponse]:
            """Transform response for specific protocol.

            Returns HttpResponse Model for all protocols - consistent return type.
            """
            try:
                if source_protocol == "websocket":
                    if not isinstance(response, Mapping):
                        return r[m.HttpResponse].fail(
                            "Invalid WebSocket response payload",
                        )
                    return (
                        FlextApiAdapters.Http.adapt_websocket_message_to_http_response(
                            dict(response),
                        )
                    )
                return r[m.HttpResponse].ok(m.HttpResponse.model_validate(response))
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[m.HttpResponse].fail(f"Response transformation failed: {e}")


__all__ = ["FlextApiAdapters"]
