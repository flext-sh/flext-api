#!/usr/bin/env python3
"""Tests for FlextApi Application Helpers - Validação real sem mocks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Testes robustos para helpers de aplicação com foco em redução massiva de código.
"""

import asyncio
from datetime import datetime
from typing import Any, Never

import pytest
from flext_core import FlextResult

from flext_api.helpers.flext_api_application import (
    FlextApiContextManager,
    FlextApiCrudHelper,
    FlextApiCrudOperations,
    FlextApiHealthCheck,
    FlextApiRequestContext,
    FlextApiServiceBase,
    FlextApiServiceResponse,
    FlextApiValidationChain,
    flext_api_auto_response,
    flext_api_cache_result,
    flext_api_create_context_manager,
    flext_api_create_crud_helper,
    flext_api_create_service_base,
    flext_api_request_logging,
    flext_api_require_auth,
    flext_api_transaction_scope,
)


class TestFlextApiCrudHelper:
    """Testes para FlextApiCrudHelper - helper para operações CRUD."""

    def test_crud_helper_initialization(self) -> None:
        """Testa inicialização do helper CRUD."""
        helper = FlextApiCrudHelper("users")

        assert helper.entity_name == "users"

    def test_create_response(self) -> None:
        """Testa criação de resposta de criação."""
        helper = FlextApiCrudHelper("users")

        user_data = {"id": 1, "name": "Test User", "email": "test@example.com"}
        response = helper.flext_api_create_response(user_data)

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"] == user_data
        assert response["errors"] == []
        assert response["metadata"]["operation"] == "create"
        assert response["metadata"]["entity"] == "users"
        assert response["metadata"]["created_id"] == 1

    def test_list_response_basic(self) -> None:
        """Testa criação de resposta de listagem básica."""
        helper = FlextApiCrudHelper("users")

        items = [
            {"id": 1, "name": "User 1"},
            {"id": 2, "name": "User 2"},
            {"id": 3, "name": "User 3"},
        ]

        response = helper.flext_api_list_response(items)

        assert response["success"] is True
        assert response["data"]["items"] == items
        assert response["data"]["pagination"]["total"] == 3
        assert response["data"]["pagination"]["page"] == 1
        assert response["data"]["pagination"]["page_size"] == 20
        assert response["data"]["pagination"]["pages"] == 1
        assert response["metadata"]["count"] == 3

    def test_list_response_with_pagination(self) -> None:
        """Testa criação de resposta de listagem com paginação."""
        helper = FlextApiCrudHelper("products")

        items = [{"id": i, "name": f"Product {i}"} for i in range(1, 11)]

        response = helper.flext_api_list_response(
            items,
            total=100,
            page=2,
            page_size=10,
        )

        assert response["data"]["pagination"]["total"] == 100
        assert response["data"]["pagination"]["page"] == 2
        assert response["data"]["pagination"]["page_size"] == 10
        assert response["data"]["pagination"]["pages"] == 10

    def test_error_response(self) -> None:
        """Testa criação de resposta de erro."""
        helper = FlextApiCrudHelper("orders")

        response = helper.flext_api_error_response("Order not found", "get")

        assert response["success"] is False
        assert response["data"] is None
        assert response["errors"] == ["Order not found"]
        assert response["metadata"]["operation"] == "get"
        assert response["metadata"]["entity"] == "orders"


class TestFlextApiContextManager:
    """Testes para FlextApiContextManager - gerenciador de contexto."""

    def test_context_manager_initialization(self) -> None:
        """Testa inicialização do gerenciador de contexto."""
        manager = FlextApiContextManager()

        assert isinstance(manager._contexts, dict)
        assert len(manager._contexts) == 0

    def test_create_context_basic(self) -> None:
        """Testa criação de contexto básico."""
        manager = FlextApiContextManager()

        context = manager.flext_api_create_context(
            request_id="req-123",
            user_id="user-456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        assert isinstance(context, dict)
        assert context["request_id"] == "req-123"
        assert context["user_id"] == "user-456"
        assert context["correlation_id"] == "req-123"  # Default to request_id
        assert context["ip_address"] == "192.168.1.1"
        assert context["user_agent"] == "Mozilla/5.0"
        assert context["timestamp"] is not None

    def test_create_context_with_correlation_id(self) -> None:
        """Testa criação de contexto com correlation_id personalizado."""
        manager = FlextApiContextManager()

        context = manager.flext_api_create_context(
            request_id="req-123",
            correlation_id="corr-789",
        )

        assert context["request_id"] == "req-123"
        assert context["correlation_id"] == "corr-789"

    def test_get_context(self) -> None:
        """Testa obtenção de contexto existente."""
        manager = FlextApiContextManager()

        # Criar contexto
        original_context = manager.flext_api_create_context("req-123")

        # Obter contexto
        retrieved_context = manager.flext_api_get_context("req-123")

        assert retrieved_context == original_context

    def test_get_nonexistent_context(self) -> None:
        """Testa obtenção de contexto inexistente."""
        manager = FlextApiContextManager()

        context = manager.flext_api_get_context("nonexistent")

        assert context is None

    def test_cleanup_context(self) -> None:
        """Testa limpeza de contexto."""
        manager = FlextApiContextManager()

        # Criar contexto
        manager.flext_api_create_context("req-123")
        assert manager.flext_api_get_context("req-123") is not None

        # Limpar contexto
        manager.flext_api_cleanup_context("req-123")
        assert manager.flext_api_get_context("req-123") is None


class TestFlextApiServiceBase:
    """Testes para FlextApiServiceBase - base para serviços."""

    def test_service_base_initialization(self) -> None:
        """Testa inicialização do serviço base."""
        service = FlextApiServiceBase("user-service")

        assert service.service_name == "user-service"
        assert service._start_time is not None

    @pytest.mark.asyncio
    async def test_execute_with_context_sync_function(self) -> None:
        """Testa execução com contexto para função síncrona."""
        service = FlextApiServiceBase("test-service")

        def sync_operation(data: dict[str, Any]) -> str:
            return f"Processed: {data}"

        context = FlextApiRequestContext(
            user_id="user-123",
            correlation_id="corr-456",
            request_id="req-789",
            ip_address="127.0.0.1",
            user_agent="test",
            timestamp=datetime.now().isoformat(),
        )

        result = await service.flext_api_execute_with_context(
            sync_operation,
            context,
            "test data",
        )

        assert result.is_success
        assert result.data == "Processed: test data"

    @pytest.mark.asyncio
    async def test_execute_with_context_async_function(self) -> None:
        """Testa execução com contexto para função assíncrona."""
        service = FlextApiServiceBase("test-service")

        async def async_operation(data: dict[str, Any]) -> str:
            await asyncio.sleep(0.01)
            return f"Async processed: {data}"

        context = FlextApiRequestContext(
            user_id="user-123",
            correlation_id="corr-456",
            request_id="req-789",
            ip_address="127.0.0.1",
            user_agent="test",
            timestamp=datetime.now().isoformat(),
        )

        result = await service.flext_api_execute_with_context(
            async_operation,
            context,
            "test data",
        )

        assert result.is_success
        assert result.data == "Async processed: test data"

    @pytest.mark.asyncio
    async def test_execute_with_context_error_handling(self) -> None:
        """Testa tratamento de erro na execução com contexto."""
        service = FlextApiServiceBase("test-service")

        def failing_operation() -> Never:
            msg = "Something went wrong"
            raise ValueError(msg)

        context = FlextApiRequestContext(
            user_id="user-123",
            correlation_id="corr-456",
            request_id="req-789",
            ip_address="127.0.0.1",
            user_agent="test",
            timestamp=datetime.now().isoformat(),
        )

        result = await service.flext_api_execute_with_context(
            failing_operation,
            context,
        )

        assert not result.is_success
        assert "Something went wrong" in result.error

    def test_health_check(self) -> None:
        """Testa health check do serviço."""
        service = FlextApiServiceBase("health-test")

        health = service.flext_api_health_check()

        assert isinstance(health, dict)
        assert health["status"] == "healthy"
        assert health["version"] == "1.0.0"
        assert health["uptime_seconds"] >= 0
        assert isinstance(health["dependencies"], dict)
        assert health["timestamp"] is not None


class TestFlextApiValidationChain:
    """Testes para FlextApiValidationChain - cadeia de validação."""

    def test_validation_chain_initialization(self) -> None:
        """Testa inicialização da cadeia de validação."""
        chain = FlextApiValidationChain("user")

        assert chain.entity_name == "user"
        assert isinstance(chain.validators, list)
        assert len(chain.validators) == 0
        assert isinstance(chain.errors, list)

    def test_add_custom_validator(self) -> None:
        """Testa adição de validador customizado."""
        chain = FlextApiValidationChain("product")

        def price_validator(data: dict[str, Any]) -> bool:
            return data.get("price", 0) > 0

        chain.flext_api_add_validator(price_validator, "Price must be positive")

        assert len(chain.validators) == 1

    def test_validate_required_fields_success(self) -> None:
        """Testa validação de campos obrigatórios com sucesso."""
        chain = FlextApiValidationChain("user")
        chain.flext_api_validate_required(["name", "email"])

        data = {
            "name": "Test User",
            "email": "test@example.com",
            "optional_field": "value",
        }

        result = chain.flext_api_execute(data)

        assert result.is_success
        assert result.data == data

    def test_validate_required_fields_failure(self) -> None:
        """Testa validação de campos obrigatórios com falha."""
        chain = FlextApiValidationChain("user")
        chain.flext_api_validate_required(["name", "email", "password"])

        data = {
            "name": "Test User",
            # email missing
            # password missing
        }

        result = chain.flext_api_execute(data)

        assert not result.is_success
        assert "email" in result.error
        assert "password" in result.error

    def test_validate_types_success(self) -> None:
        """Testa validação de tipos com sucesso."""
        chain = FlextApiValidationChain("product")
        chain.flext_api_validate_types(
            {
                "name": str,
                "price": (int, float),
                "active": bool,
            },
        )

        data = {
            "name": "Product 1",
            "price": 29.99,
            "active": True,
        }

        result = chain.flext_api_execute(data)

        assert result.is_success

    def test_validate_types_failure(self) -> None:
        """Testa validação de tipos com falha."""
        chain = FlextApiValidationChain("product")
        chain.flext_api_validate_types(
            {
                "name": str,
                "price": (int, float),
                "active": bool,
            },
        )

        data = {
            "name": 123,  # Should be string
            "price": "invalid",  # Should be number
            "active": "yes",  # Should be boolean
        }

        result = chain.flext_api_execute(data)

        assert not result.is_success
        assert "name" in result.error
        assert "price" in result.error
        assert "active" in result.error

    def test_complex_validation_chain(self) -> None:
        """Testa cadeia de validação complexa."""
        chain = FlextApiValidationChain("user")

        # Adicionar múltiplas validações
        chain.flext_api_validate_required(["name", "email", "age"])
        chain.flext_api_validate_types({"name": str, "age": int, "email": str})

        # Validador customizado para idade
        def age_validator(data: dict[str, Any]) -> bool:
            age = data.get("age", 0)
            if age < 18:
                chain.errors.append("User must be at least 18 years old")
                return False
            return True

        chain.flext_api_add_validator(age_validator, "Age validation failed")

        # Teste com dados válidos
        valid_data = {"name": "John Doe", "email": "john@example.com", "age": 25}
        result = chain.flext_api_execute(valid_data)
        assert result.is_success

        # Teste com idade inválida
        invalid_data = {"name": "Jane Doe", "email": "jane@example.com", "age": 16}
        result = chain.flext_api_execute(invalid_data)
        assert not result.is_success
        assert "18 years old" in result.error


class TestApplicationDecorators:
    """Testes para decorators específicos de aplicação."""

    @pytest.mark.asyncio
    async def test_auto_response_decorator_success(self) -> None:
        """Testa decorator auto_response com sucesso."""

        @flext_api_auto_response("user")
        async def create_user(name: str, email: str) -> dict[str, Any]:
            return {"id": 1, "name": name, "email": email}

        response = await create_user("Test User", "test@example.com")

        assert isinstance(response, dict)
        assert response["success"] is True
        assert response["data"]["name"] == "Test User"
        assert response["metadata"]["operation"] == "create_user"
        assert response["metadata"]["entity"] == "user"
        assert response["execution_time_ms"] >= 0

    @pytest.mark.asyncio
    async def test_auto_response_decorator_sync_function(self) -> None:
        """Testa decorator auto_response com função síncrona."""

        @flext_api_auto_response("product")
        def get_product(product_id: int) -> dict[str, Any]:
            return {"id": product_id, "name": f"Product {product_id}"}

        response = await get_product(123)

        assert response["success"] is True
        assert response["data"]["id"] == 123

    @pytest.mark.asyncio
    async def test_auto_response_decorator_error(self) -> None:
        """Testa decorator auto_response com erro."""

        @flext_api_auto_response("user")
        async def failing_function() -> Never:
            msg = "Something went wrong"
            raise ValueError(msg)

        response = await failing_function()

        assert response["success"] is False
        assert response["data"] is None
        assert "Something went wrong" in response["errors"][0]

    @pytest.mark.asyncio
    async def test_require_auth_decorator_success(self) -> None:
        """Testa decorator require_auth com autenticação válida."""

        @flext_api_require_auth(roles=["REDACTED_LDAP_BIND_PASSWORD", "user"])
        async def protected_function(context: dict[str, Any] | None = None) -> str:
            return "Access granted"

        context = {
            "user_id": "user-123",
            "roles": ["user"],
        }

        result = await protected_function(context=context)

        assert result == "Access granted"

    @pytest.mark.asyncio
    async def test_require_auth_decorator_no_auth(self) -> None:
        """Testa decorator require_auth sem autenticação."""

        @flext_api_require_auth()
        async def protected_function(context: dict[str, Any] | None = None) -> str:
            return "This should not execute"

        result = await protected_function(context=None)

        assert isinstance(result, FlextResult)
        assert not result.is_success
        assert "Authentication required" in result.error

    @pytest.mark.asyncio
    async def test_require_auth_decorator_insufficient_permissions(self) -> None:
        """Testa decorator require_auth com permissões insuficientes."""

        @flext_api_require_auth(roles=["REDACTED_LDAP_BIND_PASSWORD"])
        async def REDACTED_LDAP_BIND_PASSWORD_function(context: dict[str, Any] | None = None) -> str:
            return "Admin only"

        context = {
            "user_id": "user-123",
            "roles": ["user"],  # Doesn't have REDACTED_LDAP_BIND_PASSWORD role
        }

        result = await REDACTED_LDAP_BIND_PASSWORD_function(context=context)

        assert isinstance(result, FlextResult)
        assert not result.is_success
        assert "Insufficient permissions" in result.error

    @pytest.mark.asyncio
    async def test_cache_result_decorator(self) -> None:
        """Testa decorator cache_result."""
        call_count = 0

        @flext_api_cache_result(ttl_seconds=1)
        async def expensive_operation(value: str) -> str:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.01)  # Simula operação cara
            return f"Result: {value}"

        # Primeira chamada
        result1 = await expensive_operation("test")
        assert result1 == "Result: test"
        assert call_count == 1

        # Segunda chamada (deveria usar cache)
        result2 = await expensive_operation("test")
        assert result2 == "Result: test"
        assert call_count == 1  # Não incrementou

        # Terceira chamada com valor diferente
        result3 = await expensive_operation("other")
        assert result3 == "Result: other"
        assert call_count == 2


class TestAsyncContextManagers:
    """Testes para context managers assíncronos."""

    @pytest.mark.asyncio
    async def test_transaction_scope_success(self) -> None:
        """Testa transaction scope com sucesso."""
        async with flext_api_transaction_scope():
            # Operação bem-sucedida
            assert True

    @pytest.mark.asyncio
    async def test_transaction_scope_rollback(self) -> Never:
        """Testa transaction scope com rollback."""
        with pytest.raises(ValueError, match="Transaction should rollback"):
            async with flext_api_transaction_scope():
                msg = "Transaction should rollback"
                raise ValueError(msg)

    @pytest.mark.asyncio
    async def test_request_logging_success(self) -> None:
        """Testa request logging com sucesso."""
        async with flext_api_request_logging("req-123", "test_operation"):
            await asyncio.sleep(0.01)  # Simula operação

    @pytest.mark.asyncio
    async def test_request_logging_error(self) -> Never:
        """Testa request logging com erro."""
        with pytest.raises(RuntimeError):
            async with flext_api_request_logging("req-456", "failing_operation"):
                msg = "Operation failed"
                raise RuntimeError(msg)


class TestFactoryFunctions:
    """Testes para funções factory de aplicação."""

    def test_create_crud_helper_factory(self) -> None:
        """Testa factory de CRUD helper."""
        helper = flext_api_create_crud_helper("products")

        assert isinstance(helper, FlextApiCrudHelper)
        assert helper.entity_name == "products"

    def test_create_service_base_factory(self) -> None:
        """Testa factory de service base."""
        service = flext_api_create_service_base("notification-service")

        assert isinstance(service, FlextApiServiceBase)
        assert service.service_name == "notification-service"

    def test_create_context_manager_factory(self) -> None:
        """Testa factory de context manager."""
        manager = flext_api_create_context_manager()

        assert isinstance(manager, FlextApiContextManager)
        assert isinstance(manager._contexts, dict)


class TestTypedDictStructures:
    """Testes para estruturas TypedDict de aplicação."""

    def test_request_context_structure(self) -> None:
        """Testa estrutura FlextApiRequestContext."""
        context = FlextApiRequestContext(
            user_id="user-123",
            correlation_id="corr-456",
            request_id="req-789",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            timestamp="2025-01-25T10:00:00Z",
        )

        assert context["user_id"] == "user-123"
        assert context["correlation_id"] == "corr-456"
        assert context["request_id"] == "req-789"

    def test_service_response_structure(self) -> None:
        """Testa estrutura FlextApiServiceResponse."""
        response = FlextApiServiceResponse(
            success=True,
            data={"id": 1, "name": "Test"},
            errors=[],
            warnings=["Minor issue"],
            metadata={"operation": "create"},
            timestamp="2025-01-25T10:00:00Z",
            execution_time_ms=150.5,
        )

        assert response["success"] is True
        assert response["data"]["id"] == 1
        assert response["warnings"] == ["Minor issue"]
        assert response["execution_time_ms"] == 150.5

    def test_crud_operations_structure(self) -> None:
        """Testa estrutura FlextApiCrudOperations."""
        operations = FlextApiCrudOperations(
            create=True,
            read=True,
            update=True,
            delete=False,
            list=True,
            search=True,
        )

        assert operations["create"] is True
        assert operations["delete"] is False
        assert operations["search"] is True

    def test_health_check_structure(self) -> None:
        """Testa estrutura FlextApiHealthCheck."""
        health = FlextApiHealthCheck(
            status="healthy",
            version="1.0.0",
            uptime_seconds=3600.5,
            dependencies={"database": {"status": "ok"}},
            timestamp="2025-01-25T10:00:00Z",
        )

        assert health["status"] == "healthy"
        assert health["uptime_seconds"] == 3600.5
        assert health["dependencies"]["database"]["status"] == "ok"


class TestRealWorldApplicationScenarios:
    """Testes para cenários reais de aplicação."""

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(self) -> None:
        """Testa fluxo completo de CRUD com helpers."""
        # 1. Criar helper CRUD
        crud = flext_api_create_crud_helper("users")

        # 2. Criar contexto de requisição
        context_manager = flext_api_create_context_manager()
        context_manager.flext_api_create_context(
            request_id="req-123",
            user_id="REDACTED_LDAP_BIND_PASSWORD-456",
        )

        # 3. Criar validação
        validation = FlextApiValidationChain("user")
        validation.flext_api_validate_required(["name", "email"])
        validation.flext_api_validate_types({"name": str, "email": str})

        # 4. Validar dados
        user_data = {"name": "John Doe", "email": "john@example.com"}
        validation_result = validation.flext_api_execute(user_data)
        assert validation_result.is_success

        # 5. Criar resposta
        response = crud.flext_api_create_response(user_data)
        assert response["success"] is True

        # 6. Limpar contexto
        context_manager.flext_api_cleanup_context("req-123")

    @pytest.mark.asyncio
    async def test_service_layer_with_decorators(self) -> None:
        """Testa camada de serviço com decorators."""
        flext_api_create_service_base("user-service")

        @flext_api_auto_response("user")
        @flext_api_cache_result(ttl_seconds=1)
        async def get_user_profile(user_id: str) -> dict[str, Any]:
            # Simula busca de perfil
            await asyncio.sleep(0.01)
            return {"id": user_id, "name": f"User {user_id}", "profile": "complete"}

        # Primeira chamada
        response1 = await get_user_profile("123")
        assert response1["success"] is True
        assert response1["data"]["id"] == "123"

        # Segunda chamada (deveria usar cache)
        response2 = await get_user_profile("123")
        assert response2["success"] is True
        assert response2["data"] == response1["data"]

    @pytest.mark.asyncio
    async def test_context_aware_service_execution(self) -> None:
        """Testa execução de serviço com contexto."""
        service = flext_api_create_service_base("order-service")
        context_manager = flext_api_create_context_manager()

        # Criar contexto
        context = context_manager.flext_api_create_context(
            request_id="req-order-123",
            user_id="customer-456",
            correlation_id="order-flow-789",
        )

        # Operação de serviço
        async def process_order(order_data: dict[str, Any]) -> dict[str, Any]:
            await asyncio.sleep(0.01)  # Simula processamento
            return {"order_id": "order-123", "status": "processed", **order_data}

        # Executar com contexto
        result = await service.flext_api_execute_with_context(
            process_order,
            context,
            {"product_id": "prod-789", "quantity": 2},
        )

        assert result.is_success
        assert result.data["order_id"] == "order-123"
        assert result.data["status"] == "processed"

        # Limpar contexto
        context_manager.flext_api_cleanup_context("req-order-123")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
