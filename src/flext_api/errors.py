"""Generic HTTP Exceptions - Namespace class for API-specific exceptions.

Unified exception facade extending flext-core exceptions.
All exception types are organized under FlextApiErrors namespace.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import e, t


class FlextApiErrors:
    """HTTP exception types extending flext-core.

    Unified namespace class that provides HTTP-specific exceptions
    with status_code context for error handling.
    """

    class HttpError(e.BaseError):
        """HTTP error exception - real inheritance from e.BaseError.

        Provides HTTP-specific error handling with status_code context.
        Uses real inheritance to expose e.BaseError functionality through
        the HttpError namespace for HTTP operations.
        """


__all__: t.MutableSequenceOf[str] = ["FlextApiErrors"]
