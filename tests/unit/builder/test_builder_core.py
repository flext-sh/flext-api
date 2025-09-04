"""Tests for flext_api.builder module - REAL classes only.

Tests using only REAL classes directly from flext_api.
No helpers, no aliases, no compatibility layers.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_api import FlextApiModels


class TestFlextApiBuilderCore:
    """Test FlextApiModels builder functionality."""

    def test_query_builder_creation(self) -> None:
        """Test query builder creation."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        assert builder.page == 1
        assert builder.page_size == 50
        assert builder.sort_order == "asc"
        assert len(builder.filters) == 0

    def test_query_builder_add_filters(self) -> None:
        """Test adding filters to query builder."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        # Add filters
        filter_result = builder.add_filter("status", "active")
        assert filter_result.success

        # Verify filter was added
        assert len(builder.filters) == 1
        assert builder.filters["status"] == "active"

    def test_response_builder_success(self) -> None:
        """Test response builder success response."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        response_result = builder.success(data={"items": [1, 2, 3]}, message="Success")

        assert response_result.success
        response_data = response_result.data
        assert response_data["status"] == "success"
        assert response_data["message"] == "Success"
        assert response_data["data"]["items"] == [1, 2, 3]

    def test_response_builder_error(self) -> None:
        """Test response builder error response."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        response_result = builder.error("Not found", 404)

        assert response_result.success
        response_data = response_result.data
        assert response_data["status"] == "error"
        assert response_data["message"] == "Not found"
        assert response_data["status_code"] == 404

    def test_query_builder_pagination(self) -> None:
        """Test query builder pagination settings."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        builder.page = 2
        builder.page_size = 25

        assert builder.page == 2
        assert builder.page_size == 25

    def test_query_builder_sorting(self) -> None:
        """Test query builder sorting."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        builder.sort_by = "created_at"
        builder.sort_order = "desc"

        assert builder.sort_by == "created_at"
        assert builder.sort_order == "desc"

    def test_query_params_conversion(self) -> None:
        """Test converting query builder to params."""
        models = FlextApiModels()
        builder = models.HttpQuery()

        builder.add_filter("status", "active")
        builder.page = 2
        builder.page_size = 10

        params_result = builder.to_query_params()
        assert params_result.success

        params = params_result.data
        assert params["status"] == "active"
        assert params["page"] == 2
        assert params["page_size"] == 10
