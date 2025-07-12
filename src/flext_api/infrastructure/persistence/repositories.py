"""Infrastructure persistence repositories for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Using flext-core repository patterns - NO duplication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from flext_api.domain.entities import APIPipeline
from flext_api.domain.entities import APIPlugin
from flext_api.domain.entities import APIRequest
from flext_api.domain.entities import APIResponse
from flext_api.domain.ports import PipelineRepository
from flext_api.domain.ports import PluginRepository
from flext_api.domain.ports import RequestRepository
from flext_api.domain.ports import ResponseRepository
from flext_core.infrastructure.persistence.base import PostgreSQLRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class PostgreSQLPipelineRepository(
    PostgreSQLRepository[APIPipeline, UUID],
    PipelineRepository,
):
    """PostgreSQL pipeline repository implementation."""

    def __init__(self, database_url: str) -> None:
        super().__init__(database_url, APIPipeline)

    async def save(self, pipeline: APIPipeline) -> APIPipeline:
        """Save a pipeline to the database.

        Args:
            pipeline: The pipeline entity to save.

        Returns:
            The saved pipeline entity.

        """
        async with self.get_session() as session:
            # Convert to SQLAlchemy model
            pipeline_model = self._to_model(pipeline)

            # Merge or add
            if await self._exists(session, pipeline.id):
                merged = await session.merge(pipeline_model)
            else:
                session.add(pipeline_model)
                merged = pipeline_model

            await session.commit()
            await session.refresh(merged)

            return self._to_entity(merged)

    async def get(self, pipeline_id: UUID) -> APIPipeline | None:
        """Get a pipeline by ID.

        Args:
            pipeline_id: The ID of the pipeline to get.

        Returns:
            The pipeline if found, otherwise None.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, pipeline_id)
            return self._to_entity(model) if model else None

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> list[APIPipeline]:
        """List pipelines.

        Args:
            limit: The maximum number of pipelines to return.
            offset: The offset to start from.
            status: The status of the pipelines to return.

        Returns:
            A list of pipelines.

        """
        async with self.get_session() as session:
            query = self._build_query(session)

            if status:
                query = query.filter(self.model_class.status == status)

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            models = result.scalars().all()

            return [self._to_entity(model) for model in models]

    async def delete(self, pipeline_id: UUID) -> bool:
        """Delete a pipeline by ID.

        Args:
            pipeline_id: The ID of the pipeline to delete.

        Returns:
            True if the pipeline was deleted, False otherwise.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, pipeline_id)
            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True

    async def find_by_name(self, name: str) -> APIPipeline | None:
        """Find a pipeline by name.

        Args:
            name: The name of the pipeline to find.

        Returns:
            The pipeline if found, otherwise None.

        """
        async with self.get_session() as session:
            query = self._build_query(session).filter(self.model_class.name == name)
            result = await session.execute(query)
            model = result.scalar_one_or_none()

            return self._to_entity(model) if model else None

    def _to_model(
        self,
        entity: APIPipeline,
    ) -> object:
        """Convert entity to model.

        Args:
            entity: The entity to convert.

        Returns:
            The model.

        """
        # This would use a proper SQLAlchemy model
        # For now, using a simple dict representation
        return {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "status": entity.status,
            "config": entity.config,
            "owner_id": entity.owner_id,
            "project_id": entity.project_id,
            "last_run_at": entity.last_run_at,
            "run_count": entity.run_count,
            "success_count": entity.success_count,
            "failure_count": entity.failure_count,
            "endpoint": entity.endpoint,
            "method": entity.method,
            "auth_required": entity.auth_required,
            "rate_limit": entity.rate_limit,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def _to_entity(self, model: object) -> APIPipeline:
        """Convert model to entity.

        Args:
            model: The model to convert.

        Returns:
            The entity.

        """
        # This would convert from a proper SQLAlchemy model
        # For now, using a simple dict representation
        return APIPipeline(
            id=model["id"],
            name=model["name"],
            description=model["description"],
            status=model["status"],
            config=model["config"],
            owner_id=model["owner_id"],
            project_id=model["project_id"],
            last_run_at=model["last_run_at"],
            run_count=model["run_count"],
            success_count=model["success_count"],
            failure_count=model["failure_count"],
            endpoint=model["endpoint"],
            method=model["method"],
            auth_required=model["auth_required"],
            rate_limit=model["rate_limit"],
            created_at=model["created_at"],
            updated_at=model["updated_at"],
        )

    async def _exists(self, session: AsyncSession, entity_id: UUID) -> bool:
        """Check if an entity exists.

        Args:
            session: The session to use.
            entity_id: The ID of the entity to check.

        Returns:
            True if the entity exists, False otherwise.

        """
        result = await session.get(self.model_class, entity_id)
        return result is not None

    def _build_query(self, session: AsyncSession) -> object:
        """Build a query for the model.

        Args:
            session: The session to use.

        Returns:
            The query.

        """
        return session.query(self.model_class)


class PostgreSQLPluginRepository(
    PostgreSQLRepository[APIPlugin, UUID],
    PluginRepository,
):
    """PostgreSQL plugin repository implementation.

    This repository implements the PluginRepository interface and provides
    methods to save, get, list, delete, and find plugins by name.

    It uses PostgreSQL as the underlying database and SQLAlchemy for ORM.
    """

    def __init__(self, database_url: str) -> None:
        """Initialize the PostgreSQL plugin repository.

        Args:
            database_url: The URL of the PostgreSQL database.

        """
        super().__init__(database_url, APIPlugin)

    async def save(self, plugin: APIPlugin) -> APIPlugin:
        """Save a plugin.

        Args:
            plugin: The plugin to save.

        Returns:
            The saved plugin.

        """
        async with self.get_session() as session:

            # Convert to SQLAlchemy model
            plugin_model = self._to_model(plugin)

            # Merge or add
            if await self._exists(session, plugin.id):
                merged = await session.merge(plugin_model)
            else:
                session.add(plugin_model)
                merged = plugin_model

            await session.commit()
            await session.refresh(merged)

            return self._to_entity(merged)

    async def get(self, plugin_id: UUID) -> APIPlugin | None:
        """Get a plugin by ID.

        Args:
            plugin_id: The ID of the plugin to get.

        Returns:
            The plugin if found, otherwise None.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, plugin_id)
            return self._to_entity(model) if model else None

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        type: str | None = None,
        enabled: bool | None = None,
    ) -> list[APIPlugin]:
        """List plugins.

        Args:
            limit: The maximum number of plugins to return.
            offset: The offset to start from.
            type: The type of the plugins to return.
            enabled: Whether the plugins are enabled.

        Returns:
            A list of plugins.

        """
        async with self.get_session() as session:
            query = self._build_query(session)

            if type:
                query = query.filter(self.model_class.type == type)
            if enabled is not None:
                query = query.filter(self.model_class.enabled == enabled)

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            models = result.scalars().all()

            return [self._to_entity(model) for model in models]

    async def delete(self, plugin_id: UUID) -> bool:
        """Delete a plugin by ID.

        Args:
            plugin_id: The ID of the plugin to delete.

        Returns:
            True if the plugin was deleted, False if not found.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, plugin_id)
            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True

    async def find_by_name(self, name: str) -> APIPlugin | None:
        """Find a plugin by name.

        Args:
            name: The name of the plugin to find.

        Returns:
            The plugin if found, otherwise None.

        """
        async with self.get_session() as session:
            query = self._build_query(session).filter(self.model_class.name == name)
            result = await session.execute(query)
            model = result.scalar_one_or_none()

            return self._to_entity(model) if model else None

    def _to_model(self, entity: APIPlugin) -> object:
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.type,
            "version": entity.version,
            "description": entity.description,
            "config": entity.config,
            "enabled": entity.enabled,
            "author": entity.author,
            "repository_url": entity.repository_url,
            "documentation_url": entity.documentation_url,
            "schema": entity.schema,
            "capabilities": entity.capabilities,
            "api_version": entity.api_version,
            "endpoints": entity.endpoints,
            "permissions": entity.permissions,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def _to_entity(self, model: object) -> APIPlugin:
        return APIPlugin(
            id=model["id"],
            name=model["name"],
            type=model["type"],
            version=model["version"],
            description=model["description"],
            config=model["config"],
            enabled=model["enabled"],
            author=model["author"],
            repository_url=model["repository_url"],
            documentation_url=model["documentation_url"],
            schema=model["schema"],
            capabilities=model["capabilities"],
            api_version=model["api_version"],
            endpoints=model["endpoints"],
            permissions=model["permissions"],
            created_at=model["created_at"],
            updated_at=model["updated_at"],
        )

    async def _exists(self, session: AsyncSession, entity_id: UUID) -> bool:
        result = await session.get(self.model_class, entity_id)
        return result is not None

    def _build_query(self, session: AsyncSession) -> object:
        return session.query(self.model_class)


class PostgreSQLRequestRepository(
    PostgreSQLRepository[APIRequest, UUID],
    RequestRepository,
):
    """PostgreSQL request repository implementation."""

    def __init__(self, database_url: str) -> None:
        super().__init__(database_url, APIRequest)

    async def save(self, request: APIRequest) -> APIRequest:
        """Save a request to the database.

        Args:
            request: The request entity to save.

        Returns:
            The saved request entity.

        """
        async with self.get_session() as session:
            # Convert to SQLAlchemy model
            request_model = self._to_model(request)

            # Merge or add
            if await self._exists(session, request.id):
                merged = await session.merge(request_model)
            else:
                session.add(request_model)
                merged = request_model

            await session.commit()
            await session.refresh(merged)

            return self._to_entity(merged)

    async def get(self, request_id: UUID) -> APIRequest | None:
        """Get a request by ID.

        Args:
            request_id: The ID of the request to get.

        Returns:
            The request if found, otherwise None.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, request_id)
            return self._to_entity(model) if model else None

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: UUID | None = None,
    ) -> list[APIRequest]:
        """List requests.

        Args:
            limit: The maximum number of requests to return.
            offset: The offset to start from.
            user_id: The ID of the user to filter requests by.

        Returns:
            A list of requests.

        """
        async with self.get_session() as session:
            query = self._build_query(session)

            if user_id:
                query = query.filter(self.model_class.user_id == user_id)

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            models = result.scalars().all()

            return [self._to_entity(model) for model in models]

    async def delete(self, request_id: UUID) -> bool:
        """Delete a request by ID.

        Args:
            request_id: The ID of the request to delete.

        Returns:
            True if the request was deleted, False if not found.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, request_id)
            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True

    def _to_model(self, entity: APIRequest) -> object:
        return {
            "id": entity.id,
            "method": entity.method,
            "path": entity.path,
            "query_params": entity.query_params,
            "headers": entity.headers,
            "body": entity.body,
            "user_id": entity.user_id,
            "ip_address": entity.ip_address,
            "user_agent": entity.user_agent,
            "request_id": entity.request_id,
            "status_code": entity.status_code,
            "response_time_ms": entity.response_time_ms,
            "response_size": entity.response_size,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def _to_entity(self, model: object) -> APIRequest:
        return APIRequest(
            id=model["id"],
            method=model["method"],
            path=model["path"],
            query_params=model["query_params"],
            headers=model["headers"],
            body=model["body"],
            user_id=model["user_id"],
            ip_address=model["ip_address"],
            user_agent=model["user_agent"],
            request_id=model["request_id"],
            status_code=model["status_code"],
            response_time_ms=model["response_time_ms"],
            response_size=model["response_size"],
            created_at=model["created_at"],
            updated_at=model["updated_at"],
        )

    async def _exists(self, session: AsyncSession, entity_id: UUID) -> bool:
        result = await session.get(self.model_class, entity_id)
        return result is not None

    def _build_query(self, session: AsyncSession) -> object:
        return session.query(self.model_class)


class PostgreSQLResponseRepository(
    PostgreSQLRepository[APIResponse, UUID],
    ResponseRepository,
):
    """PostgreSQL response repository implementation."""

    def __init__(self, database_url: str) -> None:
        """Initialize the PostgreSQL response repository.

        Args:
            database_url: The URL of the PostgreSQL database.

        """
        super().__init__(database_url, APIResponse)

    async def save(self, response: APIResponse) -> APIResponse:
        """Save a response.

        Args:
            response: The response to save.

        Returns:
            The saved response.

        """
        async with self.get_session() as session:
            # Convert to SQLAlchemy model
            response_model = self._to_model(response)

            # Merge or add
            if await self._exists(session, response.id):
                merged = await session.merge(response_model)
            else:
                session.add(response_model)
                merged = response_model

            await session.commit()
            await session.refresh(merged)

            return self._to_entity(merged)

    async def get(self, response_id: UUID) -> APIResponse | None:
        """Get a response by ID.

        Args:
            response_id: The ID of the response to get.

        Returns:
            The response if found, otherwise None.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, response_id)
            return self._to_entity(model) if model else None

    async def list(
        self,
        limit: int = 20,
        offset: int = 0,
        request_id: UUID | None = None,
    ) -> list[APIResponse]:
        """List responses.

        Args:
            limit: The maximum number of responses to return.
            offset: The offset to start from.
            request_id: The ID of the request to filter responses by.

        Returns:
            A list of responses.

        """
        async with self.get_session() as session:
            query = self._build_query(session)

            if request_id:
                query = query.filter(self.model_class.request_id == request_id)

            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            models = result.scalars().all()

            return [self._to_entity(model) for model in models]

    async def delete(self, response_id: UUID) -> bool:
        """Delete a response by ID.

        Args:
            response_id: The ID of the response to delete.

        Returns:
            True if the response was deleted, False otherwise.

        """
        async with self.get_session() as session:
            model = await session.get(self.model_class, response_id)
            if not model:
                return False

            await session.delete(model)
            await session.commit()
            return True

    def _to_model(self, entity: APIResponse) -> object:
        """Convert entity to model.

        Args:
            entity: The entity to convert.

        Returns:
            The model.

        """
        return {
            "id": entity.id,
            "request_id": entity.request_id,
            "status_code": entity.status_code,
            "headers": entity.headers,
            "body": entity.body,
            "response_time_ms": entity.response_time_ms,
            "content_type": entity.content_type,
            "content_length": entity.content_length,
            "error_message": entity.error_message,
            "error_code": entity.error_code,
            "created_at": entity.created_at,
            "updated_at": entity.updated_at,
        }

    def _to_entity(self, model: object) -> APIResponse:
        """Convert model to entity.

        Args:
            model: The model to convert.

        Returns:
            The entity.

        """
        return APIResponse(
            id=model["id"],
            request_id=model["request_id"],
            status_code=model["status_code"],
            headers=model["headers"],
            body=model["body"],
            response_time_ms=model["response_time_ms"],
            content_type=model["content_type"],
            content_length=model["content_length"],
            error_message=model["error_message"],
            error_code=model["error_code"],
            created_at=model["created_at"],
            updated_at=model["updated_at"],
        )

    async def _exists(self, session: AsyncSession, entity_id: UUID) -> bool:
        """Check if an entity exists.

        Args:
            session: The session to use.
            entity_id: The ID of the entity to check.

        Returns:
            True if the entity exists, False otherwise.

        """
        result = await session.get(self.model_class, entity_id)
        return result is not None

    def _build_query(self, session: AsyncSession) -> object:
        """Build a query for the model.

        Args:
            session: The session to use.

        Returns:
            The query.

        """
        return session.query(self.model_class)
