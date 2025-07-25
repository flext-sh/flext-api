"""Tests for modern configuration module."""

from __future__ import annotations

import os
from unittest.mock import patch

from flext_api.config import (
    APISettings,
    create_development_api_config,
    create_production_api_config,
    get_api_settings,
)


class TestAPISettings:
    """Test cases for APISettings class."""

    def test_config_initialization_default(self) -> None:
        """Test configuration initialization with default values."""
        config = APISettings()

        assert config.project_name == "FLEXT API"
        assert config.project_version == "0.1.0"
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 8000
        assert config.log_level == "INFO"
        assert config.docs.description == "Enterprise Data Integration API"
        assert "postgresql://" in config.database_url
        assert "flext_api" in config.database_url
        assert config.security.secret_key == "test-secret-key-for-real-jwt"
        assert config.server.reload is True
        assert config.server.workers == 1

    @patch.dict(
        os.environ,
        {
            "FLEXT_API_API_HOST": "api.flext.com",
            "FLEXT_API_API_PORT": "443",
            "FLEXT_API_LOG_LEVEL": "ERROR",
            "FLEXT_API_DATABASE_URL": "postgresql://user:pass@localhost/flext",
            "FLEXT_API_SECRET_KEY": "production-secret",
            "FLEXT_API_RELOAD": "false",
            "FLEXT_API_API_WORKERS": "8",
        },
    )
    def test_config_initialization_from_env(self) -> None:
        """Test configuration initialization from environment variables."""
        config = APISettings()

        assert config.server.host == "api.flext.com"
        assert config.server.port == 443
        assert config.log_level == "ERROR"
        assert config.database_url == "postgresql://user:pass@localhost/flext"
        assert config.security.secret_key == "production-secret"
        assert config.server.reload is False
        assert config.server.workers == 8

    def test_config_nested_objects(self) -> None:
        """Test nested configuration objects."""
        config = APISettings()

        # Test server config
        assert config.server.host == "0.0.0.0"
        assert config.server.port == 8000
        assert config.server.workers == 1
        assert config.server.reload is True

        # Test CORS config
        assert config.cors.enabled is True
        assert config.cors.credentials is True
        assert "GET" in config.cors.methods

        # Test rate limit config
        assert config.rate_limit.enabled is True
        assert config.rate_limit.per_minute == 100

        # Test docs config
        assert config.docs.title == "FLEXT API"
        assert config.docs.version == "0.1.0"
        assert config.docs.url == "/docs"
        assert config.docs.redoc_url == "/redoc"

        # Test security config
        assert config.security.algorithm == "HS256"
        assert config.security.access_token_expire_minutes == 30

    def test_config_dependency_injection(self) -> None:
        """Test dependency injection configuration."""
        config = APISettings()

        # Should not raise any exceptions
        config.configure_dependencies(container=None)

        # Test with None container
        config.configure_dependencies(container=None)

    def test_config_validation(self) -> None:
        """Test configuration validation methods."""
        config = APISettings()

        # Should have database_url
        assert config.database_url.startswith("postgresql://")

        # Should have redis_url
        assert config.redis_url.startswith("redis://")

    def test_config_environment_detection(self) -> None:
        """Test environment detection via debug and log level."""
        config = APISettings()

        # Default configuration - debug is inherited from BaseSettings
        assert config.log_level == "INFO"

        # Environment should be development by default
        assert config.environment == "development"

        # Debug is true by default in development
        assert config.debug is True

    def test_config_feature_flags(self) -> None:
        """Test feature flag configuration through nested objects."""
        config = APISettings()

        # Test CORS enabled
        assert config.cors.enabled is True

        # Test rate limiting enabled
        assert config.rate_limit.enabled is True

    def test_get_api_settings_factory(self) -> None:
        """Test get_api_settings factory function."""
        config = get_api_settings()

        assert isinstance(config, APISettings)
        assert config.project_name == "FLEXT API"
        assert config.project_version == "0.1.0"
        assert "postgresql://" in config.database_url
        assert "flext_api" in config.database_url
        assert config.log_level == "INFO"

    def test_create_development_api_config(self) -> None:
        """Test development configuration factory."""
        config = create_development_api_config()

        assert isinstance(config, APISettings)
        assert config.project_name == "FLEXT API"
        assert config.reload is True

    def test_create_production_api_config(self) -> None:
        """Test production configuration factory."""
        config = create_production_api_config()

        assert isinstance(config, APISettings)
        assert config.project_name == "FLEXT API"
        assert config.reload is False

    @patch.dict(os.environ, {"FLEXT_API_DEBUG": "true"})
    def test_config_boolean_env_parsing_true(self) -> None:
        """Test boolean environment variable parsing for true values."""
        config = APISettings()
        assert config.debug is True

    @patch.dict(os.environ, {"FLEXT_API_DEBUG": "false"})
    def test_config_boolean_env_parsing_false(self) -> None:
        """Test boolean environment variable parsing for false values."""
        config = APISettings()
        assert config.debug is False

    def test_config_nested_env_vars(self) -> None:
        """Test nested environment variable parsing."""
        with patch.dict(
            os.environ,
            {
                "FLEXT_API_API_HOST": "test.example.com",
                "FLEXT_API_API_PORT": "9000",
                "FLEXT_API_RATE_LIMIT_ENABLED": "false",
                "FLEXT_API_RATE_LIMIT_PER_MINUTE": "50",
                "FLEXT_API_TITLE": "Test API",
            },
        ):
            config = APISettings()

            assert config.server.host == "test.example.com"
            assert config.server.port == 9000
            assert config.rate_limit.enabled is False
            assert config.rate_limit.per_minute == 50
            assert config.docs.title == "Test API"

    def test_config_value_objects_immutability(self) -> None:
        """Test that value objects maintain their structure."""
        config = APISettings()

        # Test that nested objects are properly typed
        assert hasattr(config.server, "host")
        assert hasattr(config.server, "port")
        assert hasattr(config.cors, "enabled")
        assert hasattr(config.rate_limit, "per_minute")
        assert hasattr(config.docs, "title")
        assert hasattr(config.security, "secret_key")

    def test_config_database_settings(self) -> None:
        """Test database configuration."""
        config = APISettings()

        assert "postgresql://" in config.database_url
        assert "flext_api" in config.database_url
        assert config.database_pool_size == 20
        assert config.redis_url == "redis://localhost:6379/0"

    def test_config_logging_settings(self) -> None:
        """Test logging configuration."""
        config = APISettings()

        assert config.log_level == "INFO"
        assert "%(asctime)s" in config.log_format

    def test_config_factory_env_isolation(self) -> None:
        """Test that factory functions respect environment."""
        # Test with environment variable for development
        with patch.dict(os.environ, {"FLEXT_API_SECRET_KEY": "env-secret-key"}):
            dev_config = create_development_api_config()
            assert "env-secret-key" in dev_config.security.secret_key

        # Test with environment variable for production
        with patch.dict(os.environ, {"FLEXT_API_SECRET_KEY": "prod-secret-key"}):
            prod_config = create_production_api_config()
            assert "prod-secret-key" in prod_config.security.secret_key
