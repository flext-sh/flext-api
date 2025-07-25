"""Infrastructure layer for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module contains the infrastructure implementations including
repositories, external service adapters, and persistence.

Uses flext-core patterns for clean architecture implementation.
"""

from __future__ import annotations

# ==============================================================================
# DOMAIN PORTS - Interface contracts from domain layer
# ==============================================================================
from flext_api.domain.ports import PipelineRepository, PluginRepository

# ==============================================================================
# DEPENDENCY INJECTION - Container and configuration
# ==============================================================================
from flext_api.infrastructure.di_container import configure_api_dependencies

# ==============================================================================
# INFRASTRUCTURE PORTS - External service adapters and gateways
# ==============================================================================
from flext_api.infrastructure.ports import (
    FlextAuthorizationStrategy,
    FlextJWTAuthService,
    FlextRoleBasedAuthorizationStrategy,
    FlextTokenManager,
)

# ==============================================================================
# REPOSITORIES - Data persistence implementations
# ==============================================================================
from flext_api.infrastructure.repositories.pipeline_repository import (
    FlextInMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    FlextInMemoryPluginRepository,
)

# ==============================================================================
# PUBLIC INFRASTRUCTURE API - Organized by semantic category
# ==============================================================================
__all__ = [
    "FlextAuthorizationStrategy"
    "FlextInMemoryPipelineRepository"
    "FlextInMemoryPluginRepository"
    "FlextJWTAuthService"
    "FlextRoleBasedAuthorizationStrategy"
    "FlextTokenManager"
    "PipelineRepository"
    "PluginRepository"
    "configure_api_dependencies"
]
