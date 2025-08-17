import pytest
from flext_core import FlextResult

class BeforePluginPass:
    name: str
    enabled: bool
    async def before_request(
        self, request: object, _context: object | None = None
    ) -> FlextResult[object] | object: ...

class BeforePluginFail:
    name: str
    enabled: bool
    async def before_request(
        self, _request: object, _context: object | None = None
    ) -> FlextResult[object]: ...

class AfterPluginFail:
    name: str
    enabled: bool
    async def after_response(
        self, _response: object, _context: object | None = None
    ) -> FlextResult[object]: ...

@pytest.mark.asyncio
async def test_prepare_request_params_and_headers_merge() -> None: ...
@pytest.mark.asyncio
async def test_plugin_before_failure_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_plugin_before_replace_request_and_after_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_format_request_error_and_legacy_make_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_response_pipeline_parse_json_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_head_and_options_methods(monkeypatch: pytest.MonkeyPatch) -> None: ...
def test_create_client_invalid_url_raises() -> None: ...
