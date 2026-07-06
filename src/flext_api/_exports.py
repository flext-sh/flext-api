# AUTO-GENERATED FILE — Regenerate with: make gen
"""Lazy export registry."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, merge_lazy_imports

_LOCAL_LAZY_IMPORTS = build_lazy_import_map(
    {
        "._constants": ("_constants",),
        "._models": ("_models",),
        "._protocols": ("_protocols",),
        "._typings": ("_typings",),
        "._utilities": ("_utilities",),
        ".api": (
            "FlextApi",
            "api",
        ),
        ".base": (
            "FlextApiServiceBase",
            "s",
        ),
        ".constants": (
            "FlextApiConstants",
            "c",
        ),
        ".models": (
            "FlextApiModels",
            "m",
        ),
        ".protocol_impls": ("protocol_impls",),
        ".protocols": (
            "FlextApiProtocols",
            "p",
        ),
        ".settings": ("FlextApiSettings",),
        ".typings": (
            "FlextApiTypes",
            "t",
        ),
        ".utilities": (
            "FlextApiUtilities",
            "u",
        ),
        "flext_core._root_typing_parts.facades": (
            "d",
            "e",
            "h",
            "r",
            "x",
        ),
    },
)

FLEXT_API_LAZY_IMPORTS = merge_lazy_imports(
    (),
    _LOCAL_LAZY_IMPORTS,
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name="flext_api",
)

__all__: list[str] = ["FLEXT_API_LAZY_IMPORTS"]
