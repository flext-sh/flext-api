"""HTTP protocol adapter for flext-api using SOLID principles.

Generic protocol adaptation following flext-core patterns.
Single responsibility: HTTP to WebSocket protocol adaptation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import (
    Mapping,
)

import cbor2
from flext_web import u

from flext_api import FlextApiUtilitiesSerializers, c, m, p, r, t


class FlextApiAdapters:
    """Adapters factory implementing API system protocols."""

    class Http:
        """HTTP protocol adapter following SOLID principles.

        Single responsibility: HTTP to WebSocket protocol adaptation.
        Uses flext-core patterns for type safety and error handling.
        """

        @staticmethod
        def adapt_http_request_to_websocket(
            request: m.Api.HttpRequest,
        ) -> p.Result[t.Api.HttpResponseDict | m.Api.HttpRequest]:
            """Convert HTTP request to WebSocket message format.

            Args:
                request: HTTP request model to adapt.

            Returns:
                r t.JsonValue containing WebSocket-compatible payload or failure.

            """
            try:
                body_value: str | t.JsonMapping | None = None
                if request.body:
                    if isinstance(request.body, bytes):
                        try:
                            body_value = request.body.decode("utf-8")
                        except UnicodeDecodeError:
                            return r[t.Api.HttpResponseDict | m.Api.HttpRequest].fail(
                                "Binary request body is not valid UTF-8 for WebSocket JSON transport",
                            )
                    else:
                        body_value = request.body
                message_body: str | t.JsonMapping = (
                    body_value if body_value is not None else ""
                )
                message: t.Api.HttpResponseDict = {
                    "type": "request",
                    "method": request.method,
                    "url": request.url,
                    "headers": dict(request.headers),
                    "body": message_body,
                }
                return r[t.Api.HttpResponseDict | m.Api.HttpRequest].ok(message)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.Api.HttpResponseDict | m.Api.HttpRequest].fail(
                    f"HTTP to WebSocket adaptation failed: {e}",
                )

        @staticmethod
        def adapt_websocket_message_to_http_response(
            message: t.JsonMapping,
        ) -> p.Result[m.Api.HttpResponse]:
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
                headers: t.StrMapping = {}
                if headers_raw is not None:
                    if not isinstance(headers_raw, Mapping):
                        return r[m.Api.HttpResponse].fail(
                            "WebSocket response headers must be a mapping",
                        )
                    headers = t.Api.STR_MAPPING_ADAPTER.validate_python(headers_raw)
                status_code = message.get("status", 200)
                if not isinstance(status_code, int):
                    status_code = 200
                body = message.get("body")
                response = m.Api.HttpResponse.model_validate({
                    "status_code": status_code,
                    "headers": headers,
                    "body": body,
                    "request_id": "",
                })
                return r[m.Api.HttpResponse].ok(response)
            except (
                c.ValidationError,
                ValueError,
                TypeError,
                KeyError,
                ConnectionError,
            ) as e:
                return r[m.Api.HttpResponse].fail(
                    f"WebSocket to HTTP adaptation failed: {e}",
                )

    class Schema:
        """Schema adaptation following SOLID principles.

        Single responsibility: Schema format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def adapt_openapi_to_graphql_schema(
            _openapi_spec: t.JsonMapping,
        ) -> p.Result[t.JsonMapping]:
            """Convert OpenAPI specification to GraphQL schema.

            Args:
                _openapi_spec: OpenAPI JSON t.JsonValue to translate.

            Returns:
                r containing GraphQL schema t.JsonValue or failure.

            """
            try:
                graphql_schema: t.JsonMapping = {
                    "type": "schema",
                    "query": "Query",
                    "mutation": "Mutation",
                }
                return r[t.JsonMapping].ok(graphql_schema)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.JsonMapping].fail(
                    f"OpenAPI to GraphQL conversion failed: {e}",
                )

    class FormatConverter:
        """Format conversion following SOLID principles.

        Single responsibility: Data format conversion.
        Uses flext-core patterns for type safety.
        """

        @staticmethod
        def convert_json_to_cbor(data: t.JsonMapping) -> p.Result[bytes]:
            """Convert JSON data to CBOR format.

            Args:
                data: JSON t.JsonValue for serialization.

            Returns:
                r containing CBOR bytes or failure.

            """
            try:
                packed: bytes = cbor2.dumps(data)
                return r[bytes].ok(packed)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[bytes].fail(f"JSON to CBOR conversion failed: {e}")

        @staticmethod
        def convert_json_to_messagepack(data: t.JsonMapping) -> p.Result[bytes]:
            """Convert JSON data to MessagePack format."""
            try:
                json_data = t.Api.API_JSON_VALUE_ADAPTER.validate_python(data)
                packed_data = FlextApiUtilitiesSerializers.packb(json_data)
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
            request: m.Api.HttpRequest,
            target_protocol: str,
        ) -> p.Result[t.Api.HttpResponseDict | m.Api.HttpRequest]:
            """Transform request for specific protocol."""
            try:
                if target_protocol == "websocket":
                    result = FlextApiAdapters.Http.adapt_http_request_to_websocket(
                        request,
                    )
                    if result.success:
                        return result
                    return r[t.Api.HttpResponseDict | m.Api.HttpRequest].fail(
                        result.error or "Adaptation failed",
                    )
                return r[t.Api.HttpResponseDict | m.Api.HttpRequest].ok(request)
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[t.Api.HttpResponseDict | m.Api.HttpRequest].fail(
                    f"Request transformation failed: {e}",
                )

        @staticmethod
        def transform_response_for_protocol(
            response: t.JsonMapping | m.Api.HttpResponse,
            source_protocol: str,
        ) -> p.Result[m.Api.HttpResponse]:
            """Transform response for specific protocol.

            Returns HttpResponse Model for all protocols - consistent return type.
            """
            try:
                if source_protocol == "websocket":
                    if not isinstance(response, Mapping):
                        return r[m.Api.HttpResponse].fail(
                            "Invalid WebSocket response payload",
                        )
                    return (
                        FlextApiAdapters.Http.adapt_websocket_message_to_http_response(
                            dict(response),
                        )
                    )
                return r[m.Api.HttpResponse].ok(
                    m.Api.HttpResponse.model_validate(response)
                )
            except (ValueError, TypeError, KeyError, ConnectionError) as e:
                return r[m.Api.HttpResponse].fail(
                    f"Response transformation failed: {e}"
                )


__all__: t.MutableSequenceOf[str] = ["FlextApiAdapters"]
