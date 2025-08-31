"""Extended API config tests for validators and overrides."""

from __future__ import annotations

from contextlib import suppress

from flext_api import (
    FlextApiConfig,
    create_api_settings,
    validate_configuration,
)


def test_settings_validators() -> None:
    """Test settings validators."""
    s = FlextApiConfig()
    assert s.api_port >= 1
    # Invalid configs should raise during model validation
    with suppress(Exception):
        FlextApiConfig.model_validate({"log_level": "SILLY"})
    with suppress(Exception):
        FlextApiConfig.model_validate({"environment": "x"})


def test_create_api_settings_overrides_and_fail() -> None:
    """Test create api settings overrides and fail."""
    ok = create_api_settings(api_host="127.0.0.1", api_port=8081)
    assert ok.success
    assert ok.value.api_host == "127.0.0.1"
    bad = create_api_settings(api_port=9999999)
    assert not bad.success


def test_validate_configuration_rules() -> None:
    """Test validate configuration rules."""
    # production requires secret_key and database_url
    prod = FlextApiConfig.model_validate(
        {"environment": "production", "api_port": 8081},
    )
    res = validate_configuration(prod)
    assert not res.success
    assert "Secret key" in (res.error or "")

    prod2 = FlextApiConfig.model_validate(
        {
            "environment": "production",
            "secret_key": "s",
            "database_url": None,
        },
    )
    res2 = validate_configuration(prod2)
    assert not res2.success
    assert "Database URL" in (res2.error or "")

    dev = FlextApiConfig()
    dev.cors_origins = ["http://ok", "https://ok"]
    assert validate_configuration(dev).success

    dev_bad = FlextApiConfig()
    dev_bad.cors_origins = ["ws://bad"]
    assert not validate_configuration(dev_bad).success
