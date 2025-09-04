"""Advanced App test factories using Pydantic V2 Builder Pattern.

Provides zero-parameter factory builders eliminating ALL parameter complexity.
Follows flext-core patterns with advanced Pydantic V2 and Python 3.13 features.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from flext_api import FlextApiApp
from flext_api.config import FlextApiConfig


class FlextApiAppBuilder(BaseModel):
    """Advanced Pydantic V2 builder for FlextApiApp - eliminates ALL parameters."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Mutable for builder pattern
        arbitrary_types_allowed=True,
    )

    settings: FlextApiConfig | None = Field(default=None, description="API settings")

    def build(self) -> FlextApiApp:
        """Build FlextApiApp using current configuration."""
        return FlextApiApp(settings=self.settings)

    def with_settings(self, settings: FlextApiConfig | None) -> FlextApiAppBuilder:
        self.settings = settings
        return self


def create_flext_api_app_config(
    settings: object | None = None,
) -> FlextApiApp:
    """Create FlextApiApp for testing - BACKWARD COMPATIBILITY."""
    api_settings = settings if isinstance(settings, FlextApiConfig) else None
    return FlextApiAppBuilder().with_settings(api_settings).build()


# =============================================================================
# MODERN BUILDER INTERFACE - ZERO PARAMETER COMPLEXITY
# =============================================================================

# Modern builder factories - PREFERRED usage (will be defined after classes)
# FastApiApp = FastApiAppBuilder  # Use: FastApiApp().with_title("My API").build()
# FlextApp = FlextApiAppBuilder  # Use: FlextApp().with_settings(config).build()

# Legacy function aliases for backward compatibility
FlextApiAppFactory = create_flext_api_app_config

# Export all modern builders
__all__ = [
    "FastApiApp",  # Alias for FastApiAppBuilder
    # Modern Builder Pattern (PREFERRED)
    "FastApiAppBuilder",
    "FastApiFactory",
    "FlextApiAppBuilder",
    "FlextApiAppFactory",
    "FlextApp",  # Alias for FlextApiAppBuilder
    # Legacy compatibility functions
    "create_fastapi_application",
    "create_flext_api_app_config",
]


# =============================================================================
# ADVANCED PYDANTIC V2 BUILDER PATTERN - ZERO PARAMETER COMPLEXITY
# =============================================================================


class FastApiAppBuilder(BaseModel):
    """Advanced Pydantic V2 builder for FastAPI - eliminates ALL parameters."""

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,  # Mutable for builder pattern
        arbitrary_types_allowed=True,
    )

    title: str = Field(default="Test FLEXT API", description="Application title")
    description: str = Field(
        default="Test API Description", description="Application description"
    )
    version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=True, description="Debug mode")
    docs_url: str = Field(default="/docs", description="Documentation URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI JSON URL")

    def build(self) -> FastAPI:
        """Build FastAPI application using current configuration."""
        return FastAPI(
            title=self.title,
            description=self.description,
            version=self.version,
            debug=self.debug,
            docs_url=self.docs_url,
            redoc_url=self.redoc_url,
            openapi_url=self.openapi_url,
        )

    # Fluent interface methods
    def with_title(self, title: str) -> FastApiAppBuilder:
        self.title = title
        return self

    def with_description(self, description: str) -> FastApiAppBuilder:
        self.description = description
        return self

    def with_version(self, version: str) -> FastApiAppBuilder:
        self.version = version
        return self

    def with_debug(self, debug: bool) -> FastApiAppBuilder:
        self.debug = debug
        return self

    def with_urls(
        self,
        docs_url: str = "/docs",
        redoc_url: str = "/redoc",
        openapi_url: str = "/openapi.json",
    ) -> FastApiAppBuilder:
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.openapi_url = openapi_url
        return self


def create_fastapi_application(
    title: str = "Test FLEXT API",
    description: str = "Test API Description",
    version: str = "0.1.0",
    *,
    debug: bool = True,
    docs_url: str = "/docs",
    redoc_url: str = "/redoc",
    openapi_url: str = "/openapi.json",
) -> FastAPI:
    """Create FastAPI application for testing - BACKWARD COMPATIBILITY."""
    return (
        FastApiAppBuilder()
        .with_title(title)
        .with_description(description)
        .with_version(version)
        .with_debug(debug)
        .with_urls(docs_url, redoc_url, openapi_url)
        .build()
    )


# Modern builder factories - PREFERRED usage (defined after classes)
FastApiApp = FastApiAppBuilder  # Use: FastApiApp().with_title("My API").build()
FlextApp = FlextApiAppBuilder  # Use: FlextApp().with_settings(config).build()

# Legacy function aliases for backward compatibility
FastApiFactory = create_fastapi_application

# Legacy aliases for backwards compatibility
FlextApiConfigFactory = create_flext_api_app_config
FastAPIApplicationFactory = create_fastapi_application
