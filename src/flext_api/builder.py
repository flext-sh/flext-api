"""FLEXT API Builder - Single intelligent builder using flext-core composition.

Consolidates FlextApiQueryBuilder, FlextApiResponseBuilder, and FlextApiBuilder
into one smart builder using flext-core patterns.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from flext_core import (
    FlextContainer,
    FlextResult,
    get_flext_container,
    get_logger,
    make_builder,
    require_non_empty,
    require_not_none,
    require_positive,
)


class FlextApiOperation(Enum):
    """Operations supported by the unified builder."""
    
    QUERY = "query"
    RESPONSE = "response"
    APP = "app"


class FlextApiBuilder:
    """Unified intelligent builder for all flext-api operations.
    
    Replaces FlextApiQueryBuilder, FlextApiResponseBuilder, and FlextApiBuilder
    with a single smart builder using flext-core composition patterns.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.container = get_flext_container()
        
        # Operation-specific state
        self._operation = FlextApiOperation.QUERY
        self._data: dict[str, Any] = {}
        
        # Query state
        self._filters: list[dict[str, Any]] = []
        self._sorts: list[dict[str, Any]] = []
        self._pagination: dict[str, Any] = {}
        
        # Response state  
        self._success: bool = True
        self._message: str = ""
        self._metadata: dict[str, Any] = {}
        
        # App state
        self._middlewares: list[Any] = []
        self._routes: list[Any] = []

    # === OPERATION SWITCHING ===
    
    def for_query(self) -> FlextApiBuilder:
        """Switch to query building mode."""
        self._operation = FlextApiOperation.QUERY
        return self
    
    def for_response(self) -> FlextApiBuilder:
        """Switch to response building mode."""
        self._operation = FlextApiOperation.RESPONSE
        return self
    
    def for_app(self) -> FlextApiBuilder:
        """Switch to app building mode."""
        self._operation = FlextApiOperation.APP
        return self

    # === QUERY OPERATIONS ===
    
    def filter(self, field: str, operator: str, value: Any = None) -> FlextApiBuilder:
        """Add filter condition with flext-core validation."""
        require_non_empty(field, "Field name cannot be empty")
        
        filter_dict = {"field": field, "operator": operator}
        if value is not None:
            filter_dict["value"] = value
            
        self._filters.append(filter_dict)
        return self
    
    def equals(self, field: str, value: Any) -> FlextApiBuilder:
        """Add equals filter."""
        return self.filter(field, "eq", value)
    
    def like(self, field: str, value: Any) -> FlextApiBuilder:
        """Add like filter."""
        return self.filter(field, "like", value)
    
    def sort(self, field: str, direction: str = "asc") -> FlextApiBuilder:
        """Add sort condition."""
        require_non_empty(field, "Sort field cannot be empty")
        self._sorts.append({"field": field, "direction": direction})
        return self
    
    def page(self, page_num: int, page_size: int = 20) -> FlextApiBuilder:
        """Set pagination."""
        require_positive(page_num, "Page number must be positive")
        require_positive(page_size, "Page size must be positive")
        
        self._pagination = {
            "page": page_num,
            "page_size": page_size,
            "offset": (page_num - 1) * page_size,
            "limit": page_size
        }
        return self

    # === RESPONSE OPERATIONS ===
    
    def success(self, data: Any = None, message: str = "Operation successful") -> FlextApiBuilder:
        """Create success response."""
        self._success = True
        self._data["response_data"] = data
        self._message = message
        return self
    
    def error(self, message: str, error_code: int = 500) -> FlextApiBuilder:
        """Create error response."""
        self._success = False
        self._message = message
        self._data["error_code"] = error_code
        return self
    
    def with_metadata(self, key: str, value: Any) -> FlextApiBuilder:
        """Add metadata with validation."""
        require_not_none(key, "Metadata key cannot be None")
        self._metadata[key] = value
        return self
    
    def with_pagination_response(self, total: int, page: int, page_size: int) -> FlextApiBuilder:
        """Add pagination to response."""
        require_positive(page_size, "Page size must be positive")
        
        self._data["pagination"] = {
            "total": max(0, total),
            "page": max(1, page),
            "page_size": page_size,
            "total_pages": math.ceil(total / page_size) if total > 0 else 0,
        }
        return self

    # === APP OPERATIONS ===
    
    def with_middleware(self, middleware: Any) -> FlextApiBuilder:
        """Add middleware to app."""
        require_not_none(middleware, "Middleware cannot be None")
        self._middlewares.append(middleware)
        return self
    
    def with_route(self, route: Any) -> FlextApiBuilder:
        """Add route to app."""
        require_not_none(route, "Route cannot be None")
        self._routes.append(route)
        return self

    # === INTELLIGENT BUILD METHODS ===
    
    def build(self) -> dict[str, Any] | Any:
        """Build based on current operation mode."""
        if self._operation == FlextApiOperation.QUERY:
            return self._build_query()
        elif self._operation == FlextApiOperation.RESPONSE:
            return self._build_response()
        elif self._operation == FlextApiOperation.APP:
            return self._build_app()
        else:
            return {}
    
    def _build_query(self) -> dict[str, Any]:
        """Build query dictionary."""
        return {
            "filters": self._filters,
            "sorts": self._sorts,
            "pagination": self._pagination,
        }
    
    def _build_response(self) -> dict[str, Any]:
        """Build response dictionary."""
        result = {
            "success": self._success,
            "message": self._message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if self._success and "response_data" in self._data:
            result["data"] = self._data["response_data"]
        
        if "error_code" in self._data:
            result["error_code"] = self._data["error_code"]
            
        if self._metadata:
            result["metadata"] = self._metadata
            
        if "pagination" in self._data:
            result["pagination"] = self._data["pagination"]
            
        return result
    
    def _build_app(self) -> Any:
        """Build FastAPI app with enterprise features."""
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        from contextlib import asynccontextmanager
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """App lifespan management."""
            self.logger.info("FLEXT API starting up")
            yield
            self.logger.info("FLEXT API shutting down")
        
        app = FastAPI(
            title="FLEXT API",
            description="Enterprise API built with flext-core",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=lifespan
        )
        
        # Add enterprise middlewares by default
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
        
        # Add registered middlewares
        for middleware in self._middlewares:
            app.add_middleware(middleware)
            
        # Add registered routes
        for route in self._routes:
            app.include_router(route)
            
        return app

    # === FACTORY METHODS ===
    
    @classmethod
    def create_query(cls) -> FlextApiBuilder:
        """Create builder for query operations."""
        return cls().for_query()
    
    @classmethod
    def create_response(cls) -> FlextApiBuilder:
        """Create builder for response operations."""
        return cls().for_response()
    
    @classmethod
    def create_app(cls) -> FlextApiBuilder:
        """Create builder for app operations.""" 
        return cls().for_app()


# === CONVENIENCE FUNCTIONS ===

def build_query(**filters: Any) -> dict[str, Any]:
    """Build query with filters using single function."""
    builder = FlextApiBuilder.create_query()
    for field, value in filters.items():
        builder.equals(field, value)
    return builder.build()


def build_success_response(data: Any, message: str = "Success") -> dict[str, Any]:
    """Build success response using single function."""
    return (FlextApiBuilder.create_response()
            .success(data, message)
            .build())


def build_error_response(message: str, error_code: int = 500) -> dict[str, Any]:
    """Build error response using single function."""
    return (FlextApiBuilder.create_response()
            .error(message, error_code)
            .build())


def build_paginated_response(
    data: Any, 
    total: int, 
    page: int, 
    page_size: int,
    message: str = "Success"
) -> dict[str, Any]:
    """Build paginated response using single function."""
    return (FlextApiBuilder.create_response()
            .success(data, message)
            .with_pagination_response(total, page, page_size)
            .build())