import pytest

@pytest.mark.asyncio
async def test_offline_stub_and_error_formatting(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
@pytest.mark.asyncio
async def test_read_response_data_fallbacks(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
