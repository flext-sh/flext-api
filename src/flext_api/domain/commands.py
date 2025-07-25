"""Command objects for FLEXT API implementing CQRS pattern.

SINGLE RESPONSIBILITY PRINCIPLE: Each command has one clear responsibility.
Commands represent write operations that modify system state.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from uuid import UUID

    from flext_core import FlextResult

# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Command Base Class
# ==============================================================================


class Command(ABC):
    """Base class for all commands (SRP compliance)."""

    @abstractmethod
    def validate_command(self) -> bool:
        """Validate command command parameters."""

    @abstractmethod
    def get_command_type(self) -> str:
        """Get command type identifier."""


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Pipeline Commands
# ==============================================================================


class CreatePipelineCommand(BaseModel, Command):
    """Command to create a new pipeline (SRP compliance)."""

    name: str = Field(..., min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    config: dict[str, Any] = Field(default_factory=dict)
    owner_id: UUID | None = None
    project_id: UUID | None = None

    def validate_command(self) -> bool:
        """Validate command create pipeline command."""
        return (
            len(self.name.strip()) >= 3
            and (self.description is None or len(self.description) <= 500)
            and isinstance(self.config, dict)
        )

    def get_command_type(self) -> str:
        """Get command type."""
        return "create_pipeline"


class UpdatePipelineCommand(BaseModel, Command):
    """Command to update an existing pipeline (SRP compliance)."""

    pipeline_id: UUID
    name: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = Field(None, max_length=500)
    config: dict[str, Any] | None = None
    status: str | None = None

    def validate_command(self) -> bool:
        """Validate command update pipeline command."""
        return (
            (self.name is None or len(self.name.strip()) >= 3)
            and (self.description is None or len(self.description) <= 500)
            and (self.config is None or isinstance(self.config, dict))
        )

    def get_command_type(self) -> str:
        """Get command type."""
        return "update_pipeline"


class DeletePipelineCommand(BaseModel, Command):
    """Command to delete a pipeline (SRP compliance)."""

    pipeline_id: UUID
    force: bool = False  # Whether to force delete even if pipeline is running

    def validate_command(self) -> bool:
        """Validate command delete pipeline command."""
        return True  # Simple validation - pipeline_id is required by Pydantic

    def get_command_type(self) -> str:
        """Get command type."""
        return "delete_pipeline"


class ExecutePipelineCommand(BaseModel, Command):
    """Command to execute a pipeline (SRP compliance)."""

    pipeline_id: UUID
    execution_params: dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10)  # 1=highest, 10=lowest

    def validate_command(self) -> bool:
        """Validate command execute pipeline command."""
        return isinstance(self.execution_params, dict) and 1 <= self.priority <= 10

    def get_command_type(self) -> str:
        """Get command type."""
        return "execute_pipeline"


# ==============================================================================
# SINGLE RESPONSIBILITY PRINCIPLE: Plugin Commands
# ==============================================================================


class RegisterPluginCommand(BaseModel, Command):
    """Command to register a new plugin (SRP compliance)."""

    name: str = Field(..., min_length=1, max_length=100)
    plugin_type: str
    version: str = Field(..., min_length=1)
    description: str | None = Field(None, max_length=500)
    config_schema: dict[str, Any] = Field(default_factory=dict)
    entry_point: str = Field(..., min_length=1)

    def validate_command(self) -> bool:
        """Validate command register plugin command."""
        return (
            len(self.name.strip()) >= 1
            and len(self.plugin_type.strip()) >= 1
            and len(self.version.strip()) >= 1
            and len(self.entry_point.strip()) >= 1
            and isinstance(self.config_schema, dict)
        )

    def get_command_type(self) -> str:
        """Get command type."""
        return "register_plugin"


class UnregisterPluginCommand(BaseModel, Command):
    """Command to unregister a plugin (SRP compliance)."""

    plugin_id: UUID
    force: bool = False  # Whether to force unregister even if plugin is in use

    def validate_command(self) -> bool:
        """Validate command unregister plugin command."""
        return True  # Simple validation - plugin_id is required by Pydantic

    def get_command_type(self) -> str:
        """Get command type."""
        return "unregister_plugin"


# ==============================================================================
# DEPENDENCY INVERSION PRINCIPLE: Command Handler Interface
# ==============================================================================


class CommandHandler(ABC):
    """Interface for command handlers (DIP compliance)."""

    @abstractmethod
    async def handle(self, command: Command) -> FlextResult[Any]:
        """Handle a command and return result."""

    @abstractmethod
    def can_handle(self, command: Command) -> bool:
        """Check if this handler can process the command."""


# Export all commands for use in application layer
__all__ = [
    "Command",
    "CommandHandler",
    "CreatePipelineCommand",
    "DeletePipelineCommand",
    "ExecutePipelineCommand",
    "RegisterPluginCommand",
    "UnregisterPluginCommand",
    "UpdatePipelineCommand",
]
