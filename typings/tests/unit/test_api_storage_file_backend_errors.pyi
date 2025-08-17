import pytest

@pytest.mark.asyncio
async def test_file_backend_save_and_delete_error_paths(
    tmp_path: object, monkeypatch: pytest.MonkeyPatch
) -> None: ...
