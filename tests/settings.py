"""Runtime settings for flext-api tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_tests import FlextTestsSettings

from flext_api import FlextApiSettings


class TestsFlextApiSettings(FlextApiSettings, FlextTestsSettings):
    """API settings extended with the shared test namespace."""


__all__: list[str] = ["TestsFlextApiSettings"]
