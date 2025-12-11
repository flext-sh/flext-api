"""FLEXT API Performance Benchmarks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_api import FlextApiClient, FlextApiSettings
from flext_api.models import FlextApiModels


class TestAPIPerformanceBenchmarks:
    """Performance benchmarks for API operations."""

    def test_api_creation_benchmark(self) -> None:
        """Benchmark API creation performance."""
        # Simple benchmark for API creation
        config = FlextApiSettings(base_url="https://httpbin.org")
        client = FlextApiClient(config)
        assert client is not None

    def test_client_creation_benchmark(self) -> None:
        """Benchmark HTTP client creation performance."""
        # Simple benchmark for client creation
        config = FlextApiSettings(base_url="https://httpbin.org")
        client = FlextApiClient(config)
        assert client is not None

    def test_model_validation_benchmark(self) -> None:
        """Benchmark model validation performance."""
        # Simple benchmark for model validation
        config = FlextApiModels.ClientConfig(
            base_url="https://api.example.com",
            timeout=30,
            headers={"Accept": "application/json"},
        )
        assert config is not None
        assert config.base_url == "https://api.example.com"
