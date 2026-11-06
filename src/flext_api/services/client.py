"""Generic HTTP client facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence

from flext_api.services import FlextApiClientBase
from flext_api.services._services import FlextApiClientRequest


class FlextApiClient(FlextApiClientRequest, FlextApiClientBase):
    """Generic HTTP client using FLEXT patterns."""


__all__: MutableSequence[str] = ["FlextApiClient"]
