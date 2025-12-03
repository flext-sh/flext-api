"""Generic HTTP Exceptions - Use flext-core only.

NO local exception classes. Delegate all error handling to e.
Use e.BaseError for all HTTP errors with status_code context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import e

# Re-export for convenience - but use FlextExceptions directly
HttpError = e.BaseError

__all__ = ["HttpError"]
