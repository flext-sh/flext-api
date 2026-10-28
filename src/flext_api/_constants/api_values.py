"""API scalar constants.

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

from collections.abc import Mapping, MutableSequence
from http import HTTPMethod
from types import MappingProxyType
from typing import Final

from flext_core import c
from flext_web import t
from httpx import HTTPError as _HttpxError

from flext_api._constants import FlextApiConstantsEnums


class FlextApiConstantsValues(FlextApiConstantsEnums):
    """API scalar constants mixed into ``c.Api``."""

    EXC_HTTPX: Final[tuple[type[Exception], ...]] = (
        *c.EXC_HTTP_PROCESSING,
        _HttpxError,
    )
    SAFE_METHODS: Final[frozenset[str]] = frozenset(
        member.value
        for member in (
            HTTPMethod.GET,
            HTTPMethod.HEAD,
            HTTPMethod.OPTIONS,
            HTTPMethod.TRACE,
        )
    )
    TERMINAL_STATUSES: Final[frozenset[str]] = frozenset(
        member.value
        for member in (
            FlextApiConstantsEnums.Status.COMPLETED,
            FlextApiConstantsEnums.Status.FAILED,
            FlextApiConstantsEnums.Status.ERROR,
        )
    )
    VALID_STATUSES: Final[frozenset[str]] = frozenset(
        member.value for member in FlextApiConstantsEnums.Status.__members__.values()
    )
    DEFAULT_TIMEOUT: Final[int] = c.DEFAULT_TIMEOUT_SECONDS
    MAX_HOSTNAME_LENGTH: Final[int] = 253
    MAX_URL_LENGTH: Final[int] = 2048
    MIN_PORT: Final[int] = c.MIN_PORT
    MAX_PORT: Final[int] = c.MAX_PORT
    VALID_HTTP_METHODS: Final[frozenset[str]] = frozenset(
        member.value for member in HTTPMethod
    )
    HTTP_SUCCESS_MIN: Final[int] = 200
    HTTP_SUCCESS_MAX: Final[int] = 300
    HTTP_REDIRECT_MIN: Final[int] = 300
    HTTP_REDIRECT_MAX: Final[int] = 400
    HTTP_CLIENT_ERROR_MIN: Final[int] = 400
    HTTP_CLIENT_ERROR_MAX: Final[int] = 500
    HTTP_STATUS_MIN: Final[int] = 100
    HTTP_STATUS_MAX: Final[int] = 599
    HTTP_SERVER_ERROR_MIN: Final[int] = 500
    HTTP_ERROR_MIN: Final[int] = 400
    HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
    HEADER_AUTHORIZATION: Final[str] = "Authorization"
    HEADER_ACCEPT: Final[str] = "Accept"
    URL_PATH_SEPARATOR: Final[str] = "/"
    URL_PATH_EMPTY_ERROR: Final[str] = "URL path cannot be empty"
    REQUEST_EXTENSION_SNI_HOSTNAME: Final[str] = "sni_hostname"
    VALIDATION_LIMITS: Final[Mapping[str, t.Numeric]] = MappingProxyType({
        "MAX_URL_LENGTH": MAX_URL_LENGTH,
        "MIN_TIMEOUT": 0.1,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    })


__all__: MutableSequence[str] = ["FlextApiConstantsValues"]
