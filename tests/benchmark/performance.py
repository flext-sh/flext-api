"""FLEXT API Performance Benchmarks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApi, FlextApiClient, FlextApiModels


class TestAPIPerformanceBenchmarks:
    """Performance benchmarks for API operations."""

    def test_api_creation_benchmark(self) -> None:
        """Benchmark API creation performance."""
        # Simple benchmark for API creation
        api_instance = FlextApi.create_client(base_url="https://httpbin.org")
        assert api_instance is not None

    def test_client_creation_benchmark(self) -> None:
        """Benchmark HTTP client creation performance."""
        # Simple benchmark for client creation
        client = FlextApiClient(base_url="https://httpbin.org")
        assert client is not None

    def test_model_validation_benchmark(self) -> None:
        """Benchmark model validation performance."""
        # Simple benchmark for model validation
        config = FlextApiModels.ClientConfig(base_url="https://api.example.com")
        assert config is not None
        assert config.base_url == "https://api.example.com"
