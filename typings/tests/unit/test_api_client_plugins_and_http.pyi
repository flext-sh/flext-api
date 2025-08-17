import pytest
from _typeshed import Incomplete
from flext_core import FlextResult

from flext_api import FlextApiClientRequest, FlextApiClientResponse

class _CM:
    def __init__(self, resp: _FakeResponse) -> None: ...
    async def __aenter__(self) -> _FakeResponse: ...
    async def __aexit__(self, *_args: object, **_kwargs: object) -> None: ...

class _FakeResponse:
    status: Incomplete
    headers: Incomplete
    def __init__(
        self, status: int, headers: dict[str, str], json_obj: object, text_value: str
    ) -> None: ...
    async def json(self) -> object: ...
    async def text(self) -> str: ...

class _FakeSession:
    closed: bool
    def __init__(self, resp: _FakeResponse) -> None: ...
    def request(self, *_args: object, **_kwargs: object) -> _CM: ...
    async def close(self) -> None: ...

@pytest.mark.asyncio
async def test_perform_http_request_success_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_perform_http_request_text_jsonlike(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...

class _PluginFail:
    enabled: bool
    async def before_request(
        self, _request: object, _context: object = None
    ) -> FlextResult[object]: ...

class _PluginModify:
    enabled: bool
    async def before_request(
        self, request: FlextApiClientRequest, _context: object = None
    ) -> FlextApiClientRequest: ...

class _PluginAfterFail:
    enabled: bool
    async def after_response(
        self, _response: object, _context: object = None
    ) -> FlextResult[object]: ...

class _PluginAfterModify:
    enabled: bool
    async def after_response(
        self, response: FlextApiClientResponse, _context: object = None
    ) -> FlextResult[object]: ...

@pytest.mark.asyncio
async def test_plugins_before_and_after_paths() -> None: ...
def test_format_request_error_variants() -> None: ...
@pytest.mark.asyncio
async def test_build_stub_response_variants() -> None: ...
