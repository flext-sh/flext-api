from _typeshed import Incomplete
from flext_core.constants import FlextConstants

__all__ = [
    "FLEXT_API_CACHE_TTL",
    "FLEXT_API_MAX_RETRIES",
    "FLEXT_API_TIMEOUT",
    "FLEXT_API_VERSION",
    "FlextApiConstants",
    "FlextApiEndpoints",
    "FlextApiFieldType",
    "FlextApiStatus",
]

FlextApiConstants = FlextConstants

class FlextApiStatus:
    PENDING: str
    PROCESSING: str
    COMPLETED: str
    FAILED: str
    CANCELLED: str
    HEALTHY: str
    DEGRADED: str
    UNHEALTHY: str
    MAINTENANCE: str
    PIPELINE_IDLE: str
    PIPELINE_RUNNING: str
    PIPELINE_SUCCESS: str
    PIPELINE_ERROR: str
    PIPELINE_TIMEOUT: str
    PLUGIN_LOADED: str
    PLUGIN_ACTIVE: str
    PLUGIN_INACTIVE: str
    PLUGIN_ERROR: str

class FlextApiFieldType:
    API_KEY: str
    BEARER_TOKEN: str
    PIPELINE_CONFIG: str
    PLUGIN_CONFIG: str
    USER_ROLE: str
    ENDPOINT_PATH: str
    HTTP_METHOD: str
    RESPONSE_FORMAT: str

class FlextApiEndpoints:
    API_V1: str
    HEALTH: str
    METRICS: str
    DOCS: str
    AUTH_LOGIN: Incomplete
    AUTH_LOGOUT: Incomplete
    AUTH_REFRESH: Incomplete
    AUTH_VERIFY: Incomplete
    PIPELINES: Incomplete
    PIPELINE_RUN: Incomplete
    PIPELINE_STATUS: Incomplete
    PIPELINE_LOGS: Incomplete
    PLUGINS: Incomplete
    PLUGIN_INSTALL: Incomplete
    PLUGIN_UNINSTALL: Incomplete
    PLUGIN_CONFIG: Incomplete

FLEXT_API_VERSION: str
FLEXT_API_TIMEOUT: int
FLEXT_API_MAX_RETRIES: int
FLEXT_API_CACHE_TTL: int

class Validation:
    MAX_REQUEST_SIZE: int
    MAX_RESPONSE_SIZE: int
    MIN_PORT: int
    MAX_PORT: int
    MAX_URL_LENGTH: int
    MAX_HEADER_SIZE: int
    MAX_ERROR_VALUE_LENGTH: int

class Auth:
    JWT_PARTS_COUNT: int
    JWT_SEPARATOR_COUNT: int
    MIN_TOKEN_LENGTH: int

class Connection:
    POOL_SIZE: int
    MAX_CONNECTIONS: int
    KEEP_ALIVE_TIMEOUT: int
    IDLE_TIMEOUT: int

class Performance:
    SLOW_REQUEST_THRESHOLD: float
    CRITICAL_LATENCY_THRESHOLD: float
    MONITORING_SAMPLE_RATE: float
