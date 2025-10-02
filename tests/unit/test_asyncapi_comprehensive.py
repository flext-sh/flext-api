"""Comprehensive tests for AsyncAPI schema validator with real functionality.

Tests AsyncAPISchemaValidator with complete schema validation scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api.schemas import AsyncAPISchemaValidator


class TestAsyncAPISchemaValidatorInitialization:
    """Tests for AsyncAPI schema validator initialization."""

    def test_validator_initialization_default(self) -> None:
        """Test validator initialization with defaults."""
        validator = AsyncAPISchemaValidator()

        assert validator is not None
        assert validator.name == "asyncapi"
        assert validator._strict_mode is True
        assert validator._validate_messages is True
        assert validator._validate_bindings is True

    def test_validator_initialization_custom(self) -> None:
        """Test validator initialization with custom settings."""
        validator = AsyncAPISchemaValidator(
            strict_mode=False,
            validate_messages=False,
            validate_bindings=False,
        )

        assert validator._strict_mode is False
        assert validator._validate_messages is False
        assert validator._validate_bindings is False

    def test_validator_supported_protocols(self) -> None:
        """Test validator has correct supported protocols."""
        validator = AsyncAPISchemaValidator()

        assert "ws" in validator._supported_protocols
        assert "wss" in validator._supported_protocols
        assert "http" in validator._supported_protocols
        assert "https" in validator._supported_protocols
        assert "mqtt" in validator._supported_protocols
        assert "kafka" in validator._supported_protocols


class TestAsyncAPISchemaValidation:
    """Tests for AsyncAPI schema validation."""

    def test_validate_minimal_asyncapi_2_schema(self) -> None:
        """Test validation of minimal AsyncAPI 2.x schema."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {
                "title": "User Service",
                "version": "1.0.0",
                "description": "User management service",
            },
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        validated = result.unwrap()
        assert validated["valid"] is True
        assert validated["version"] == "2.6.0"
        assert validated["title"] == "User Service"

    def test_validate_minimal_asyncapi_3_schema(self) -> None:
        """Test validation of minimal AsyncAPI 3.x schema."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Message Service", "version": "2.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        validated = result.unwrap()
        assert validated["valid"] is True
        assert validated["version"] == "3.0.0"

    def test_validate_missing_asyncapi_version(self) -> None:
        """Test validation fails for missing asyncapi version."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing 'asyncapi' version field" in result.error

    def test_validate_unsupported_asyncapi_version(self) -> None:
        """Test validation fails for unsupported version."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "1.0.0",  # Unsupported version
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Unsupported AsyncAPI version" in result.error

    def test_validate_missing_required_fields(self) -> None:
        """Test validation fails for missing required fields."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            # Missing 'info' and 'channels'
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing required fields" in result.error

    def test_validate_missing_info_fields(self) -> None:
        """Test validation fails for missing info fields."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {
                "title": "Test",
                # Missing 'version'
            },
            "channels": {},
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing required info fields" in result.error


class TestAsyncAPIChannelValidation:
    """Tests for AsyncAPI channel validation."""

    def test_validate_asyncapi_2_with_publish_operation(self) -> None:
        """Test AsyncAPI 2.x schema with publish operation."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Notification Service", "version": "1.0.0"},
            "channels": {
                "user/signup": {
                    "publish": {
                        "summary": "User signup event",
                        "message": {
                            "payload": {
                                "type": "object",
                                "properties": {
                                    "userId": {"type": "string"},
                                    "email": {"type": "string"},
                                },
                            }
                        },
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success
        validated = result.unwrap()
        assert "user/signup" in validated["channels"]

    def test_validate_asyncapi_2_with_subscribe_operation(self) -> None:
        """Test AsyncAPI 2.x schema with subscribe operation."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Event Listener", "version": "1.0.0"},
            "channels": {
                "notifications": {
                    "subscribe": {
                        "summary": "Subscribe to notifications",
                        "message": {
                            "payload": {
                                "type": "object",
                                "properties": {"message": {"type": "string"}},
                            }
                        },
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_asyncapi_3_with_address(self) -> None:
        """Test AsyncAPI 3.x schema with channel address."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Message Service", "version": "1.0.0"},
            "channels": {
                "userEvents": {
                    "address": "/users/events",
                    "messages": {
                        "userSignup": {
                            "payload": {
                                "type": "object",
                                "properties": {"userId": {"type": "string"}},
                            }
                        }
                    },
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_asyncapi_3_missing_address_strict_mode(self) -> None:
        """Test AsyncAPI 3.x validation fails for missing address in strict mode."""
        validator = AsyncAPISchemaValidator(strict_mode=True)

        schema = {
            "asyncapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {
                "testChannel": {
                    # Missing 'address' in strict mode
                    "messages": {}
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Missing 'address'" in result.error

    def test_validate_channel_with_multiple_operations(self) -> None:
        """Test channel with both publish and subscribe operations."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Bidirectional Service", "version": "1.0.0"},
            "channels": {
                "chat/messages": {
                    "publish": {
                        "message": {
                            "payload": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                            }
                        }
                    },
                    "subscribe": {
                        "message": {
                            "payload": {
                                "type": "object",
                                "properties": {"text": {"type": "string"}},
                            }
                        }
                    },
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success


class TestAsyncAPIServerValidation:
    """Tests for AsyncAPI server validation."""

    def test_validate_websocket_server(self) -> None:
        """Test validation of WebSocket server."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "WebSocket Service", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "production": {
                    "url": "wss://api.example.com",
                    "protocol": "wss",
                    "description": "Production WebSocket server",
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_mqtt_server(self) -> None:
        """Test validation of MQTT server."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "MQTT Service", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "broker": {
                    "url": "mqtt://broker.example.com:1883",
                    "protocol": "mqtt",
                    "description": "MQTT message broker",
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_kafka_server(self) -> None:
        """Test validation of Kafka server."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Kafka Service", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "kafka": {
                    "url": "kafka://kafka.example.com:9092",
                    "protocol": "kafka",
                    "description": "Kafka cluster",
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_server_missing_url(self) -> None:
        """Test validation fails for server missing URL/host."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "test": {
                    "protocol": "wss",
                    # Missing 'url' and 'host'
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "missing 'url' or 'host'" in result.error

    def test_validate_server_missing_protocol(self) -> None:
        """Test validation fails for server missing protocol."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "test": {
                    "url": "wss://example.com",
                    # Missing 'protocol'
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "missing 'protocol'" in result.error

    def test_validate_server_unsupported_protocol_strict_mode(self) -> None:
        """Test validation fails for unsupported protocol in strict mode."""
        validator = AsyncAPISchemaValidator(strict_mode=True)

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "servers": {
                "test": {
                    "url": "custom://example.com",
                    "protocol": "custom-protocol",  # Unsupported
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Unsupported protocol" in result.error


class TestAsyncAPIComponentValidation:
    """Tests for AsyncAPI components validation."""

    def test_validate_components_schemas(self) -> None:
        """Test validation of components with schemas."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Service", "version": "1.0.0"},
            "channels": {},
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                        },
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_components_messages(self) -> None:
        """Test validation of components with messages."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Service", "version": "1.0.0"},
            "channels": {},
            "components": {
                "messages": {
                    "userCreated": {
                        "payload": {
                            "type": "object",
                            "properties": {"userId": {"type": "string"}},
                        }
                    }
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_components_security_schemes(self) -> None:
        """Test validation of components with security schemes."""
        validator = AsyncAPISchemaValidator()

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Service", "version": "1.0.0"},
            "channels": {},
            "components": {
                "securitySchemes": {
                    "apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
                }
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_success

    def test_validate_invalid_component_section_strict_mode(self) -> None:
        """Test validation fails for invalid component section in strict mode."""
        validator = AsyncAPISchemaValidator(strict_mode=True)

        schema = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
            "components": {
                "invalidSection": {}  # Not a valid component section
            },
        }

        result = validator.validate_schema(schema)

        assert result.is_failure
        assert "Invalid component section" in result.error


class TestAsyncAPISchemaSupport:
    """Tests for schema type support checking."""

    def test_supports_asyncapi_schema(self) -> None:
        """Test validator supports asyncapi schema type."""
        validator = AsyncAPISchemaValidator()

        assert validator.supports_schema("asyncapi") is True
        assert validator.supports_schema("async-api") is True
        assert validator.supports_schema("asyncapi2") is True
        assert validator.supports_schema("asyncapi3") is True
        assert validator.supports_schema("ASYNCAPI") is True  # Case insensitive

    def test_does_not_support_other_schemas(self) -> None:
        """Test validator doesn't support other schema types."""
        validator = AsyncAPISchemaValidator()

        assert validator.supports_schema("openapi") is False
        assert validator.supports_schema("json-schema") is False
        assert validator.supports_schema("graphql") is False

    def test_get_supported_schemas(self) -> None:
        """Test getting list of supported schemas."""
        validator = AsyncAPISchemaValidator()

        supported = validator.get_supported_schemas()

        assert "asyncapi" in supported
        assert "async-api" in supported
        assert "asyncapi2" in supported
        assert "asyncapi3" in supported


class TestAsyncAPIRequestResponseValidation:
    """Tests for request/response validation."""

    def test_validate_request(self) -> None:
        """Test validating request against schema."""
        validator = AsyncAPISchemaValidator()

        request = {"message": "test"}
        schema = {"asyncapi": "2.6.0"}

        result = validator.validate_request(request, schema)

        # Currently returns success - placeholder implementation
        assert result.is_success

    def test_validate_response(self) -> None:
        """Test validating response against schema."""
        validator = AsyncAPISchemaValidator()

        response = {"data": "test"}
        schema = {"asyncapi": "2.6.0"}

        result = validator.validate_response(response, schema)

        # Currently returns success - placeholder implementation
        assert result.is_success


class TestAsyncAPISchemaLoading:
    """Tests for schema loading."""

    def test_load_schema_from_dict(self) -> None:
        """Test loading schema from dictionary."""
        validator = AsyncAPISchemaValidator()

        schema_dict = {
            "asyncapi": "2.6.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "channels": {},
        }

        result = validator.load_schema(schema_dict)

        assert result.is_success
        loaded = result.unwrap()
        assert loaded == schema_dict

    def test_load_schema_from_file_path_not_implemented(self) -> None:
        """Test loading schema from file path (not implemented)."""
        validator = AsyncAPISchemaValidator()

        result = validator.load_schema("/path/to/schema.yaml")

        assert result.is_failure
        assert "File loading not implemented" in result.error
