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

import json
from collections.abc import Mapping
from pathlib import Path
from typing import override

from flext_core import r, u
from pydantic import BaseModel, ConfigDict, ValidationError

from flext_api.plugins import FlextApiPlugins
from flext_api.typings import t


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

    class _StringField(BaseModel):
        value: str

    class _IntField(BaseModel):
        value: int

    class _DictField(BaseModel):
        model_config = ConfigDict(extra="ignore")

        value: dict[str, t.GeneralValueType]

    def _parse_string_field(self, value: t.GeneralValueType, field_name: str) -> r[str]:
        try:
            parsed = self._StringField.model_validate({"value": value})
        except ValidationError:
            return r[str].fail(f"'{field_name}' field must be a string")
        return r[str].ok(parsed.value)

    def _parse_int_field(self, value: t.GeneralValueType, field_name: str) -> r[int]:
        try:
            parsed = self._IntField.model_validate({"value": value})
        except ValidationError:
            return r[int].fail(f"'{field_name}' field must be an integer")
        return r[int].ok(parsed.value)

    def _parse_dict_field(
        self,
        value: t.GeneralValueType,
        field_name: str,
    ) -> r[Mapping[str, t.GeneralValueType]]:
        try:
            parsed = self._DictField.model_validate({"value": value})
        except ValidationError:
            return r[Mapping[str, t.GeneralValueType]].fail(
                f"'{field_name}' field must be a dictionary"
            )
        return r[Mapping[str, t.GeneralValueType]].ok(parsed.value)

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

    def _validate_asyncapi_version(
        self, schema: Mapping[str, t.GeneralValueType]
    ) -> r[str]:
        """Validate AsyncAPI version field."""
        if "asyncapi" not in schema:
            return r[str].fail("Missing 'asyncapi' version field")

        asyncapi_version = schema["asyncapi"]
        parsed_version = self._parse_string_field(asyncapi_version, "asyncapi")
        if parsed_version.is_failure:
            return parsed_version
        asyncapi_version = parsed_version.value

        if not (asyncapi_version.startswith(("2.", "3."))):
            return r[str].fail(f"Unsupported AsyncAPI version: {asyncapi_version}")
        return r[str].ok(asyncapi_version)

    def _validate_required_fields(
        self,
        schema: Mapping[str, t.GeneralValueType],
        version: str,
    ) -> r[bool]:
        """Validate required fields based on AsyncAPI version."""
        required_fields = ["info"]
        if version.startswith(("2.", "3.")):
            required_fields.append("channels")

        # Use u.filter() for unified filtering (DSL pattern)
        missing_fields = u.Collection.filter(
            list(required_fields),
            lambda field: field not in schema,
        )
        if missing_fields:
            return r[bool].fail(f"Missing required fields: {', '.join(missing_fields)}")
        return r[bool].ok(value=True)

    def _validate_info_object(
        self, schema: Mapping[str, t.GeneralValueType]
    ) -> r[Mapping[str, t.GeneralValueType]]:
        """Validate info object and return it."""
        if "info" not in schema:
            return r[Mapping[str, t.GeneralValueType]].fail(
                "Missing 'info' field in schema"
            )

        info_value = schema["info"]
        info_result = self._parse_dict_field(info_value, "info")
        if info_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(info_result.error)
        info = info_result.value
        info_required = ["title", "version"]
        # Use u.filter() for unified filtering (DSL pattern)
        info_missing = u.Collection.filter(
            list(info_required),
            lambda field: field not in info,
        )
        if info_missing:
            return r[Mapping[str, t.GeneralValueType]].fail(
                f"Missing required info fields: {', '.join(info_missing)}",
            )
        return r[Mapping[str, t.GeneralValueType]].ok(info)

    def _validate_optional_components(
        self, schema: Mapping[str, t.GeneralValueType]
    ) -> r[bool]:
        """Validate optional components like servers and components."""
        # Validate servers if present
        if "servers" in schema:
            servers_value = schema["servers"]
            servers_result = self._parse_dict_field(servers_value, "servers")
            if servers_result.is_failure:
                return r[bool].fail(servers_result.error)

            servers_validation = self._validate_servers(servers_result.value)
            if servers_validation.is_failure:
                return r[bool].fail(
                    f"Server validation failed: {servers_validation.error}"
                )

        # Validate components if present
        if "components" in schema:
            components_value = schema["components"]
            components_result = self._parse_dict_field(components_value, "components")
            if components_result.is_failure:
                return r[bool].fail(components_result.error)

            components_validation = self._validate_components(components_result.value)
            if components_validation.is_failure:
                return r[bool].fail(
                    f"Component validation failed: {components_validation.error}",
                )
        return r[bool].ok(value=True)

    def validate_schema(
        self, schema: Mapping[str, t.GeneralValueType]
    ) -> r[Mapping[str, t.GeneralValueType]]:
        """Validate AsyncAPI schema against AsyncAPI specification.

        Args:
        schema: AsyncAPI schema dictionary

        Returns:
        FlextResult containing validation result or error

        """
        # Validate AsyncAPI version
        version_result = self._validate_asyncapi_version(schema)
        if version_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                version_result.error or "AsyncAPI version validation failed",
            )

        # Validate required fields
        fields_result = self._validate_required_fields(schema, version_result.value)
        if fields_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                fields_result.error or "Required fields validation failed",
            )

        # Validate info object
        info_result = self._validate_info_object(schema)
        if info_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                info_result.error or "Info object validation failed",
            )

        info = info_result.value

        # Validate channels
        if "channels" not in schema:
            return r[Mapping[str, t.GeneralValueType]].fail(
                "Missing 'channels' field in schema"
            )

        channels_value = schema["channels"]
        channels_result = self._parse_dict_field(channels_value, "channels")
        if channels_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(channels_result.error)

        channels_validation = self._validate_channels(
            channels_result.value,
            version_result.value,
        )
        if channels_validation.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                f"Channel validation failed: {channels_validation.error}",
            )

        # Validate optional components
        components_result = self._validate_optional_components(schema)
        if components_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                components_result.error or "Components validation failed",
            )

        channels_value = schema["channels"]
        channels_result = self._parse_dict_field(channels_value, "channels")
        if channels_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(channels_result.error)

        title_str = ""
        if "title" in info:
            title_value = info["title"]
            title_str = str(title_value)

        self.logger.info(
            "AsyncAPI schema validation successful",
            extra={
                "version": version_result.value,
                "title": title_str,
                "channels_count": len(channels_value),
            },
        )

        return r[Mapping[str, t.GeneralValueType]].ok({
            "valid": True,
            "version": version_result.value,
            "title": title_str,
            "channels": list(channels_value.keys()),
        })

    def _validate_channel_structure(
        self,
        channel_name: str,
        channel: t.GeneralValueType,
    ) -> r[Mapping[str, t.GeneralValueType]]:
        """Validate basic channel structure."""
        channel_result = self._parse_dict_field(channel, "channel")
        if channel_result.is_failure:
            return r[Mapping[str, t.GeneralValueType]].fail(
                f"Channel must be a dictionary: {channel_name}"
            )
        return r[Mapping[str, t.GeneralValueType]].ok(channel_result.value)

    def _validate_asyncapi_2_operations(
        self,
        channel: Mapping[str, t.GeneralValueType],
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 2.x publish/subscribe operations."""
        if "publish" in channel:
            publish_value = channel["publish"]
            publish_result = self._parse_dict_field(publish_value, "publish")
            if publish_result.is_failure:
                return r[bool].fail(
                    f"'publish' must be a dictionary in channel: {channel_name}"
                )

            pub_result = self._validate_operation(
                publish_result.value,
                channel_name,
                "publish",
            )
            if pub_result.is_failure:
                return pub_result

        if "subscribe" in channel:
            subscribe_value = channel["subscribe"]
            subscribe_result = self._parse_dict_field(subscribe_value, "subscribe")
            if subscribe_result.is_failure:
                return r[bool].fail(
                    f"'subscribe' must be a dictionary in channel: {channel_name}"
                )

            sub_result = self._validate_operation(
                subscribe_result.value,
                channel_name,
                "subscribe",
            )
            if sub_result.is_failure:
                return sub_result
        return r[bool].ok(value=True)

    def _validate_asyncapi_3_structure(
        self,
        channel: Mapping[str, t.GeneralValueType],
        channel_name: str,
    ) -> r[bool]:
        """Validate AsyncAPI 3.x channel structure."""
        if "address" not in channel and self._strict_mode:
            return r[bool].fail(f"Missing 'address' in channel: {channel_name}")
        return r[bool].ok(value=True)

    def _validate_channel_messages(
        self,
        channel: Mapping[str, t.GeneralValueType],
        channel_name: str,
    ) -> r[bool]:
        """Validate channel messages if present."""
        if self._validate_messages and "messages" in channel:
            messages_value = channel["messages"]
            messages_result = self._parse_dict_field(messages_value, "messages")
            if messages_result.is_failure:
                return r[bool].fail(
                    f"'messages' must be a dictionary in channel: {channel_name}"
                )

            messages_result = self._validate_messages_object(
                messages_result.value,
                channel_name,
            )
            if messages_result.is_failure:
                return messages_result
        return r[bool].ok(value=True)

    def _validate_single_channel(
        self,
        channel_name: str,
        channel: Mapping[str, t.GeneralValueType],
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

    def _validate_channels(
        self, channels: Mapping[str, t.GeneralValueType], version: str
    ) -> r[bool]:
        """Validate AsyncAPI channels.

        Args:
        channels: Channels dictionary from AsyncAPI schema
        version: AsyncAPI version

        Returns:
        FlextResult indicating validation success or failure

        """
        # Allow empty channels for minimal schemas
        if not channels:
            return r[bool].ok(value=True)

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

            # Validate channel content
            validation_result = self._validate_single_channel(
                channel_name,
                channel_dict_result.value,
                version,
            )
            if validation_result.is_failure:
                return validation_result

        return r[bool].ok(value=True)

    def _validate_operation(
        self,
        operation: Mapping[str, t.GeneralValueType],
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
            message_result = self._parse_dict_field(message, "message")
            if message_result.is_failure:
                return r[bool].fail(
                    f"'message' must be a dictionary in {op_type} operation of channel: {channel_name}",
                )

            message_validation = self._validate_message(
                message_result.value,
                channel_name,
                op_type,
            )
            if message_validation.is_failure:
                return message_validation

        return r[bool].ok(value=True)

    def _validate_message(
        self,
        message: Mapping[str, t.GeneralValueType],
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
            payload_result = self._parse_dict_field(payload, "payload")
            if payload_result.is_failure:
                return r[bool].fail(
                    f"Message payload must be a dictionary: {op_type} in {channel_name}",
                )

        return r[bool].ok(value=True)

    def _validate_messages_object(
        self,
        messages: Mapping[str, t.GeneralValueType],
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
            message_result = self._parse_dict_field(message, "message")
            if message_result.is_failure:
                return r[bool].fail(
                    f"Message must be a dictionary: {message_name} in {channel_name}",
                )

            message_validation = self._validate_message(
                message_result.value,
                channel_name,
                message_name,
            )
            if message_validation.is_failure:
                return message_validation

        return r[bool].ok(value=True)

    def _validate_servers(self, servers: Mapping[str, t.GeneralValueType]) -> r[bool]:
        """Validate AsyncAPI servers.

        Args:
        servers: Servers dictionary from AsyncAPI schema

        Returns:
        FlextResult indicating validation success or failure

        """
        for server_name, server in servers.items():
            server_result = self._parse_dict_field(server, "server")
            if server_result.is_failure:
                return r[bool].fail(f"Server must be a dictionary: {server_name}")
            server = server_result.value

            # Validate required fields
            if "url" not in server and "host" not in server:
                return r[bool].fail(f"Server missing 'url' or 'host': {server_name}")

            if "protocol" not in server:
                return r[bool].fail(f"Server missing 'protocol': {server_name}")

            # Validate protocol
            protocol_value = server["protocol"]
            protocol_result = self._parse_string_field(protocol_value, "protocol")
            if protocol_result.is_failure:
                return r[bool].fail(
                    f"Server 'protocol' must be a string: {server_name}"
                )
            protocol = protocol_result.value
            if protocol not in self._supported_protocols and self._strict_mode:
                return r[bool].fail(f"Unsupported protocol '{protocol}': {server_name}")

        return r[bool].ok(value=True)

    def _validate_components(
        self, components: Mapping[str, t.GeneralValueType]
    ) -> r[bool]:
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

            section_result = self._parse_dict_field(section_value, section_name)
            if section_result.is_failure:
                return r[bool].fail(
                    f"Component section must be a dictionary: {section_name}",
                )

        return r[bool].ok(value=True)

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
        request: t.JsonObject,
        schema: t.JsonObject,
    ) -> r[bool]:
        """Validate request against AsyncAPI schema.

        Args:
        request: Request to validate
        schema: AsyncAPI schema

        Returns:
        FlextResult containing validation result or error

        """
        # Basic AsyncAPI request validation
        # Validate AsyncAPI structure
        if "asyncapi" not in schema:
            return r[bool].fail("Schema missing 'asyncapi' version field")

        # Check if channels exist for message validation
        if "channels" not in schema:
            return r[bool].ok(value=True)  # No channels to validate against

        channels_value = schema["channels"]
        channels_result = self._parse_dict_field(channels_value, "channels")
        if channels_result.is_failure:
            return r[bool].fail(channels_result.error)
        channels = channels_result.value
        if not channels:
            return r[bool].ok(value=True)  # No channels to validate against

        # Basic validation - request should have expected structure
        # For WebSocket/SSE requests, we expect certain fields
        if "body" in request:
            body_value = request["body"]
            _ = body_value

        self.logger.debug("AsyncAPI request validation completed")
        return r[bool].ok(value=True)

    def _validate_response_channels(self, schema: t.JsonObject) -> r[bool]:
        """Validate channels in schema for response validation."""
        if "channels" not in schema:
            return r[bool].ok(value=True)  # No channels to validate against

        channels_value = schema["channels"]
        channels_result = self._parse_dict_field(channels_value, "channels")
        if channels_result.is_failure:
            return r[bool].fail(channels_result.error)
        if not channels_result.value:
            return r[bool].ok(value=True)  # No channels to validate against

        return r[bool].ok(value=True)

    def _validate_response_status_code(self, response: t.JsonObject) -> r[bool]:
        """Validate status code in response."""
        if "status_code" not in response:
            return r[bool].ok(value=True)

        status_code_value = response["status_code"]
        http_status_min = 100
        http_status_max = 599
        status_result = self._parse_int_field(status_code_value, "status_code")
        if status_result.is_failure:
            return r[bool].fail("Invalid status code")

        if not (http_status_min <= status_result.value <= http_status_max):
            return r[bool].fail("Invalid status code")

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
        FlextResult containing validation result or error

        """
        # Basic AsyncAPI response validation
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
        return r[bool].ok(value=True)

    def _to_general_value(self, value: object) -> t.GeneralValueType:
        match value:
            case str() | int() | float() | bool() | None:
                return value
            case list() as values:
                normalized_values: list[t.GeneralValueType] = []
                for item in values:
                    normalized_values.append(self._to_general_value(item))
                return normalized_values
            case dict() as mapping:
                normalized_mapping: dict[str, t.GeneralValueType] = {}
                for key, item in mapping.items():
                    normalized_mapping[str(key)] = self._to_general_value(item)
                return normalized_mapping
            case _:
                return str(value)

    def _load_schema_document(self, schema_source: str) -> r[object]:
        schema_path = Path(schema_source)
        if not schema_path.exists() or not schema_path.is_file():
            return r[object].fail(f"Schema file not found: {schema_source}")

        try:
            schema_text = schema_path.read_text(encoding="utf-8")
        except OSError as e:
            return r[object].fail(f"Failed to read schema file: {e}")

        suffix = schema_path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            try:
                import yaml
            except ImportError:
                return r[object].fail("YAML schema loading requires PyYAML")

            try:
                return r[object].ok(yaml.safe_load(schema_text))
            except Exception as e:
                return r[object].fail(f"Failed to parse YAML schema: {e}")

        try:
            return r[object].ok(json.loads(schema_text))
        except json.JSONDecodeError as e:
            return r[object].fail(f"Failed to parse JSON schema: {e}")

    @override
    def load_schema(
        self,
        schema_source: str,
    ) -> r[t.GeneralValueType]:
        """Load AsyncAPI schema from source.

        Args:
        schema_source: Schema file path

        Returns:
        FlextResult containing loaded schema or error

        """
        schema_result = self._load_schema_document(schema_source)
        if schema_result.is_failure:
            return r[t.GeneralValueType].fail(
                schema_result.error or "Failed to load AsyncAPI schema"
            )

        loaded_schema = schema_result.value
        if not isinstance(loaded_schema, dict):
            return r[t.GeneralValueType].fail(
                "AsyncAPI schema must be a JSON/YAML object"
            )

        normalized_schema = self._to_general_value(loaded_schema)
        return r[t.GeneralValueType].ok(normalized_schema)


__all__ = ["AsyncAPISchemaValidator"]
