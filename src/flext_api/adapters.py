"""Protocol and format adapters for flext-api.

Provides adapters for:
|- Protocol adaptation (HTTP <-> WebSocket <-> GraphQL)
|- Schema adaptation (OpenAPI <-> API <-> GraphQL Schema)
|- Format conversion (JSON <-> MessagePack <-> CBOR)
|- Legacy API adaptation
|- Request/response transformation

See TRANSFORMATION_PLAN.md - Phase 8 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import cast

from flext_core import (
    FlextBus,
    FlextConstants,
    FlextContainer,
    FlextContext,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)
from pydantic import PrivateAttr

from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes


class FlextApiAdapters(FlextService[None]):
    """Unified API adapters service with complete flext-core integration.

    Provides protocol adaptation, schema conversion, and legacy API integration.
    All functionality consolidated into direct methods following FLEXT standards.

    Integration:
        - Extends FlextService for service lifecycle management
        - Uses FlextLogger for structured logging
        - Uses FlextResult for railway-oriented error handling
        - Uses FlextContainer for dependency injection
        - Uses FlextContext for operation context
        - Uses FlextBus for event emission
        - Uses FlextConstants for configuration values
    """

    # Type annotations for private attributes
    logger: FlextLogger = PrivateAttr()
    _container: FlextContainer = PrivateAttr()
    _context: FlextContext = PrivateAttr()
    _bus: FlextBus = PrivateAttr()
    _endpoint: str = PrivateAttr()
    _base_url: str = PrivateAttr()

    def __init__(self, endpoint: str = "/graphql", base_url: str = "") -> None:
        """Initialize the unified adapters service with complete flext-core integration."""
        # Complete flext-core integration
        self.logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        self._context = FlextContext()
        self._bus = FlextBus()

        self._endpoint = endpoint  # Default GraphQL endpoint
        self._base_url = base_url  # For legacy API adapter

    def adapt_http_request_to_websocket(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[dict[str, FlextApiTypes.JsonValue]]:
        """Convert HTTP request to WebSocket message format."""
        # Railway-oriented HTTP to WebSocket adaptation - operations are safe
        message: dict[str, FlextApiTypes.JsonValue] = {
            "type": "request",
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers) if request.headers else {},
            "body": request.body or {},
        }

        self.logger.debug(
            "HTTP request adapted to WebSocket message",
            extra={"method": request.method, "url": str(request.url)},
        )

        return FlextResult[dict[str, FlextApiTypes.JsonValue]].ok(message)

    def adapt_websocket_message_to_http_response(
        self, message: dict[str, FlextApiTypes.JsonValue]
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Adapt WebSocket message to HTTP response.

        Args:
            message: WebSocket message

        Returns:
            FlextResult containing HTTP response or error

        """
        try:
            # Convert WebSocket message to HTTP response
            status_code = message.get("status", 200)
            body = message.get("body", {})
            headers = message.get("headers", {})
            url = message.get("url", "/")
            method = message.get("method", "GET")

            request = FlextApiModels.HttpRequest(
                url=url,
                method=method,
                headers=headers,
                body=body,
            )

            response = FlextApiModels.HttpResponse(
                status_code=status_code,
                headers=headers,
                body=body,
                url=url,
                method=method,
                request=request,
            )

            self.logger.debug(
                "WebSocket message adapted to HTTP response",
                extra={"status": status_code},
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"WebSocket to HTTP adaptation failed: {e}"
            )

    def adapt_graphql_query_to_http_request(
        self, query: str, variables: FlextTypes.Dict | None = None
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Adapt GraphQL query to HTTP request.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            FlextResult containing HTTP request or error

        """
        try:
            # Convert GraphQL query to HTTP POST request
            request = FlextApiModels.HttpRequest(
                method="POST",
                url=self._endpoint,
                body={
                    "query": query,
                    "variables": variables or {},
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )

            self.logger.debug("GraphQL query adapted to HTTP request")

            return FlextResult[FlextApiModels.HttpRequest].ok(request)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpRequest].fail(
                f"GraphQL to HTTP adaptation failed: {e}"
            )

    def adapt_http_response_to_graphql_result(
        self, response: FlextApiModels.HttpResponse
    ) -> FlextResult[FlextTypes.Dict]:
        """Adapt HTTP response to GraphQL result.

        Args:
            response: HTTP response

        Returns:
            FlextResult containing GraphQL result or error

        """
        try:
            # Extract GraphQL result from HTTP response
            if response.status_code != FlextConstants.Http.HTTP_OK:
                return FlextResult[FlextTypes.Dict].fail(
                    f"GraphQL request failed with status {response.status_code}"
                )

            result = response.body if hasattr(response, "body") else {}

            # Check for GraphQL errors
            if isinstance(result, dict) and "errors" in result:
                errors = result["errors"]
                error_messages = [e.get("message", "Unknown error") for e in errors]
                return FlextResult[FlextTypes.Dict].fail(
                    f"GraphQL errors: {', '.join(error_messages)}"
                )

            self.logger.debug("HTTP response adapted to GraphQL result")

            data = result.get("data", {}) if isinstance(result, dict) else {}
            return FlextResult[FlextTypes.Dict].ok(data)

        except Exception as e:
            return FlextResult[FlextTypes.Dict].fail(
                f"HTTP to GraphQL result adaptation failed: {e}"
            )

    def convert_openapi_to_api_schema(
        self, openapi_schema: dict[str, FlextApiTypes.JsonValue]
    ) -> FlextResult[dict[str, FlextApiTypes.JsonValue]]:
        """Convert OpenAPI schema to API schema.

        Args:
            openapi_schema: OpenAPI schema

        Returns:
            FlextResult containing API schema or error

        """
        try:
            # Basic conversion from OpenAPI to API
            api_schema: dict[str, FlextApiTypes.JsonValue] = {
                "api": "3.0.0",
                "info": openapi_schema.get("info", {}),
                "channels": {},
            }

            # Convert paths to channels
            paths = openapi_schema.get("paths", {})
            if not isinstance(paths, dict):
                paths = {}
            for path, operations in paths.items():
                if not isinstance(operations, dict):
                    continue
                channel_name = path.replace("/", "_").strip("_")
                channels = api_schema["channels"]
                if not isinstance(channels, dict):
                    channels = {}
                    api_schema["channels"] = channels

                channels = cast("dict[str, FlextApiTypes.JsonValue]", channels)
                channels[channel_name] = {
                    "address": path,
                    "messages": {},
                }

                # Convert operations to messages
                channel_data = channels[channel_name]
                if isinstance(channel_data, dict):
                    messages = channel_data.get("messages", {})
                    if not isinstance(messages, dict):
                        messages = {}
                        channel_data["messages"] = messages

                    messages = cast("dict[str, FlextApiTypes.JsonValue]", messages)
                    operations_dict = cast(
                        "dict[str, FlextApiTypes.JsonValue]", operations
                    )
                    for method, operation in operations_dict.items():
                        if not isinstance(operation, dict):
                            continue
                        if method in {"get", "post", "put", "delete"}:
                            message_name = f"{method}_{channel_name}"
                            request_body = operation.get("requestBody", {})
                            if isinstance(request_body, dict):
                                content = request_body.get("content", {})
                                if isinstance(content, dict):
                                    json_content = content.get("application/json", {})
                                    if isinstance(json_content, dict):
                                        schema = json_content.get("schema", {})
                                    else:
                                        schema = {}
                                else:
                                    schema = {}
                            else:
                                schema = {}

                            messages_dict = cast(
                                "dict[str, FlextApiTypes.JsonValue]", messages
                            )
                            messages_dict[message_name] = {"payload": schema}

            self.logger.debug("OpenAPI schema converted to API")

            return FlextResult[dict[str, FlextApiTypes.JsonValue]].ok(api_schema)

        except Exception as e:
            return FlextResult[dict[str, FlextApiTypes.JsonValue]].fail(
                f"OpenAPI to API conversion failed: {e}"
            )

    def convert_openapi_to_graphql_schema(
        self, openapi_schema: dict[str, FlextApiTypes.JsonValue]
    ) -> FlextResult[str]:
        """Convert OpenAPI schema to GraphQL schema SDL.

        Args:
            openapi_schema: OpenAPI schema

        Returns:
            FlextResult containing GraphQL schema SDL or error

        """
        try:
            # Basic conversion from OpenAPI to GraphQL SDL
            types = []
            queries = []
            mutations = []

            # Convert components/schemas to GraphQL types
            components = openapi_schema.get("components", {})
            if not isinstance(components, dict):
                components = {}
            schemas = components.get("schemas", {})
            if not isinstance(schemas, dict):
                schemas = {}

            for schema_name, schema_def in schemas.items():
                if not isinstance(schema_def, dict):
                    continue
                if schema_def.get("type") == "object":
                    properties = schema_def.get("properties", {})
                    if not isinstance(properties, dict):
                        properties = {}
                    fields: FlextTypes.StringList = []

                    for prop_name, prop_def in properties.items():
                        if not isinstance(prop_def, dict):
                            continue
                        prop_type = self._map_openapi_type_to_graphql(
                            str(prop_def.get("type", "String"))
                        )
                        fields.append(f"  {prop_name}: {prop_type}")

                    type_def = f"type {schema_name} {{\n" + "\n".join(fields) + "\n}"
                    types.append(type_def)

            # Convert paths to queries and mutations
            paths = openapi_schema.get("paths", {})
            if not isinstance(paths, dict):
                paths = {}
            for path, operations in paths.items():
                if not isinstance(operations, dict):
                    continue
                for method, operation in operations.items():
                    if not isinstance(operation, dict):
                        continue
                    operation_id = operation.get("operationId", path.replace("/", "_"))
                    if not isinstance(operation_id, str):
                        operation_id = str(operation_id)

                    if method == "get":
                        # GET -> Query
                        queries.append(f"  {operation_id}: String")
                    elif method in {"post", "put", "delete"}:
                        # POST/PUT/DELETE -> Mutation
                        mutations.append(f"  {operation_id}: String")

            # Build GraphQL schema SDL
            sdl_parts = []
            sdl_parts.extend(types)

            if queries:
                sdl_parts.append("type Query {\n" + "\n".join(queries) + "\n}")

            if mutations:
                sdl_parts.append("type Mutation {\n" + "\n".join(mutations) + "\n}")

            graphql_sdl = "\n\n".join(sdl_parts)

            self.logger.debug("OpenAPI schema converted to GraphQL SDL")

            return FlextResult[str].ok(graphql_sdl)

        except Exception as e:
            return FlextResult[str].fail(
                f"OpenAPI to GraphQL schema conversion failed: {e}"
            )

    def adapt_request_to_legacy_format(
        self, modern_request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Transform request to legacy format."""
        try:
            legacy_request = FlextApiModels.HttpRequest(
                method=modern_request.method,
                url=f"{self._base_url}{modern_request.url}",
                headers=self._adapt_headers_to_legacy(
                    dict(modern_request.headers or {})
                ),
                body=self._adapt_payload_to_legacy(
                    modern_request.body if isinstance(modern_request.body, dict) else {}
                ),
            )

            self.logger.debug(
                "Modern request adapted to legacy format",
                extra={"url": str(legacy_request.url)},
            )

            return FlextResult[FlextApiModels.HttpRequest].ok(legacy_request)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpRequest].fail(
                f"Request adaptation failed: {e}"
            )

    def adapt_legacy_response_to_modern(
        self, legacy_response: FlextApiModels.HttpResponse
    ) -> FlextResult[FlextApiModels.HttpResponse]:
        """Adapt legacy response to modern API format.

        Args:
            legacy_response: Legacy API response

        Returns:
            FlextResult containing modern response or error

        """
        try:
            # Transform response to modern format
            modern_response = FlextApiModels.HttpResponse(
                status_code=self._adapt_legacy_status_code(legacy_response.status_code),
                headers=legacy_response.headers,
                body=self._normalize_legacy_payload(
                    legacy_response.body
                    if isinstance(legacy_response.body, dict)
                    else {}
                ),
                url=legacy_response.url,
                method=legacy_response.method,
                request=legacy_response.request,
            )

            self.logger.debug(
                "Legacy response adapted to modern format",
                extra={"status": modern_response.status_code},
            )

            return FlextApiModels.HttpResponse.ok(modern_response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Response adaptation failed: {e}"
            )

    def _adapt_headers_to_legacy(
        self, headers: FlextTypes.StringDict
    ) -> FlextTypes.StringDict:
        """Adapt headers to legacy format.

        Args:
            headers: Modern headers

        Returns:
            Legacy headers

        """
        # Example: rename authorization header
        adapted = headers.copy()

        if "Authorization" in adapted:
            # Legacy API might use different auth header
            adapted["X-API-Key"] = adapted.pop("Authorization")

        return adapted

    def _adapt_payload_to_legacy(self, payload: FlextTypes.Dict) -> FlextTypes.Dict:
        """Adapt payload to legacy format.

        Args:
            payload: Modern payload

        Returns:
            Legacy payload

        """
        # Example: transform field names
        adapted = {}

        for key, value in payload.items():
            # Legacy API might use snake_case instead of camelCase
            legacy_key = self._convert_camel_to_snake(key)
            adapted[legacy_key] = value

        return adapted

    def _normalize_legacy_payload(self, payload: FlextTypes.Dict) -> FlextTypes.Dict:
        """Normalize legacy payload to modern format.

        Args:
            payload: Legacy payload

        Returns:
            Modern payload

        """
        # Example: transform field names back
        normalized = {}

        for key, value in payload.items():
            # Convert snake_case back to camelCase
            modern_key = self._convert_snake_to_camel(key)
            normalized[modern_key] = value

        return normalized

    def _adapt_legacy_status_code(self, legacy_code: int) -> int:
        """Adapt legacy status code to modern standard.

        Args:
            legacy_code: Legacy status code

        Returns:
            Modern status code

        """
        # Example: map legacy codes to standard HTTP codes
        code_mapping = {
            1: 200,  # Legacy success -> 200 OK
            2: 400,  # Legacy validation error -> 400 Bad Request
            3: 401,  # Legacy auth error -> 401 Unauthorized
            4: 404,  # Legacy not found -> 404 Not Found
            5: 500,  # Legacy server error -> 500 Internal Server Error
        }

        return code_mapping.get(legacy_code, legacy_code)

    def _map_openapi_type_to_graphql(self, openapi_type: str) -> str:
        """Map OpenAPI type to GraphQL type.

        Args:
            openapi_type: OpenAPI type

        Returns:
            GraphQL type

        """
        type_mapping = {
            "string": "String",
            "integer": "Int",
            "number": "Float",
            "boolean": "Boolean",
            "array": "[String]",
            "object": "JSON",
        }

        return type_mapping.get(openapi_type, "String")

    def _convert_camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case.

        Args:
            name: camelCase name

        Returns:
            snake_case name

        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def _convert_snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase.

        Args:
            name: snake_case name

        Returns:
            camelCase name

        """
        components = name.split("_")
        return components[0] + "".join(x.title() for x in components[1:])


__all__ = ["FlextApiAdapters"]
