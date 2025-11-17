"""Generic HTTP Operations following SOLID principles.

REMOVED: FlextApiOperations was a stub class that only raised NotImplementedError.
Use FlextApi or FlextApiClient directly for HTTP operations.

All HTTP operations should use:
- FlextApi.get(), .post(), .put(), .delete(), .patch() for high-level API
- FlextApiClient.request() for low-level request execution
- FlextApiModels.HttpRequest/HttpResponse for request/response models

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# This module is kept for backward compatibility but is deprecated.
# Use FlextApi or FlextApiClient directly instead.

__all__: list[str] = []
