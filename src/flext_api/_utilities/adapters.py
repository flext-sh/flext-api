"""API typings adapters — real class for stand-in composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import ClassVar, TYPE_CHECKING

from flext_web import FlextWebTypes, p, u

if TYPE_CHECKING:
    from flext_api._typings.base import FlextApiTypingsBase


class FlextApiTypingsAdapters:
    """API type adapter instances referenced by the facade."""

    API_JSON_VALUE_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.JsonValue]] = (
        u.json_value_adapter()
    )
    BINARY_CONTENT_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.StrictBytes]] = (
        u.binary_content_adapter()
    )
    STR_MAPPING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[Mapping[str, str]]] = (
        u.str_mapping_adapter()
    )
    HOSTNAME_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.HostnameStr]] = (
        u.hostname_str_adapter()
    )
    PORT_NUMBER_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.PortNumber]] = (
        u.port_number_adapter()
    )
    STRING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.StrictStr]] = (
        u.str_adapter()
    )
    STORAGE_ENTRY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]] = (
        u.json_mapping_adapter()
    )
    REQUEST_BODY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter["FlextApiTypingsBase.RequestBody"]] = u.type_adapter(
        "FlextApiTypingsBase.RequestBody",
    )
    RESPONSE_BODY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter["FlextApiTypingsBase.ResponseBody"]] = u.type_adapter(
        "FlextApiTypingsBase.ResponseBody",
    )
    DICT_BODY_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]] = (
        u.json_mapping_adapter()
    )
    JSON_HEADERS_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]] = (
        u.json_mapping_adapter()
    )


__all__: list[str] = ["FlextApiTypingsAdapters"]