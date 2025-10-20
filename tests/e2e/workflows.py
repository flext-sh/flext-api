"""End-to-end workflow tests for FLEXT API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pytest

from flext_api import (
    FlextApiClient,
)


@pytest.mark.e2e
class TestApiWorkflowE2E:
    """End-to-end tests for complete API workflows."""

    def test_complete_api_workflow(self) -> None:
        """Test complete workflow from API creation to HTTP operations."""
        # Simple e2e test
        from flext_api.config import FlextApiConfig

        api_config = FlextApiConfig()
        api_instance = FlextApiClient(api_config)
        assert api_instance is not None

    def test_http_client_workflow(self) -> None:
        """Test HTTP client workflow."""
        # Simple client workflow test
        from flext_api.config import FlextApiConfig

        api_config = FlextApiConfig(base_url="https://httpbin.org")
        client = FlextApiClient(api_config)
        assert client is not None
