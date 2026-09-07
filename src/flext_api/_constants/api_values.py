"""API scalar constants."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Final

from httpx import HTTPError as _HttpxError

from flext_web import FlextWebConstants, t

from .api_enums import FlextApiConstantsEnums

if TYPE_CHECKING:
    from collections.abc import Mapping


class FlextApiConstantsValues(FlextApiConstantsEnums):
    """API scalar constants mixed into ``c.Api``."""

    EXC_HTTPX: Final[t.VariadicTuple[type[Exception]]] = (
        ConnectionError,
        KeyError,
        TypeError,
        ValueError,
        _HttpxError,
    )
    METHOD_LITERALS_HEAD_LOWER: Final[str] = "head"
    SAFE_METHODS: Final[frozenset[str]] = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
    TERMINAL_STATUSES: Final[frozenset[str]] = frozenset({
        "completed",
        "failed",
        "error",
    })
    VALID_STATUSES: Final[frozenset[str]] = frozenset(
        member.value for member in FlextApiConstantsEnums.Status.__members__.values()
    )
    DEFAULT_TIMEOUT: Final[float] = float(FlextWebConstants.DEFAULT_TIMEOUT_SECONDS)
    DEFAULT_BASE_URL: Final[str] = "http://localhost:8000"
    MAX_HOSTNAME_LENGTH: Final[int] = 253
    MAX_URL_LENGTH: Final[int] = 2048
    MIN_PORT: Final[int] = 1
    MAX_PORT: Final[int] = 65535
    VALID_HTTP_METHODS: Final[frozenset[str]] = frozenset({
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "CONNECT",
        "TRACE",
    })
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
    VALIDATION_LIMITS: Final[Mapping[str, t.Numeric]] = MappingProxyType({
        "MAX_URL_LENGTH": MAX_URL_LENGTH,
        "MIN_TIMEOUT": 0.1,
        "MAX_TIMEOUT": 300.0,
        "MIN_RETRIES": 0,
        "MAX_RETRIES": 10,
    })


__all__: t.MutableSequenceOf[str] = ["FlextApiConstantsValues"]
