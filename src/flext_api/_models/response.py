"""API response models."""

from __future__ import annotations

from types import MappingProxyType
from typing import Annotated, ClassVar

from flext_api.constants import c
from flext_api.typings import t
from flext_web import m, u


class FlextApiModelsResponse:
    """Response model shard for ``m.Api``."""

    @staticmethod
    def _normalize_response_body(v: t.JsonValue) -> t.Api.ResponseBody:
        """Normalize response body."""
        if v is None:
            return None
        return t.Api.RESPONSE_BODY_ADAPTER.validate_python(v)

    class HttpResponse(m.Value):
        """Immutable HTTP response value object."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        status_code: Annotated[
            t.HttpStatusCode,
            u.Field(
                ...,
                description=(
                    f"HTTP status code ({c.Api.HTTP_STATUS_MIN}-"
                    f"{c.Api.HTTP_STATUS_MAX})"
                ),
            ),
        ]
        headers: Annotated[
            t.StrMapping,
            u.Field(description="HTTP response headers"),
        ] = u.Field(default_factory=lambda: MappingProxyType({}))
        body: Annotated[
            t.Api.ResponseBody | None,
            m.BeforeValidator(
                lambda v: FlextApiModelsResponse._normalize_response_body(v)
            ),
            u.Field(description="Response body"),
        ] = None
        request_id: Annotated[
            str,
            u.Field(default="", description="Associated request ID for tracking"),
        ]

        @u.computed_field(return_type=bool)
        @property
        def client_error(self) -> bool:
            """Return whether response is a 4xx client error."""
            status_code: int = self.status_code
            return (
                c.Api.HTTP_CLIENT_ERROR_MIN <= status_code < c.Api.HTTP_CLIENT_ERROR_MAX
            )

        @u.computed_field(return_type=bool)
        @property
        def error(self) -> bool:
            """Return whether response is an HTTP error."""
            status_code: int = self.status_code
            return status_code >= c.Api.HTTP_ERROR_MIN

        @u.computed_field(return_type=bool)
        @property
        def redirect(self) -> bool:
            """Return whether response is a redirect."""
            status_code: int = self.status_code
            return c.Api.HTTP_REDIRECT_MIN <= status_code < c.Api.HTTP_REDIRECT_MAX

        @u.computed_field(return_type=bool)
        @property
        def server_error(self) -> bool:
            """Return whether response is a server error."""
            status_code: int = self.status_code
            return status_code >= c.Api.HTTP_SERVER_ERROR_MIN

        @u.computed_field(return_type=bool)
        @property
        def success(self) -> bool:
            """Return whether response is successful."""
            status_code: int = self.status_code
            return c.Api.HTTP_SUCCESS_MIN <= status_code < c.Api.HTTP_SUCCESS_MAX

    @classmethod
    def create_response(
        cls,
        status_code: int,
        body: t.Api.ResponseBody | None = None,
        headers: t.StrMapping | None = None,
        request_id: str | None = None,
    ) -> HttpResponse:
        """Create HttpResponse from parameters."""
        return cls.HttpResponse(
            status_code=status_code,
            body=body if body is not None else {},
            headers=headers if headers is not None else {},
            request_id=request_id if request_id is not None else "",
        )


__all__: list[str] = ["FlextApiModelsResponse"]
