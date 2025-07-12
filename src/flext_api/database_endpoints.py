"""FLEXT API Database Pipeline Endpoints - Modern Python 3.13 + Clean Architecture.

Copyright (c) 2025 FLEXT Team. All rights reserved.

Database pipeline management endpoints with enterprise features:
- Pipeline CRUD operations
- Async/await pattern
- SQLAlchemy integration
- Authentication integration
- Error handling
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import NoReturn
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from pydantic import Field

from flext_api.dependencies import get_db_session
from flext_api.repositories.pipeline import DatabasePipelineRepository
from flext_core.config import get_config
from flext_core.domain.pydantic_base import APIRequest
from flext_core.domain.pydantic_base import APIResponse

if TYPE_CHECKING:
    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession

    from flext_api.models.pipeline import PipelineCreateRequest
    from flext_api.models.pipeline import PipelineExecutionRequest
    from flext_api.models.pipeline import PipelineResponse
    from flext_api.models.pipeline import PipelineUpdateRequest


def _raise_bad_request_error(message: str) -> NoReturn:
    """Raise HTTP 400 Bad Request error."""
    raise HTTPException(status_code=400, detail=message)


def _raise_not_found_error(message: str) -> NoReturn:
    """Raise HTTP 404 Not Found error."""
    raise HTTPException(status_code=404, detail=message)


def _raise_internal_error(message: str) -> NoReturn:
    """Raise HTTP 500 Internal Server error."""
    raise HTTPException(status_code=500, detail=message)


# Get configuration
config = get_config()


class PipelineListParams(APIRequest):
    """Parameters for pipeline listing operations."""

    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page",
    )
    status: str | None = Field(default=None, description="Filter by pipeline status")
    search: str | None = Field(
        default=None,
        description="Search term for name/description",
    )


async def create_pipeline_db(
    pipeline_data: PipelineCreateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PipelineResponse:
    """Create a new pipeline in the database.

    Args:
        pipeline_data: Pipeline creation request data
        request: FastAPI request object
        session: Database session

    Returns:
        PipelineResponse: Created pipeline data

    Raises:
        HTTPException: If authentication fails or creation errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.create_pipeline(
        pipeline_data=pipeline_data,
        created_by=user.get("username", "unknown"),
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "ValidationError":
        _raise_bad_request_error(error.message)
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    else:
        _raise_internal_error("Unknown error occurred")


async def get_pipeline_db(
    pipeline_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PipelineResponse:
    """Get a pipeline by ID from the database.

    Args:
        pipeline_id: UUID string of the pipeline
        request: FastAPI request object
        session: Database session

    Returns:
        PipelineResponse: Pipeline data

    Raises:
        HTTPException: If authentication fails or pipeline not found

    """
    # Validate UUID format
    try:
        uuid_id = UUID(pipeline_id)
    except ValueError:
        _raise_bad_request_error("Invalid pipeline ID format")

    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.get_pipeline(uuid_id)

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Pipeline not found")
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def update_pipeline_db(
    pipeline_id: str,
    pipeline_data: PipelineUpdateRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> PipelineResponse:
    """Update a pipeline in the database.

    Args:
        pipeline_id: UUID string of the pipeline
        pipeline_data: Pipeline update request data
        request: FastAPI request object
        session: Database session

    Returns:
        PipelineResponse: Updated pipeline data

    Raises:
        HTTPException: If authentication fails or update errors occur

    """
    # Validate UUID format
    try:
        uuid_id = UUID(pipeline_id)
    except ValueError:
        _raise_bad_request_error("Invalid pipeline ID format")

    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.update_pipeline(
        pipeline_id=uuid_id,
        pipeline_data=pipeline_data,
        updated_by=user.get("username", "unknown"),
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Pipeline not found")
    elif error.error_type == "ValidationError":
        _raise_bad_request_error(error.message)
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def delete_pipeline_db(
    pipeline_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> APIResponse:
    """Delete a pipeline from the database.

    Args:
        pipeline_id: UUID string of the pipeline
        request: FastAPI request object
        session: Database session

    Returns:
        APIResponse: Success response

    Raises:
        HTTPException: If authentication fails or deletion errors occur

    """
    # Validate UUID format
    try:
        uuid_id = UUID(pipeline_id)
    except ValueError:
        _raise_bad_request_error("Invalid pipeline ID format")

    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.delete_pipeline(uuid_id)

    # Handle service result
    if result.is_success:
        return APIResponse(success=True, message="Pipeline deleted successfully")
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Pipeline not found")
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def list_pipelines_db(
    request: Request,
    params: PipelineListParams = PipelineListParams(),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """List pipelines with pagination and filtering.

    Args:
        request: FastAPI request object
        params: Pagination and filtering parameters
        session: Database session

    Returns:
        dict[str, Any]: Paginated pipeline list

    Raises:
        HTTPException: If authentication fails or listing errors occur

    """
    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.list_pipelines(
        page=params.page,
        page_size=params.page_size,
        status_filter=params.status,
        search_term=params.search,
    )

    # Handle service result
    if result.is_success:
        return result.value
    error = result.error
    if error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")


async def execute_pipeline_db(
    pipeline_id: str,
    execution_data: PipelineExecutionRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    """Execute a pipeline with given parameters.

    Args:
        pipeline_id: UUID string of the pipeline
        execution_data: Pipeline execution request data
        request: FastAPI request object
        session: Database session

    Returns:
        dict[str, str]: Execution result with execution_id

    Raises:
        HTTPException: If authentication fails or execution errors occur

    """
    # Validate UUID format
    try:
        uuid_id = UUID(pipeline_id)
    except ValueError:
        _raise_bad_request_error("Invalid pipeline ID format")

    # Get authenticated user from request state
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
        )

    # Create repository and execute operation
    repo = DatabasePipelineRepository(session)
    result = await repo.execute_pipeline(
        pipeline_id=uuid_id,
        execution_data=execution_data,
        executed_by=user.get("username", "unknown"),
    )

    # Handle service result
    if result.is_success:
        return {"execution_id": str(result.value)}
    error = result.error
    if error.error_type == "NotFoundError":
        _raise_not_found_error("Pipeline not found")
    elif error.error_type == "ValidationError":
        _raise_bad_request_error(error.message)
    elif error.error_type == "InternalError":
        _raise_internal_error(error.message)
    _raise_internal_error("Unknown error occurred")
