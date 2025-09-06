"""FLEXT API - HTTP Foundation Library for FLEXT Ecosystem.

Real functionality implementation following flext-core patterns.
Single unified classes following PEP8 naming conventions.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

# Import all modules with proper type handling
from flext_api.models import *
from flext_api.client import *
from flext_api.storage import *
from flext_api.api import *
from flext_api.app import *
from flext_api.config import *
from flext_api.exceptions import *
from flext_api.utilities import *
from flext_api.plugins import *
from flext_api.protocols import *
from flext_api.typings import *

# Collect all exports from modules dynamically - FLEXT Pattern
import flext_api.api as _api
import flext_api.client as _client
import flext_api.storage as _storage
import flext_api.models as _models
import flext_api.app as _app
import flext_api.config as _config
import flext_api.exceptions as _exceptions
import flext_api.utilities as _utilities
import flext_api.plugins as _plugins
import flext_api.protocols as _protocols
import flext_api.typings as _typings

# Build __all__ from actual module exports - FLEXT Pattern
__all__ = []
for module in [
    _api,
    _client,
    _storage,
    _models,
    _app,
    _config,
    _exceptions,
    _utilities,
    _plugins,
    _protocols,
    _typings,
]:
    if hasattr(module, "__all__"):
        __all__ += module.__all__

# Remove duplicates and sort - FLEXT Pattern
_all_exports = sorted(set(__all__))
__all__ = list(_all_exports)

# Version information
__version__ = "0.9.0"
