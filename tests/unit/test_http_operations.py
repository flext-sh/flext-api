"""Tests for FlextAPI HTTP operations."""

from __future__ import annotations

import pytest

from flext_api.http_operations import FlextApiOperations


class TestFlextApiOperations:
    """Test FlextApiOperations functionality."""

    def test_execute_get_raises_not_implemented(self) -> None:
        """Test that execute_get raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_get"
        ):
            FlextApiOperations.execute_get("https://api.example.com/users")

    def test_execute_get_with_params(self) -> None:
        """Test that execute_get with params raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_get"
        ):
            FlextApiOperations.execute_get(
                "https://api.example.com/users",
                params={"page": "1", "limit": "10"},
                headers={"Accept": "application/json"},
                timeout=30.0,
            )

    def test_execute_post_raises_not_implemented(self) -> None:
        """Test that execute_post raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_post"
        ):
            FlextApiOperations.execute_post("https://api.example.com/users")

    def test_execute_post_with_data(self) -> None:
        """Test that execute_post with data raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_post"
        ):
            FlextApiOperations.execute_post(
                "https://api.example.com/users",
                json_data={"name": "John", "email": "john@example.com"},
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )

    def test_execute_put_raises_not_implemented(self) -> None:
        """Test that execute_put raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_put"
        ):
            FlextApiOperations.execute_put("https://api.example.com/users/1")

    def test_execute_put_with_data(self) -> None:
        """Test that execute_put with data raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_put"
        ):
            FlextApiOperations.execute_put(
                "https://api.example.com/users/1",
                json_data={"name": "Jane", "email": "jane@example.com"},
                timeout=30.0,
            )

    def test_execute_delete_raises_not_implemented(self) -> None:
        """Test that execute_delete raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_delete"
        ):
            FlextApiOperations.execute_delete("https://api.example.com/users/1")

    def test_execute_delete_with_params(self) -> None:
        """Test that execute_delete with params raises NotImplementedError."""
        with pytest.raises(
            NotImplementedError, match="HTTP client must implement execute_delete"
        ):
            FlextApiOperations.execute_delete(
                "https://api.example.com/users/1",
                params={"force": "true"},
                headers={"Authorization": "Bearer token"},
                timeout=15.0,
            )
