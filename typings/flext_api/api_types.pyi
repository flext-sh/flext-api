from typing import ClassVar, Generic, TypeVar

from _typeshed import Incomplete
from flext_core.fields import FlextFieldCore, FlextFields

from flext_api.typings import FlextTypes

__all__ = [
    "APITypes",
    "APITypesCompat",
    "FlextAPIFieldCore",
    "FlextAPIFields",
    "FlextFieldCore",
    "FlextFields",
    "api_key_field",
    "bearer_token_field",
    "endpoint_path_field",
    "get_api_types",
    "http_method_field",
    "pipeline_config_field",
    "plugin_config_field",
    "response_format_field",
    "user_role_field",
]

_T_Response = TypeVar("_T_Response")
_T_Request = TypeVar("_T_Request")

# Publicly exported TypeVars expected by package __init__
T_Payload = _T_Response
T_Request = _T_Request
T_Response = _T_Response

type TData = dict[str, object]

class APITypes:
    Core: Incomplete

    class HTTP:
        Method = str
        Endpoint = str
        StatusCode = int
        ContentType = str

        class Request(Generic[_T_Request]): ...
        class Response(Generic[_T_Response]): ...

        type Headers = dict[str, str]
        type QueryParams = dict[str, str | list[str]]
        type PathParams = dict[str, str]

        AuthToken = str
        APIKey = str
        BearerToken = str

    class Validation:
        ErrorCode = str
        ErrorMessage = str
        ErrorDetails = FlextTypes.Core.JsonDict

        type ValidationErrors = dict[str, list[str]]
        type FieldError = dict[str, str]

    class Serialization:
        JSONData = FlextTypes.Core.JsonDict
        type JSONArray = list[object]
        JSONString = str
        SchemaVersion = str
        SchemaDefinition = FlextTypes.Core.JsonDict

class FlextAPIFieldCore:
    @classmethod
    def api_key_field(
        cls, description: str = "API key for authentication", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def bearer_token_field(
        cls, description: str = "Bearer token for authentication", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def pipeline_config_field(
        cls, description: str = "Pipeline configuration data", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def plugin_config_field(
        cls, description: str = "Plugin configuration data", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def user_role_field(
        cls, description: str = "User role for authorization", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def endpoint_path_field(
        cls, description: str = "API endpoint path", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def http_method_field(
        cls, description: str = "HTTP method", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...
    @classmethod
    def response_format_field(
        cls, description: str = "Response format type", **kwargs: object
    ) -> FlextTypes.Core.JsonDict: ...

class FlextAPIFields:
    API_KEY: Incomplete
    BEARER_TOKEN: Incomplete
    PIPELINE_CONFIG: Incomplete
    PLUGIN_CONFIG: Incomplete
    USER_ROLE: Incomplete
    ENDPOINT_PATH: Incomplete
    HTTP_METHOD: Incomplete
    RESPONSE_FORMAT: Incomplete
    USERNAME: ClassVar[FlextTypes.Core.JsonDict]
    EMAIL: ClassVar[FlextTypes.Core.JsonDict]
    PASSWORD: ClassVar[FlextTypes.Core.JsonDict]
    PIPELINE_NAME: ClassVar[FlextTypes.Core.JsonDict]
    PIPELINE_DESCRIPTION: ClassVar[FlextTypes.Core.JsonDict]
    PIPELINE_TIMEOUT: ClassVar[FlextTypes.Core.JsonDict]
    PLUGIN_ID: ClassVar[FlextTypes.Core.JsonDict]
    PLUGIN_VERSION: ClassVar[FlextTypes.Core.JsonDict]
    PLUGIN_ENABLED: ClassVar[FlextTypes.Core.JsonDict]
    SYSTEM_STATUS: ClassVar[FlextTypes.Core.JsonDict]
    LOG_LEVEL: ClassVar[FlextTypes.Core.JsonDict]
    REQUEST_ID: ClassVar[FlextTypes.Core.JsonDict]
    CORRELATION_ID: ClassVar[FlextTypes.Core.JsonDict]
    TIMESTAMP: ClassVar[FlextTypes.Core.JsonDict]

def api_key_field(
    description: str = "API key for authentication", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def bearer_token_field(
    description: str = "Bearer token for authentication", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def pipeline_config_field(
    description: str = "Pipeline configuration data", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def plugin_config_field(
    description: str = "Plugin configuration data", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def user_role_field(
    description: str = "User role for authorization", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def endpoint_path_field(
    description: str = "API endpoint path", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def http_method_field(
    description: str = "HTTP method", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...
def response_format_field(
    description: str = "Response format type", **kwargs: object
) -> FlextTypes.Core.JsonDict: ...

class APITypesCompat:
    HTTPMethod: Incomplete
    HTTPEndpoint: Incomplete
    HTTPStatusCode: Incomplete
    HTTPHeaders: Incomplete
    APIResponse = APITypes.HTTP.Response
    APIRequest = APITypes.HTTP.Request
    ValidationError: Incomplete

def get_api_types() -> FlextTypes.Core.JsonDict: ...
