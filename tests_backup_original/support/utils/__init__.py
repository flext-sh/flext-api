"""Utility functions for flext-api testing.

Provides common testing utilities following SOLID principles
and flext-core patterns.


Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations
from flext_core import FlextTypes
from tests.support.utils.api_utils import (
    assert_flext_result_success,
    assert_flext_result_failure,
    create_test_request,
    create_test_response,
)
from tests.support.utils.async_utils import (
    run_async_test,
    wait_for_condition,
)
from tests.support.utils.file_utils import (
    create_temp_json_file,
    create_readonly_file,
)

__all__ = [
    "assert_flext_result_success",
    "assert_flext_result_failure",
    "create_test_request",
    "create_test_response",
    "run_async_test",
    "wait_for_condition",
    "create_temp_json_file",
    "create_readonly_file",
]
