from typing import ClassVar

from _typeshed import Incomplete
from flext_core import FlextBaseConfigModel, FlextResult, FlextSettings as FlextSettings

from flext_api.constants import FlextApiConstants as FlextApiConstants
from flext_api.typings import FlextTypes as FlextTypes

class FlextApiSettings(FlextBaseConfigModel):
    api_host: str
    api_port: int
    api_workers: int
    default_timeout: int
    max_retries: int
    enable_caching: bool
    cache_ttl: int
    database_url: str | None
    database_pool_size: int
    database_timeout: int
    external_api_timeout: int
    external_api_retries: int
    secret_key: str | None
    jwt_expiry: int
    cors_origins: list[str]
    environment: str
    debug: bool
    log_level: str
    model_config: ClassVar[Incomplete]
    @classmethod
    def validate_port(cls, v: int) -> int: ...
    @classmethod
    def validate_environment(cls, v: str) -> str: ...
    @classmethod
    def validate_log_level(cls, v: str) -> str: ...
    def validate_business_rules(self) -> FlextResult[None]: ...
    @classmethod
    def create_with_validation(
        cls, overrides: FlextTypes.Core.JsonDict | None = None, **kwargs: object
    ) -> FlextResult[FlextSettings]: ...

def create_api_settings(**overrides: object) -> FlextResult[FlextApiSettings]: ...
def load_configuration(
    environment: str = "development",
) -> FlextResult[FlextApiSettings]: ...
def validate_configuration(settings: FlextApiSettings) -> FlextResult[None]: ...
