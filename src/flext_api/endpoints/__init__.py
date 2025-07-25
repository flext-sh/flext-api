"""API endpoints for FLEXT API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides the API endpoint definitions for the FLEXT platform
organized by functional areas for maintainability and scalability.
"""

from __future__ import annotations

from flext_api.endpoints.auth import auth_router

# Temporarily disabled due to missing models
# from flext_api.endpoints.pipelines import pipelines_router
# from flext_api.endpoints.plugins import plugins_router
from flext_api.endpoints.system import system_router

__all__ = ["auth_router", "system_router"]
