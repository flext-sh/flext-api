"""API config constants — real class for stand-in composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar


class FlextApiConfig:
    """SSOT for API-specific config loading defaults."""

    CONFIG_DIR_NAME: ClassVar[str] = "config"
    CONFIG_SCHEMAS_DIR_NAME: ClassVar[str] = "schemas"
    CONFIG_TEMPLATES_DIR_NAME: ClassVar[str] = "templates"
    CONFIG_SETTINGS_FILE_NAME: ClassVar[str] = "settings.yaml"
    CONFIG_SCHEMA_SUFFIX: ClassVar[str] = ".schema.json"
    CONFIG_DEFAULT_ENCODING: ClassVar[str] = "utf-8"
    CONFIG_TOML_SUFFIX: ClassVar[str] = ".toml"
    CONFIG_YAML_SUFFIX: ClassVar[str] = ".yaml"
    CONFIG_JSON_SUFFIX: ClassVar[str] = ".json"
    CONFIG_EXPAND_MAX_PASSES: ClassVar[int] = 10

    # Model config (moved from _models/config.py for ENFORCE-079)
    MODEL_CONFIG_FROZEN: ClassVar[bool] = True
    MODEL_CONFIG_STR_STRIP_WHITESPACE: ClassVar[bool] = True

    # Typings config (moved from _typings/config.py for ENFORCE-079)
    TYPE_SYSTEM_VERSION: ClassVar[str] = "3.13"

    # Utilities config (moved from _utilities/config.py for ENFORCE-079)
    UTILS_RETRY_DEFAULT: ClassVar[int] = 3
    UTILS_TIMEOUT_DEFAULT: ClassVar[int] = 30


__all__: list[str] = ["FlextApiConfig"]
