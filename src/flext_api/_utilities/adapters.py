"""API typings adapters — real class for stand-in composition.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar

from flext_web import FlextWebTypes, u

if TYPE_CHECKING:
    pass


class FlextApiTypingsAdapters:
    """API type adapter instances referenced by the facade."""

    API_JSON_VALUE_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonValue]
    ] = u.json_value_adapter()
    BINARY_CONTENT_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.StrictBytes]
    ] = u.binary_content_adapter()
    STR_MAPPING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[Mapping[str, str]]] = (
        u.str_mapping_adapter()
    )
    HOSTNAME_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.HostnameStr]
    ] = u.hostname_str_adapter()
    PORT_NUMBER_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.PortNumber]
    ] = u.port_number_adapter()
    STRING_ADAPTER: ClassVar[FlextWebTypes.ValueAdapter[FlextWebTypes.StrictStr]] = (
        u.str_adapter()
    )
    STORAGE_ENTRY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()
    REQUEST_BODY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes]
    ] = u.type_adapter(FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes)
    RESPONSE_BODY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[
            FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes | None
        ]
    ] = u.type_adapter(FlextWebTypes.JsonValue | FlextWebTypes.StrictBytes | None)
    DICT_BODY_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()
    JSON_HEADERS_ADAPTER: ClassVar[
        FlextWebTypes.ValueAdapter[FlextWebTypes.JsonMapping]
    ] = u.json_mapping_adapter()


__all__: list[str] = ["FlextApiTypingsAdapters"]
