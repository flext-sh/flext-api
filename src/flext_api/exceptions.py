"""Generic HTTP Exceptions - Use flext-core only.

NO local exception classes. Delegate all error handling to e.
Use e.BaseError for all HTTP errors with status_code context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext import e


class HttpError(e.BaseError):
    """HTTP error exception - real inheritance from e.BaseError.

    Provides HTTP-specific error handling with status_code context.
    Uses real inheritance to expose e.BaseError functionality through
    the HttpError namespace for HTTP operations.
    """


__all__ = ["HttpError"]
