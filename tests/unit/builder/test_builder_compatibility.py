"""Test builder compatibility module coverage."""

from __future__ import annotations


def test_builder_module_imports() -> None:
    """Test all imports from builder module work correctly."""
    from flext_api.builder import (
        FlextApiBuilder,
        FlextApiQuery,
        FlextApiQueryBuilder,
        FlextApiResponse,
        FlextApiResponseBuilder,
        PaginatedResponseBuilder,
        PaginationConfig,
        ResponseConfig,
        build_error_response_object,
        build_paginated_response_object,
        build_query,
        build_success_response_object,
    )

    # Verify all classes and functions are importable
    assert FlextApiBuilder is not None
    assert FlextApiQuery is not None
    assert FlextApiQueryBuilder is not None
    assert FlextApiResponse is not None
    assert FlextApiResponseBuilder is not None
    assert PaginatedResponseBuilder is not None
    assert PaginationConfig is not None
    assert ResponseConfig is not None
    assert build_error_response_object is not None
    assert build_paginated_response_object is not None
    assert build_query is not None
    assert build_success_response_object is not None


def test_builder_compatibility_aliases() -> None:
    """Test compatibility aliases work correctly."""
    from flext_api.builder import (
        build_error_response_object,
        build_paginated_response_object,
        build_success_response_object,
    )
    from flext_api.client import (
        build_error_response,
        build_paginated_response,
        build_success_response,
    )

    # Verify aliases point to the correct functions
    assert build_success_response_object is build_success_response
    assert build_error_response_object is build_error_response
    assert build_paginated_response_object is build_paginated_response


def test_builder_module_all_exports() -> None:
    """Test __all__ exports are complete."""
    import flext_api.builder as builder_module

    expected_exports = {
        "FlextApiBuilder",
        "FlextApiQuery",
        "FlextApiQueryBuilder",
        "FlextApiResponse",
        "FlextApiResponseBuilder",
        "PaginatedResponseBuilder",
        "PaginationConfig",
        "ResponseConfig",
        "build_error_response_object",
        "build_paginated_response_object",
        "build_query",
        "build_success_response_object",
    }

    assert hasattr(builder_module, "__all__")
    actual_exports = set(builder_module.__all__)
    assert actual_exports == expected_exports

    # Verify all exported items are actually available
    for export_name in expected_exports:
        assert hasattr(builder_module, export_name)


def test_builder_functional_usage() -> None:
    """Test functional usage of builder components."""
    from flext_api.builder import (
        FlextApiBuilder,
        build_success_response_object,
    )

    # Test builder instantiation
    builder = FlextApiBuilder()
    assert builder is not None

    # Test query builder
    query_builder = builder.for_query()
    assert query_builder is not None

    # Test response builder
    response_builder = builder.for_response()
    assert response_builder is not None

    # Test function usage
    response = build_success_response_object({"test": "data"})
    assert response is not None
    assert response.success is True
    assert response.value == {"test": "data"}
