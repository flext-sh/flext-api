# Pydantic Standardization for flext-api

## Overview

This document summarizes the standardization of Pydantic usage in flext-api to use the base models from flext-core.

## Changes Made

### 1. Model Base Class Updates

All Pydantic models now inherit from the appropriate flext-core base classes:

- **Request Models**: Now inherit from `APIRequest` instead of `BaseModel`
- **Response Models**: Now inherit from `APIResponse` instead of `BaseModel`
- **General API Models**: Now inherit from `APIBaseModel` instead of `BaseModel`
- **Value Objects**: Now inherit from `DomainValueObject` instead of `ValueObject`

### 2. Shared Model Reuse

Removed duplicate definitions and now use shared models from flext-core:

- `APIResponse` - Standard API response with success, message, timestamp
- `ComponentHealth` - Component health status (replaced ComponentHealthAPI)
- `PluginType` - Plugin type enumeration
- `OperationStatus` - Operation status enumeration (replaced ExecutionStatus)
- `ErrorResponse` - Standard error response
- `AuthToken`, `UserInfo` - Authentication models

### 3. Files Updated

#### Model Files

- `models/auth.py` - All auth models now use appropriate base classes
- `models/system.py` - Removed duplicate APIResponse, all models use base classes
- `models/monitoring.py` - Uses ComponentHealth from flext_core
- `models/pipeline.py` - Uses OperationStatus from flext_core
- `models/plugin.py` - Uses PluginType from flext_core

#### Endpoint Files

- `main.py` - Uses APIInfoResponse and SimpleHealthResponse
- `pipeline_execution_endpoints.py` - Updated param classes
- `database_endpoints.py` - Fixed import path for APIResponse
- `endpoints/pipelines.py` - Updated param classes

### 4. Backward Compatibility

The `models/__init__.py` file now re-exports shared models from flext_core to maintain backward compatibility for any code that imports from `flext_api.models`.

### 5. Benefits

- **Consistency**: All FLEXT modules now use the same base Pydantic models
- **Reduced Duplication**: No more duplicate model definitions across modules
- **Type Safety**: Consistent validation and configuration across all models
- **Performance**: Shared base configurations optimized for each use case
- **Maintainability**: Changes to base models automatically propagate

## Import Pattern

All modules should now follow this import pattern:

```python
from pydantic import Field, field_validator  # Only import what's needed
from flext_core import (
    APIBaseModel,
    APIRequest,
    APIResponse,
    DomainValueObject,
    # ... other shared models as needed
)
```

## Configuration

The base models provide appropriate configurations:

- `APIRequest/APIResponse`: Flexible for external data (`extra="ignore"`)
- `DomainValueObject`: Strict and immutable (`frozen=True`, `extra="forbid"`)
- `APIBaseModel`: Balanced for general API usage
