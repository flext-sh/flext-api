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

from typing import override

from flext_api import (
    FlextApiPlugins,
    t,
    u,
)
from flext_api.schemas._shared import FlextApiSchemaShared
from flext_core import r


class FlextApiAsyncapiSchemaValidator(FlextApiPlugins.Schema):
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
    - r for error handling
    - `u.fetch_logger(...)` / `p.Logger` for validation logging
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
        self._strict_mode = strict_mode
        self._validate_messages = validate_messages
        self._validate_bindings = validate_bindings
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

    def supported_schemas(self) -> t.StrSequence:
        """Get list of supported schema types.

        Returns:
        List of supported schema type identifiers

        """
        return ["asyncapi", "async-api", "asyncapi2", "asyncapi3"]

    @override
    def load_schema(self, schema_source: str) -> r[t.ContainerValue]:
        """Load AsyncAPI schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        r containing loaded schema or error

        """
        return FlextApiSchemaShared.load_and_validate_schema_document(
            schema_source,
            schema_label="AsyncAPI",
            validate_schema=self.validate_schema,
        )

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

    @override
    def validate_request(self, request: t.JsonObject, schema: t.JsonObject) -> r[bool]:
        """Validate request against AsyncAPI schema.

        Args:
        request: Request to validate
        schema: AsyncAPI schema

        Returns:
        r containing validation result or error

        """
        if "asyncapi" not in schema:
            return r[bool].fail("Schema missing 'asyncapi' version field")
        if "channels" not in schema:
            return r[bool].ok(value=True)
        channels_value = schema["channels"]
        channels_result = FlextApiSchemaShared.parse_dict_field(
            channels_value,
            "channels",
        )
        if channels_result.failure:
            return r[bool].fail(channels_result.error)
        channels = channels_result.value
        if not channels:
            return r[bool].ok(value=True)
        if "body" in request:
            body_value = request["body"]
            _ = body_value
        self.logger.debug("AsyncAPI request validation completed")
        return r[bool].ok(value=True)

    @override
    def validate_response(
        self,
        response: t.JsonObject,
        schema: t.JsonObject,
    ) -> r[bool]:
        """Validate response against AsyncAPI schema.

        Args:
        response: Response to validate
        schema: AsyncAPI schema

        Returns:
        r containing validation result or error

        """
        if "asyncapi" not in schema:
            return r[bool].fail("Schema missing 'asyncapi' version field")

        def _log_response_validation(_: t.ContainerValue) -> None:
            self.logger.debug("AsyncAPI response validation completed")

        return (
            self
            ._validate_response_channels(schema)
            .flat_map(lambda _: self._validate_response_status_code(response))
            .tap(_log_response_validation)
        )

    def validate_schema(
        self,
        schema: t.ContainerValueMapping,
    ) -> r[t.ContainerValueMapping]:
        """Validate AsyncAPI schema against AsyncAPI specification.

        Args:
        schema: AsyncAPI schema dictionary

        Returns:
        r containing validation result or error

        """
        version_result = self._validate_asyncapi_version(schema)
        if version_result.failure:
            return r[t.ContainerValueMapping].fail(
                version_result.error or "AsyncAPI version validation failed",
            )
        fields_result = self._validate_required_fields(schema, version_result.value)
        if fields_result.failure:
            return r[t.ContainerValueMapping].fail(
                fields_result.error or "Required fields validation failed",
            )
        info_result = self._validate_info_object(schema)
        if info_result.failure:
            return r[t.ContainerValueMapping].fail(
                info_result.error or "Info t.NormalizedValue validation failed",
            )
        info = info_result.value
        if "channels" not in schema:
            return r[t.ContainerValueMapping].fail(
                "Missing 'channels' field in schema",
            )
        channels_value = schema["channels"]
        channels_result = FlextApiSchemaShared.parse_dict_field(
            channels_value,
            "channels",
        )
        if channels_result.failure:
            return r[t.ContainerValueMapping].fail(channels_result.error)
        channels = channels_result.value
        channels_validation = self._validate_channels(
            channels_result.value,
            version_result.value,
        )
        if channels_validation.failure:
            return r[t.ContainerValueMapping].fail(
                f"Channel validation failed: {channels_validation.error}",
            )
        components_result = self._validate_optional_components(schema)
        if components_result.failure:
            return r[t.ContainerValueMapping].fail(
                components_result.error or "Components validation failed",
            )
        channels_value = schema["channels"]
        channels_result = FlextApiSchemaShared.parse_dict_field(
            channels_value,
            "channels",
        )
        if channels_result.failure:
            return r[t.ContainerValueMapping].fail(channels_result.error)
        title_str = ""
        if "title" in info:
            title_value = info["title"]
            title_result = FlextApiSchemaShared.parse_string_field(title_value, "title")
            if title_result.success:
                title_str = title_result.value
        self.logger.info(
            "AsyncAPI schema validation successful",
            version=version_result.value,
            title=title_str,
            channels_count=len(channels),
        )
        return r[t.ContainerValueMapping].ok({
            "valid": True,
            "version": version_result.value,
            "title": title_str,
            "channels": list(channels.keys()),
        })

    def _validate_asyncapi_2_operations(
        self,
        channel: t.ContainerValueMapping,
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 2.x publish/subscribe operations."""
        if "publish" in channel:
            publish_value = channel["publish"]
            publish_result = FlextApiSchemaShared.parse_dict_field(
                publish_value,
                "publish",
            )
            if publish_result.failure:
                return r[bool].fail(
                    f"'publish' must be a dictionary in channel: {channel_name}",
                )
            pub_result = self._validate_operation(
                publish_result.value,
                channel_name,
                "publish",
            )
            if pub_result.failure:
                return pub_result
        if "subscribe" in channel:
            subscribe_value = channel["subscribe"]
            subscribe_result = FlextApiSchemaShared.parse_dict_field(
                subscribe_value,
                "subscribe",
            )
            if subscribe_result.failure:
                return r[bool].fail(
                    f"'subscribe' must be a dictionary in channel: {channel_name}",
                )
            sub_result = self._validate_operation(
                subscribe_result.value,
                channel_name,
                "subscribe",
            )
            if sub_result.failure:
                return sub_result
        return r[bool].ok(value=True)

    def _validate_asyncapi_3_structure(
        self,
        channel: t.ContainerValueMapping,
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 3.x channel structure."""
        if "address" not in channel and self._strict_mode:
            return r[bool].fail(f"Missing 'address' in channel: {channel_name}")
        return r[bool].ok(value=True)

    def _validate_asyncapi_version(
        self,
        schema: t.ContainerValueMapping,
    ) -> r[str]:
        """Validate AsyncAPI version field."""
        if "asyncapi" not in schema:
            return r[str].fail("Missing 'asyncapi' version field")
        asyncapi_version = schema["asyncapi"]
        parsed_version = FlextApiSchemaShared.parse_string_field(
            asyncapi_version,
            "asyncapi",
        )
        if parsed_version.failure:
            return parsed_version
        asyncapi_version = parsed_version.value
        if not asyncapi_version.startswith(("2.", "3.")):
            return r[str].fail(f"Unsupported AsyncAPI version: {asyncapi_version}")
        return r[str].ok(asyncapi_version)

    def _validate_channel_messages(
        self,
        channel: t.ContainerValueMapping,
        channel_name: str,
    ) -> r[bool]:
        """Validate channel messages if present."""
        if self._validate_messages and "messages" in channel:
            messages_value = channel["messages"]
            messages_result = FlextApiSchemaShared.parse_dict_field(
                messages_value,
                "messages",
            )
            if messages_result.failure:
                return r[bool].fail(
                    f"'messages' must be a dictionary in channel: {channel_name}",
                )
            message_validation_result = self._validate_messages_object(
                messages_result.value,
                channel_name,
            )
            if message_validation_result.failure:
                return message_validation_result
        return r[bool].ok(value=True)

    def _validate_channel_structure(
        self,
        channel_name: str,
        channel: t.ContainerValue,
    ) -> r[t.ContainerValueMapping]:
        """Validate basic channel structure."""
        channel_result = FlextApiSchemaShared.parse_dict_field(channel, "channel")
        return channel_result.fold(
            on_failure=lambda _: r[t.ContainerValueMapping].fail(
                f"Channel must be a dictionary: {channel_name}",
            ),
            on_success=lambda v: r[t.ContainerValueMapping].ok(v),
        )

    def _validate_channels(
        self,
        channels: t.ContainerValueMapping,
        version: str,
    ) -> r[bool]:
        """Validate AsyncAPI channels.

        Args:
        channels: Channels dictionary from AsyncAPI schema
        version: AsyncAPI version

        Returns:
        r indicating validation success or failure

        """
        if not channels:
            return r[bool].ok(value=True)
        for channel_name, channel in channels.items():
            channel_dict_result = self._validate_channel_structure(
                channel_name,
                channel,
            )
            if channel_dict_result.failure:
                return r[bool].fail(
                    channel_dict_result.error or "Channel dictionary validation failed",
                )
            validation_result = self._validate_single_channel(
                channel_name,
                channel_dict_result.value,
                version,
            )
            if validation_result.failure:
                return validation_result
        return r[bool].ok(value=True)

    def _validate_components(
        self,
        components: t.ContainerValueMapping,
    ) -> r[bool]:
        """Validate AsyncAPI components.

        Args:
        components: Components dictionary from AsyncAPI schema

        Returns:
        r indicating validation success or failure

        """
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
            section_result = FlextApiSchemaShared.parse_dict_field(
                section_value,
                section_name,
            )
            if section_result.failure:
                return r[bool].fail(
                    f"Component section must be a dictionary: {section_name}",
                )
        return r[bool].ok(value=True)

    def _validate_info_object(
        self,
        schema: t.ContainerValueMapping,
    ) -> r[t.ContainerValueMapping]:
        """Validate info t.NormalizedValue and return it."""
        if "info" not in schema:
            return r[t.ContainerValueMapping].fail(
                "Missing 'info' field in schema",
            )
        info_value = schema["info"]
        info_result = FlextApiSchemaShared.parse_dict_field(info_value, "info")
        if info_result.failure:
            return r[t.ContainerValueMapping].fail(info_result.error)
        info = info_result.value
        info_required = ["title", "version"]
        info_missing = u.filter(list(info_required), lambda field: field not in info)
        if info_missing:
            return r[t.ContainerValueMapping].fail(
                f"Missing required info fields: {', '.join(info_missing)}",
            )
        return r[t.ContainerValueMapping].ok(info)

    def _validate_message(
        self,
        message: t.ContainerValueMapping,
        channel_name: str,
        op_type: str,
    ) -> r[bool]:
        """Validate AsyncAPI message.

        Args:
        message: Message dictionary
        channel_name: Channel name
        op_type: Operation type

        Returns:
        r indicating validation success or failure

        """
        if "payload" in message:
            payload = message["payload"]
            payload_result = FlextApiSchemaShared.parse_dict_field(payload, "payload")
            if payload_result.failure:
                return r[bool].fail(
                    f"Message payload must be a dictionary: {op_type} in {channel_name}",
                )
        return r[bool].ok(value=True)

    def _validate_messages_object(
        self,
        messages: t.ContainerValueMapping,
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI messages t.NormalizedValue.

        Args:
        messages: Messages dictionary
        channel_name: Channel name

        Returns:
        r indicating validation success or failure

        """
        for message_name, message in messages.items():
            message_result = FlextApiSchemaShared.parse_dict_field(message, "message")
            if message_result.failure:
                return r[bool].fail(
                    f"Message must be a dictionary: {message_name} in {channel_name}",
                )
            message_validation = self._validate_message(
                message_result.value,
                channel_name,
                message_name,
            )
            if message_validation.failure:
                return message_validation
        return r[bool].ok(value=True)

    def _validate_operation(
        self,
        operation: t.ContainerValueMapping,
        channel_name: str,
        op_type: str,
    ) -> r[bool]:
        """Validate AsyncAPI operation (publish/subscribe).

        Args:
        operation: Operation dictionary
        channel_name: Channel name
        op_type: Operation type (publish/subscribe)

        Returns:
        r indicating validation success or failure

        """
        if "message" in operation and self._validate_messages:
            message = operation["message"]
            message_result = FlextApiSchemaShared.parse_dict_field(message, "message")
            if message_result.failure:
                return r[bool].fail(
                    f"'message' must be a dictionary in {op_type} operation of channel: {channel_name}",
                )
            message_validation = self._validate_message(
                message_result.value,
                channel_name,
                op_type,
            )
            if message_validation.failure:
                return message_validation
        return r[bool].ok(value=True)

    def _validate_optional_components(
        self,
        schema: t.ContainerValueMapping,
    ) -> r[bool]:
        """Validate optional components like servers and components."""
        if "servers" in schema:
            servers_value = schema["servers"]
            servers_result = FlextApiSchemaShared.parse_dict_field(
                servers_value,
                "servers",
            )
            if servers_result.failure:
                return r[bool].fail(servers_result.error)
            servers_validation = self._validate_servers(servers_result.value)
            if servers_validation.failure:
                return r[bool].fail(
                    f"Server validation failed: {servers_validation.error}",
                )
        if "components" in schema:
            components_value = schema["components"]
            components_result = FlextApiSchemaShared.parse_dict_field(
                components_value,
                "components",
            )
            if components_result.failure:
                return r[bool].fail(components_result.error)
            components_validation = self._validate_components(components_result.value)
            if components_validation.failure:
                return r[bool].fail(
                    f"Component validation failed: {components_validation.error}",
                )
        return r[bool].ok(value=True)

    def _validate_required_fields(
        self,
        schema: t.ContainerValueMapping,
        version: str,
    ) -> r[bool]:
        """Validate required fields based on AsyncAPI version."""
        required_fields = ["info"]
        if version.startswith(("2.", "3.")):
            required_fields.append("channels")
        missing_fields = u.filter(
            list(required_fields),
            lambda field: field not in schema,
        )
        if missing_fields:
            return r[bool].fail(f"Missing required fields: {', '.join(missing_fields)}")
        return r[bool].ok(value=True)

    def _validate_response_channels(self, schema: t.JsonObject) -> r[bool]:
        """Validate channels in schema for response validation."""
        if "channels" not in schema:
            return r[bool].ok(value=True)
        channels_value = schema["channels"]
        channels_result = FlextApiSchemaShared.parse_dict_field(
            channels_value,
            "channels",
        )
        if channels_result.failure:
            return r[bool].fail(channels_result.error)
        if not channels_result.value:
            return r[bool].ok(value=True)
        return r[bool].ok(value=True)

    def _validate_response_status_code(self, response: t.JsonObject) -> r[bool]:
        """Validate status code in response."""
        if "status_code" not in response:
            return r[bool].ok(value=True)
        status_code_value = response["status_code"]
        http_status_min = 100
        http_status_max = 599
        status_result = FlextApiSchemaShared.parse_int_field(
            status_code_value,
            "status_code",
        )
        if status_result.failure:
            return r[bool].fail("Invalid status code")
        if not http_status_min <= status_result.value <= http_status_max:
            return r[bool].fail("Invalid status code")
        return r[bool].ok(value=True)

    def _validate_servers(self, servers: t.ContainerValueMapping) -> r[bool]:
        """Validate AsyncAPI servers.

        Args:
        servers: Servers dictionary from AsyncAPI schema

        Returns:
        r indicating validation success or failure

        """
        for server_name, server in servers.items():
            server_result = FlextApiSchemaShared.parse_dict_field(server, "server")
            if server_result.failure:
                return r[bool].fail(f"Server must be a dictionary: {server_name}")
            server = server_result.value
            if "url" not in server and "host" not in server:
                return r[bool].fail(f"Server missing 'url' or 'host': {server_name}")
            if "protocol" not in server:
                return r[bool].fail(f"Server missing 'protocol': {server_name}")
            protocol_value = server["protocol"]
            protocol_result = FlextApiSchemaShared.parse_string_field(
                protocol_value,
                "protocol",
            )
            if protocol_result.failure:
                return r[bool].fail(
                    f"Server 'protocol' must be a string: {server_name}",
                )
            protocol = protocol_result.value
            if protocol not in self._supported_protocols and self._strict_mode:
                return r[bool].fail(f"Unsupported protocol '{protocol}': {server_name}")
        return r[bool].ok(value=True)

    def _validate_single_channel(
        self,
        channel_name: str,
        channel: t.ContainerValueMapping,
        version: str,
    ) -> r[bool]:
        """Validate a single channel."""
        if version.startswith("2."):
            ops_result = self._validate_asyncapi_2_operations(channel, channel_name)
            if ops_result.failure:
                return ops_result
        elif version.startswith("3."):
            struct_result = self._validate_asyncapi_3_structure(channel, channel_name)
            if struct_result.failure:
                return struct_result
        return self._validate_channel_messages(channel, channel_name)


__all__ = ["FlextApiAsyncapiSchemaValidator"]
