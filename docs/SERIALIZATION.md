# Serialization Guide

**flext-api Serialization System**
**Version**: 1.0.0 | **Last Updated**: 2025-10-01

## Overview

The flext-api serialization system provides multiple format support with automatic content-type negotiation, graceful degradation for optional dependencies, and a flexible registry pattern.

## Supported Formats

### 1. JSON Serialization

**Format**: `application/json`
**Implementation**: `JSONSerializer`
**Features**:
- Fast serialization with orjson (falls back to standard json)
- UTF-8 encoding
- Pretty printing support
- Custom type handling

**Usage**:
```python
from flext_api.serializers import JSONSerializer

# Create serializer
serializer = JSONSerializer(pretty=False)

# Serialize data
data = {"user": "john", "age": 30}
serialized = serializer.serialize(data)
# Returns: b'{"user":"john","age":30}'

# Deserialize data
deserialized = serializer.deserialize(serialized)
# Returns: {"user": "john", "age": 30}

# Pretty printing
pretty_serializer = JSONSerializer(pretty=True)
pretty_json = pretty_serializer.serialize(data)
# Returns formatted JSON with indentation
```

**Performance**:
- With orjson: ~3-5x faster than standard json
- Fallback: Standard json module (always available)

### 2. MessagePack Serialization

**Format**: `application/msgpack`
**Implementation**: `MessagePackSerializer`
**Features**:
- Compact binary format
- Efficient for large datasets
- Type preservation
- Streaming support

**Installation**:
```bash
pip install msgpack
```

**Usage**:
```python
from flext_api.serializers import MessagePackSerializer

# Create serializer
serializer = MessagePackSerializer()

# Check availability
if not serializer._available:
    print("msgpack not installed")

# Serialize data
data = {"test": "data", "list": [1, 2, 3]}
serialized = serializer.serialize(data)
# Returns: binary msgpack data

# Deserialize data
deserialized = serializer.deserialize(serialized)
# Returns: {"test": "data", "list": [1, 2, 3]}
```

**Benefits**:
- 30-50% smaller than JSON
- Faster serialization/deserialization
- Maintains type information

### 3. CBOR Serialization

**Format**: `application/cbor`
**Implementation**: `CBORSerializer`
**Features**:
- Compact binary format
- Self-describing
- Extensible type system
- Standards-based (RFC 8949)

**Installation**:
```bash
pip install cbor2
```

**Usage**:
```python
from flext_api.serializers import CBORSerializer

# Create serializer
serializer = CBORSerializer()

# Serialize data
data = {"test": "data", "binary": b"bytes"}
serialized = serializer.serialize(data)
# Returns: binary CBOR data

# Deserialize data
deserialized = serializer.deserialize(serialized)
# Returns: {"test": "data", "binary": b"bytes"}
```

**Use Cases**:
- IoT data exchange
- Binary protocol communication
- Efficient data storage
- Interoperability with other languages

## Serializer Registry

The `SerializerRegistry` provides unified access to all serializers with automatic content-type negotiation.

### Basic Usage

```python
from flext_api.serializers import SerializerRegistry, SerializationFormat

# Create registry (automatically registers default serializers)
registry = SerializerRegistry()

# Serialize with specific format
data = {"key": "value"}
result = registry.serialize(data, SerializationFormat.JSON)

if result.is_success:
    serialized = result.unwrap()
    print(f"Serialized: {serialized}")

# Deserialize with specific format
result = registry.deserialize(serialized, SerializationFormat.JSON)

if result.is_success:
    data = result.unwrap()
    print(f"Data: {data}")
```

### Content-Type Negotiation

```python
from flext_api.serializers import SerializerRegistry

registry = SerializerRegistry()

# Get serializer by content type
content_type = "application/json"
result = registry.get_serializer_by_content_type(content_type)

if result.is_success:
    serializer = result.unwrap()
    # Use serializer
    serialized = serializer.serialize({"test": "data"})
```

### Default Format Configuration

```python
from flext_api.serializers import SerializerRegistry, SerializationFormat

registry = SerializerRegistry()

# Set default format
registry.set_default_format(SerializationFormat.MSGPACK)

# Serialize without specifying format (uses default)
data = {"key": "value"}
result = registry.serialize(data)  # Uses MessagePack
```

### Custom Serializers

Register custom serializers for your own formats:

```python
from flext_api.serializers import SerializerRegistry, SerializerProtocol
from flext_core import FlextResult
from typing import Any

class CustomSerializer:
    """Custom serializer implementation."""

    def serialize(self, data: Any) -> bytes:
        # Custom serialization logic
        return b"custom_data"

    def deserialize(self, data: bytes) -> Any:
        # Custom deserialization logic
        return {"custom": "data"}

    @property
    def content_type(self) -> str:
        return "application/x-custom"

# Register custom serializer
registry = SerializerRegistry()
custom_serializer = CustomSerializer()
registry.register_serializer("custom", custom_serializer)

# Use custom serializer
result = registry.serialize(data, "custom")
```

## Error Handling

All serialization operations return `FlextResult` for type-safe error handling:

```python
from flext_api.serializers import SerializerRegistry, SerializationFormat

registry = SerializerRegistry()

# Handle serialization errors
data = {"key": "value"}
result = registry.serialize(data, SerializationFormat.JSON)

if result.is_success:
    serialized = result.unwrap()
    print(f"Success: {serialized}")
else:
    print(f"Error: {result.error}")

# Handle deserialization errors
result = registry.deserialize(b"invalid data", SerializationFormat.JSON)

if result.is_failure:
    print(f"Deserialization failed: {result.error}")
```

## Integration with HTTP Clients

Use serialization in HTTP requests and responses:

```python
from flext_api import FlextApiClient
from flext_api.serializers import SerializerRegistry, SerializationFormat
from flext_api.models import FlextApiModels

# Create client and registry
client = FlextApiClient(base_url="https://api.example.com")
registry = SerializerRegistry()

# Serialize request body
request_data = {"user": "john", "action": "login"}
serialize_result = registry.serialize(request_data, SerializationFormat.JSON)

if serialize_result.is_success:
    serialized_body = serialize_result.unwrap()

    # Create HTTP request
    request = FlextApiModels.Request(
        method="POST",
        url="/auth/login",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body=serialized_body
    )

    # Send request ()
    # response = client.request(request)
```

## Best Practices

### 1. Choose the Right Format

- **JSON**: Human-readable, web APIs, debugging
- **MessagePack**: Performance-critical, large datasets, internal services
- **CBOR**: IoT, embedded systems, standards compliance

### 2. Handle Optional Dependencies

```python
from flext_api.serializers import MessagePackSerializer

serializer = MessagePackSerializer()

if not serializer._available:
    # Fallback to JSON
    from flext_api.serializers import JSONSerializer
    serializer = JSONSerializer()
```

### 3. Use Registry for Flexibility

```python
# Registry allows runtime format selection
registry = SerializerRegistry()

def process_data(data: dict, format: str):
    result = registry.serialize(data, format)
    if result.is_success:
        return result.unwrap()
    # Handle error
```

### 4. Content-Type Negotiation

```python
def handle_request(request_data: bytes, content_type: str):
    registry = SerializerRegistry()

    # Get appropriate deserializer
    serializer_result = registry.get_serializer_by_content_type(content_type)

    if serializer_result.is_success:
        serializer = serializer_result.unwrap()
        return serializer.deserialize(request_data)
```

## Performance Considerations

### JSON Performance
- **orjson**: 3-5x faster serialization, 2-3x faster deserialization
- **Fallback**: Standard json always available, no dependencies

### MessagePack Performance
- **Size**: 30-50% smaller than JSON
- **Speed**: 2-3x faster than standard JSON
- **Trade-off**: Requires msgpack dependency

### CBOR Performance
- **Size**: Similar to MessagePack
- **Standards**: RFC 8949 compliance
- **Compatibility**: Better language interoperability

## Testing

```python
import pytest
from flext_api.serializers import JSONSerializer, SerializerRegistry

def test_json_roundtrip():
    """Test JSON serialization roundtrip."""
    serializer = JSONSerializer()
    original = {"test": "data", "nested": {"key": "value"}}

    # Serialize
    serialized = serializer.serialize(original)

    # Deserialize
    deserialized = serializer.deserialize(serialized)

    assert deserialized == original

def test_registry_format_selection():
    """Test registry format selection."""
    registry = SerializerRegistry()
    data = {"key": "value"}

    # Test each format
    for format in ["json", "msgpack", "cbor"]:
        result = registry.serialize(data, format)
        assert result.is_success or "not installed" in result.error
```

## Troubleshooting

### ImportError for Optional Dependencies

**Problem**: `msgpack not installed` or `cbor2 not installed`

**Solution**:
```bash
# Install optional dependencies
pip install msgpack
pip install cbor2

# Or check availability
from flext_api.serializers import MessagePackSerializer
serializer = MessagePackSerializer()
if not serializer._available:
    print("Please install msgpack: pip install msgpack")
```

### SerializationError

**Problem**: `Serialization failed: ...`

**Solution**: Check data types and format compatibility
```python
# Ensure data is serializable
import json

data = {"key": "value"}
try:
    json.dumps(data)  # Test with standard json
except TypeError as e:
    print(f"Data not serializable: {e}")
```

## API Reference

### JSONSerializer
- `__init__(pretty: bool = False)`
- `serialize(data: Any) -> bytes`
- `deserialize(data: bytes) -> Any`
- `content_type: str` → `"application/json"`

### MessagePackSerializer
- `__init__()`
- `serialize(data: Any) -> bytes`
- `deserialize(data: bytes) -> Any`
- `content_type: str` → `"application/msgpack"`
- `_available: bool` → Installation status

### CBORSerializer
- `__init__()`
- `serialize(data: Any) -> bytes`
- `deserialize(data: bytes) -> Any`
- `content_type: str` → `"application/cbor"`
- `_available: bool` → Installation status

### SerializerRegistry
- `__init__()`
- `register_serializer(format, serializer) -> FlextResult[None]`
- `get_serializer(format) -> FlextResult[Serializer]`
- `get_serializer_by_content_type(content_type) -> FlextResult[Serializer]`
- `serialize(data, format=None) -> FlextResult[bytes]`
- `deserialize(data, format=None) -> FlextResult[Any]`
- `set_default_format(format) -> FlextResult[None]`

---

**Copyright (c) 2025 FLEXT Team. All rights reserved.**
**License**: MIT
