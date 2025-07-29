"""Tests to cover missing lines in builder.py."""

from flext_api.builder import (
    build_error_response,
    build_paginated_response,
    build_query,
    build_success_response,
)


class TestMissingBuilderCoverage:
    """Test missing coverage in builder.py."""

    def test_build_query_with_gt_operator(self) -> None:
        """Test build_query with gt operator - covers lines 337-338."""
        filters = [
            {"field": "status", "operator": "equals", "value": "active"},
            {"field": "age", "operator": "gt", "value": 18}
        ]

        query = build_query(filters)

        assert len(query.filters) == 2
        assert query.filters[0]["operator"] == "equals"
        assert query.filters[1]["operator"] == "gt"
        assert query.filters[1]["field"] == "age"
        assert query.filters[1]["value"] == 18

    def test_build_error_response_with_details(self) -> None:
        """Test build_error_response with details - covers lines 375-376."""
        details = {"field_errors": ["name is required", "email invalid"]}
        result = build_error_response("Validation failed", 400, details)

        assert result["success"] is False
        assert result["message"] == "Validation failed"
        assert "metadata" in result
        assert result["metadata"]["details"] == details

    def test_build_paginated_response_with_metadata(self) -> None:
        """Test build_paginated_response with metadata - covers lines 396-398."""
        data = [{"id": 1}, {"id": 2}]
        metadata = {"custom_field": "value", "another": 123}
        result = build_paginated_response(
            data=data,
            total=100,
            page=1,
            page_size=10,
            message="Data retrieved",
            metadata=metadata
        )

        assert result["success"] is True
        assert result["data"] == data
        assert result["metadata"]["custom_field"] == "value"
        assert result["metadata"]["another"] == 123

    def test_build_success_response_with_metadata(self) -> None:
        """Test build_success_response with metadata - covers lines 411-412."""
        data = {"result": "success"}
        metadata = {"request_id": "12345", "timestamp": "2023-01-01"}
        result = build_success_response(data, "Operation successful", metadata)

        assert result["success"] is True
        assert result["data"] == data
        assert result["metadata"]["request_id"] == "12345"
        assert result["metadata"]["timestamp"] == "2023-01-01"
