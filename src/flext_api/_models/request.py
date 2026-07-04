"""API request models."""

from __future__ import annotations

from types import MappingProxyType
from typing import Annotated, ClassVar

from flext_api import c, t
from flext_web import m, u


class FlextApiModelsRequest:
    """Request model shard for ``m.Api``."""

    @staticmethod
    def _normalize_request_body(v: t.JsonValue) -> t.Api.RequestBody:
        """Normalize request body."""
        if v is None:
            return {}
        return t.Api.REQUEST_BODY_ADAPTER.validate_python(v)

    class HttpRequest(m.Value):
        """Immutable HTTP request value object."""

        _flext_enforcement_exempt: ClassVar[bool] = True

        method: Annotated[
            c.Api.Method | str,
            u.Field(
                default="GET",
                description="HTTP method",
                pattern=r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)$",
            ),
        ]
        url: Annotated[
            t.NonEmptyStr,
            u.Field(..., max_length=c.Api.MAX_URL_LENGTH, description="Request URL"),
        ]
        headers: Annotated[
            t.StrMapping,
            u.Field(description="HTTP request headers"),
        ] = u.Field(default_factory=lambda: MappingProxyType({}))
        body: Annotated[
            t.Api.RequestBody | None,
            m.BeforeValidator(
                FlextApiModelsRequest._normalize_request_body,
            ),
            u.Field(description="Request body"),
        ] = None
        query_params: Annotated[
            t.Api.WebParams | None,
            u.Field(description="Query parameters"),
        ] = None
        timeout: Annotated[
            t.PositiveTimeout,
            u.Field(
                default=float(c.Api.DEFAULT_TIMEOUT),
                description="Request timeout in seconds",
            ),
        ]

        @u.computed_field(return_type=str)
        @property
        def content_type(self) -> str:
            """Get content type from headers."""
            if c.Api.HEADER_CONTENT_TYPE in self.headers:
                header_value: str = self.headers[c.Api.HEADER_CONTENT_TYPE]
                return header_value
            lower_name = c.Api.HEADER_CONTENT_TYPE.lower()
            if lower_name in self.headers:
                lowercase_header_value: str = self.headers[lower_name]
                return lowercase_header_value
            return str(c.Api.ContentType.JSON)


__all__: list[str] = ["FlextApiModelsRequest"]
