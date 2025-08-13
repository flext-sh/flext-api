from __future__ import annotations

import os

import pytest

from flext_api.api_config import FlextApiSettings, create_api_settings, validate_configuration


def test_settings_validators() -> None:
    s = FlextApiSettings()
    assert s.api_port >= 1
    with pytest.raises(ValueError):
        FlextApiSettings.model_validate({"log_level": "SILLY"})
    with pytest.raises(ValueError):
        FlextApiSettings.model_validate({"environment": "x"})


def test_create_api_settings_overrides_and_fail() -> None:
    ok = create_api_settings(api_host="127.0.0.1", api_port=8081)
    assert ok.success and ok.data.api_host == "127.0.0.1"
    bad = create_api_settings(api_port=9999999)
    assert not bad.success


def test_validate_configuration_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    # production requires secret_key and database_url
    prod = FlextApiSettings.model_validate({"environment": "production", "api_port": 8081})
    res = validate_configuration(prod)
    assert not res.success and "Secret key" in (res.error or "")

    prod2 = FlextApiSettings.model_validate(
        {
            "environment": "production",
            "secret_key": "s",
            "database_url": None,
        }
    )
    res2 = validate_configuration(prod2)
    assert not res2.success and "Database URL" in (res2.error or "")

    dev = FlextApiSettings()
    dev.cors_origins = ["http://ok", "https://ok"]
    assert validate_configuration(dev).success

    dev_bad = FlextApiSettings()
    dev_bad.cors_origins = ["ws://bad"]
    assert not validate_configuration(dev_bad).success
