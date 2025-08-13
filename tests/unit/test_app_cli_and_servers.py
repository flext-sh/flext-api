"""Tests for CLI entrypoints and server runners in flext_api.api_app."""

from __future__ import annotations

from typing import Any

import pytest
from flext_core import FlextResult

from flext_api import api_app as api_app_module


def test_run_development_server_invokes_uvicorn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ensure development server calls uvicorn.run with factory flag."""
    calls: list[dict[str, Any]] = []

    def fake_run(*args: Any, **kwargs: Any) -> None:  # uvicorn.run
        calls.append({"args": args, "kwargs": kwargs})

    monkeypatch.setattr(
        api_app_module,
        "uvicorn",
        type("_U", (), {"run": staticmethod(fake_run)}),
    )

    # Should not raise and must call uvicorn.run with factory path
    api_app_module.run_development_server(
        host="127.0.0.1",
        port=8081,
        reload=False,
        log_level="warning",
    )
    assert calls, "uvicorn.run was not called"
    assert calls[0]["kwargs"]["factory"] is True


def test_run_production_server_invokes_uvicorn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure production server passes explicit host/port to uvicorn.run."""
    calls: list[dict[str, Any]] = []

    def fake_run(*args: Any, **kwargs: Any) -> None:  # uvicorn.run
        calls.append({"args": args, "kwargs": kwargs})

    monkeypatch.setattr(
        api_app_module,
        "uvicorn",
        type("_U", (), {"run": staticmethod(fake_run)}),
    )

    # Force specific host/port
    api_app_module.run_production_server(host="127.0.0.1", port=8082)
    assert calls, "uvicorn.run was not called in production"
    assert calls[0]["kwargs"]["host"] == "127.0.0.1"
    assert calls[0]["kwargs"]["port"] == 8082


def test_create_flext_api_app_with_settings_success() -> None:
    """App factory with debug flag returns app with state config."""
    app = api_app_module.create_flext_api_app_with_settings(debug=True)
    assert hasattr(app.state, "config")


def test_create_flext_api_app_with_settings_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When settings creation fails, the wrapper raises RuntimeError."""

    def fake_create_api_settings(**_: Any) -> FlextResult[object]:
        return FlextResult.fail("boom")

    monkeypatch.setattr(api_app_module, "create_api_settings", fake_create_api_settings)

    with pytest.raises(RuntimeError):
        _ = api_app_module.create_flext_api_app_with_settings(debug=True)


def test_main_entrypoint_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    """Smoke test for main entrypoint wiring and uvicorn invocation."""
    calls: list[dict[str, Any]] = []

    def fake_run(*args: Any, **kwargs: Any) -> None:
        calls.append({"args": args, "kwargs": kwargs})

    monkeypatch.setattr(
        api_app_module,
        "uvicorn",
        type("_U", (), {"run": staticmethod(fake_run)}),
    )
    monkeypatch.setenv("PYTEST_RUNNING", "1")
    # Simula execução de main com args
    monkeypatch.setattr(
        "sys.argv",
        ["prog", "--host", "127.0.0.1", "--port", "8090", "--log-level", "warning"],
        raising=False,
    )
    api_app_module.main()
    assert calls, "main did not call uvicorn.run"
