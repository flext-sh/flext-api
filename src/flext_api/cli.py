"""CLI facade for flext-api — thin transport adapter.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.services.cli import FlextCliCli


class FlextApiCli(FlextCliCli):
    """Flext-api CLI facade — extends flext-cli CLI."""


def main() -> int:
    """Console-script entry point — commands are not implemented yet.

    Returns:
        The resulting ``int``.

    """
    return 0


__all__: tuple[str, ...] = ("FlextApiCli", "main")
