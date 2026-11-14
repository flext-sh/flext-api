# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Api. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_api._constants.api import FlextApiConstantsApi
    from flext_api._constants.api_enums import FlextApiConstantsEnums
    from flext_api._constants.api_values import FlextApiConstantsValues
    from flext_api._constants.base import FlextApiConstantsBase
    from flext_api._constants.config import FlextApiConstantsConfig


__all__: tuple[str, ...] = (
    "FlextApiConstantsApi",
    "FlextApiConstantsBase",
    "FlextApiConstantsConfig",
    "FlextApiConstantsEnums",
    "FlextApiConstantsValues",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextApiConstantsApi": ".api",
        "FlextApiConstantsBase": ".base",
        "FlextApiConstantsConfig": ".config",
        "FlextApiConstantsEnums": ".api_enums",
        "FlextApiConstantsValues": ".api_values",
    },
    public_exports=__all__,
    deferred_members={
        "FlextApiConstantsApi": (
            "SAFE_METHODS",
            "TERMINAL_STATUSES",
            "VALID_STATUSES",
            "DEFAULT_TIMEOUT",
            "MAX_HOSTNAME_LENGTH",
            "MAX_URL_LENGTH",
            "MIN_PORT",
            "MAX_PORT",
            "VALID_HTTP_METHODS",
            "HTTP_SUCCESS_MIN",
            "HTTP_SUCCESS_MAX",
            "HTTP_REDIRECT_MIN",
            "HTTP_REDIRECT_MAX",
            "HTTP_CLIENT_ERROR_MIN",
            "HTTP_CLIENT_ERROR_MAX",
            "HTTP_STATUS_MIN",
            "HTTP_STATUS_MAX",
            "HTTP_SERVER_ERROR_MIN",
            "HTTP_ERROR_MIN",
            "HEADER_CONTENT_TYPE",
            "HEADER_AUTHORIZATION",
            "HEADER_ACCEPT",
            "URL_PATH_SEPARATOR",
            "URL_PATH_EMPTY_ERROR",
            "REQUEST_EXTENSION_SNI_HOSTNAME",
            "VALIDATION_LIMITS",
            "Method",
            "ProtocolMethod",
            "Status",
            "WebhookDeliveryStatus",
            "WebhookAlgorithm",
            "ContentType",
            "OpenApiSecuritySchemeType",
            "HttpProtocol",
        ),
        "FlextApiConstantsBase": (),
        "FlextApiConstantsConfig": (
            "CONFIG_DIR_NAME",
            "CONFIG_SCHEMAS_DIR_NAME",
            "CONFIG_TEMPLATES_DIR_NAME",
            "CONFIG_SETTINGS_FILE_NAME",
            "CONFIG_SCHEMA_SUFFIX",
            "CONFIG_DEFAULT_ENCODING",
            "CONFIG_TOML_SUFFIX",
            "CONFIG_YAML_SUFFIX",
            "CONFIG_JSON_SUFFIX",
            "CONFIG_EXPAND_MAX_PASSES",
            "MODEL_CONFIG_FROZEN",
            "MODEL_CONFIG_STR_STRIP_WHITESPACE",
            "TYPE_SYSTEM_VERSION",
            "UTILS_RETRY_DEFAULT",
            "UTILS_TIMEOUT_DEFAULT",
        ),
        "FlextApiConstantsEnums": (
            "Method",
            "ProtocolMethod",
            "Status",
            "WebhookDeliveryStatus",
            "WebhookAlgorithm",
            "ContentType",
            "OpenApiSecuritySchemeType",
            "HttpProtocol",
        ),
        "FlextApiConstantsValues": (
            "SAFE_METHODS",
            "TERMINAL_STATUSES",
            "VALID_STATUSES",
            "DEFAULT_TIMEOUT",
            "MAX_HOSTNAME_LENGTH",
            "MAX_URL_LENGTH",
            "MIN_PORT",
            "MAX_PORT",
            "VALID_HTTP_METHODS",
            "HTTP_SUCCESS_MIN",
            "HTTP_SUCCESS_MAX",
            "HTTP_REDIRECT_MIN",
            "HTTP_REDIRECT_MAX",
            "HTTP_CLIENT_ERROR_MIN",
            "HTTP_CLIENT_ERROR_MAX",
            "HTTP_STATUS_MIN",
            "HTTP_STATUS_MAX",
            "HTTP_SERVER_ERROR_MIN",
            "HTTP_ERROR_MIN",
            "HEADER_CONTENT_TYPE",
            "HEADER_AUTHORIZATION",
            "HEADER_ACCEPT",
            "URL_PATH_SEPARATOR",
            "URL_PATH_EMPTY_ERROR",
            "REQUEST_EXTENSION_SNI_HOSTNAME",
            "VALIDATION_LIMITS",
            "Method",
            "ProtocolMethod",
            "Status",
            "WebhookDeliveryStatus",
            "WebhookAlgorithm",
            "ContentType",
            "OpenApiSecuritySchemeType",
            "HttpProtocol",
        ),
    },
)
