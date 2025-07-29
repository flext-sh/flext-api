#!/usr/bin/env python3
"""Tests for FlextApi Integration Helpers - Validação real sem mocks.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Testes robustos para helpers de integração externa com foco em funcionalidade real.
"""

import asyncio
from datetime import datetime
from typing import Any

import pytest
from flext_core import FlextResult

from flext_api.helpers.flext_api_integrations import (
    FlextApiDatabaseHelper,
    FlextApiDatabaseOperation,
    FlextApiHttpClient,
    FlextApiHttpRequest,
    FlextApiHttpResponse,
    FlextApiMessageConsumer,
    FlextApiMessagePayload,
    FlextApiMessageProducer,
    flext_api_circuit_breaker,
    flext_api_create_database_helper,
    flext_api_create_http_client,
    flext_api_create_message_consumer,
    flext_api_create_message_producer,
    flext_api_rate_limiter,
)


class TestFlextApiHttpClient:
    """Testes para FlextApiHttpClient - cliente HTTP padronizado."""

    def test_http_client_initialization(self) -> None:
        """Testa inicialização do cliente HTTP."""
        base_url = "https://api.example.com"
        client = FlextApiHttpClient(base_url)

        assert client.base_url == base_url
        assert client.default_timeout == 30
        assert isinstance(client.default_headers, dict)

    def test_http_client_with_custom_headers(self) -> None:
        """Testa cliente HTTP com headers customizados."""
        base_url = "https://api.example.com"
        headers = {"Authorization": "Bearer token", "Content-Type": "application/json"}

        client = FlextApiHttpClient(base_url, default_headers=headers)

        assert client.default_headers == headers

    def test_build_request_basic(self) -> None:
        """Testa construção de requisição HTTP básica."""
        client = FlextApiHttpClient("https://api.example.com")

        request = client.flext_api_build_request("GET", "/users")

        assert isinstance(request, dict)
        assert request["method"] == "GET"
        assert request["url"] == "https://api.example.com/users"
        assert request["timeout"] == 30
        assert request["retries"] == 3

    def test_build_request_with_body_and_headers(self) -> None:
        """Testa construção de requisição com body e headers."""
        client = FlextApiHttpClient("https://api.example.com")

        body = {"name": "Test User", "email": "test@example.com"}
        headers = {"X-Custom": "value"}

        request = client.flext_api_build_request(
            "POST",
            "/users",
            body=body,
            headers=headers,
            timeout=60,
        )

        assert request["method"] == "POST"
        assert request["body"] == body
        assert "X-Custom" in request["headers"]
        assert request["timeout"] == 60

    @pytest.mark.asyncio
    async def test_execute_request_success(self) -> None:
        """Testa execução de requisição HTTP bem-sucedida."""
        client = FlextApiHttpClient("https://api.example.com")

        request = client.flext_api_build_request("GET", "/health")
        result = await client.flext_api_execute_request(request)

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.data, dict)

        response = result.data
        assert response["success"] is True
        assert response["status_code"] == 200
        assert response["execution_time_ms"] > 0

    @pytest.mark.asyncio
    async def test_http_convenience_methods(self) -> None:
        """Testa métodos de conveniência HTTP."""
        client = FlextApiHttpClient("https://api.example.com")

        # Test GET
        get_result = await client.flext_api_get("/users")
        assert get_result.is_success

        # Test POST
        post_data = {"name": "Test"}
        post_result = await client.flext_api_post("/users", post_data)
        assert post_result.is_success

        # Test PUT
        put_data = {"name": "Updated"}
        put_result = await client.flext_api_put("/users/1", put_data)
        assert put_result.is_success

        # Test DELETE
        delete_result = await client.flext_api_delete("/users/1")
        assert delete_result.is_success


class TestFlextApiDatabaseHelper:
    """Testes para FlextApiDatabaseHelper - helper de banco de dados."""

    def test_database_helper_initialization(self) -> None:
        """Testa inicialização do helper de banco."""
        connection_string = "postgresql://user:pass@localhost/db"
        helper = FlextApiDatabaseHelper(connection_string)

        assert helper.connection_string == connection_string

    def test_build_select_operation(self) -> None:
        """Testa construção de operação SELECT."""
        helper = FlextApiDatabaseHelper("test://connection")

        operation = helper.flext_api_build_select(
            table="users",
            fields=["id", "name", "email"],
            conditions={"active": True},
            limit=10,
            offset=20,
        )

        assert isinstance(operation, dict)
        assert operation["operation"] == "select"
        assert operation["table"] == "users"
        assert operation["fields"] == ["id", "name", "email"]
        assert operation["conditions"] == {"active": True}
        assert operation["limit"] == 10
        assert operation["offset"] == 20

    def test_build_insert_operation(self) -> None:
        """Testa construção de operação INSERT."""
        helper = FlextApiDatabaseHelper("test://connection")

        data = {"name": "Test User", "email": "test@example.com"}
        operation = helper.flext_api_build_insert("users", data)

        assert operation["operation"] == "insert"
        assert operation["table"] == "users"
        assert operation["fields"] == ["name", "email"]
        assert operation["data"] == data

    def test_build_update_operation(self) -> None:
        """Testa construção de operação UPDATE."""
        helper = FlextApiDatabaseHelper("test://connection")

        data = {"name": "Updated User"}
        conditions = {"id": 1}
        operation = helper.flext_api_build_update("users", data, conditions)

        assert operation["operation"] == "update"
        assert operation["data"] == data
        assert operation["conditions"] == conditions

    def test_build_delete_operation(self) -> None:
        """Testa construção de operação DELETE."""
        helper = FlextApiDatabaseHelper("test://connection")

        conditions = {"id": 1}
        operation = helper.flext_api_build_delete("users", conditions)

        assert operation["operation"] == "delete"
        assert operation["conditions"] == conditions

    @pytest.mark.asyncio
    async def test_execute_database_operations(self) -> None:
        """Testa execução de operações de banco."""
        helper = FlextApiDatabaseHelper("test://connection")

        # Test SELECT
        select_op = helper.flext_api_build_select("users")
        select_result = await helper.flext_api_execute_operation(select_op)
        assert select_result.is_success
        assert isinstance(select_result.data, list)

        # Test INSERT
        insert_op = helper.flext_api_build_insert("users", {"name": "Test"})
        insert_result = await helper.flext_api_execute_operation(insert_op)
        assert insert_result.is_success
        assert "affected_rows" in insert_result.data

        # Test UPDATE
        update_op = helper.flext_api_build_update(
            "users",
            {"name": "Updated"},
            {"id": 1},
        )
        update_result = await helper.flext_api_execute_operation(update_op)
        assert update_result.is_success

        # Test DELETE
        delete_op = helper.flext_api_build_delete("users", {"id": 1})
        delete_result = await helper.flext_api_execute_operation(delete_op)
        assert delete_result.is_success


class TestFlextApiMessageQueue:
    """Testes para FlextApiMessageProducer e FlextApiMessageConsumer."""

    def test_message_producer_initialization(self) -> None:
        """Testa inicialização do producer de mensagens."""
        broker_url = "redis://localhost:6379"
        producer = FlextApiMessageProducer(broker_url, topic_prefix="test")

        assert producer.broker_url == broker_url
        assert producer.topic_prefix == "test"

    def test_create_message(self) -> None:
        """Testa criação de payload de mensagem."""
        producer = FlextApiMessageProducer("redis://localhost", "test")

        data = {"user_id": 123, "action": "login"}
        message = producer.flext_api_create_message("user.login", data, "corr-123")

        assert isinstance(message, dict)
        assert message["type"] == "user.login"
        assert message["data"] == data
        assert message["source"] == "flext-api"
        assert message["correlation_id"] == "corr-123"
        assert message["retry_count"] == 0
        assert message["id"].startswith("test_")

    @pytest.mark.asyncio
    async def test_send_message(self) -> None:
        """Testa envio de mensagem."""
        producer = FlextApiMessageProducer("redis://localhost", "test")

        message = producer.flext_api_create_message("test.event", {"key": "value"})
        result = await producer.flext_api_send_message("events", message)

        assert result.is_success
        assert result.data == message["id"]

    def test_message_consumer_initialization(self) -> None:
        """Testa inicialização do consumer de mensagens."""
        consumer = FlextApiMessageConsumer("redis://localhost", "test")

        assert consumer.broker_url == "redis://localhost"
        assert consumer.topic_prefix == "test"
        assert isinstance(consumer.handlers, dict)

    def test_register_message_handler(self) -> None:
        """Testa registro de handler de mensagem."""
        consumer = FlextApiMessageConsumer("redis://localhost")

        def test_handler(message: dict[str, Any]) -> str:
            return f"Processed: {message['id']}"

        consumer.flext_api_register_handler("test.event", test_handler)

        assert "test.event" in consumer.handlers
        assert consumer.handlers["test.event"] == test_handler

    @pytest.mark.asyncio
    async def test_process_message_sync_handler(self) -> None:
        """Testa processamento de mensagem com handler síncrono."""
        consumer = FlextApiMessageConsumer("redis://localhost")

        def sync_handler(message: dict[str, Any]) -> str:
            return f"Processed sync: {message['type']}"

        consumer.flext_api_register_handler("test.sync", sync_handler)

        message = FlextApiMessagePayload(
            id="test-123",
            type="test.sync",
            source="test",
            data={"test": True},
            timestamp=datetime.now().isoformat(),
            correlation_id=None,
            retry_count=0,
        )

        result = await consumer.flext_api_process_message(message)
        assert result.is_success
        assert "Processed sync" in result.data

    @pytest.mark.asyncio
    async def test_process_message_async_handler(self) -> None:
        """Testa processamento de mensagem com handler assíncrono."""
        consumer = FlextApiMessageConsumer("redis://localhost")

        async def async_handler(message: dict[str, Any]) -> str:
            await asyncio.sleep(0.01)  # Simula processamento async
            return f"Processed async: {message['type']}"

        consumer.flext_api_register_handler("test.async", async_handler)

        message = FlextApiMessagePayload(
            id="test-456",
            type="test.async",
            source="test",
            data={"test": True},
            timestamp=datetime.now().isoformat(),
            correlation_id=None,
            retry_count=0,
        )

        result = await consumer.flext_api_process_message(message)
        assert result.is_success
        assert "Processed async" in result.data

    @pytest.mark.asyncio
    async def test_process_message_no_handler(self) -> None:
        """Testa processamento de mensagem sem handler registrado."""
        consumer = FlextApiMessageConsumer("redis://localhost")

        message = FlextApiMessagePayload(
            id="test-789",
            type="unknown.type",
            source="test",
            data={},
            timestamp=datetime.now().isoformat(),
            correlation_id=None,
            retry_count=0,
        )

        result = await consumer.flext_api_process_message(message)
        assert not result.is_success
        assert "No handler for message type" in result.error


class TestIntegrationPatterns:
    """Testes para padrões de integração (circuit breaker, rate limiter)."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self) -> None:
        """Testa circuit breaker em operação normal."""
        async with flext_api_circuit_breaker(failure_threshold=3, timeout_seconds=5):
            # Operação normal - deve passar
            assert True

    @pytest.mark.asyncio
    async def test_rate_limiter_normal_operation(self) -> None:
        """Testa rate limiter em operação normal."""
        start_time = asyncio.get_event_loop().time()

        async with flext_api_rate_limiter(requests_per_second=5):
            # Primeira requisição - deve passar imediatamente
            pass

        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time

        # Deve executar rapidamente na primeira vez
        assert execution_time < 0.1


class TestFactoryFunctions:
    """Testes para funções factory de integração."""

    def test_create_http_client_factory(self) -> None:
        """Testa factory de cliente HTTP."""
        base_url = "https://api.test.com"
        client = flext_api_create_http_client(base_url)

        assert isinstance(client, FlextApiHttpClient)
        assert client.base_url == base_url

    def test_create_database_helper_factory(self) -> None:
        """Testa factory de helper de banco."""
        connection_string = "postgresql://test"
        helper = flext_api_create_database_helper(connection_string)

        assert isinstance(helper, FlextApiDatabaseHelper)
        assert helper.connection_string == connection_string

    def test_create_message_producer_factory(self) -> None:
        """Testa factory de producer de mensagens."""
        broker_url = "redis://localhost"
        producer = flext_api_create_message_producer(broker_url, topic_prefix="test")

        assert isinstance(producer, FlextApiMessageProducer)
        assert producer.broker_url == broker_url
        assert producer.topic_prefix == "test"

    def test_create_message_consumer_factory(self) -> None:
        """Testa factory de consumer de mensagens."""
        broker_url = "redis://localhost"
        consumer = flext_api_create_message_consumer(broker_url, topic_prefix="test")

        assert isinstance(consumer, FlextApiMessageConsumer)
        assert consumer.broker_url == broker_url
        assert consumer.topic_prefix == "test"


class TestTypedDictStructures:
    """Testes para estruturas TypedDict de integração."""

    def test_http_request_structure(self) -> None:
        """Testa estrutura FlextApiHttpRequest."""
        request = FlextApiHttpRequest(
            method="POST",
            url="https://api.test.com/users",
            headers={"Content-Type": "application/json"},
            body={"name": "Test"},
            timeout=30,
            retries=3,
        )

        assert request["method"] == "POST"
        assert request["url"] == "https://api.test.com/users"
        assert isinstance(request["headers"], dict)
        assert request["timeout"] == 30

    def test_http_response_structure(self) -> None:
        """Testa estrutura FlextApiHttpResponse."""
        response = FlextApiHttpResponse(
            status_code=200,
            headers={"Content-Type": "application/json"},
            body={"success": True},
            success=True,
            error=None,
            execution_time_ms=150.5,
        )

        assert response["status_code"] == 200
        assert response["success"] is True
        assert response["execution_time_ms"] == 150.5

    def test_database_operation_structure(self) -> None:
        """Testa estrutura FlextApiDatabaseOperation."""
        operation = FlextApiDatabaseOperation(
            operation="select",
            table="users",
            fields=["id", "name"],
            conditions={"active": True},
            data=None,
            limit=10,
            offset=0,
        )

        assert operation["operation"] == "select"
        assert operation["table"] == "users"
        assert operation["fields"] == ["id", "name"]

    def test_message_payload_structure(self) -> None:
        """Testa estrutura FlextApiMessagePayload."""
        payload = FlextApiMessagePayload(
            id="msg-123",
            type="user.created",
            source="api",
            data={"user_id": 456},
            timestamp="2025-01-25T10:00:00Z",
            correlation_id="corr-789",
            retry_count=0,
        )

        assert payload["id"] == "msg-123"
        assert payload["type"] == "user.created"
        assert payload["retry_count"] == 0


class TestRealWorldScenarios:
    """Testes para cenários reais de integração."""

    @pytest.mark.asyncio
    async def test_complete_api_integration_flow(self) -> None:
        """Testa fluxo completo de integração com API externa."""
        # 1. Criar cliente HTTP
        client = flext_api_create_http_client("https://jsonplaceholder.typicode.com")

        # 2. Fazer requisição
        result = await client.flext_api_get("/posts/1")

        # 3. Verificar resultado
        assert result.is_success
        response = result.data
        assert response["success"] is True
        assert response["status_code"] == 200

    @pytest.mark.asyncio
    async def test_database_crud_operations_flow(self) -> None:
        """Testa fluxo completo de operações CRUD em banco."""
        # 1. Criar helper de banco
        db = flext_api_create_database_helper("postgresql://test")

        # 2. Executar operações CRUD
        insert_op = db.flext_api_build_insert("users", {"name": "Test User"})
        insert_result = await db.flext_api_execute_operation(insert_op)
        assert insert_result.is_success

        select_op = db.flext_api_build_select("users", conditions={"name": "Test User"})
        select_result = await db.flext_api_execute_operation(select_op)
        assert select_result.is_success

        update_op = db.flext_api_build_update("users", {"name": "Updated"}, {"id": 1})
        update_result = await db.flext_api_execute_operation(update_op)
        assert update_result.is_success

        delete_op = db.flext_api_build_delete("users", {"id": 1})
        delete_result = await db.flext_api_execute_operation(delete_op)
        assert delete_result.is_success

    @pytest.mark.asyncio
    async def test_message_queue_producer_consumer_flow(self) -> None:
        """Testa fluxo completo de producer/consumer de mensagens."""
        # 1. Criar producer e consumer
        producer = flext_api_create_message_producer(
            "redis://localhost",
            topic_prefix="test",
        )
        consumer = flext_api_create_message_consumer(
            "redis://localhost",
            topic_prefix="test",
        )

        # 2. Registrar handler
        processed_messages = []

        def message_handler(message: dict[str, Any]) -> str:
            processed_messages.append(message)
            return f"Processed: {message['id']}"

        consumer.flext_api_register_handler("test.event", message_handler)

        # 3. Criar e enviar mensagem
        message = producer.flext_api_create_message("test.event", {"test": True})
        send_result = await producer.flext_api_send_message("events", message)
        assert send_result.is_success

        # 4. Processar mensagem
        process_result = await consumer.flext_api_process_message(message)
        assert process_result.is_success
        assert len(processed_messages) == 1
        assert processed_messages[0]["id"] == message["id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
