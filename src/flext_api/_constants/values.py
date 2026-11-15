"""API scalar constants — real class for stand-in composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from http import HTTPMethod
from types import MappingProxyType
from typing import ClassVar

from flext_core import c


class FlextApiValues:
    """API scalar constants referenced by the facade."""

    SAFE_METHODS: ClassVar[frozenset[str]] = frozenset(
        member.value
        for member in (
            HTTPMethod.GET,
            HTTPMethod.HEAD,
            HTTPMethod.OPTIONS,
            HTTPMethod.TRACE,
        )
    )
    TERMINAL_STATUSES: ClassVar[frozenset[str]] = frozenset(
        member
        for member in (
            "completed",
            "failed",
            "error",
        )
    )
    VALID_STATUSES: ClassVar[frozenset[str]] = frozenset(
        member for member in (
            "idle",
            "pending",
            "running",
            "completed",
            "failed",
            "error",
            "success",
        )
    )
    DEFAULT_TIMEOUT: ClassVar[int] = c.DEFAULT_TIMEOUT_SECONDS
    MAX_HOSTNAME_LENGTH: ClassVar[int] = 253
    MAX_URL_LENGTH: ClassVar[int] = 2048
    MIN_PORT: ClassVar[int] = c.MIN_PORT
    MAX_PORT: ClassVar[int] = c.MAX_PORT
    VALID_HTTP_METHODS: ClassVar[frozenset[str]] = frozenset(
        member.value for member in HTTPMethod
    )
    HTTP_SUCCESS_MIN: ClassVar[int] = 200
    HTTP_SUCCESS_MAX: ClassVar[int] = 300
    HTTP_REDIRECT_MIN: ClassVar[int] = 300
    HTTP_REDIRECT_MAX: ClassVar[int] = 400
    HTTP_CLIENT_ERROR_MIN: ClassVar[int] = 400
    HTTP_CLIENT_ERROR_MAX: ClassVar[int] = 500
    HTTP_STATUS_MIN: ClassVar[int] = 100
    HTTP_STATUS_MAX: ClassVar[int] = 599
    HTTP_SERVER_ERROR_MIN: ClassVar[int] = 500
    HTTP_ERROR_MIN: ClassVar[int] = 400
    HEADER_CONTENT_TYPE: ClassVar[str] = "Content-Type"
    HEADER_AUTHORIZATION: ClassVar[str] = "Authorization"
    HEADER_ACCEPT: ClassVar[str] = "Accept"
    URL_PATH_SEPARATOR: ClassVar[str] = "/"
    URL_PATH_EMPTY_ERROR: ClassVar[str] = "URL path cannot be empty"
    REQUEST_EXTENSION_SNI_HOSTNAME: ClassVar[str] = "sni_hostname"
    VALIDATION_LIMITS: ClassVar[Mapping[str, float]] = MappingProxyType({
        "MAX_URL_LENGTH": MAX_URL_LENGTH,
        "MIN_TIMEOUT": 0.1,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    })


__all__: list[str] = ["FlextApiValues"]
