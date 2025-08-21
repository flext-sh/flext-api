"""
Factory Boy factories for flext-api core objects.

Uses factory_boy for consistent test data generation.
"""

from __future__ import annotations

import factory
from factory import Faker
from flext_core import FlextResult

from flext_api import (
    FlextApiClientRequest,
    FlextApiClientResponse,
    FlextApiConfig,
)
from flext_api.types import FlextTypes


class FlextApiClientRequestFactory(factory.Factory):
    """Factory for FlextApiClientRequest objects."""
    
    class Meta:
        model = FlextApiClientRequest
    
    method = "GET"
    url = Faker("url")
    headers = factory.Dict({})
    params = factory.Dict({})
    json_data = None
    data = None
    timeout = 30.0


class FlextApiClientResponseFactory(factory.Factory):
    """Factory for FlextApiClientResponse objects."""
    
    class Meta:
        model = FlextApiClientResponse
    
    status_code = 200
    headers = factory.Dict({"content-type": "application/json"})
    data = factory.Dict({"message": "success"})
    elapsed_time = 0.5
    request_id = Faker("uuid4")
    from_cache = False


class FlextApiConfigFactory(factory.Factory):
    """Factory for FlextApiConfig objects."""
    
    class Meta:
        model = FlextApiConfig
    
    base_url = Faker("url")
    timeout = 30.0
    headers = factory.Dict({})
    max_retries = 3
    verify_ssl = True
    follow_redirects = True