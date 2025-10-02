"""Protocol and format adapters for flext-api.

Provides adapters for:
- Protocol adaptation (HTTP <-> WebSocket <-> GraphQL)
- Schema adaptation (OpenAPI <-> API <-> GraphQL Schema)
- Format conversion (JSON <-> MessagePack <-> CBOR)
- Legacy API adaptation
- Request/response transformation

See TRANSFORMATION_PLAN.md - Phase 8 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import Any, Protocol as TypingProtocol

from flext_api.models import FlextApiModels
from flext_api.typings import FlextApiTypes
from flext_core import FlextConstants, FlextLogger, FlextResult


class ProtocolAdapterProtocol(TypingProtocol):
    """Protocol for protocol adapters."""

    def adapt_request(
        self, request: FlextApiTypes.RequestData
    ) -> FlextResult[FlextApiTypes.RequestData]:
        """Adapt request from one protocol to another.

        Args:
            request: Source protocol request

        Returns:
            FlextResult containing adapted request or error

        """
        ...

    def adapt_response(
        self, response: FlextApiTypes.ResponseData
    ) -> FlextResult[FlextApiTypes.ResponseData]:
        """Adapt response from one protocol to another.

        Args:
            response: Source protocol response

        Returns:
            FlextResult containing adapted response or error

        """
        ...


class HttpToWebSocketAdapter:
    """Adapter for HTTP to WebSocket protocol conversion.

    Features:
    - Convert HTTP requests to WebSocket messages
    - Convert WebSocket messages to HTTP responses
    - Query parameter handling
    - Header preservation
    - Event stream simulation
    """

    def __init__(self) -> None:
        """Initialize HTTP to WebSocket adapter."""
        self._logger = FlextLogger(__name__)

    def adapt_request(
        self, request: FlextApiModels.HttpRequest
    ) -> FlextResult[dict[str, Any]]:
        """Adapt HTTP request to WebSocket message.

        Args:
            request: HTTP request

        Returns:
            FlextResult containing WebSocket message or error

        """
        try:
            # Convert HTTP request to WebSocket message format
            message = {
                "type": "request",
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers) if request.headers else {},
                "body": request.body or {},
            }

            self._logger.debug(
                "HTTP request adapted to WebSocket message",
                extra={"method": request.method, "url": str(request.url)},
            )

            return FlextResult[dict[str, Any]].ok(message)

        except Exception as e:
            return FlextResult[dict[str, Any]].fail(
                f"HTTP to WebSocket adaptation failed: {e}"
            )

    def adapt_response(
        self, message: dict[str, Any]
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

            response = FlextApiModels.HttpResponse(
                status_code=status_code,
                headers=headers,
                body=body,
                url=url,
                method=method,
            )

            self._logger.debug(
                "WebSocket message adapted to HTTP response",
                extra={"status": status_code},
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"WebSocket to HTTP adaptation failed: {e}"
            )


class GraphQLToHttpAdapter:
    """Adapter for GraphQL to HTTP protocol conversion.

    Features:
    - Convert GraphQL queries to HTTP requests
    - Convert HTTP responses to GraphQL results
    - Variable handling
    - Fragment support
    - Error formatting
    """

    def __init__(self, endpoint: str = "/graphql") -> None:
        """Initialize GraphQL to HTTP adapter.

        Args:
            endpoint: GraphQL endpoint path

        """
        self._logger = FlextLogger(__name__)
        self._endpoint = endpoint

    def adapt_query_to_request(
        self, query: str, variables: dict[str, Any] | None = None
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

            self._logger.debug("GraphQL query adapted to HTTP request")

            return FlextResult[FlextApiModels.HttpRequest].ok(request)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpRequest].fail(
                f"GraphQL to HTTP adaptation failed: {e}"
            )

    def adapt_response_to_result(
        self, response: FlextApiModels.HttpResponse
    ) -> FlextResult[dict[str, Any]]:
        """Adapt HTTP response to GraphQL result.

        Args:
            response: HTTP response

        Returns:
            FlextResult containing GraphQL result or error

        """
        try:
            # Extract GraphQL result from HTTP response
            if response.status_code != FlextConstants.Http.HTTP_OK:
                return FlextResult[dict[str, Any]].fail(
                    f"GraphQL request failed with status {response.status_code}"
                )

            result = response.body if hasattr(response, "body") else {}

            # Check for GraphQL errors
            if isinstance(result, dict) and "errors" in result:
                errors = result["errors"]
                error_messages = [e.get("message", "Unknown error") for e in errors]
                return FlextResult[dict[str, Any]].fail(
                    f"GraphQL errors: {', '.join(error_messages)}"
                )

            self._logger.debug("HTTP response adapted to GraphQL result")

            data = result.get("data", {}) if isinstance(result, dict) else {}
            return FlextResult[dict[str, Any]].ok(data)

        except Exception as e:
            return FlextResult[dict[str, Any]].fail(
                f"HTTP to GraphQL result adaptation failed: {e}"
            )


class SchemaAdapter:
    """Adapter for schema format conversion.

    Features:
    - OpenAPI <-> API conversion
    - OpenAPI <-> GraphQL Schema conversion
    - Schema validation
    - Type mapping
    - Documentation preservation
    """

    def __init__(self) -> None:
        """Initialize schema adapter."""
        self._logger = FlextLogger(__name__)

    def openapi_toapi(
        self, openapi_schema: dict[str, Any]
    ) -> FlextResult[dict[str, Any]]:
        """Convert OpenAPI schema to API schema.

        Args:
            openapi_schema: OpenAPI schema

        Returns:
            FlextResult containing API schema or error

        """
        try:
            # Basic conversion from OpenAPI to API
            api_schema: dict[str, Any] = {
                "api": "3.0.0",
                "info": openapi_schema.get("info", {}),
                "channels": {},
            }

            # Convert paths to channels
            paths = openapi_schema.get("paths", {})
            for path, operations in paths.items():
                channel_name = path.replace("/", "_").strip("_")
                api_schema["channels"][channel_name] = {
                    "address": path,
                    "messages": {},
                }

                # Convert operations to messages
                for method, operation in operations.items():
                    if method in {"get", "post", "put", "delete"}:
                        message_name = f"{method}_{channel_name}"
                        api_schema["channels"][channel_name]["messages"][
                            message_name
                        ] = {
                            "payload": operation.get("requestBody", {})
                            .get("content", {})
                            .get("application/json", {})
                            .get("schema", {})
                        }

            self._logger.debug("OpenAPI schema converted to API")

            return FlextResult[dict[str, Any]].ok(api_schema)

        except Exception as e:
            return FlextResult[dict[str, Any]].fail(
                f"OpenAPI to API conversion failed: {e}"
            )

    def openapi_to_graphql_schema(
        self, openapi_schema: dict[str, Any]
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
            schemas = components.get("schemas", {})

            for schema_name, schema_def in schemas.items():
                if schema_def.get("type") == "object":
                    properties = schema_def.get("properties", {})
                    fields: list[str] = []

                    for prop_name, prop_def in properties.items():
                        prop_type = self._map_openapi_type_to_graphql(
                            prop_def.get("type", "String")
                        )
                        fields.append(f"  {prop_name}: {prop_type}")

                    type_def = f"type {schema_name} {{\n" + "\n".join(fields) + "\n}"
                    types.append(type_def)

            # Convert paths to queries and mutations
            paths = openapi_schema.get("paths", {})
            for path, operations in paths.items():
                for method, operation in operations.items():
                    operation_id = operation.get("operationId", path.replace("/", "_"))

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

            self._logger.debug("OpenAPI schema converted to GraphQL SDL")

            return FlextResult[str].ok(graphql_sdl)

        except Exception as e:
            return FlextResult[str].fail(
                f"OpenAPI to GraphQL schema conversion failed: {e}"
            )

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


class LegacyApiAdapter:
    """Adapter for legacy API integration.

    Features:
    - Legacy endpoint wrapping
    - Request transformation
    - Response normalization
    - Error code mapping
    - Authentication adaptation
    """

    def __init__(self, base_url: str) -> None:
        """Initialize legacy API adapter.

        Args:
            base_url: Legacy API base URL

        """
        self._logger = FlextLogger(__name__)
        self._base_url = base_url

    def adapt_request(
        self, modern_request: FlextApiModels.HttpRequest
    ) -> FlextResult[FlextApiModels.HttpRequest]:
        """Adapt modern request to legacy API format.

        Args:
            modern_request: Modern API request

        Returns:
            FlextResult containing legacy request or error

        """
        try:
            # Transform request to legacy format
            legacy_request = FlextApiModels.HttpRequest(
                method=modern_request.method,
                url=f"{self._base_url}{modern_request.url}",
                headers=self._adapt_headers(dict(modern_request.headers or {})),
                body=self._adapt_payload(
                    modern_request.body if isinstance(modern_request.body, dict) else {}
                ),
            )

            self._logger.debug(
                "Modern request adapted to legacy format",
                extra={"url": str(legacy_request.url)},
            )

            return FlextResult[FlextApiModels.HttpRequest].ok(legacy_request)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpRequest].fail(
                f"Request adaptation failed: {e}"
            )

    def adapt_response(
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
                status_code=self._adapt_status_code(legacy_response.status_code),
                headers=legacy_response.headers,
                body=self._normalize_payload(
                    legacy_response.body
                    if isinstance(legacy_response.body, dict)
                    else {}
                ),
                url=legacy_response.url,
                method=legacy_response.method,
            )

            self._logger.debug(
                "Legacy response adapted to modern format",
                extra={"status": modern_response.status_code},
            )

            return FlextResult[FlextApiModels.HttpResponse].ok(modern_response)

        except Exception as e:
            return FlextResult[FlextApiModels.HttpResponse].fail(
                f"Response adaptation failed: {e}"
            )

    def _adapt_headers(self, headers: dict[str, str]) -> dict[str, str]:
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

    def _adapt_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
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
            legacy_key = self._camel_to_snake(key)
            adapted[legacy_key] = value

        return adapted

    def _normalize_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
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
            modern_key = self._snake_to_camel(key)
            normalized[modern_key] = value

        return normalized

    def _adapt_status_code(self, legacy_code: int) -> int:
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

    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case.

        Args:
            name: camelCase name

        Returns:
            snake_case name

        """
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase.

        Args:
            name: snake_case name

        Returns:
            camelCase name

        """
        components = name.split("_")
        return components[0] + "".join(x.title() for x in components[1:])


__all__ = [
    "GraphQLToHttpAdapter",
    "HttpToWebSocketAdapter",
    "LegacyApiAdapter",
    "ProtocolAdapterProtocol",
    "SchemaAdapter",
]
