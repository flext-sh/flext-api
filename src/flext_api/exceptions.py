"""Generic HTTP Exceptions - Use flext-core only.

NO local exception classes. Delegate all error handling to FlextExceptions.
Use FlextExceptions.BaseError for all HTTP errors with status_code context.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from flext_core import FlextExceptions

# Re-export for convenience - but use FlextExceptions directly
HttpError = FlextExceptions.BaseError

__all__ = ["HttpError"]
