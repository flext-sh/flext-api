"""Extended tests for auth, repo, handler, and streaming base services."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import ClassVar

import pytest
from flext_core import FlextResult

from flext_api import (
    FlextApiBaseAuthService,
    FlextApiBaseHandlerService,
    FlextApiBaseRepositoryService,
    FlextApiBaseStreamingService,
)


class DummyAuth(FlextApiBaseAuthService):
    """Minimal auth service for path coverage."""

    service_name: str = "dummy-auth"

    async def _do_start(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_authenticate(
      self,
      _credentials: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
      return FlextResult.ok({"token": "t"})

    async def _do_validate_token(self, token: str) -> FlextResult[bool]:
      return FlextResult.ok(token == "valid")

    async def _do_refresh_token(self, token: str) -> FlextResult[str]:
      return FlextResult.ok(token + ".ref")


@pytest.mark.asyncio
async def test_auth_service_paths() -> None:
    """Test auth service paths."""
    # Ensure model is fully built before instantiation
    DummyAuth.model_rebuild()
    auth = DummyAuth()
    # Empty credentials -> fail
    assert not (await auth.authenticate({})).success
    # Valid credentials -> ok and session creation pass-through
    ok = await auth.authenticate({"u": 1})
    assert ok.success
    assert ok.data.get("token") == "t"
    # Token validation
    assert (await auth.validate_token("valid")).data is True
    assert (await auth.validate_token("")).data is False
    # Refresh invalid -> fail
    assert not (await auth.refresh_token("invalid")).success


class DummyRepo(FlextApiBaseRepositoryService):
    """Minimal repository service for path coverage."""

    service_name: str = "dummy-repo"
    entity_type: type = dict

    async def _do_start(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_find_by_id(self, entity_id: str) -> FlextResult[dict[str, object]]:
      return FlextResult.ok({"id": entity_id})

    async def _do_find_all(
      self,
      _filters: dict[str, object] | None,
      _limit: int | None,
      _offset: int | None,
    ) -> FlextResult[list[dict[str, object]]]:
      return FlextResult.ok([{}, {}, {}])

    async def _do_save(
      self,
      entity: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
      return FlextResult.ok(entity | {"saved": True})

    async def _do_delete(self, _entity_id: str) -> FlextResult[None]:
      return FlextResult.ok(None)


@pytest.mark.asyncio
async def test_repository_service_paths() -> None:
    """Test repository service paths."""
    repo = DummyRepo()
    assert not (await repo.find_by_id("")).success
    assert not (await repo.find_all(limit=0)).success
    assert not (await repo.find_all(offset=-1)).success
    assert (await repo.find_all()).success
    assert not (await repo.save({})).success
    assert (await repo.save({"id": 1})).success
    # delete will first call find_by_id; ensure failure propagates

    async def fail_find(_: object) -> FlextResult[object]:
      return FlextResult.fail("nf")

    repo._do_find_by_id = fail_find  # type: ignore[assignment]
    assert not (await repo.delete("1")).success


class DummyMw:
    """Simple middleware to mutate request/response dicts."""

    async def process_request(
      self,
      req: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
      r = dict(req)
      r["mw"] = 1
      return FlextResult.ok(r)

    async def process_response(
      self,
      resp: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
      r = dict(resp)
      r["mw2"] = 1
      return FlextResult.ok(r)


class DummyHandler(FlextApiBaseHandlerService):
    """Handler service with two middlewares and simple echo handle."""

    service_name: str = "dummy-handler"
    middlewares: ClassVar[list[DummyMw]] = [DummyMw()]

    async def _do_start(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_handle(
      self,
      request: dict[str, object],
    ) -> FlextResult[dict[str, object]]:
      if request.get("crash"):
          return FlextResult.fail("boom")
      return FlextResult.ok(request | {"handled": True})


@pytest.mark.asyncio
async def test_handler_middleware_chain_and_error() -> None:
    """Test handler middleware chain and error."""
    h = DummyHandler()
    ok = await h.handle({"a": 1})
    assert ok.success
    assert ok.data["mw2"] == 1
    assert ok.data["handled"] is True
    bad = await h.handle({"crash": True})
    assert not bad.success


class DummyStream(FlextApiBaseStreamingService):
    """Streaming service yielding bytes and raising on fail."""

    service_name: str = "dummy-stream"

    async def _do_start(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stop(self) -> FlextResult[None]:
      return FlextResult.ok(None)

    async def _do_stream(self, source: object) -> AsyncIterator[bytes]:
      if isinstance(source, dict) and source.get("fail"):
          msg = "stream fail"
          raise RuntimeError(msg)
      yield b"x"
      yield b"y"


@pytest.mark.asyncio
async def test_streaming_validation_and_errors() -> None:
    """Test streaming validation and errors."""
    s = DummyStream()
    chunks = [c async for c in s.stream_data(b"abc")]
    assert b"x" in chunks
    assert b"y" in chunks
    with pytest.raises(RuntimeError):
      await anext(s.stream_data({"fail": True}))
