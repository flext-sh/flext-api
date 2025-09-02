"""FLEXT API Configuration - Configuration management following FLEXT patterns.

HTTP-specific configuration system providing FlextApiConfig class with settings
management, validation, and FlextResult integration for type-safe configuration.

Module Role in Architecture:
    FlextApiConfig serves as the HTTP API configuration system, providing centralized
    configuration management, environment variable handling, validation patterns,
    and settings distribution following Pydantic patterns.

Classes and Methods:
    FlextApiConfig:                         # Hierarchical HTTP API configuration system
        # Server Configuration:
        ServerConfig(BaseConfig)            # HTTP server settings
        ClientConfig(BaseConfig)            # HTTP client settings
        SecurityConfig(BaseConfig)          # CORS and security settings

        # Environment Handling:
        EnvConfig(BaseConfig)               # Environment variable mapping

        # Factory Methods:
        create_server_config() -> FlextResult[ServerConfig]
        create_client_config() -> FlextResult[ClientConfig]
        create_security_config() -> FlextResult[SecurityConfig]

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_core import FlextLogger, FlextModels, FlextResult
from pydantic import Field, field_validator

from flext_api.constants import FlextApiConstants

logger = FlextLogger(__name__)


class FlextApiConfig(FlextModels.BaseConfig):
    """Single consolidated class containing ALL HTTP API configuration management.

    This is the ONLY configuration class in this module, containing all HTTP API
    configuration classes as nested classes. Follows the single-class-per-module
    pattern rigorously.
    """

    class ServerConfig(FlextModels.BaseConfig):
        """HTTP server configuration with validation."""

        host: str = Field(default="127.0.0.1", description="Server host address")
        port: int = Field(default=8000, ge=1, le=65535, description="Server port")
        workers: int = Field(default=1, ge=1, description="Number of worker processes")
        debug: bool = Field(default=False, description="Debug mode")
        reload: bool = Field(default=False, description="Auto-reload on code changes")
        access_log: bool = Field(default=True, description="Enable access logging")

        @field_validator("host")
        @classmethod
        def validate_host(cls, v: str) -> str:
            """Validate host address."""
            if not v or not v.strip():
                msg = "Host cannot be empty"
                raise ValueError(msg)
            return v.strip()

        @field_validator("workers")
        @classmethod
        def validate_workers(cls, v: int) -> int:
            """Validate worker count."""
            if v < 1:
                msg = "Workers must be at least 1"
                raise ValueError(msg)
            if v > FlextApiConstants.Server.MAX_WORKERS:
                msg = f"Workers cannot exceed {FlextApiConstants.Server.MAX_WORKERS}"
                raise ValueError(msg)
            return v

        def to_uvicorn_config(self) -> FlextResult[dict[str, object]]:
            """Convert to Uvicorn server configuration."""
            try:
                config = {
                    "host": self.host,
                    "port": self.port,
                    "workers": self.workers,
                    "reload": self.reload,
                    "access_log": self.access_log,
                    "log_level": "debug" if self.debug else "info",
                }
                return FlextResult[dict[str, object]].ok(config)
            except Exception as e:
                logger.exception("Failed to create Uvicorn config", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Failed to create Uvicorn config: {e}"
                )

    class ClientConfig(FlextModels.BaseConfig):
        """HTTP client configuration with validation."""

        base_url: str = Field(
            default="http://localhost:8000", description="Default base URL for clients"
        )
        timeout: float = Field(
            default=FlextApiConstants.Http.DEFAULT_TIMEOUT,
            gt=0,
            description="Default HTTP timeout in seconds",
        )
        max_retries: int = Field(
            default=FlextApiConstants.Client.DEFAULT_MAX_RETRIES,
            ge=0,
            description="Maximum retry attempts",
        )
        verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
        follow_redirects: bool = Field(
            default=True, description="Follow HTTP redirects"
        )
        max_redirects: int = Field(
            default=FlextApiConstants.Http.MAX_REDIRECTS,
            ge=0,
            description="Maximum redirect follows",
        )
        user_agent: str = Field(
            default=FlextApiConstants.Http.USER_AGENT,
            description="HTTP User-Agent header",
        )
        headers: dict[str, str] = Field(
            default_factory=FlextApiConstants.Client.DEFAULT_HEADERS.copy,
            description="Default HTTP headers",
        )

        @field_validator("base_url")
        @classmethod
        def validate_base_url(cls, v: str) -> str:
            """Validate base URL format."""
            if not v or not v.strip():
                msg = "Base URL cannot be empty"
                raise ValueError(msg)

            v = v.strip()
            if not v.startswith(("http://", "https://")):
                msg = "Base URL must start with http:// or https://"
                raise ValueError(msg)

            # Remove trailing slash for consistency
            return v.rstrip("/")

        @field_validator("timeout")
        @classmethod
        def validate_timeout(cls, v: float) -> float:
            """Validate timeout value."""
            if v <= 0:
                msg = "Timeout must be positive"
                raise ValueError(msg)
            if v > FlextApiConstants.HttpValidation.MAX_TIMEOUT:
                msg = f"Timeout cannot exceed {FlextApiConstants.HttpValidation.MAX_TIMEOUT}"
                raise ValueError(msg)
            return v

        def to_httpx_config(self) -> FlextResult[dict[str, object]]:
            """Convert to HTTPX client configuration."""
            try:
                config = {
                    "base_url": self.base_url,
                    "timeout": self.timeout,
                    "verify": self.verify_ssl,
                    "follow_redirects": self.follow_redirects,
                    "headers": self.headers.copy(),
                }
                return FlextResult[dict[str, object]].ok(config)
            except Exception as e:
                logger.exception("Failed to create HTTPX config", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Failed to create HTTPX config: {e}"
                )

    class SecurityConfig(FlextModels.BaseConfig):
        """HTTP security and CORS configuration."""

        cors_enabled: bool = Field(default=True, description="Enable CORS middleware")
        cors_origins: list[str] = Field(
            default_factory=lambda: ["*"], description="CORS allowed origins"
        )
        cors_methods: list[str] = Field(
            default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            description="CORS allowed methods",
        )
        cors_headers: list[str] = Field(
            default_factory=lambda: ["*"], description="CORS allowed headers"
        )
        cors_credentials: bool = Field(
            default=True, description="CORS allow credentials"
        )
        max_age: int = Field(
            default=FlextApiConstants.Security.CORS_MAX_AGE,
            description="CORS preflight max age",
        )

        # Security headers
        security_headers_enabled: bool = Field(
            default=True, description="Enable security headers"
        )
        hsts_enabled: bool = Field(
            default=True, description="Enable HTTP Strict Transport Security"
        )
        frame_options_deny: bool = Field(
            default=True, description="Set X-Frame-Options to DENY"
        )

        @field_validator("cors_origins")
        @classmethod
        def validate_cors_origins(cls, v: list[str]) -> list[str]:
            """Validate CORS origins."""
            if not v:
                return ["*"]

            # Validate each origin
            validated = []
            for origin in v:
                if origin == "*":
                    validated.append(origin)
                elif origin.startswith(("http://", "https://")):
                    validated.append(origin.rstrip("/"))
                else:
                    msg = f"Invalid CORS origin format: {origin}"
                    raise ValueError(msg)

            return validated

        def to_cors_config(self) -> FlextResult[dict[str, object]]:
            """Convert to FastAPI CORS configuration."""
            try:
                config = {
                    "allow_origins": self.cors_origins,
                    "allow_methods": self.cors_methods,
                    "allow_headers": self.cors_headers,
                    "allow_credentials": self.cors_credentials,
                    "max_age": self.max_age,
                }
                return FlextResult[dict[str, object]].ok(config)
            except Exception as e:
                logger.exception("Failed to create CORS config", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Failed to create CORS config: {e}"
                )

    class EnvConfig(FlextModels.BaseConfig):
        """Environment variable configuration mapping."""

        # Server environment variables
        server_host: str = Field(
            default="127.0.0.1",
            description="Server host from env",
            validation_alias="FLEXT_API_HOST",
        )
        server_port: int = Field(
            default=8000,
            description="Server port from env",
            validation_alias="FLEXT_API_PORT",
        )
        debug_mode: bool = Field(
            default=False,
            description="Debug mode from env",
            validation_alias="FLEXT_API_DEBUG",
        )

        # Client environment variables
        base_url: str = Field(
            default="http://localhost:8000",
            description="Base URL from env",
            validation_alias="FLEXT_API_BASE_URL",
        )
        timeout: float = Field(
            default=30.0,
            description="Timeout from env",
            validation_alias="FLEXT_API_TIMEOUT",
        )

        # Security environment variables
        cors_origins: str = Field(
            default="*",
            description="CORS origins (comma-separated)",
            validation_alias="FLEXT_API_CORS_ORIGINS",
        )

        def to_server_config(self) -> FlextResult[FlextApiConfig.ServerConfig]:
            """Convert environment config to server config."""
            try:
                config = FlextApiConfig.ServerConfig(
                    host=self.server_host,
                    port=self.server_port,
                    debug=self.debug_mode,
                )
                return FlextResult[FlextApiConfig.ServerConfig].ok(config)
            except Exception as e:
                logger.exception(
                    "Failed to create server config from env", error=str(e)
                )
                return FlextResult[FlextApiConfig.ServerConfig].fail(
                    f"Failed to create server config from env: {e}"
                )

        def to_client_config(self) -> FlextResult[FlextApiConfig.ClientConfig]:
            """Convert environment config to client config."""
            try:
                config = FlextApiConfig.ClientConfig(
                    base_url=self.base_url,
                    timeout=self.timeout,
                )
                return FlextResult[FlextApiConfig.ClientConfig].ok(config)
            except Exception as e:
                logger.exception(
                    "Failed to create client config from env", error=str(e)
                )
                return FlextResult[FlextApiConfig.ClientConfig].fail(
                    f"Failed to create client config from env: {e}"
                )

        def to_security_config(self) -> FlextResult[FlextApiConfig.SecurityConfig]:
            """Convert environment config to security config."""
            try:
                # Parse comma-separated CORS origins
                origins = [
                    origin.strip()
                    for origin in self.cors_origins.split(",")
                    if origin.strip()
                ]
                if not origins:
                    origins = ["*"]

                config = FlextApiConfig.SecurityConfig(
                    cors_origins=origins,
                )
                return FlextResult[FlextApiConfig.SecurityConfig].ok(config)
            except Exception as e:
                logger.exception(
                    "Failed to create security config from env", error=str(e)
                )
                return FlextResult[FlextApiConfig.SecurityConfig].fail(
                    f"Failed to create security config from env: {e}"
                )

    class MainConfig(FlextModels.BaseConfig):
        """Main configuration combining all config types."""

        server: FlextApiConfig.ServerConfig = Field(
            default_factory=FlextApiConfig.ServerConfig
        )
        client: FlextApiConfig.ClientConfig = Field(
            default_factory=FlextApiConfig.ClientConfig
        )
        security: FlextApiConfig.SecurityConfig = Field(
            default_factory=FlextApiConfig.SecurityConfig
        )

        def create_complete_config(
            self,
        ) -> FlextResult[dict[str, object]]:
            """Create complete configuration dictionary."""
            try:
                server_result = self.server.to_uvicorn_config()
                if not server_result.success:
                    return FlextResult[dict[str, object]].fail(
                        f"Server config failed: {server_result.error}"
                    )

                client_result = self.client.to_httpx_config()
                if not client_result.success:
                    return FlextResult[dict[str, object]].fail(
                        f"Client config failed: {client_result.error}"
                    )

                security_result = self.security.to_cors_config()
                if not security_result.success:
                    return FlextResult[dict[str, object]].fail(
                        f"Security config failed: {security_result.error}"
                    )

                complete_config: dict[str, object] = {
                    "server": server_result.value,
                    "client": client_result.value,
                    "security": security_result.value,
                }

                return FlextResult[dict[str, object]].ok(complete_config)

            except Exception as e:
                logger.exception("Failed to create complete config", error=str(e))
                return FlextResult[dict[str, object]].fail(
                    f"Failed to create complete config: {e}"
                )


# Factory functions following FlextResult patterns
def create_server_config(**kwargs: object) -> FlextResult[FlextApiConfig.ServerConfig]:
    """Create server configuration with validation."""
    try:
        # Filter kwargs to compatible types for ServerConfig
        compatible_kwargs = {
            k: v
            for k, v in kwargs.items()
            if isinstance(v, (str, int, bool, type(None)))
            or (
                isinstance(v, (list, tuple)) and k in {"template_dirs", "allowed_hosts"}
            )
        }
        config = FlextApiConfig.ServerConfig.model_validate(compatible_kwargs)
        return FlextResult["FlextApiConfig.ServerConfig"].ok(config)
    except Exception as e:
        logger.exception("Failed to create server config", error=str(e))
        return FlextResult["FlextApiConfig.ServerConfig"].fail(
            f"Failed to create server config: {e}"
        )


def create_client_config(**kwargs: object) -> FlextResult[FlextApiConfig.ClientConfig]:
    """Create client configuration with validation."""
    try:
        # Filter kwargs to compatible types for ClientConfig
        compatible_kwargs = {
            k: v
            for k, v in kwargs.items()
            if isinstance(v, (str, int, float, bool, dict, type(None)))
        }
        config = FlextApiConfig.ClientConfig.model_validate(compatible_kwargs)
        return FlextResult["FlextApiConfig.ClientConfig"].ok(config)
    except Exception as e:
        logger.exception("Failed to create client config", error=str(e))
        return FlextResult["FlextApiConfig.ClientConfig"].fail(
            f"Failed to create client config: {e}"
        )


def create_security_config(
    **kwargs: object,
) -> FlextResult[FlextApiConfig.SecurityConfig]:
    """Create security configuration with validation."""
    try:
        # Filter kwargs to compatible types for SecurityConfig
        compatible_kwargs = {
            k: v
            for k, v in kwargs.items()
            if isinstance(v, (str, int, bool, list, type(None)))
        }
        config = FlextApiConfig.SecurityConfig.model_validate(compatible_kwargs)
        return FlextResult["FlextApiConfig.SecurityConfig"].ok(config)
    except Exception as e:
        logger.exception("Failed to create security config", error=str(e))
        return FlextResult["FlextApiConfig.SecurityConfig"].fail(
            f"Failed to create security config: {e}"
        )


def create_main_config(**kwargs: object) -> FlextResult[FlextApiConfig.MainConfig]:
    """Create main configuration with validation."""
    try:
        # Filter kwargs to compatible types for MainConfig
        # MainConfig expects nested config objects, so we skip filtering for now
        # and let Pydantic handle the validation
        config = FlextApiConfig.MainConfig.model_validate(kwargs)
        return FlextResult["FlextApiConfig.MainConfig"].ok(config)
    except Exception as e:
        logger.exception("Failed to create main config", error=str(e))
        return FlextResult["FlextApiConfig.MainConfig"].fail(
            f"Failed to create main config: {e}"
        )


def load_from_env() -> FlextResult[FlextApiConfig.MainConfig]:
    """Load configuration from environment variables."""
    try:
        env_config = FlextApiConfig.EnvConfig()

        server_result = env_config.to_server_config()
        if not server_result.success:
            return FlextResult["FlextApiConfig.MainConfig"].fail(
                f"Server config from env failed: {server_result.error}"
            )

        client_result = env_config.to_client_config()
        if not client_result.success:
            return FlextResult["FlextApiConfig.MainConfig"].fail(
                f"Client config from env failed: {client_result.error}"
            )

        security_result = env_config.to_security_config()
        if not security_result.success:
            return FlextResult["FlextApiConfig.MainConfig"].fail(
                f"Security config from env failed: {security_result.error}"
            )

        main_config = FlextApiConfig.MainConfig(
            server=server_result.value,
            client=client_result.value,
            security=security_result.value,
        )

        return FlextResult["FlextApiConfig.MainConfig"].ok(main_config)

    except Exception as e:
        logger.exception("Failed to load config from environment", error=str(e))
        return FlextResult["FlextApiConfig.MainConfig"].fail(
            f"Failed to load config from environment: {e}"
        )


__all__ = ["FlextApiConfig"]
