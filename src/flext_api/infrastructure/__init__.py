"""Infrastructure layer for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module contains the infrastructure implementations including
repositories, external service adapters, and persistence.

Uses flext-core patterns for clean architecture implementation.
"""

from __future__ import annotations

from flext_api.domain.ports import PipelineRepository, PluginRepository
from flext_api.infrastructure.repositories.pipeline_repository import (
    InMemoryPipelineRepository,
)
from flext_api.infrastructure.repositories.plugin_repository import (
    InMemoryPluginRepository,
)

__all__ = [
    "InMemoryPipelineRepository",
    "InMemoryPluginRepository",
    "PipelineRepository",
    "PluginRepository",
]
