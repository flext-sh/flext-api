from _typeshed import Incomplete
from fastapi import FastAPI

from flext_api.api_config import FlextApiSettings
from flext_api.api_storage import FlextApiStorage

__all__ = [
    "app",
    "create_flext_api_app",
    "run_development_server",
    "run_production_server",
    "storage",
]

class FlextApiAppConfig:
    settings: Incomplete
    storage: FlextApiStorage | None
    def __init__(self, settings: FlextApiSettings | None = None) -> None: ...
    def get_cors_origins(self) -> list[str]: ...
    def get_title(self) -> str: ...
    def get_description(self) -> str: ...
    def get_version(self) -> str: ...

class FlextApiHealthChecker:
    config: Incomplete
    def __init__(self, config: FlextApiAppConfig) -> None: ...
    async def comprehensive_health_check(self, app: FastAPI) -> dict[str, object]: ...
    def liveness_check(self) -> dict[str, object]: ...
    def readiness_check(self, app: FastAPI) -> dict[str, object]: ...

def create_flext_api_app(config: FlextApiAppConfig | None = None) -> FastAPI: ...
def create_flext_api_app_with_settings(
    settings: FlextApiAppConfig | None = None,
) -> FastAPI: ...
def run_development_server(
    host: str = "127.0.0.1",
    port: int | None = None,
    *,
    reload: bool = True,
    log_level: str = "info",
) -> None: ...
def run_production_server(host: str | None = None, port: int | None = None) -> None: ...

app: Incomplete
storage: Incomplete
