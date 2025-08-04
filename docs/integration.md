# Ecosystem Integration Guide

**Integration patterns and cross-service communication for FLEXT API**

> **Navigation**: [FLEXT Hub](../../docs/NAVIGATION.md) > [flext-api](../README.md) > Integration

---

## 🎯 Integration Overview

FLEXT API serves as the **HTTP foundation library** for the entire FLEXT ecosystem, providing standardized communication patterns across all 33 interconnected projects. This guide covers integration patterns, service communication, and ecosystem-wide standards.

### **Integration Scope**

- **Core Services** - FlexCore (Go:8080) and FLEXT Service (Go/Py:8081)
- **Application Services** - flext-auth, flext-web, flext-cli, flext-quality
- **Infrastructure Libraries** - Oracle, LDAP, LDIF, WMS, gRPC, Meltano
- **Singer Ecosystem** - 15 taps, targets, and DBT projects
- **Enterprise Implementations** - ALGAR and GrupoNos specialized projects

---

## 🏗️ Core Service Integration

### **FlexCore Runtime Container (Go:8080)**

FlexCore integrates with FLEXT API for HTTP communication between Go and Python services.

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class FlexCoreClient:
    """HTTP client for FlexCore runtime service."""

    def __init__(self):
        self.api = create_flext_api()
        self.client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8080",
            "timeout": 30,
            "headers": {
                "Content-Type": "application/json",
                "X-Service": "flext-api"
            }
        })

        if not self.client_result.success:
            logger.error("Failed to create FlexCore client", error=self.client_result.error)

    def health_check(self) -> FlextResult[dict]:
        """Check FlexCore service health."""
        if not self.client_result.success:
            return FlextResult.fail("Client not initialized")

        client = self.client_result.data
        response = client.get("/health")

        if response.success:
            logger.info("FlexCore health check successful")
            return FlextResult.ok(response.data)
        else:
            logger.warning("FlexCore health check failed", error=response.error)
            return FlextResult.fail(f"Health check failed: {response.error}")

    def execute_plugin(self, plugin_name: str, command: dict) -> FlextResult[dict]:
        """Execute plugin command via FlexCore."""
        if not self.client_result.success:
            return FlextResult.fail("Client not initialized")

        client = self.client_result.data
        response = client.post(
            f"/api/v1/plugins/{plugin_name}/execute",
            json=command
        )

        if response.success:
            logger.info("Plugin executed successfully", plugin=plugin_name)
            return FlextResult.ok(response.data)
        else:
            logger.error("Plugin execution failed", plugin=plugin_name, error=response.error)
            return FlextResult.fail(f"Plugin execution failed: {response.error}")
```

### **FLEXT Service (Go/Python:8081)**

FLEXT Service acts as the data platform service with Python bridge integration.

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any

logger = get_logger(__name__)

class FlextServiceClient:
    """HTTP client for FLEXT data platform service."""

    def __init__(self):
        self.api = create_flext_api()
        self.client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8081",
            "timeout": 60,  # Longer timeout for data operations
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "flext-api",
                "X-Version": "0.9.0"
            }
        })

    def execute_meltano_pipeline(self, pipeline_config: Dict[str, Any]) -> FlextResult[dict]:
        """Execute Meltano pipeline via FLEXT Service."""
        if not self.client_result.success:
            return FlextResult.fail("Client not initialized")

        client = self.client_result.data
        response = client.post(
            "/api/v1/meltano/execute",
            json=pipeline_config
        )

        if response.success:
            logger.info("Meltano pipeline executed", pipeline=pipeline_config.get('name'))
            return FlextResult.ok(response.data)
        else:
            logger.error("Meltano pipeline failed", error=response.error)
            return FlextResult.fail(f"Pipeline execution failed: {response.error}")

    def get_pipeline_status(self, pipeline_id: str) -> FlextResult[dict]:
        """Get pipeline execution status."""
        if not self.client_result.success:
            return FlextResult.fail("Client not initialized")

        client = self.client_result.data
        response = client.get(f"/api/v1/pipelines/{pipeline_id}/status")

        if response.success:
            return FlextResult.ok(response.data)
        else:
            return FlextResult.fail(f"Status check failed: {response.error}")
```

---

## 🔐 Authentication Service Integration

### **flext-auth Integration**

FLEXT API integrates with flext-auth for distributed authentication across the ecosystem.

```python
from flext_api import create_flext_api, FlextApiAuthPlugin
from flext_core import get_logger, FlextResult
from typing import Optional

logger = get_logger(__name__)

class AuthenticatedApiClient:
    """API client with flext-auth integration."""

    def __init__(self, auth_service_url: str = "http://localhost:8082"):
        self.auth_service_url = auth_service_url
        self.api = create_flext_api()
        self.auth_token: Optional[str] = None

    def authenticate(self, username: str, password: str) -> FlextResult[str]:
        """Authenticate with flext-auth service."""
        # Create temporary client for authentication
        auth_client_result = self.api.flext_api_create_client({
            "base_url": self.auth_service_url,
            "timeout": 10
        })

        if not auth_client_result.success:
            return FlextResult.fail("Auth client creation failed")

        auth_client = auth_client_result.data
        response = auth_client.post("/auth/login", json={
            "username": username,
            "password": password
        })

        if response.success:
            token = response.data.get("access_token")
            if token:
                self.auth_token = token
                logger.info("Authentication successful", username=username)
                return FlextResult.ok(token)
            else:
                return FlextResult.fail("No token in response")
        else:
            logger.warning("Authentication failed", username=username)
            return FlextResult.fail(f"Authentication failed: {response.error}")

    def create_authenticated_client(self, base_url: str) -> FlextResult[object]:
        """Create HTTP client with authentication headers."""
        if not self.auth_token:
            return FlextResult.fail("Not authenticated")

        client_result = self.api.flext_api_create_client({
            "base_url": base_url,
            "timeout": 30,
            "headers": {
                "Authorization": f"Bearer {self.auth_token}",
                "X-Auth-Service": "flext-auth"
            }
        })

        if client_result.success:
            logger.info("Authenticated client created", base_url=base_url)

        return client_result
```

### **Authentication Plugin Pattern**

```python
from flext_api import FlextApiPlugin
from flext_core import FlextResult
from typing import Dict, Any

class FlextApiAuthPlugin(FlextApiPlugin):
    """Authentication plugin for HTTP clients."""

    def __init__(self, auth_token: str):
        self.auth_token = auth_token

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Add authentication headers before request."""
        headers = request_config.get("headers", {})
        headers["Authorization"] = f"Bearer {self.auth_token}"
        request_config["headers"] = headers

        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Process response and handle auth errors."""
        if response.get("status_code") == 401:
            return FlextResult.fail("Authentication expired")

        return FlextResult.ok(response)
```

---

## 📊 Observability Integration

### **flext-observability Integration**

Integration with the observability stack for metrics, tracing, and health monitoring.

```python
from flext_api import create_flext_api
from flext_observability import FlextMetrics, FlextTracer
from flext_core import get_logger, FlextResult
from typing import Dict, Any

logger = get_logger(__name__)
metrics = FlextMetrics()
tracer = FlextTracer()

class ObservableApiClient:
    """API client with observability integration."""

    def __init__(self):
        self.api = create_flext_api()

    def create_monitored_client(self, config: Dict[str, Any]) -> FlextResult[object]:
        """Create HTTP client with observability features."""

        # Add observability plugins
        plugins = [
            FlextApiMetricsPlugin(metrics),
            FlextApiTracingPlugin(tracer)
        ]

        client_result = self.api.flext_api_create_client_with_plugins(
            config, plugins
        )

        if client_result.success:
            logger.info("Monitored client created", base_url=config.get("base_url"))
            metrics.increment("flext_api.client.created")
        else:
            logger.error("Client creation failed", error=client_result.error)
            metrics.increment("flext_api.client.creation_failed")

        return client_result

class FlextApiMetricsPlugin:
    """Plugin for HTTP request metrics collection."""

    def __init__(self, metrics: FlextMetrics):
        self.metrics = metrics

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Record request metrics."""
        self.metrics.increment("flext_api.requests.started")
        self.metrics.histogram("flext_api.request.size", len(str(request_config)))
        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Record response metrics."""
        status_code = response.get("status_code", 0)
        self.metrics.increment(f"flext_api.responses.{status_code}")
        self.metrics.histogram("flext_api.response.size", len(str(response)))
        return FlextResult.ok(response)

class FlextApiTracingPlugin:
    """Plugin for distributed tracing."""

    def __init__(self, tracer: FlextTracer):
        self.tracer = tracer

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Start trace span."""
        span = self.tracer.start_span("http_request")
        span.set_attribute("http.method", request_config.get("method", "GET"))
        span.set_attribute("http.url", request_config.get("url", ""))

        # Store span in request context
        request_config["_trace_span"] = span
        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Complete trace span."""
        span = response.get("_trace_span")
        if span:
            span.set_attribute("http.status_code", response.get("status_code", 0))
            span.finish()

        return FlextResult.ok(response)
```

---

## 🗄️ Infrastructure Library Integration

### **Oracle Database Integration**

Integration with flext-db-oracle for database operations.

```python
from flext_api import create_flext_api
from flext_db_oracle import FlextOracleClient
from flext_core import get_logger, FlextResult
from typing import Dict, Any, List

logger = get_logger(__name__)

class OracleApiIntegration:
    """Integration between FLEXT API and Oracle database operations."""

    def __init__(self, db_config: Dict[str, Any]):
        self.api = create_flext_api()
        self.db_client = FlextOracleClient(db_config)

    def create_data_api_client(self, base_url: str) -> FlextResult[object]:
        """Create API client for Oracle-backed services."""

        # Test database connectivity first
        db_health = self.db_client.health_check()
        if not db_health.success:
            logger.warning("Database connectivity issue", error=db_health.error)

        # Create HTTP client with database context
        client_result = self.api.flext_api_create_client({
            "base_url": base_url,
            "timeout": 45,  # Longer timeout for database operations
            "headers": {
                "X-Database": "oracle",
                "X-Schema": self.db_client.schema_name
            }
        })

        return client_result

    def sync_api_data_to_db(self, api_data: List[Dict[str, Any]]) -> FlextResult[int]:
        """Synchronize API data to Oracle database."""
        try:
            records_processed = 0

            for record in api_data:
                insert_result = self.db_client.insert_record("api_data", record)
                if insert_result.success:
                    records_processed += 1
                else:
                    logger.warning("Record insert failed", record_id=record.get("id"))

            logger.info("Data sync completed", records=records_processed)
            return FlextResult.ok(records_processed)

        except Exception as e:
            logger.exception("Data sync failed")
            return FlextResult.fail(f"Sync failed: {e}")
```

### **LDAP Integration**

Integration with flext-ldap for directory services.

```python
from flext_api import create_flext_api
from flext_ldap import FlextLdapClient
from flext_core import get_logger, FlextResult
from typing import Dict, Any

logger = get_logger(__name__)

class LdapApiIntegration:
    """Integration between FLEXT API and LDAP directory services."""

    def __init__(self, ldap_config: Dict[str, Any]):
        self.api = create_flext_api()
        self.ldap_client = FlextLdapClient(ldap_config)

    def authenticate_api_request(self, username: str, password: str) -> FlextResult[Dict[str, Any]]:
        """Authenticate API request against LDAP directory."""

        # Authenticate with LDAP
        auth_result = self.ldap_client.authenticate(username, password)
        if not auth_result.success:
            return FlextResult.fail(f"LDAP authentication failed: {auth_result.error}")

        # Get user attributes
        user_result = self.ldap_client.get_user_attributes(username)
        if not user_result.success:
            return FlextResult.fail(f"User lookup failed: {user_result.error}")

        user_data = user_result.data
        logger.info("User authenticated successfully", username=username)

        return FlextResult.ok({
            "authenticated": True,
            "username": username,
            "attributes": user_data
        })

    def create_ldap_backed_client(self, base_url: str, username: str) -> FlextResult[object]:
        """Create API client with LDAP user context."""

        # Get user information from LDAP
        user_result = self.ldap_client.get_user_attributes(username)
        if not user_result.success:
            return FlextResult.fail("User not found in LDAP")

        user_data = user_result.data

        # Create client with user context headers
        client_result = self.api.flext_api_create_client({
            "base_url": base_url,
            "timeout": 30,
            "headers": {
                "X-User": username,
                "X-Department": user_data.get("department", ""),
                "X-Groups": ",".join(user_data.get("groups", []))
            }
        })

        return client_result
```

---

## 🎵 Singer Ecosystem Integration

### **Meltano Pipeline Integration**

Integration with flext-meltano for Singer tap and target orchestration.

```python
from flext_api import create_flext_api
from flext_meltano import FlextMeltanoClient
from flext_core import get_logger, FlextResult
from typing import Dict, Any

logger = get_logger(__name__)

class MeltanoPipelineApi:
    """API integration for Meltano pipeline management."""

    def __init__(self):
        self.api = create_flext_api()
        self.meltano_client = FlextMeltanoClient()

    def execute_singer_pipeline(self, pipeline_config: Dict[str, Any]) -> FlextResult[str]:
        """Execute Singer tap-to-target pipeline via API."""

        # Create client for pipeline API
        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8081",
            "timeout": 300,  # Long timeout for pipeline execution
            "headers": {
                "Content-Type": "application/json",
                "X-Pipeline-Type": "singer"
            }
        })

        if not client_result.success:
            return FlextResult.fail("Pipeline client creation failed")

        client = client_result.data

        # Submit pipeline execution request
        response = client.post("/api/v1/pipelines/execute", json={
            "tap": pipeline_config.get("tap"),
            "target": pipeline_config.get("target"),
            "config": pipeline_config.get("config", {}),
            "catalog": pipeline_config.get("catalog"),
            "state": pipeline_config.get("state")
        })

        if response.success:
            execution_id = response.data.get("execution_id")
            logger.info("Pipeline execution started", execution_id=execution_id)
            return FlextResult.ok(execution_id)
        else:
            logger.error("Pipeline execution failed", error=response.error)
            return FlextResult.fail(f"Execution failed: {response.error}")

    def monitor_pipeline_execution(self, execution_id: str) -> FlextResult[Dict[str, Any]]:
        """Monitor pipeline execution status."""

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8081",
            "timeout": 10
        })

        if not client_result.success:
            return FlextResult.fail("Monitoring client creation failed")

        client = client_result.data
        response = client.get(f"/api/v1/pipelines/{execution_id}/status")

        if response.success:
            status_data = response.data
            logger.info("Pipeline status retrieved",
                       execution_id=execution_id,
                       status=status_data.get("status"))
            return FlextResult.ok(status_data)
        else:
            return FlextResult.fail(f"Status retrieval failed: {response.error}")
```

### **DBT Transformation Integration**

Integration with DBT projects for data transformation.

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any, List

logger = get_logger(__name__)

class DbtTransformationApi:
    """API integration for DBT transformations."""

    def __init__(self):
        self.api = create_flext_api()

    def execute_dbt_models(self, project_path: str, models: List[str]) -> FlextResult[Dict[str, Any]]:
        """Execute DBT models via transformation API."""

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8081",
            "timeout": 600,  # Very long timeout for transformations
            "headers": {
                "Content-Type": "application/json",
                "X-Transformation-Engine": "dbt"
            }
        })

        if not client_result.success:
            return FlextResult.fail("DBT client creation failed")

        client = client_result.data
        response = client.post("/api/v1/transformations/dbt/run", json={
            "project_path": project_path,
            "models": models,
            "vars": {},
            "target": "dev"
        })

        if response.success:
            result = response.data
            logger.info("DBT models executed",
                       models=models,
                       status=result.get("status"))
            return FlextResult.ok(result)
        else:
            logger.error("DBT execution failed", models=models, error=response.error)
            return FlextResult.fail(f"DBT execution failed: {response.error}")
```

---

## 🌐 Web Interface Integration

### **flext-web Integration**

Integration with the web interface for dashboard and UI functionality.

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any

logger = get_logger(__name__)

class WebInterfaceApi:
    """API client for web interface backend services."""

    def __init__(self):
        self.api = create_flext_api()

    def get_dashboard_data(self) -> FlextResult[Dict[str, Any]]:
        """Retrieve dashboard data for web interface."""

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8083",  # flext-web service
            "timeout": 15,
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "flext-api"
            }
        })

        if not client_result.success:
            return FlextResult.fail("Web client creation failed")

        client = client_result.data
        response = client.get("/api/v1/dashboard/data")

        if response.success:
            dashboard_data = response.data
            logger.info("Dashboard data retrieved successfully")
            return FlextResult.ok(dashboard_data)
        else:
            logger.warning("Dashboard data retrieval failed", error=response.error)
            return FlextResult.fail(f"Dashboard data failed: {response.error}")

    def update_pipeline_status_ui(self, pipeline_id: str, status: str) -> FlextResult[bool]:
        """Update pipeline status in web interface."""

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8083",
            "timeout": 10
        })

        if not client_result.success:
            return FlextResult.fail("Web client creation failed")

        client = client_result.data
        response = client.put(f"/api/v1/pipelines/{pipeline_id}/status", json={
            "status": status,
            "timestamp": "2024-01-01T00:00:00Z"
        })

        if response.success:
            logger.info("Pipeline status updated in UI", pipeline_id=pipeline_id, status=status)
            return FlextResult.ok(data=True)
        else:
            return FlextResult.fail(f"Status update failed: {response.error}")
```

---

## 🔧 CLI Integration

### **flext-cli Integration**

Integration with command-line tools for automation and scripting.

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any, List

logger = get_logger(__name__)

class CliApiIntegration:
    """API integration for CLI command execution."""

    def __init__(self):
        self.api = create_flext_api()

    def execute_cli_command(self, command: List[str], options: Dict[str, Any] = None) -> FlextResult[Dict[str, Any]]:
        """Execute CLI command via API."""

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8084",  # flext-cli service
            "timeout": 120,  # Longer timeout for CLI operations
            "headers": {
                "Content-Type": "application/json",
                "X-Execution-Mode": "api"
            }
        })

        if not client_result.success:
            return FlextResult.fail("CLI client creation failed")

        client = client_result.data
        response = client.post("/api/v1/cli/execute", json={
            "command": command,
            "options": options or {},
            "working_directory": "/workspace"
        })

        if response.success:
            result = response.data
            logger.info("CLI command executed", command=" ".join(command))
            return FlextResult.ok(result)
        else:
            logger.error("CLI command failed", command=" ".join(command), error=response.error)
            return FlextResult.fail(f"CLI execution failed: {response.error}")
```

---

## 📚 Integration Best Practices

### **Service Discovery Pattern**

```python
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult
from typing import Dict, Any, Optional

logger = get_logger(__name__)

class FlextServiceDiscovery:
    """Service discovery for FLEXT ecosystem."""

    def __init__(self):
        self.api = create_flext_api()
        self.service_registry: Dict[str, str] = {
            "flexcore": "http://localhost:8080",
            "flext-service": "http://localhost:8081",
            "flext-auth": "http://localhost:8082",
            "flext-web": "http://localhost:8083",
            "flext-cli": "http://localhost:8084"
        }

    def get_service_client(self, service_name: str, timeout: int = 30) -> FlextResult[object]:
        """Get HTTP client for specified service."""

        service_url = self.service_registry.get(service_name)
        if not service_url:
            return FlextResult.fail(f"Service not found: {service_name}")

        # Health check service before creating client
        health_result = self.check_service_health(service_name)
        if not health_result.success:
            logger.warning("Service health check failed", service=service_name)

        client_result = self.api.flext_api_create_client({
            "base_url": service_url,
            "timeout": timeout,
            "headers": {
                "X-Source-Service": "flext-api",
                "X-Target-Service": service_name
            }
        })

        return client_result

    def check_service_health(self, service_name: str) -> FlextResult[Dict[str, Any]]:
        """Check health of specified service."""

        service_url = self.service_registry.get(service_name)
        if not service_url:
            return FlextResult.fail(f"Service not found: {service_name}")

        client_result = self.api.flext_api_create_client({
            "base_url": service_url,
            "timeout": 5  # Short timeout for health checks
        })

        if not client_result.success:
            return FlextResult.fail("Health check client creation failed")

        client = client_result.data
        response = client.get("/health")

        if response.success:
            return FlextResult.ok(response.data)
        else:
            return FlextResult.fail(f"Health check failed: {response.error}")
```

### **Circuit Breaker Pattern**

```python
from flext_api import FlextApiCircuitBreakerPlugin
from flext_core import get_logger, FlextResult
from typing import Dict, Any
import time

logger = get_logger(__name__)

class FlextCircuitBreakerPlugin(FlextApiCircuitBreakerPlugin):
    """Circuit breaker for service integration."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def before_request(self, request_config: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Check circuit breaker state before request."""

        current_time = time.time()

        if self.state == "OPEN":
            if current_time - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                return FlextResult.fail("Circuit breaker OPEN - service unavailable")

        return FlextResult.ok(request_config)

    def after_response(self, response: Dict[str, Any]) -> FlextResult[Dict[str, Any]]:
        """Update circuit breaker state after response."""

        status_code = response.get("status_code", 0)

        if status_code >= 500:  # Server error
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning("Circuit breaker OPENED", failures=self.failure_count)
        else:
            # Successful response
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED - service recovered")
            elif self.state == "CLOSED" and self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)

        return FlextResult.ok(response)
```

---

## 📚 Related Documentation

- **[Architecture](architecture.md)** - System design and integration patterns
- **[Configuration](configuration.md)** - Service configuration and settings
- **[Development](development.md)** - Development workflows and standards
- **[API Reference](api-reference.md)** - Complete HTTP client API documentation
- **[Main Documentation Hub](../../docs/NAVIGATION.md)** - FLEXT ecosystem navigation

---

**Integration Guide v0.9.0** - Comprehensive ecosystem integration patterns for FLEXT API HTTP foundation library.
