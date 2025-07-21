"""Tests for FLEXT API domain ports (interfaces)."""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from flext_core.domain.types import ServiceResult

from flext_api.domain.ports import (
    APIAuthenticationService,
    APIResponseBuilder,
    AuditService,
    AuthService,
    CacheService,
    HealthCheckService,
    MetricsService,
    NotificationService,
    PipelineExecutionService,
    PipelineRepository,
    PluginManagementService,
    PluginRepository,
    RateLimitService,
    RequestRepository,
    ResponseRepository,
    ServerService,
    ValidationService,
    WebFrameworkService,
)

if TYPE_CHECKING:
    from flext_api.domain.entities import APIPipeline as Pipeline, Plugin


class TestRepositoryPorts:
    """Test repository port interfaces."""

    def test_pipeline_repository_is_abstract(self) -> None:
        """Test PipelineRepository is an abstract interface."""
        assert hasattr(PipelineRepository, "__abstractmethods__")
        assert len(PipelineRepository.__abstractmethods__) > 0

    def test_pipeline_repository_required_methods(self) -> None:
        """Test PipelineRepository defines required methods."""
        required_methods = ["save", "get", "list", "delete"]

        for method_name in required_methods:
            assert hasattr(PipelineRepository, method_name), (
                f"PipelineRepository missing {method_name} method"
            )

    def test_plugin_repository_is_abstract(self) -> None:
        """Test PluginRepository is an abstract interface."""
        assert hasattr(PluginRepository, "__abstractmethods__")
        assert len(PluginRepository.__abstractmethods__) > 0

    def test_plugin_repository_required_methods(self) -> None:
        """Test PluginRepository defines required methods."""
        required_methods = ["save", "get", "list", "delete"]

        for method_name in required_methods:
            assert hasattr(PluginRepository, method_name), (
                f"PluginRepository missing {method_name} method"
            )

    def test_request_repository_is_abstract(self) -> None:
        """Test RequestRepository is an abstract interface."""
        assert hasattr(RequestRepository, "__abstractmethods__")
        assert len(RequestRepository.__abstractmethods__) > 0

    def test_response_repository_is_abstract(self) -> None:
        """Test ResponseRepository is an abstract interface."""
        assert hasattr(ResponseRepository, "__abstractmethods__")
        assert len(ResponseRepository.__abstractmethods__) > 0


class TestServicePorts:
    """Test service port interfaces."""

    def test_auth_service_is_abstract(self) -> None:
        """Test AuthService is an abstract interface."""
        assert hasattr(AuthService, "__abstractmethods__")
        assert len(AuthService.__abstractmethods__) > 0

    def test_auth_service_required_methods(self) -> None:
        """Test AuthService defines required methods."""
        required_methods = [
            "authenticate",
            "authorize",
            "generate_token",
            "validate_token",
        ]

        for method_name in required_methods:
            assert hasattr(AuthService, method_name), (
                f"AuthService missing {method_name} method"
            )

    def test_cache_service_is_abstract(self) -> None:
        """Test CacheService is an abstract interface."""
        assert hasattr(CacheService, "__abstractmethods__")
        assert len(CacheService.__abstractmethods__) > 0

    def test_cache_service_required_methods(self) -> None:
        """Test CacheService defines required methods."""
        required_methods = ["get", "set", "delete", "clear"]

        for method_name in required_methods:
            assert hasattr(CacheService, method_name), (
                f"CacheService missing {method_name} method"
            )

    def test_health_check_service_is_abstract(self) -> None:
        """Test HealthCheckService is an abstract interface."""
        assert hasattr(HealthCheckService, "__abstractmethods__")
        assert len(HealthCheckService.__abstractmethods__) > 0

    def test_metrics_service_is_abstract(self) -> None:
        """Test MetricsService is an abstract interface."""
        assert hasattr(MetricsService, "__abstractmethods__")
        assert len(MetricsService.__abstractmethods__) > 0

    def test_validation_service_is_abstract(self) -> None:
        """Test ValidationService is an abstract interface."""
        assert hasattr(ValidationService, "__abstractmethods__")
        assert len(ValidationService.__abstractmethods__) > 0


class TestManagementServicePorts:
    """Test management service port interfaces."""

    def test_pipeline_execution_service_is_abstract(self) -> None:
        """Test PipelineExecutionService is an abstract interface."""
        assert hasattr(PipelineExecutionService, "__abstractmethods__")
        assert len(PipelineExecutionService.__abstractmethods__) > 0

    def test_pipeline_execution_service_required_methods(self) -> None:
        """Test PipelineExecutionService defines required methods."""
        required_methods = [
            "execute_pipeline",
            "get_execution_status",
            "cancel_execution",
        ]

        for method_name in required_methods:
            assert hasattr(PipelineExecutionService, method_name), (
                f"PipelineExecutionService missing {method_name} method"
            )

    def test_plugin_management_service_is_abstract(self) -> None:
        """Test PluginManagementService is an abstract interface."""
        assert hasattr(PluginManagementService, "__abstractmethods__")
        assert len(PluginManagementService.__abstractmethods__) > 0

    def test_plugin_management_service_required_methods(self) -> None:
        """Test PluginManagementService defines required methods."""
        required_methods = [
            "install_plugin",
            "uninstall_plugin",
            "update_plugin_config",
        ]

        for method_name in required_methods:
            assert hasattr(PluginManagementService, method_name), (
                f"PluginManagementService missing {method_name} method"
            )


class TestExternalServicePorts:
    """Test external service port interfaces."""

    def test_notification_service_is_abstract(self) -> None:
        """Test NotificationService is an abstract interface."""
        assert hasattr(NotificationService, "__abstractmethods__")
        assert len(NotificationService.__abstractmethods__) > 0

    def test_audit_service_is_abstract(self) -> None:
        """Test AuditService is an abstract interface."""
        assert hasattr(AuditService, "__abstractmethods__")
        assert len(AuditService.__abstractmethods__) > 0


class TestAPIServicePorts:
    """Test API service port interfaces."""

    def test_api_authentication_service_is_abstract(self) -> None:
        """Test APIAuthenticationService is an abstract interface."""
        assert hasattr(APIAuthenticationService, "__abstractmethods__")
        assert len(APIAuthenticationService.__abstractmethods__) > 0

    def test_api_response_builder_is_abstract(self) -> None:
        """Test APIResponseBuilder is an abstract interface."""
        assert hasattr(APIResponseBuilder, "__abstractmethods__")
        assert len(APIResponseBuilder.__abstractmethods__) > 0


class TestPortImplementation:
    """Test port implementations work correctly."""

    def test_auth_service_implementation(self) -> None:
        """Test AuthService can be implemented."""

        class MockAuthService(AuthService):
            """Mock implementation of AuthService."""

            async def authenticate(self, token: str) -> dict[str, Any] | None:
                if token == "valid_token":
                    return {"user_id": "123", "username": "test_user"}
                return None

            async def authorize(
                self,
                user_id: UUID,
                resource: str,
                action: str,
            ) -> bool:
                return str(user_id) == "123"

            async def generate_token(self, user_data: dict[str, Any]) -> str:
                return f"token_for_{user_data.get('username', 'unknown')}"

            async def validate_token(self, token: str) -> dict[str, Any] | None:
                return await self.authenticate(token)

        # Should be able to instantiate
        auth_service = MockAuthService()
        assert isinstance(auth_service, AuthService)

    def test_pipeline_repository_implementation(self) -> None:
        """Test PipelineRepository can be implemented."""

        class MockPipelineRepository(PipelineRepository):
            def __init__(self) -> None:
                self._storage: dict[UUID, Pipeline] = {}

            async def create(self, pipeline: Pipeline) -> ServiceResult[Pipeline]:
                self._storage[pipeline.id] = pipeline
                return ServiceResult.ok(pipeline)

            async def update(self, pipeline: Pipeline) -> ServiceResult[Pipeline]:
                if pipeline.id in self._storage:
                    self._storage[pipeline.id] = pipeline
                    return ServiceResult.ok(pipeline)
                return ServiceResult.fail(f"Pipeline {pipeline.id} not found")

            async def count(
                self,
                owner_id: UUID | None = None,
                project_id: UUID | None = None,
                status: str | None = None,
            ) -> ServiceResult[int]:
                return ServiceResult.ok(len(self._storage))

            async def get(self, pipeline_id: UUID) -> ServiceResult[Pipeline]:
                pipeline = self._storage.get(pipeline_id)
                if pipeline:
                    return ServiceResult.ok(pipeline)
                return ServiceResult.fail(f"Pipeline {pipeline_id} not found")

            async def list(
                self,
                limit: int = 20,
                offset: int = 0,
                owner_id: UUID | None = None,
                project_id: UUID | None = None,
                status: str | None = None,
            ) -> ServiceResult[list[Pipeline]]:
                pipelines = list(self._storage.values())[offset : offset + limit]
                return ServiceResult.ok(pipelines)

            async def delete(self, pipeline_id: UUID) -> ServiceResult[bool]:
                if pipeline_id in self._storage:
                    del self._storage[pipeline_id]
                    return ServiceResult.ok(True)
                return ServiceResult.ok(False)

        # Should be able to instantiate
        repo = MockPipelineRepository()
        assert isinstance(repo, PipelineRepository)

    def test_plugin_repository_implementation(self) -> None:
        """Test PluginRepository can be implemented."""

        class MockPluginRepository(PluginRepository):
            def __init__(self) -> None:
                self._storage: dict[UUID, Plugin] = {}

            async def create(self, plugin: Plugin) -> ServiceResult[Plugin]:
                self._storage[plugin.id] = plugin
                return ServiceResult.ok(plugin)

            async def update(self, plugin: Plugin) -> ServiceResult[Plugin]:
                if plugin.id in self._storage:
                    self._storage[plugin.id] = plugin
                    return ServiceResult.ok(plugin)
                return ServiceResult.fail(f"Plugin {plugin.id} not found")

            async def count(
                self,
                plugin_type: str | None = None,
                status: str | None = None,
            ) -> ServiceResult[int]:
                return ServiceResult.ok(len(self._storage))

            async def get(self, plugin_id: UUID) -> ServiceResult[Plugin]:
                plugin = self._storage.get(plugin_id)
                if plugin:
                    return ServiceResult.ok(plugin)
                return ServiceResult.fail(f"Plugin {plugin_id} not found")

            async def list(
                self,
                limit: int = 20,
                offset: int = 0,
                plugin_type: str | None = None,
                status: str | None = None,
            ) -> ServiceResult[list[Plugin]]:
                """List plugins with pagination and filtering."""
                # Create filtered list without modifying storage
                plugins = list(self._storage.values())

                # Filter by plugin type if provided
                if plugin_type:
                    plugins = [p for p in plugins if p.plugin_type == plugin_type]

                # Filter by status if provided (map to enabled for now)
                if status is not None:
                    # Simple status mapping: "active" -> enabled=True, others -> enabled=False
                    enabled_filter = status.lower() == "active"
                    plugins = [p for p in plugins if p.enabled == enabled_filter]

                # Apply pagination
                paginated_plugins = plugins[offset : offset + limit]
                return ServiceResult.ok(paginated_plugins)

            async def delete(self, plugin_id: UUID) -> ServiceResult[bool]:
                if plugin_id in self._storage:
                    self._storage.pop(plugin_id)
                    return ServiceResult.ok(True)
                return ServiceResult.ok(False)

        # Should be able to instantiate
        repo = MockPluginRepository()
        assert isinstance(repo, PluginRepository)

    def test_cache_service_implementation(self) -> None:
        """Test CacheService can be implemented."""

        class MockCacheService(CacheService):
            def __init__(self) -> None:
                self._cache: dict[str, str | bytes | dict[str, object]] = {}

            async def get(self, key: str) -> str | None:
                value = self._cache.get(key)
                return str(value) if value is not None else None

            async def set(
                self,
                key: str,
                value: str | bytes | dict[str, object],
                ttl: int | None = None,
            ) -> bool:
                self._cache[key] = value
                return True

            async def delete(self, key: str) -> bool:
                return self._cache.pop(key, None) is not None

            async def clear(self) -> bool:
                self._cache.clear()
                return True

        # Should be able to instantiate
        cache_service = MockCacheService()
        assert isinstance(cache_service, CacheService)

    def test_health_check_service_implementation(self) -> None:
        """Test HealthCheckService can be implemented."""

        class MockHealthCheckService(HealthCheckService):
            async def check_health(self) -> dict[str, str]:
                return {"status": "healthy", "timestamp": "2025-01-01T00:00:00Z"}

            async def check_database(self) -> bool:
                return True

            async def check_cache(self) -> bool:
                return True

            async def check_dependencies(self) -> dict[str, dict[str, str]]:
                return {
                    "database": {"status": "healthy"},
                    "cache": {"status": "healthy"},
                }

        # Should be able to instantiate
        health_service = MockHealthCheckService()
        assert isinstance(health_service, HealthCheckService)


class TestPortMocking:
    """Test port interfaces can be properly mocked."""

    @pytest.mark.asyncio
    async def test_auth_service_mock_implementation(self) -> None:
        """Test AuthService mock implementation works."""
        from uuid import UUID  # Local import for nested class scope

        class TestAuthService(AuthService):
            async def authenticate(self, token: str) -> dict[str, Any] | None:
                return (
                    {"user_id": "test_user", "roles": ["user"]}
                    if token == "valid"
                    else None
                )

            async def authorize(
                self,
                user_id: UUID,
                resource: str,
                action: str,
            ) -> bool:
                return str(
                    user_id,
                ) == "12345678-1234-5678-1234-567812345678" and action in {
                    "read",
                    "list",
                }

            async def generate_token(self, user_data: dict[str, Any]) -> str:
                return f"generated_token_{user_data.get('user_id')}"

            async def validate_token(self, token: str) -> dict[str, Any] | None:
                return await self.authenticate(token)

        service = TestAuthService()

        # Test authenticate
        result = await service.authenticate("valid")
        assert result is not None
        assert result["user_id"] == "test_user"

        invalid_result = await service.authenticate("invalid")
        assert invalid_result is None

        # Test authorize

        test_user_uuid = UUID("12345678-1234-5678-1234-567812345678")
        authorized = await service.authorize(test_user_uuid, "pipelines", "read")
        assert authorized is True

        unauthorized = await service.authorize(test_user_uuid, "REDACTED_LDAP_BIND_PASSWORD", "delete")
        assert unauthorized is False

        # Test generate_token
        token = await service.generate_token({"user_id": "test_user"})
        assert token == "generated_token_test_user"

        # Test validate_token
        validated = await service.validate_token("valid")
        assert validated is not None
        assert validated["user_id"] == "test_user"

    @pytest.mark.asyncio
    async def test_cache_service_mock_implementation(self) -> None:
        """Test CacheService mock implementation works."""

        class TestCacheService(CacheService):
            def __init__(self) -> None:
                self._cache: dict[str, str | bytes | dict[str, object]] = {
                    "initial_key": "initial_value",
                }

            async def get(self, key: str) -> str | None:
                value = self._cache.get(key)
                return str(value) if value is not None else None

            async def set(
                self,
                key: str,
                value: str | bytes | dict[str, object],
                ttl: int | None = None,
            ) -> bool:
                self._cache[key] = value
                return True

            async def delete(self, key: str) -> bool:
                return self._cache.pop(key, None) is not None

            async def clear(self) -> bool:
                self._cache.clear()
                return True

        service = TestCacheService()

        # Test get with existing key
        value = await service.get("initial_key")
        assert value == "initial_value"

        # Test get with missing key
        value = await service.get("nonexistent")
        assert value is None

        # Test set
        result = await service.set("new_key", "new_value")
        assert result is True
        value = await service.get("new_key")
        assert value == "new_value"

        # Test delete
        result = await service.delete("new_key")
        assert result is True
        value = await service.get("new_key")
        assert value is None

        # Test clear
        result = await service.clear()
        assert result is True
        value = await service.get("initial_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_pipeline_execution_service_mock_implementation(self) -> None:
        """Test PipelineExecutionService mock implementation works."""

        class TestPipelineExecutionService(PipelineExecutionService):
            def __init__(self) -> None:
                self._executions: dict[str, dict[str, object]] = {}

            async def execute_pipeline(
                self,
                pipeline_id: UUID,
                config: dict[str, str] | None = None,
            ) -> ServiceResult[str]:
                execution_id = f"exec_{pipeline_id}_{len(self._executions)}"
                self._executions[execution_id] = {
                    "pipeline_id": pipeline_id,
                    "status": "running",
                    "config": config,
                }
                return ServiceResult.ok(execution_id)

            async def get_execution_status(
                self,
                execution_id: str,
            ) -> ServiceResult[dict[str, str]]:
                """Get execution status."""
                if execution_id in self._executions:
                    execution_data = self._executions[execution_id]
                    # Convert to dict[str, str] as expected by interface
                    status_dict = {k: str(v) for k, v in execution_data.items()}
                    return ServiceResult.ok(status_dict)
                return ServiceResult.fail(f"Execution {execution_id} not found")

            async def cancel_execution(
                self,
                execution_id: str,
            ) -> ServiceResult[bool]:
                """Cancel execution."""
                if execution_id in self._executions:
                    self._executions[execution_id]["status"] = "cancelled"
                    return ServiceResult.ok(True)
                return ServiceResult.fail(f"Execution {execution_id} not found")

        service = TestPipelineExecutionService()

        # Test execute_pipeline
        pipeline_id = uuid4()
        result = await service.execute_pipeline(pipeline_id, {"param": "value"})
        assert result.is_success
        execution_id = result.unwrap()
        assert execution_id.startswith(f"exec_{pipeline_id}")

        # Test get_execution_status
        status_result = await service.get_execution_status(execution_id)
        assert status_result.is_success
        status = status_result.unwrap()
        assert status["pipeline_id"] == str(pipeline_id)
        assert status["status"] == "running"
        assert status["config"] == str({"param": "value"})

        # Test cancel_execution
        cancel_result = await service.cancel_execution(execution_id)
        assert cancel_result.is_success
        assert cancel_result.unwrap() is True

        # Verify cancellation
        status_result = await service.get_execution_status(execution_id)
        status = status_result.unwrap()
        assert status["status"] == "cancelled"


class TestPortInteroperability:
    """Test ports work together properly."""

    @pytest.mark.asyncio
    async def test_ports_can_be_mocked_together(self) -> None:
        """Test that all ports can be mocked and used together."""
        # Create mock implementations
        auth_service = Mock(spec=AuthService)
        auth_service.authenticate = AsyncMock(return_value={"user_id": "test"})
        auth_service.authorize = AsyncMock(return_value=True)

        pipeline_repo = Mock(spec=PipelineRepository)
        pipeline_repo.list = AsyncMock(return_value=[])

        plugin_repo = Mock(spec=PluginRepository)
        plugin_repo.list = AsyncMock(return_value=[])

        cache_service = Mock(spec=CacheService)
        cache_service.get = AsyncMock(return_value="cached_value")

        health_service = Mock(spec=HealthCheckService)
        health_service.check_health = AsyncMock(return_value={"status": "healthy"})

        # Test they can all be used together
        user = await auth_service.authenticate("token")
        assert user["user_id"] == "test"

        authorized = await auth_service.authorize("test", "resource", "action")
        assert authorized is True

        pipelines = await pipeline_repo.list()
        assert pipelines == []

        plugins = await plugin_repo.list()
        assert plugins == []

        cached_value = await cache_service.get("key")
        assert cached_value == "cached_value"

        health = await health_service.check_health()
        assert health["status"] == "healthy"

        # Verify all mocks were called
        auth_service.authenticate.assert_called_once()
        auth_service.authorize.assert_called_once()
        pipeline_repo.list.assert_called_once()
        plugin_repo.list.assert_called_once()
        cache_service.get.assert_called_once()
        health_service.check_health.assert_called_once()

    def test_port_inheritance_hierarchy(self) -> None:
        """Test port inheritance hierarchy is correct."""
        # All ports should inherit from ABC
        ports = [
            AuthService,
            PipelineRepository,
            PluginRepository,
            CacheService,
            HealthCheckService,
            MetricsService,
            ValidationService,
            PipelineExecutionService,
            PluginManagementService,
            RequestRepository,
            ResponseRepository,
            RateLimitService,
            ServerService,
            WebFrameworkService,
            NotificationService,
            AuditService,
            APIAuthenticationService,
            APIResponseBuilder,
        ]

        for port in ports:
            assert issubclass(port, ABC), f"{port.__name__} should inherit from ABC"
            assert hasattr(port, "__abstractmethods__"), (
                f"{port.__name__} should have abstract methods"
            )


class TestPortContractValidation:
    """Test port contract validation."""

    def test_abstract_methods_cannot_be_instantiated(self) -> None:
        """Test abstract ports cannot be instantiated directly."""
        abstract_ports = [
            AuthService,
            PipelineRepository,
            PluginRepository,
            CacheService,
            HealthCheckService,
        ]

        for port_class in abstract_ports:
            with pytest.raises(TypeError):
                port_class()  # Should raise TypeError due to abstract methods

    def test_concrete_implementations_can_be_instantiated(self) -> None:
        """Test concrete implementations can be instantiated."""

        class ConcreteAuthService(AuthService):
            async def authenticate(self, token: str) -> None:
                return None

            async def authorize(
                self,
                user_id: UUID,
                resource: str,
                action: str,
            ) -> bool:
                return False

            async def generate_token(self, user_data: dict[str, object]) -> str:
                return "token"

            async def validate_token(self, token: str) -> dict[str, object] | None:
                return None

        class ConcreteCacheService(CacheService):
            async def get(self, key: str) -> str | None:
                return None

            async def set(
                self,
                key: str,
                value: str | bytes | dict[str, object],
                ttl: int | None = None,
            ) -> bool:
                return True

            async def delete(self, key: str) -> bool:
                return True

            async def clear(self) -> bool:
                return True

        # These should instantiate without error
        auth_service = ConcreteAuthService()
        assert isinstance(auth_service, AuthService)

        cache_service = ConcreteCacheService()
        assert isinstance(cache_service, CacheService)

    def test_incomplete_implementations_cannot_be_instantiated(self) -> None:
        """Test incomplete implementations cannot be instantiated."""

        class IncompleteAuthService(AuthService):
            async def authenticate(self, token: str) -> dict[str, Any] | None:
                return None

            # Missing other required methods: authorize, generate_token, validate_token

        class IncompleteCacheService(CacheService):
            async def get(self, key: str) -> str | None:
                return None

            # Missing other required methods: set, delete, clear

        # These should raise TypeError due to missing abstract methods
        with pytest.raises(TypeError, match="abstract"):
            IncompleteAuthService()  # type: ignore[abstract]

        with pytest.raises(TypeError, match="abstract"):
            IncompleteCacheService()  # type: ignore[abstract]
