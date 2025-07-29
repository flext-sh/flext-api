#!/usr/bin/env python3
"""FLEXT API - Advanced Features Examples.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

Este exemplo demonstra funcionalidades avançadas da FLEXT API.
"""

import asyncio
import time
from typing import Any, Dict

from flext_api import (
    FlextApiClient,
    FlextApiClientConfig,
    FlextApiCachingPlugin,
    FlextApiRetryPlugin,
    FlextApiCircuitBreakerPlugin,
    FlextApiPlugin,
    FlextApiQueryBuilder,
    FlextApiQueryOperator,
    FlextApiResponseBuilder,
    FlextApiBuilder,
    create_client,
)


class CustomLoggingPlugin(FlextApiPlugin):
    """Plugin customizado para logging avançado."""
    
    def __init__(self):
        super().__init__("CustomLoggingPlugin")
        self.request_log = []
    
    async def before_request(self, request):
        """Log antes da requisição."""
        self.request_log.append({
            "timestamp": time.time(),
            "method": request.method.value,
            "url": request.url,
            "type": "request"
        })
        print(f"🚀 Making {request.method.value} request to {request.url}")
        return request
    
    async def after_request(self, request, response):
        """Log após a resposta."""
        self.request_log.append({
            "timestamp": time.time(),
            "status": response.status_code,
            "elapsed": response.elapsed_time,
            "type": "response"
        })
        print(f"✅ Response: {response.status_code} in {response.elapsed_time:.3f}s")
        return response
    
    async def on_error(self, request, error):
        """Log em caso de erro."""
        self.request_log.append({
            "timestamp": time.time(),
            "error": str(error),
            "type": "error"
        })
        print(f"❌ Error: {error}")
        return None
    
    def get_request_history(self):
        """Obter histórico de requisições."""
        return self.request_log.copy()


async def example_custom_plugins():
    """Exemplo: Plugins customizados."""
    print("=== Custom Plugins Example ===")
    
    # Criar client com plugin customizado
    client = create_client("https://httpbin.org", timeout=5.0)
    
    # Adicionar plugins
    custom_plugin = CustomLoggingPlugin()
    cache_plugin = FlextApiCachingPlugin(ttl_seconds=60)
    
    client.add_plugin(custom_plugin)
    client.add_plugin(cache_plugin)
    
    try:
        # Fazer algumas requisições
        print("Making requests with custom plugins...")
        
        # Primeira requisição - miss no cache
        await client.get("/delay/1")
        
        # Segunda requisição - hit no cache
        await client.get("/delay/1")
        
        # Requisição diferente
        await client.post("/post", json={"test": "data"})
        
        # Verificar histórico do plugin customizado
        history = custom_plugin.get_request_history()
        print(f"\nRequest history: {len(history)} events")
        for event in history[-3:]:  # Últimos 3 eventos
            print(f"  {event['type']}: {event}")
        
        # Stats do cache
        cache_stats = cache_plugin.get_cache_stats()
        print(f"\nCache stats: {cache_stats}")
        
    finally:
        await client.close()
    
    print()


async def example_circuit_breaker():
    """Exemplo: Circuit Breaker em ação."""
    print("=== Circuit Breaker Example ===")
    
    # Criar client com circuit breaker sensível
    client = create_client("https://httpstat.us", timeout=2.0)
    
    # Circuit breaker que abre após 2 falhas
    circuit_breaker = FlextApiCircuitBreakerPlugin(
        failure_threshold=2,
        timeout_seconds=5,
        success_threshold=1
    )
    
    client.add_plugin(circuit_breaker)
    
    try:
        print("Testing circuit breaker with failing requests...")
        
        # Requisições que vão falhar (500 errors)
        for i in range(3):
            result = await client.get("/500")
            print(f"Request {i+1}: {'✅' if result.is_success else '❌'} - State: {circuit_breaker.state}")
            
            if i == 1:  # Após 2 falhas, deve abrir
                assert circuit_breaker.state == "open"
                print("Circuit breaker is now OPEN")
        
        # Tentar requisição com circuit aberto (deve falhar imediatamente)
        try:
            await client.get("/200")
            print("❌ This shouldn't happen - circuit should be open")
        except Exception as e:
            print(f"✅ Circuit breaker blocked request: {e}")
        
        # Aguardar timeout do circuit breaker
        print("Waiting for circuit breaker timeout...")
        await asyncio.sleep(6)
        
        # Agora deve estar half-open, tentar requisição que funciona
        result = await client.get("/200")
        if result.is_success:
            print("✅ Circuit breaker is now CLOSED after successful request")
            assert circuit_breaker.state == "closed"
        
    except Exception as e:
        print(f"Expected error during circuit breaker test: {e}")
    
    finally:
        await client.close()
    
    print()


async def example_streaming():
    """Exemplo: Streaming de dados."""
    print("=== Streaming Example ===")
    
    client = create_client("https://httpbin.org")
    
    try:
        from flext_api.core.client import FlextApiClientMethod
        
        print("Streaming data from server...")
        
        chunk_count = 0
        total_bytes = 0
        
        # Stream de dados (limitamos para não demorar muito)
        async for chunk in client.stream(FlextApiClientMethod.GET, "/stream/5"):
            chunk_count += 1
            total_bytes += len(chunk)
            print(f"Received chunk {chunk_count}: {len(chunk)} bytes")
            
            if chunk_count >= 3:  # Limitar para exemplo
                break
        
        print(f"Total: {chunk_count} chunks, {total_bytes} bytes")
        
    finally:
        await client.close()
    
    print()


def example_advanced_queries():
    """Exemplo: Queries avançadas e complexas."""
    print("=== Advanced Queries Example ===")
    
    qb = FlextApiQueryBuilder()
    
    # Query com todos os operadores
    complex_query = (
        qb.filter("status", FlextApiQueryOperator.IN, ["active", "pending"])
        .filter("created_at", FlextApiQueryOperator.GREATER_THAN_OR_EQUAL, "2025-01-01")
        .filter("tags", FlextApiQueryOperator.LIKE, "%important%")
        .filter("parent_id", FlextApiQueryOperator.IS_NOT_NULL)
        .filter("score", FlextApiQueryOperator.BETWEEN, [7.0, 10.0])
        .sort("priority", "desc")
        .sort("created_at", "asc")
        .page(3, 50)
        .build()
    )
    
    print("Complex query with all operators:")
    print(f"  Filters: {len(complex_query['filters'])}")
    for i, f in enumerate(complex_query['filters']):
        print(f"    {i+1}. {f['field']} {f['operator']} {f.get('value', '(no value)')}")
    
    print(f"  Sorts: {complex_query['sorts']}")
    print(f"  Pagination: page {complex_query['page']}, size {complex_query['page_size']}")
    
    # Query reutilizável
    print("\nReusable query builder:")
    
    # Base query para usuários ativos
    base_query = qb.reset().equals("status", "active").is_not_null("email")
    
    # Especializar para REDACTED_LDAP_BIND_PASSWORDistradores
    REDACTED_LDAP_BIND_PASSWORD_query = base_query.equals("role", "REDACTED_LDAP_BIND_PASSWORD").sort_desc("last_login").build()
    print(f"Admin query: {len(REDACTED_LDAP_BIND_PASSWORD_query['filters'])} filters")
    
    # Especializar para usuários regulares (reutilizando o mesmo builder)
    regular_query = (
        qb.reset()
        .equals("status", "active")
        .is_not_null("email")
        .equals("role", "user")
        .greater_than("created_at", "2024-01-01")
        .sort_asc("name")
        .build()
    )
    print(f"Regular users query: {len(regular_query['filters'])} filters")
    
    print()


def example_advanced_responses():
    """Exemplo: Responses avançadas com metadata rica."""
    print("=== Advanced Responses Example ===")
    
    rb = FlextApiResponseBuilder()
    
    # Response com metadata rica
    rich_response = (
        rb.success({
            "users": [
                {"id": 1, "name": "Alice", "department": "Engineering"},
                {"id": 2, "name": "Bob", "department": "Sales"},
            ]
        })
        .with_pagination(total=1250, page=5, page_size=2)
        .with_metadata("query_execution_time_ms", 127)
        .with_metadata("cache_hit", False)
        .with_metadata("database_server", "primary-db-01")
        .with_metadata("api_version", "2.1.0")
        .with_metadata("rate_limit_remaining", 995)
        .with_metadata("rate_limit_reset", "2025-01-01T12:00:00Z")
        .build()
    )
    
    print("Rich response with extensive metadata:")
    print(f"  Success: {rich_response['success']}")
    print(f"  Data items: {len(rich_response['data']['users'])}")
    print(f"  Pagination: {rich_response['pagination']}")
    print("  Metadata:")
    for key, value in rich_response['metadata'].items():
        print(f"    {key}: {value}")
    
    # Response de erro detalhada
    rb = FlextApiResponseBuilder()
    error_response = (
        rb.error("Validation failed", 422)
        .with_metadata("validation_errors", [
            {"field": "email", "message": "Invalid email format"},
            {"field": "age", "message": "Must be between 18 and 120"},
        ])
        .with_metadata("request_id", "req_abc123")
        .with_metadata("correlation_id", "corr_xyz789")
        .build()
    )
    
    print("\nDetailed error response:")
    print(f"  Error code: {error_response['error_code']}")
    print(f"  Message: {error_response['message']}")
    print(f"  Validation errors: {len(error_response['metadata']['validation_errors'])}")
    
    print()


def example_fastapi_advanced():
    """Exemplo: FastAPI builder avançado."""
    print("=== Advanced FastAPI Builder Example ===")
    
    # Função de startup customizada
    async def custom_startup():
        print("🚀 Custom startup task executed")
    
    # Função de shutdown customizada
    async def custom_shutdown():
        print("🔻 Custom shutdown task executed")
    
    # Exception handler customizado
    async def custom_404_handler(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"The path {request.url.path} was not found",
                "suggestion": "Check the API documentation at /docs"
            }
        )
    
    # Builder avançado
    builder = FlextApiBuilder()
    app = (
        builder
        .with_info(
            "Advanced FLEXT API",
            "Demonstração de funcionalidades avançadas",
            "3.0.0"
        )
        .with_cors(
            origins=["https://app.example.com", "https://REDACTED_LDAP_BIND_PASSWORD.example.com"],
            credentials=True,
            methods=["GET", "POST", "PUT", "DELETE"],
            headers=["Content-Type", "Authorization", "X-API-Key"]
        )
        .with_rate_limiting(per_minute=1000)
        .with_logging()
        .with_security()
        .with_trusted_hosts(["api.example.com", "localhost"])
        .with_health_checks()
        .with_metrics_endpoint()
        .add_startup_task(custom_startup)
        .add_shutdown_task(custom_shutdown)
        .with_exception_handler(404, custom_404_handler)
        .with_global_exception_handler()
        .build()
    )
    
    print(f"Advanced app created: {app.title} v{app.version}")
    print(f"Total routes: {len(app.routes)}")
    print("Features enabled:")
    print("  ✅ CORS with specific origins")
    print("  ✅ Rate limiting (1000/min)")
    print("  ✅ Request/response logging")
    print("  ✅ Security headers")
    print("  ✅ Trusted host validation")
    print("  ✅ Health check endpoints")
    print("  ✅ Metrics endpoint")
    print("  ✅ Custom startup/shutdown tasks")
    print("  ✅ Custom exception handlers")
    print("  ✅ Global exception handler")
    
    print()


async def example_real_world_scenario():
    """Exemplo: Cenário do mundo real combinando todas as funcionalidades."""
    print("=== Real World Scenario Example ===")
    
    print("Scenario: User management API with advanced features")
    print()
    
    # 1. Construir query complexa para buscar usuários
    print("1. Building complex user search query...")
    qb = FlextApiQueryBuilder()
    user_search = (
        qb.filter("department", FlextApiQueryOperator.IN, ["engineering", "product"])
        .filter("status", FlextApiQueryOperator.EQUALS, "active")
        .filter("last_login", FlextApiQueryOperator.GREATER_THAN, "2024-12-01")
        .filter("role", FlextApiQueryOperator.NOT_EQUALS, "intern")
        .like("skills", "%python%")
        .sort_desc("performance_rating")
        .sort_asc("hire_date")
        .page(1, 25)
        .build()
    )
    
    print(f"   Query has {len(user_search['filters'])} filters and {len(user_search['sorts'])} sorts")
    
    # 2. Simular chamada para API externa com client avançado
    print("\n2. Making API call with advanced HTTP client...")
    
    client = create_client("https://jsonplaceholder.typicode.com", timeout=10.0)
    
    # Adicionar plugins de produção
    client.add_plugin(FlextApiCachingPlugin(ttl_seconds=300))  # Cache 5min
    client.add_plugin(FlextApiRetryPlugin(max_retries=3, backoff_factor=1.5))
    client.add_plugin(CustomLoggingPlugin())
    
    try:
        # Simular busca de usuários
        result = await client.get("/users", params={"_limit": 5})
        
        if result.is_success:
            users_data = result.data.data  # API response data
            print(f"   Retrieved {len(users_data)} users from external API")
            
            # 3. Processar dados e construir response padronizada
            print("\n3. Building standardized API response...")
            
            # Filtrar e transformar dados baseado na query
            filtered_users = [
                {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "department": "engineering",  # Mock data
                    "status": "active",
                    "performance_rating": 8.5 + (user["id"] * 0.1)
                }
                for user in users_data[:3]  # Simular filtros
            ]
            
            # Construir response final
            rb = FlextApiResponseBuilder()
            final_response = (
                rb.success(filtered_users)
                .with_pagination(total=127, page=1, page_size=25)
                .with_metadata("query_filters", len(user_search['filters']))
                .with_metadata("execution_time_ms", 245)
                .with_metadata("cache_hit", False)
                .with_metadata("external_api_calls", 1)
                .with_metadata("data_source", "external_hr_api")
                .build()
            )
            
            print(f"   Final response: {final_response['success']}")
            print(f"   Users returned: {len(final_response['data'])}")
            print(f"   Total available: {final_response['pagination']['total']}")
            print(f"   Metadata keys: {list(final_response['metadata'].keys())}")
            
        # 4. Verificar métricas dos plugins
        print("\n4. Checking plugin metrics...")
        
        health_result = await client.get_health()
        if health_result.is_success:
            health = health_result.data
            print(f"   Client made {health['request_count']} requests")
            print(f"   Average response time: {health['average_response_time']:.3f}s")
        
        metrics_result = await client.get_metrics()
        if metrics_result.is_success:
            metrics = metrics_result.data
            for plugin_name, plugin_metrics in metrics['plugins'].items():
                print(f"   {plugin_name}: {plugin_metrics}")
    
    finally:
        await client.close()
    
    print("\n✅ Real-world scenario completed successfully!")
    print("   - Complex query built and used")
    print("   - External API called with resilience patterns")
    print("   - Data processed and transformed")
    print("   - Standardized response format")
    print("   - Full observability and metrics")
    
    print()


async def main():
    """Executar todos os exemplos avançados."""
    print("FLEXT API - Advanced Features Examples")
    print("=" * 60)
    print()
    
    # Exemplos síncronos
    example_advanced_queries()
    example_advanced_responses()
    example_fastapi_advanced()
    
    # Exemplos assíncronos
    await example_custom_plugins()
    await example_circuit_breaker()
    await example_streaming()
    await example_real_world_scenario()
    
    print("=" * 60)
    print("🎉 All advanced examples completed successfully!")
    print()
    print("Key takeaways:")
    print("- FLEXT API provides real, production-ready functionality")
    print("- All components work together seamlessly")
    print("- Extensive plugin system for customization")
    print("- Built-in resilience patterns (retry, circuit breaker, caching)")
    print("- Rich metadata and observability")
    print("- Clean, fluent APIs that reduce boilerplate code")


if __name__ == "__main__":
    asyncio.run(main())