"""
Factory Boy factories for FastAPI app configuration.

Uses factory_boy for consistent app test data generation.
"""

from __future__ import annotations

import factory
from factory import Faker
from fastapi import FastAPI

from flext_api.config import FlextApiAppConfig


class FlextApiAppConfigFactory(factory.Factory):
    """Factory for FlextApiAppConfig objects."""
    
    class Meta:
        model = FlextApiAppConfig
    
    title = "Test FLEXT API"
    description = "Test API Description"
    version = "0.1.0"
    debug = True
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"


class FastAPIApplicationFactory(factory.Factory):
    """Factory for FastAPI applications with test configuration."""
    
    class Meta:
        model = FastAPI
    
    title = "Test FLEXT API"
    description = "Test API Description"
    version = "0.1.0"
    debug = True
    docs_url = "/docs"
    redoc_url = "/redoc"
    openapi_url = "/openapi.json"