# Domain Layer

**Domain entities and value objects for FLEXT API**

## Overview

This directory contains domain-driven design (DDD) components including entities and value objects that represent core business concepts for HTTP API operations.

## Components

### Domain Entities (entities.py)

- Rich domain objects with identity and behavior
- Business logic encapsulation
- State management and validation

### Value Objects (value_objects.py)

- Immutable domain values
- Validation and business rules
- Type-safe domain primitives

## Usage

```python
from flext_api.domain.entities import SomeEntity
from flext_api.domain.value_objects import SomeValue

# Create domain entities with business logic
entity = SomeEntity.create(data)

# Use immutable value objects
value = SomeValue.from_string("example")
```

## Development

Domain components follow DDD principles with clear separation of business logic from infrastructure concerns. See project documentation for full development guidelines.
