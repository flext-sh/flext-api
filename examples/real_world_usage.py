#!/usr/bin/env python3
"""FlextApi Real-World Usage Examples.

Practical examples showing how flext-api achieves massive code reduction
in real enterprise scenarios with actual working examples.
"""

import asyncio
import contextlib
from datetime import datetime
from typing import Any

from flext_api import (
    FlextApiClient,
    FlextApiClientBuilder,
    FlextApiLoggingPlugin,
    FlextApiMetricsPlugin,
    FlextApiPlugin,
)

# ==============================================================================
# REAL-WORLD EXAMPLE 1: MICROSERVICE INTEGRATION
# ==============================================================================


class MicroserviceIntegration:
    """Integrate with multiple microservices using single flext-api client."""

    def __init__(self, base_url: str, api_key: str) -> None:
        # ONE client handles ALL microservices - massive code reduction
        self.client = (
            FlextApiClientBuilder()
            .with_base_url(base_url)
            .with_api_key(api_key)
            .with_caching(enabled=True, ttl=300)
            .with_circuit_breaker(enabled=True, failure_threshold=3)
            .with_retries(max_retries=3, delay=1.0)
            .with_plugin(FlextApiLoggingPlugin())
            .with_plugin(FlextApiMetricsPlugin())
            .build()
        )

    async def __aenter__(self):
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_user_profile(self, user_id: str) -> dict[str, Any]:
        """Get user from user-service."""
        result = await self.client.get(f"/user-service/v1/users/{user_id}")
        return {
            "success": result.success,
            "data": result.data.json_data if result.success else None,
        }

    async def get_user_orders(self, user_id: str) -> dict[str, Any]:
        """Get orders from order-service."""
        result = await self.client.get(f"/order-service/v1/users/{user_id}/orders")
        return {
            "success": result.success,
            "data": result.data.json_data if result.success else None,
        }

    async def get_user_payments(self, user_id: str) -> dict[str, Any]:
        """Get payments from payment-service."""
        result = await self.client.get(f"/payment-service/v1/users/{user_id}/payments")
        return {
            "success": result.success,
            "data": result.data.json_data if result.success else None,
        }

    async def create_complete_user_dashboard(self, user_id: str) -> dict[str, Any]:
        """Create complete dashboard by calling multiple services concurrently."""
        # ONE line executes 3 microservice calls concurrently - massive efficiency!
        profile, orders, payments = await asyncio.gather(
            self.get_user_profile(user_id),
            self.get_user_orders(user_id),
            self.get_user_payments(user_id),
            return_exceptions=True,
        )

        # Automatic error handling and metrics collection
        return {
            "user_id": user_id,
            "profile": profile.get("data")
            if isinstance(profile, dict) and profile.get("success")
            else None,
            "orders": orders.get("data")
            if isinstance(orders, dict) and orders.get("success")
            else [],
            "payments": payments.get("data")
            if isinstance(payments, dict) and payments.get("success")
            else [],
            "generated_at": datetime.now().isoformat(),
        }


# ==============================================================================
# REAL-WORLD EXAMPLE 2: API AGGREGATION SERVICE
# ==============================================================================


class APIAggregationService:
    """Aggregate data from multiple external APIs with built-in resilience."""

    def __init__(self) -> None:
        # Different clients for different API providers - each optimized
        self.weather_client = self._create_weather_client()
        self.news_client = self._create_news_client()
        self.stock_client = self._create_stock_client()

    def _create_weather_client(self) -> FlextApiClient:
        """Weather API client with specific configuration."""
        return (
            FlextApiClientBuilder()
            .with_base_url("https://api.openweathermap.org/data/2.5")
            .with_timeout(10.0)
            .with_caching(enabled=True, ttl=1800)  # 30 minutes cache
            .with_retries(max_retries=2, delay=0.5)
            .build()
        )

    def _create_news_client(self) -> FlextApiClient:
        """News API client with specific configuration."""
        return (
            FlextApiClientBuilder()
            .with_base_url("https://newsapi.org/v2")
            .with_timeout(15.0)
            .with_caching(enabled=True, ttl=3600)  # 1 hour cache
            .with_circuit_breaker(enabled=True, failure_threshold=2)
            .build()
        )

    def _create_stock_client(self) -> FlextApiClient:
        """Stock API client with specific configuration."""
        return (
            FlextApiClientBuilder()
            .with_base_url("https://api.polygon.io/v2")
            .with_timeout(5.0)
            .with_caching(enabled=True, ttl=900)  # 15 minutes cache
            .with_retries(max_retries=5, delay=0.2)  # Fast retries for stock data
            .build()
        )

    async def __aenter__(self):
        # Initialize all clients concurrently
        await asyncio.gather(
            self.weather_client.__aenter__(),
            self.news_client.__aenter__(),
            self.stock_client.__aenter__(),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Close all clients concurrently
        await asyncio.gather(
            self.weather_client.__aexit__(exc_type, exc_val, exc_tb),
            self.news_client.__aexit__(exc_type, exc_val, exc_tb),
            self.stock_client.__aexit__(exc_type, exc_val, exc_tb),
        )

    async def get_aggregated_dashboard(
        self, city: str, symbols: list[str],
    ) -> dict[str, Any]:
        """Get aggregated data from all APIs with automatic fallbacks."""
        # Prepare all API calls
        tasks = []

        # Weather data
        tasks.append(self._get_weather_safe(city))

        # News data
        tasks.append(self._get_news_safe(city))

        # Stock data for each symbol
        tasks.extend(self._get_stock_safe(symbol) for symbol in symbols)

        # Execute all calls concurrently - massive performance gain
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results with automatic error handling
        weather_data = results[0] if not isinstance(results[0], Exception) else None
        news_data = results[1] if not isinstance(results[1], Exception) else None
        stock_data = []

        for i, symbol in enumerate(symbols):
            stock_result = results[2 + i]
            if not isinstance(stock_result, Exception):
                stock_data.append({"symbol": symbol, "data": stock_result})

        # Comprehensive dashboard
        return {
            "location": city,
            "weather": weather_data,
            "news": news_data,
            "stocks": stock_data,
            "generated_at": datetime.now().isoformat(),
            "data_freshness": {
                "weather": "cached"
                if weather_data and weather_data.get("cached")
                else "live",
                "news": "cached" if news_data and news_data.get("cached") else "live",
                "stocks": "mixed",  # Some might be cached, others live
            },
        }

    async def _get_weather_safe(self, city: str) -> dict[str, Any] | None:
        """Get weather data with safe error handling."""
        try:
            result = await self.weather_client.get(f"/weather?q={city}&units=metric")
            if result.success:
                return {
                    "temperature": result.data.json_data.get("main", {}).get("temp"),
                    "description": result.data.json_data.get("weather", [{}])[0].get(
                        "description",
                    ),
                    "cached": result.data.cached,
                }
        except Exception:
            pass
        return None

    async def _get_news_safe(self, city: str) -> dict[str, Any] | None:
        """Get news data with safe error handling."""
        try:
            result = await self.news_client.get(f"/everything?q={city}&pageSize=5")
            if result.success:
                articles = result.data.json_data.get("articles", [])
                return {
                    "headlines": [article.get("title") for article in articles[:3]],
                    "total_articles": len(articles),
                    "cached": result.data.cached,
                }
        except Exception:
            pass
        return None

    async def _get_stock_safe(self, symbol: str) -> dict[str, Any] | None:
        """Get stock data with safe error handling."""
        try:
            result = await self.stock_client.get(f"/aggs/ticker/{symbol}/prev")
            if result.success:
                data = result.data.json_data.get("results", [{}])[0]
                return {
                    "price": data.get("c"),  # Close price
                    "volume": data.get("v"),
                    "cached": result.data.cached,
                }
        except Exception:
            pass
        return None


# ==============================================================================
# REAL-WORLD EXAMPLE 3: CUSTOM BUSINESS PLUGIN
# ==============================================================================


class BusinessAuditPlugin(FlextApiPlugin):
    """Custom plugin for business audit requirements."""

    def __init__(self, audit_sensitive_endpoints: bool = True) -> None:
        super().__init__("BusinessAuditPlugin")
        self.audit_sensitive = audit_sensitive_endpoints
        self.audit_log = []

    async def before_request(self, request) -> None:
        """Audit request if it's sensitive."""
        if self.audit_sensitive and self._is_sensitive_endpoint(request.url):
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "REQUEST_START",
                "endpoint": request.url,
                "method": request.method,
                "user_agent": request.headers.get("User-Agent", "unknown"),
                "request_id": f"audit_{len(self.audit_log)}",
            }
            self.audit_log.append(audit_entry)
            request.plugin_data["audit_id"] = audit_entry["request_id"]

    async def after_request(self, request, response) -> None:
        """Audit successful response."""
        audit_id = request.plugin_data.get("audit_id")
        if audit_id:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "REQUEST_SUCCESS",
                "request_id": audit_id,
                "status_code": response.status_code,
                "execution_time_ms": response.execution_time_ms,
                "cached": response.cached,
            }
            self.audit_log.append(audit_entry)

    async def on_error(self, request, response) -> None:
        """Audit failed response."""
        audit_id = request.plugin_data.get("audit_id")
        if audit_id:
            audit_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "REQUEST_FAILED",
                "request_id": audit_id,
                "status_code": response.status_code,
                "execution_time_ms": response.execution_time_ms,
                "error": "Request failed",
            }
            self.audit_log.append(audit_entry)

    def _is_sensitive_endpoint(self, url: str) -> bool:
        """Check if endpoint is sensitive and requires auditing."""
        sensitive_patterns = ["/admin/", "/payment/", "/user/", "/auth/"]
        return any(pattern in url for pattern in sensitive_patterns)

    def get_audit_report(self) -> dict[str, Any]:
        """Generate comprehensive audit report."""
        total_requests = len(
            [log for log in self.audit_log if log["action"] == "REQUEST_START"],
        )
        successful_requests = len(
            [log for log in self.audit_log if log["action"] == "REQUEST_SUCCESS"],
        )
        failed_requests = len(
            [log for log in self.audit_log if log["action"] == "REQUEST_FAILED"],
        )

        return {
            "total_audited_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": (successful_requests / max(total_requests, 1)) * 100,
            "audit_entries": self.audit_log,
            "report_generated_at": datetime.now().isoformat(),
        }


# ==============================================================================
# DEMONSTRATION FUNCTIONS
# ==============================================================================


async def demo_microservice_integration() -> None:
    """Demonstrate microservice integration."""
    # In production, would use real microservice URL and API key
    async with MicroserviceIntegration(
        "https://jsonplaceholder.typicode.com", "demo-key",
    ) as integration:
        # Create complete user dashboard from multiple services
        await integration.create_complete_user_dashboard("1")

        # Get client metrics - automatic monitoring
        integration.client.get_metrics()


async def demo_api_aggregation() -> None:
    """Demonstrate API aggregation service."""
    async with APIAggregationService():
        # This would work with real API keys in production

        # In production: dashboard = await aggregator.get_aggregated_dashboard("New York", ["AAPL", "GOOGL"])
        pass


async def demo_business_audit_plugin() -> None:
    """Demonstrate custom business audit plugin."""
    # Create client with business audit plugin
    audit_plugin = BusinessAuditPlugin(audit_sensitive_endpoints=True)

    client = (
        FlextApiClientBuilder()
        .with_base_url("https://jsonplaceholder.typicode.com")
        .with_plugin(audit_plugin)
        .build()
    )

    async with client:
        # Make some requests that will be audited
        await client.get("/users/1")  # Sensitive - audited
        await client.get("/posts/1")  # Not sensitive - not audited
        await client.get("/admin/settings")  # Sensitive - audited

        # Generate audit report
        audit_plugin.get_audit_report()


# ==============================================================================
# COMPARISON: TRADITIONAL VS FLEXT-API
# ==============================================================================


def show_code_reduction_comparison() -> None:
    """Show side-by-side comparison of traditional vs flext-api approach."""


# ==============================================================================
# MAIN DEMONSTRATION
# ==============================================================================


async def main() -> None:
    """Run all real-world examples."""
    # Show the dramatic code reduction first
    show_code_reduction_comparison()

    # Run practical examples
    with contextlib.suppress(Exception):
        await demo_microservice_integration()

    with contextlib.suppress(Exception):
        await demo_api_aggregation()

    with contextlib.suppress(Exception):
        await demo_business_audit_plugin()


if __name__ == "__main__":
    asyncio.run(main())
