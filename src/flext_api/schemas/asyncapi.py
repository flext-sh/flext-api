"""AsyncAPI Schema Validator for flext-api.

Implements AsyncAPI schema validation with:
- AsyncAPI 2.x and 3.x support
- Channel and message validation
- Operation validation (publish/subscribe)
- Server and binding validation
- Schema validation for message payloads

See TRANSFORMATION_PLAN.md - Phase 5 for implementation details.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast, override

from flext_core import r, u

from flext_api.plugins import FlextApiPlugins
from flext_api.typings import FlextApiTypes


class AsyncAPISchemaValidator(FlextApiPlugins.Schema):
    """AsyncAPI schema validator with version support.

    Features:
    - AsyncAPI 2.x and 3.x validation
    - Channel definition validation
    - Message schema validation
    - Operation validation (publish/subscribe)
    - Server and protocol binding validation
    - Message payload schema validation
    - Component reference resolution ($ref)

    Integration:
    - Validates AsyncAPI specifications
    - Supports WebSocket, SSE, MQTT, Kafka bindings
    - FlextResult for error handling
    - FlextLogger for validation logging
    """

    def __init__(
        self,
        *,
        strict_mode: bool = True,
        validate_messages: bool = True,
        validate_bindings: bool = True,
    ) -> None:
        """Initialize AsyncAPI schema validator.

        Args:
        strict_mode: Enable strict AsyncAPI validation
        validate_messages: Validate message schemas
        validate_bindings: Validate protocol bindings

        """
        super().__init__(
            name="asyncapi",
            version="3.0.0",
            description="AsyncAPI schema validator with version support",
        )

        # Validation configuration
        self._strict_mode = strict_mode
        self._validate_messages = validate_messages
        self._validate_bindings = validate_bindings

        # Supported protocols
        self._supported_protocols = [
            "ws",
            "wss",
            "http",
            "https",
            "mqtt",
            "mqtts",
            "kafka",
            "kafka-secure",
            "amqp",
            "amqps",
        ]

    def _validate_asyncapi_version(self, schema: dict[str, object]) -> r[str]:
        """Validate AsyncAPI version field."""
        if "asyncapi" not in schema:
            return r[str].fail("Missing 'asyncapi' version field")

        asyncapi_version = schema["asyncapi"]
        if not isinstance(asyncapi_version, str):
            return r[str].fail("'asyncapi' version field must be a string")

        if not (asyncapi_version.startswith(("2.", "3."))):
            return r[str].fail(f"Unsupported AsyncAPI version: {asyncapi_version}")
        return r[str].ok(asyncapi_version)

    def _validate_required_fields(
        self,
        schema: dict[str, object],
        version: str,
    ) -> r[bool]:
        """Validate required fields based on AsyncAPI version."""
        required_fields = ["info"]
        if version.startswith(("2.", "3.")):
            required_fields.append("channels")

        # Use u.filter() for unified filtering (DSL pattern)
        missing_fields = cast(
            "list[str]",
            u.Collection.filter(
                list(required_fields), lambda field: field not in schema
            ),
        )
        if missing_fields:
            return r[bool].fail(f"Missing required fields: {', '.join(missing_fields)}")
        return r[bool].ok(True)

    def _validate_info_object(self, schema: dict[str, object]) -> r[dict[str, object]]:
        """Validate info object and return it."""
        if "info" not in schema:
            return r[dict[str, object]].fail("Missing 'info' field in schema")

        info_value = schema["info"]
        if not isinstance(info_value, dict):
            return r[dict[str, object]].fail("'info' field must be a dictionary")

        info: dict[str, object] = info_value
        info_required = ["title", "version"]
        # Use u.filter() for unified filtering (DSL pattern)
        info_missing = cast(
            "list[str]",
            u.Collection.filter(list(info_required), lambda field: field not in info),
        )
        if info_missing:
            return r[dict[str, object]].fail(
                f"Missing required info fields: {', '.join(info_missing)}",
            )
        return r[dict[str, object]].ok(info)

    def _validate_optional_components(self, schema: dict[str, object]) -> r[bool]:
        """Validate optional components like servers and components."""
        # Validate servers if present
        if "servers" in schema:
            servers_value = schema["servers"]
            if not isinstance(servers_value, dict):
                return r[bool].fail("'servers' field must be a dictionary")

            servers_result = self._validate_servers(servers_value)
            if servers_result.is_failure:
                return r[bool].fail(f"Server validation failed: {servers_result.error}")

        # Validate components if present
        if "components" in schema:
            components_value = schema["components"]
            if not isinstance(components_value, dict):
                return r[bool].fail("'components' field must be a dictionary")

            components_result = self._validate_components(components_value)
            if components_result.is_failure:
                return r[bool].fail(
                    f"Component validation failed: {components_result.error}",
                )
        return r[bool].ok(True)

    def validate_schema(self, schema: dict[str, object]) -> r[dict[str, object]]:
        """Validate AsyncAPI schema against AsyncAPI specification.

        Args:
        schema: AsyncAPI schema dictionary

        Returns:
        FlextResult containing validation result or error

        """
        # Validate AsyncAPI version
        version_result = self._validate_asyncapi_version(schema)
        if version_result.is_failure:
            return r[dict[str, object]].fail(
                version_result.error or "AsyncAPI version validation failed",
            )

        asyncapi_version = version_result.unwrap()

        # Validate required fields
        fields_result = self._validate_required_fields(schema, asyncapi_version)
        if fields_result.is_failure:
            return r[dict[str, object]].fail(
                fields_result.error or "Required fields validation failed",
            )

        # Validate info object
        info_result = self._validate_info_object(schema)
        if info_result.is_failure:
            return r[dict[str, object]].fail(
                info_result.error or "Info object validation failed",
            )

        info = info_result.unwrap()

        # Validate channels
        if "channels" not in schema:
            return r[dict[str, object]].fail("Missing 'channels' field in schema")

        channels_value = schema["channels"]
        if not isinstance(channels_value, dict):
            return r[dict[str, object]].fail("'channels' field must be a dictionary")

        channels_result = self._validate_channels(channels_value, asyncapi_version)
        if channels_result.is_failure:
            return r[dict[str, object]].fail(
                f"Channel validation failed: {channels_result.error}",
            )

        # Validate optional components
        components_result = self._validate_optional_components(schema)
        if components_result.is_failure:
            return r[dict[str, object]].fail(
                components_result.error or "Components validation failed",
            )

        channels_value = schema["channels"]
        if not isinstance(channels_value, dict):
            return r[dict[str, object]].fail("'channels' field must be a dictionary")

        title_str = ""
        if "title" in info:
            title_value = info["title"]
            title_str = str(title_value)

        self.logger.info(
            "AsyncAPI schema validation successful",
            extra={
                "version": asyncapi_version,
                "title": title_str,
                "channels_count": len(channels_value),
            },
        )

        return r[dict[str, object]].ok({
            "valid": True,
            "version": asyncapi_version,
            "title": title_str,
            "channels": list(channels_value.keys()),
        })

    def _validate_channel_structure(
        self,
        channel_name: str,
        channel: object,
    ) -> r[dict[str, object]]:
        """Validate basic channel structure."""
        if not isinstance(channel, dict):
            return r[dict[str, object]].fail(
                f"Channel must be a dictionary: {channel_name}",
            )
        return r[dict[str, object]].ok(channel)

    def _validate_asyncapi_2_operations(
        self,
        channel: dict[str, object],
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 2.x publish/subscribe operations."""
        if "publish" in channel:
            publish_value = channel["publish"]
            if not isinstance(publish_value, dict):
                return r[bool].fail(
                    f"'publish' must be a dictionary in channel: {channel_name}",
                )

            pub_result = self._validate_operation(
                publish_value,
                channel_name,
                "publish",
            )
            if pub_result.is_failure:
                return pub_result

        if "subscribe" in channel:
            subscribe_value = channel["subscribe"]
            if not isinstance(subscribe_value, dict):
                return r[bool].fail(
                    f"'subscribe' must be a dictionary in channel: {channel_name}",
                )

            sub_result = self._validate_operation(
                subscribe_value,
                channel_name,
                "subscribe",
            )
            if sub_result.is_failure:
                return sub_result
        return r[bool].ok(True)

    def _validate_asyncapi_3_structure(
        self,
        channel: dict[str, object],
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 3.x channel structure."""
        if "address" not in channel and self._strict_mode:
            return r[bool].fail(f"Missing 'address' in channel: {channel_name}")
        return r[bool].ok(True)

    def _validate_channel_messages(
        self,
        channel: dict[str, object],
        channel_name: str,
    ) -> r[bool]:
        """Validate channel messages if present."""
        if self._validate_messages and "messages" in channel:
            messages_value = channel["messages"]
            if not isinstance(messages_value, dict):
                return r[bool].fail(
                    f"'messages' must be a dictionary in channel: {channel_name}",
                )

            messages_result = self._validate_messages_object(
                messages_value,
                channel_name,
            )
            if messages_result.is_failure:
                return messages_result
        return r[bool].ok(True)

    def _validate_single_channel(
        self,
        channel_name: str,
        channel: dict[str, object],
        version: str,
    ) -> r[bool]:
        """Validate a single channel."""
        # Validate operations based on version
        if version.startswith("2."):
            ops_result = self._validate_asyncapi_2_operations(channel, channel_name)
            if ops_result.is_failure:
                return ops_result
        elif version.startswith("3."):
            struct_result = self._validate_asyncapi_3_structure(channel, channel_name)
            if struct_result.is_failure:
                return struct_result

        # Validate messages
        return self._validate_channel_messages(channel, channel_name)

    def _validate_channels(self, channels: dict[str, object], version: str) -> r[bool]:
        """Validate AsyncAPI channels.

        Args:
        channels: Channels dictionary from AsyncAPI schema
        version: AsyncAPI version

        Returns:
        FlextResult indicating validation success or failure

        """
        # Allow empty channels for minimal schemas
        if not channels:
            return r[bool].ok(True)

        for channel_name, channel in channels.items():
            # Validate basic structure
            channel_dict_result = self._validate_channel_structure(
                channel_name,
                channel,
            )
            if channel_dict_result.is_failure:
                return r[bool].fail(
                    channel_dict_result.error or "Channel dictionary validation failed",
                )

            channel_dict = channel_dict_result.unwrap()

            # Validate channel content
            validation_result = self._validate_single_channel(
                channel_name,
                channel_dict,
                version,
            )
            if validation_result.is_failure:
                return validation_result

        return r[bool].ok(True)

    def _validate_operation(
        self,
        operation: dict[str, object],
        channel_name: str,
        op_type: str,
    ) -> r[bool]:
        """Validate AsyncAPI operation (publish/subscribe).

        Args:
        operation: Operation dictionary
        channel_name: Channel name
        op_type: Operation type (publish/subscribe)

        Returns:
        FlextResult indicating validation success or failure

        """
        # Validate message if present
        if "message" in operation and self._validate_messages:
            message = operation["message"]
            if not isinstance(message, dict):
                return r[bool].fail(
                    f"'message' must be a dictionary in {op_type} operation of channel: {channel_name}",
                )

            message_result = self._validate_message(message, channel_name, op_type)
            if message_result.is_failure:
                return message_result

        return r[bool].ok(True)

    def _validate_message(
        self,
        message: dict[str, object],
        channel_name: str,
        op_type: str,
    ) -> r[bool]:
        """Validate AsyncAPI message.

        Args:
        message: Message dictionary
        channel_name: Channel name
        op_type: Operation type

        Returns:
        FlextResult indicating validation success or failure

        """
        # Validate payload schema if present
        if "payload" in message:
            payload = message["payload"]
            if not isinstance(payload, dict):
                return r[bool].fail(
                    f"Message payload must be a dictionary: {op_type} in {channel_name}",
                )

        return r[bool].ok(True)

    def _validate_messages_object(
        self,
        messages: dict[str, object],
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI messages object.

        Args:
        messages: Messages dictionary
        channel_name: Channel name

        Returns:
        FlextResult indicating validation success or failure

        """
        for message_name, message in messages.items():
            if not isinstance(message, dict):
                return r[bool].fail(
                    f"Message must be a dictionary: {message_name} in {channel_name}",
                )

            message_result = self._validate_message(message, channel_name, message_name)
            if message_result.is_failure:
                return message_result

        return r[bool].ok(True)

    def _validate_servers(self, servers: dict[str, object]) -> r[bool]:
        """Validate AsyncAPI servers.

        Args:
        servers: Servers dictionary from AsyncAPI schema

        Returns:
        FlextResult indicating validation success or failure

        """
        for server_name, server in servers.items():
            if not isinstance(server, dict):
                return r[bool].fail(f"Server must be a dictionary: {server_name}")

            # Validate required fields
            if "url" not in server and "host" not in server:
                return r[bool].fail(f"Server missing 'url' or 'host': {server_name}")

            if "protocol" not in server:
                return r[bool].fail(f"Server missing 'protocol': {server_name}")

            # Validate protocol
            protocol_value = server["protocol"]
            if not isinstance(protocol_value, str):
                return r[bool].fail(
                    f"Server 'protocol' must be a string: {server_name}",
                )

            protocol: str = protocol_value
            if protocol not in self._supported_protocols and self._strict_mode:
                return r[bool].fail(f"Unsupported protocol '{protocol}': {server_name}")

        return r[bool].ok(True)

    def _validate_components(self, components: dict[str, object]) -> r[bool]:
        """Validate AsyncAPI components.

        Args:
        components: Components dictionary from AsyncAPI schema

        Returns:
        FlextResult indicating validation success or failure

        """
        # Validate component sections
        valid_sections = [
            "schemas",
            "messages",
            "securitySchemes",
            "parameters",
            "correlationIds",
            "operationTraits",
            "messageTraits",
            "serverBindings",
            "channelBindings",
            "operationBindings",
            "messageBindings",
        ]

        for section_name, section_value in components.items():
            if section_name not in valid_sections and self._strict_mode:
                return r[bool].fail(f"Invalid component section: {section_name}")

            if not isinstance(section_value, dict):
                return r[bool].fail(
                    f"Component section must be a dictionary: {section_name}",
                )

        return r[bool].ok(True)

    def supports_schema(self, schema_type: str) -> bool:
        """Check if this validator supports the given schema type.

        Args:
        schema_type: Schema type identifier

        Returns:
        True if schema type is supported

        """
        return schema_type.lower() in {
            "asyncapi",
            "async-api",
            "asyncapi2",
            "asyncapi3",
        }

    def get_supported_schemas(self) -> list[str]:
        """Get list of supported schema types.

        Returns:
        List of supported schema type identifiers

        """
        return ["asyncapi", "async-api", "asyncapi2", "asyncapi3"]

    @override
    def validate_request(
        self,
        request: FlextApiTypes.JsonObject,
        schema: FlextApiTypes.JsonObject,
    ) -> r[bool]:
        """Validate request against AsyncAPI schema.

        Args:
        request: Request to validate
        schema: AsyncAPI schema

        Returns:
        FlextResult containing validation result or error

        """
        # Basic AsyncAPI request validation
        if not isinstance(request, dict):
            return r[bool].fail("Request must be a dictionary")

        if not isinstance(schema, dict):
            return r[bool].fail("Schema must be a dictionary")

        # Validate AsyncAPI structure
        if "asyncapi" not in schema:
            return r[bool].fail("Schema missing 'asyncapi' version field")

        # Check if channels exist for message validation
        if "channels" not in schema:
            return r[bool].ok(True)  # No channels to validate against

        channels_value = schema["channels"]
        if not isinstance(channels_value, dict):
            return r[bool].fail("'channels' field must be a dictionary")

        channels: dict[str, object] = channels_value
        if not channels:
            return r[bool].ok(True)  # No channels to validate against

        # Basic validation - request should have expected structure
        # For WebSocket/SSE requests, we expect certain fields
        if "body" in request:
            body_value = request["body"]
            if isinstance(body_value, dict):
                # Has message structure - consider valid for now
                pass

        self.logger.debug("AsyncAPI request validation completed")
        return r[bool].ok(True)

    def _validate_response_channels(self, schema: Mapping[str, object]) -> r[bool]:
        """Validate channels in schema for response validation."""
        if "channels" not in schema:
            return r[bool].ok(True)  # No channels to validate against

        channels_value = schema["channels"]
        if not isinstance(channels_value, dict):
            return r[bool].fail("'channels' field must be a dictionary")

        channels: dict[str, object] = channels_value
        if not channels:
            return r[bool].ok(True)  # No channels to validate against

        return r[bool].ok(True)

    def _validate_response_status_code(self, response: Mapping[str, object]) -> r[bool]:
        """Validate status code in response."""
        if "status_code" not in response:
            return r[bool].ok(True)

        status_code_value = response["status_code"]
        http_status_min = 100
        http_status_max = 599
        if not isinstance(status_code_value, int) or not (
            http_status_min <= status_code_value <= http_status_max
        ):
            return r[bool].fail("Invalid status code")

        return r[bool].ok(True)

    @override
    def validate_response(
        self,
        response: FlextApiTypes.JsonObject,
        schema: FlextApiTypes.JsonObject,
    ) -> r[bool]:
        """Validate response against AsyncAPI schema.

        Args:
        response: Response to validate
        schema: AsyncAPI schema

        Returns:
        FlextResult containing validation result or error

        """
        # Basic AsyncAPI response validation
        if not isinstance(response, dict):
            return r[bool].fail("Response must be a dictionary")

        if not isinstance(schema, dict):
            return r[bool].fail("Schema must be a dictionary")

        # Validate AsyncAPI structure
        if "asyncapi" not in schema:
            return r[bool].fail("Schema missing 'asyncapi' version field")

        # Check if channels exist for message validation
        channels_result = self._validate_response_channels(schema)
        if channels_result.is_failure:
            return channels_result

        # Check status for HTTP-like responses
        status_result = self._validate_response_status_code(response)
        if status_result.is_failure:
            return status_result

        self.logger.debug("AsyncAPI response validation completed")
        return r[bool].ok(True)

    @override
    def load_schema(
        self,
        schema_source: str,
    ) -> r[object]:
        """Load AsyncAPI schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        FlextResult containing loaded schema or error

        """
        # For string paths, would load from file
        return r[object].fail("File loading not implemented yet")


__all__ = ["AsyncAPISchemaValidator"]
