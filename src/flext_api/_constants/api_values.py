"""API scalar constants — stand-in for facade MRO composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api._constants import FlextApiConstantsEnums
from flext_api._constants.values import FlextApiValues


class FlextApiConstantsValues(FlextApiConstantsEnums, FlextApiValues):
    """API scalar constants mixed into ``c.Api`` via stand-in composition."""

    pass


__all__: list[str] = ["FlextApiConstantsValues"]
