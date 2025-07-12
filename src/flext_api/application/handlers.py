"""Application command handlers for FLEXT-API.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module contains the command handlers for the FLEXT API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_api.domain.entities import Pipeline
from flext_api.domain.entities import Plugin
from flext_core.application.commands import Command
from flext_core.application.handlers import CommandHandler
from flext_core.domain.types import ServiceResult

if TYPE_CHECKING:
    from uuid import UUID

    from flext_api.domain.ports import AuthService
    from flext_api.domain.ports import HealthCheckService
    from flext_api.domain.ports import PipelineRepository
    from flext_api.domain.ports import PluginRepository
    from flext_api.infrastructure.config import APIConfig


# ==============================================================================
# COMMANDS
# ==============================================================================


class AuthenticateCommand(Command):
    """Authenticate user command."""

    def __init__(self, token: str) -> None:
        """Initialize the authenticate command.

        Args:
            token: The token to authenticate with.

        """
        self.token = token


class CreatePipelineCommand(Command):
    """Create pipeline command."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        config: dict | None = None,
    ) -> None:
        """Initialize the create pipeline command.

        Args:
            name: The name of the pipeline.
            description: The description of the pipeline.
            config: The configuration of the pipeline.

        """
        self.name = name
        self.description = description
        self.config = config or {}


class GetPipelineCommand(Command):
    """Get pipeline command."""

    def __init__(self, pipeline_id: UUID) -> None:
        """Initialize the get pipeline command.

        Args:
            pipeline_id: The ID of the pipeline to get.

        """
        self.pipeline_id = pipeline_id


class ListPipelinesCommand(Command):
    """List pipelines command."""

    def __init__(
        self,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
    ) -> None:
        """Initialize the list pipelines command.

        Args:
            limit: The number of pipelines to return.
            offset: The offset of the pipelines to return.
            status: The status of the pipelines to filter by.

        """
        self.limit = limit
        self.offset = offset
        self.status = status


class UpdatePipelineCommand(Command):
    """Update pipeline command."""

    def __init__(
        self,
        pipeline_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict | None = None,
    ) -> None:
        """Initialize the update pipeline command.

        Args:
            pipeline_id: The ID of the pipeline to update.
            name: The name of the pipeline.
            description: The description of the pipeline.
            config: The configuration of the pipeline.

        """
        self.pipeline_id = pipeline_id
        self.name = name
        self.description = description
        self.config = config


class DeletePipelineCommand(Command):
    """Delete pipeline command."""

    def __init__(self, pipeline_id: UUID) -> None:
        """Initialize the delete pipeline command.

        Args:
            pipeline_id: The ID of the pipeline to delete.

        """
        self.pipeline_id = pipeline_id


class CreatePluginCommand(Command):
    """Create plugin command."""

    def __init__(
        self,
        name: str,
        type: str,  # noqa: A002
        version: str,
        description: str | None = None,
        config: dict | None = None,
    ) -> None:
        """Initialize the create plugin command.

        Args:
            name: The name of the plugin.
            type: The type of the plugin.
            version: The version of the plugin.
            description: The description of the plugin.
            config: The configuration of the plugin.

        """
        self.name = name
        self.type = type
        self.version = version
        self.description = description
        self.config = config or {}


class GetPluginCommand(Command):
    """Get plugin command."""

    def __init__(self, plugin_id: UUID) -> None:
        self.plugin_id = plugin_id


class ListPluginsCommand(Command):
    """List plugins command."""

    def __init__(
        self,
        limit: int = 20,
        offset: int = 0,
        type: str | None = None,  # noqa: A002
        enabled: bool | None = None,
    ) -> None:
        self.limit = limit
        self.offset = offset
        self.type = type
        self.enabled = enabled


class UpdatePluginCommand(Command):
    """Update plugin command."""

    def __init__(
        self,
        plugin_id: UUID,
        name: str | None = None,
        description: str | None = None,
        config: dict | None = None,
        enabled: bool | None = None,
    ) -> None:
        self.plugin_id = plugin_id
        self.name = name
        self.description = description
        self.config = config
        self.enabled = enabled


class DeletePluginCommand(Command):
    """Delete plugin command."""

    def __init__(self, plugin_id: UUID) -> None:
        self.plugin_id = plugin_id


class GetSystemInfoCommand(Command):
    """Get system info command."""

    def __init__(self) -> None:
        pass


class GetSystemHealthCommand(Command):
    """Get system health command."""

    def __init__(self) -> None:
        pass


# ==============================================================================
# HANDLERS
# ==============================================================================


class AuthenticateHandler(CommandHandler[AuthenticateCommand, dict]):
    """Authenticate user handler."""

    def __init__(self, auth_service: AuthService, config: APIConfig) -> None:
        self.auth_service = auth_service
        self.config = config

    async def handle(self, command: AuthenticateCommand) -> ServiceResult[dict]:
        """Handle user authentication command.

        Args:
            command: The authentication command containing token.

        Returns:
            ServiceResult containing user data if successful.

        """
        try:
            user_data = await self.auth_service.authenticate(command.token)
            if not user_data:
                return ServiceResult.fail("Invalid token")

            return ServiceResult.ok(user_data)
        except (ValueError, RuntimeError, TypeError, ConnectionError) as e:
            return ServiceResult.fail(f"Authentication failed: {e!s}")


class CreatePipelineHandler(CommandHandler[CreatePipelineCommand, Pipeline]):
    """Create pipeline handler."""

    def __init__(self, repository: PipelineRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: CreatePipelineCommand) -> ServiceResult[Pipeline]:
        """Handle pipeline creation command.

        Args:
            command: The pipeline creation command.

        Returns:
            ServiceResult containing created pipeline.

        """
        try:
            pipeline = Pipeline(
                name=command.name,
                description=command.description,
                config=command.config,
            )

            saved_pipeline = await self.repository.save(pipeline)
            return ServiceResult.ok(saved_pipeline)
        except (ValueError, RuntimeError, TypeError) as e:
            return ServiceResult.fail(f"Failed to create pipeline: {e!s}")


class GetPipelineHandler(CommandHandler[GetPipelineCommand, Pipeline]):
    """Get pipeline handler."""

    def __init__(self, repository: PipelineRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: GetPipelineCommand) -> ServiceResult[Pipeline]:
        """Handle get pipeline command.

        Args:
            command: The get pipeline command containing pipeline ID.

        Returns:
            ServiceResult containing requested pipeline.

        """
        try:
            pipeline = await self.repository.get(command.pipeline_id)
            if not pipeline:
                return ServiceResult.fail(f"Pipeline {command.pipeline_id} not found")

            return ServiceResult.ok(pipeline)
        except (ValueError, KeyError, RuntimeError) as e:
            return ServiceResult.fail(f"Failed to get pipeline: {e!s}")


class ListPipelinesHandler(CommandHandler[ListPipelinesCommand, list[Pipeline]]):
    """List pipelines handler."""

    def __init__(self, repository: PipelineRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(
        self,
        command: ListPipelinesCommand,
    ) -> ServiceResult[list[Pipeline]]:
        """Handle list pipelines command.

        Args:
            command: The list pipelines command.

        Returns:
            ServiceResult containing list of pipelines.

        """
        try:
            pipelines = await self.repository.list(
                limit=command.limit,
                offset=command.offset,
                status=command.status,
            )

            return ServiceResult.ok(pipelines)
        except (ValueError, RuntimeError, OSError) as e:
            return ServiceResult.fail(f"Failed to list pipelines: {e!s}")


class UpdatePipelineHandler(CommandHandler[UpdatePipelineCommand, Pipeline]):
    """Update pipeline handler."""

    def __init__(self, repository: PipelineRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: UpdatePipelineCommand) -> ServiceResult[Pipeline]:
        """Handle pipeline update command.

        Args:
            command: The pipeline update command.

        Returns:
            ServiceResult containing updated pipeline.

        """
        try:
            pipeline = await self.repository.get(command.pipeline_id)
            if not pipeline:
                return ServiceResult.fail(f"Pipeline {command.pipeline_id} not found")

            # Update fields
            if command.name is not None:
                pipeline.name = command.name
            if command.description is not None:
                pipeline.description = command.description
            if command.config is not None:
                pipeline.config = command.config

            updated_pipeline = await self.repository.save(pipeline)
            return ServiceResult.ok(updated_pipeline)
        except (ValueError, KeyError, RuntimeError, TypeError) as e:
            return ServiceResult.fail(f"Failed to update pipeline: {e!s}")


class DeletePipelineHandler(CommandHandler[DeletePipelineCommand, bool]):
    """Delete pipeline handler."""

    def __init__(self, repository: PipelineRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: DeletePipelineCommand) -> ServiceResult[bool]:
        """Handle pipeline deletion command.

        Args:
            command: The pipeline deletion command.

        Returns:
            ServiceResult indicating deletion success.

        """
        try:
            success = await self.repository.delete(command.pipeline_id)
            if not success:
                return ServiceResult.fail(f"Pipeline {command.pipeline_id} not found")

            return ServiceResult.ok(True)
        except (ValueError, KeyError, RuntimeError) as e:
            return ServiceResult.fail(f"Failed to delete pipeline: {e!s}")


class CreatePluginHandler(CommandHandler[CreatePluginCommand, Plugin]):
    """Create plugin handler."""

    def __init__(self, repository: PluginRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: CreatePluginCommand) -> ServiceResult[Plugin]:
        """Handle plugin creation command.

        Args:
            command: The plugin creation command.

        Returns:
            ServiceResult containing created plugin.

        """
        try:
            plugin = Plugin(
                name=command.name,
                type=command.type,
                version=command.version,
                description=command.description,
                config=command.config,
            )

            saved_plugin = await self.repository.save(plugin)
            return ServiceResult.ok(saved_plugin)
        except (ValueError, RuntimeError, TypeError) as e:
            return ServiceResult.fail(f"Failed to create plugin: {e!s}")


class GetPluginHandler(CommandHandler[GetPluginCommand, Plugin]):
    """Get plugin handler."""

    def __init__(self, repository: PluginRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: GetPluginCommand) -> ServiceResult[Plugin]:
        """Handle get plugin command.

        Args:
            command: The get plugin command containing plugin ID.

        Returns:
            ServiceResult containing requested plugin.

        """
        try:
            plugin = await self.repository.get(command.plugin_id)
            if not plugin:
                return ServiceResult.fail(f"Plugin {command.plugin_id} not found")

            return ServiceResult.ok(plugin)
        except (ValueError, KeyError, RuntimeError) as e:
            return ServiceResult.fail(f"Failed to get plugin: {e!s}")


class ListPluginsHandler(CommandHandler[ListPluginsCommand, list[Plugin]]):
    """List plugins handler."""

    def __init__(self, repository: PluginRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: ListPluginsCommand) -> ServiceResult[list[Plugin]]:
        """Handle list plugins command.

        Args:
            command: The list plugins command.

        Returns:
            ServiceResult containing list of plugins.

        """
        try:
            plugins = await self.repository.list(
                limit=command.limit,
                offset=command.offset,
                type=command.type,
                enabled=command.enabled,
            )

            return ServiceResult.ok(plugins)
        except (ValueError, RuntimeError, OSError) as e:
            return ServiceResult.fail(f"Failed to list plugins: {e!s}")


class UpdatePluginHandler(CommandHandler[UpdatePluginCommand, Plugin]):
    """Update plugin handler."""

    def __init__(self, repository: PluginRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: UpdatePluginCommand) -> ServiceResult[Plugin]:
        """Handle plugin update command.

        Args:
            command: The plugin update command.

        Returns:
            ServiceResult containing updated plugin.

        """
        try:
            plugin = await self.repository.get(command.plugin_id)
            if not plugin:
                return ServiceResult.fail(f"Plugin {command.plugin_id} not found")

            # Update fields
            if command.name is not None:
                plugin.name = command.name
            if command.description is not None:
                plugin.description = command.description
            if command.config is not None:
                plugin.config = command.config
            if command.enabled is not None:
                plugin.enabled = command.enabled

            updated_plugin = await self.repository.save(plugin)
            return ServiceResult.ok(updated_plugin)
        except (ValueError, KeyError, RuntimeError, TypeError) as e:
            return ServiceResult.fail(f"Failed to update plugin: {e!s}")


class DeletePluginHandler(CommandHandler[DeletePluginCommand, bool]):
    """Delete plugin handler."""

    def __init__(self, repository: PluginRepository, config: APIConfig) -> None:
        self.repository = repository
        self.config = config

    async def handle(self, command: DeletePluginCommand) -> ServiceResult[bool]:
        """Handle plugin deletion command.

        Args:
            command: The plugin deletion command.

        Returns:
            ServiceResult indicating deletion success.

        """
        try:
            success = await self.repository.delete(command.plugin_id)
            if not success:
                return ServiceResult.fail(f"Plugin {command.plugin_id} not found")

            return ServiceResult.ok(True)
        except (ValueError, KeyError, RuntimeError) as e:
            return ServiceResult.fail(f"Failed to delete plugin: {e!s}")


class GetSystemInfoHandler(CommandHandler[GetSystemInfoCommand, dict]):
    """Get system info handler."""

    def __init__(self, config: APIConfig) -> None:
        self.config = config

    async def handle(self, command: GetSystemInfoCommand) -> ServiceResult[dict]:
        """Handle get system info command.

        Args:
            command: The get system info command.

        Returns:
            ServiceResult containing system information.

        """
        try:
            system_info = {
                "api_version": self.config.version,
                "api_title": self.config.title,
                "api_description": self.config.description,
                "environment": (
                    "development" if self.config.is_development else "production"
                ),
                "features": {
                    "websocket": self.config.websocket_enabled,
                    "metrics": self.config.metrics_enabled,
                    "cache": self.config.cache_enabled,
                    "rate_limiting": self.config.rate_limit_enabled,
                },
            }

            return ServiceResult.ok(system_info)
        except (ValueError, RuntimeError, OSError) as e:
            return ServiceResult.fail(f"Failed to get system info: {e!s}")


class GetSystemHealthHandler(CommandHandler[GetSystemHealthCommand, dict]):
    """Get system health handler."""

    def __init__(self, health_service: HealthCheckService, config: APIConfig) -> None:
        self.health_service = health_service
        self.config = config

    async def handle(self, command: GetSystemHealthCommand) -> ServiceResult[dict]:
        """Handle get system health command.

        Args:
            command: The get system health command.

        Returns:
            ServiceResult containing system health status.

        """
        try:
            health_status = await self.health_service.check_health()

            return ServiceResult.ok(health_status)
        except (ValueError, RuntimeError, OSError, ConnectionError) as e:
            return ServiceResult.fail(f"Failed to check system health: {e!s}")
