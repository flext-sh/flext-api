from __future__ import annotations

from flext_api.api_types import get_api_types


def test_get_api_types_contains_expected_keys() -> None:
    t = get_api_types()
    assert "Method" in t
    assert "Headers" in t
    assert "JSONData" in t
