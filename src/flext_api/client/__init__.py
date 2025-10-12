"""FlextApiClient components package.

This package contains the modular components of the FlextApiClient
extracted for better maintainability and separation of concerns.

Components:
- http_operations: Core HTTP method implementations
- configuration_manager: Configuration management functionality
- lifecycle_manager: Client lifecycle and resource management

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from .configuration_manager import ConfigurationManager
from .http_operations import HttpOperations
from .lifecycle_manager import LifecycleManager

# Try to import FlextApiClient from the main client module
try:
    from .client import FlextApiClient

    _flext_api_client_available = True
except ImportError:
    _flext_api_client_available = False
    FlextApiClient = None

__all__ = [
    "ConfigurationManager",
    "HttpOperations",
    "LifecycleManager",
]

if _flext_api_client_available:
    __all__.append("FlextApiClient")
