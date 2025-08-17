import pytest

@pytest.mark.asyncio
async def test_request_build_failure_and_pipeline_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None: ...
