from pathlib import Path

import pytest

@pytest.mark.asyncio
async def test_file_backend_load_data_failure_and_close(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None: ...
