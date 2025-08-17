import pytest

@pytest.mark.asyncio
async def test_read_response_data_parse_errors() -> None: ...
@pytest.mark.asyncio
async def test_prepare_headers_merge_and_request_build() -> None: ...
@pytest.mark.asyncio
async def test_execute_request_pipeline_empty_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
