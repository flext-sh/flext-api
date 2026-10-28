"""Generic HTTP client facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.services import FlextApiClientBase
from flext_api.services._services import FlextApiClientRequest

if TYPE_CHECKING:
    from flext_api import t


class FlextApiClient(FlextApiClientRequest, FlextApiClientBase):
    """Generic HTTP client using FLEXT patterns."""


__all__: t.MutableSequenceOf[str] = ["FlextApiClient"]
