"""Main entry module for compatibility with tests.

Exposes `app` and `storage` matching test expectations.
"""

from __future__ import annotations

from flext_api.api_app import app as _default_app
from flext_api.storage import FlextAPIStorage

# Default app and storage for tests
app = _default_app
# Provide a synchronous storage instance expected by tests
storage: FlextAPIStorage = FlextAPIStorage()

__all__ = ["app", "storage"]
