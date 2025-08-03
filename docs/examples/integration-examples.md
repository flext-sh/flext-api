# Integration Examples

**Real-world integration patterns for FLEXT API with ecosystem services**

> **Navigation**: [FLEXT Hub](../../../docs/NAVIGATION.md) > [flext-api](../../README.md) > [Examples](../) > Integration Examples

---

## 🎯 Integration Examples Overview

This guide demonstrates practical integration patterns between FLEXT API and the broader FLEXT ecosystem, covering service-to-service communication, authentication flows, data pipeline orchestration, and enterprise deployment patterns.

### **Integration Scope**

- **Core Services** - FlexCore (Go:8080) and FLEXT Service (Go/Py:8081)
- **Authentication** - flext-auth service integration with JWT tokens
- **Data Pipelines** - Singer ecosystem with Meltano orchestration
- **Observability** - Metrics, tracing, and health monitoring
- **Enterprise Patterns** - Circuit breakers, retry logic, and fault tolerance

---

## 🏗️ Core Service Integration Examples

### **FlexCore Runtime Integration**

Complete example of integrating with FlexCore for plugin execution and service coordination.

```python
#!/usr/bin/env python3
"""
FlexCore Integration Example
Demonstrates HTTP communication with FlexCore runtime container service.
"""

import asyncio
from typing import Dict, Any, List
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class FlexCoreIntegrationExample:
    """Complete FlexCore integration example."""

    def __init__(self):
        self.api = create_flext_api()
        self.flexcore_client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize FlexCore HTTP client with proper configuration."""
        logger.info("Initializing FlexCore client")

        client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8080",
            "timeout": 60,  # Longer timeout for plugin operations
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "FLEXT-API-Integration/0.9.0",
                "X-Service": "flext-api",
                "X-Integration": "flexcore"
            }
        })

        if client_result.is_success:
            self.flexcore_client = client_result.data
            logger.info("FlexCore client initialized successfully")
        else:
            logger.error("FlexCore client initialization failed", error=client_result.error)
            raise RuntimeError(f"FlexCore client initialization failed: {client_result.error}")

    def health_check(self) -> FlextResult[Dict[str, Any]]:
        """Check FlexCore service health with detailed diagnostics."""
        logger.info("Performing FlexCore health check")

        response = self.flexcore_client.get("/health")

        if response.is_success:
            health_data = response.data
            logger.info("FlexCore health check successful",
                       status=health_data.get("status"),
                       uptime=health_data.get("uptime"))
            return FlextResult.ok(health_data)
        else:
            logger.warning("FlexCore health check failed", error=response.error)
            return FlextResult.fail(f"Health check failed: {response.error}")

    def list_available_plugins(self) -> FlextResult[List[Dict[str, Any]]]:
        """List all available plugins in FlexCore runtime."""
        logger.info("Retrieving available plugins from FlexCore")

        response = self.flexcore_client.get("/api/v1/plugins")

        if response.is_success:
            plugins = response.data.get("plugins", [])
            logger.info("Retrieved plugins list", plugin_count=len(plugins))
            return FlextResult.ok(plugins)
        else:
            logger.error("Failed to retrieve plugins", error=response.error)
            return FlextResult.fail(f"Plugin list retrieval failed: {response.error}")

    def execute_meltano_pipeline(self, pipeline_config: Dict[str, Any]) -> FlextResult[str]:
        """Execute Meltano pipeline via FlexCore plugin system."""
        logger.info("Executing Meltano pipeline via FlexCore",
                   pipeline=pipeline_config.get("name"))

        command = {
            "operation": "execute_pipeline",
            "config": pipeline_config,
            "async": True  # Execute asynchronously
        }

        response = self.flexcore_client.post(
            "/api/v1/plugins/meltano/execute",
            json=command
        )

        if response.is_success:
            execution_id = response.data.get("execution_id")
            logger.info("Meltano pipeline execution started",
                       execution_id=execution_id,
                       pipeline=pipeline_config.get("name"))
            return FlextResult.ok(execution_id)
        else:
            logger.error("Meltano pipeline execution failed",
                        pipeline=pipeline_config.get("name"),
                        error=response.error)
            return FlextResult.fail(f"Pipeline execution failed: {response.error}")

    def monitor_execution(self, execution_id: str) -> FlextResult[Dict[str, Any]]:
        """Monitor plugin execution status."""
        logger.info("Monitoring execution status", execution_id=execution_id)

        response = self.flexcore_client.get(f"/api/v1/executions/{execution_id}/status")

        if response.is_success:
            status_data = response.data
            logger.info("Execution status retrieved",
                       execution_id=execution_id,
                       status=status_data.get("status"),
                       progress=status_data.get("progress", 0))
            return FlextResult.ok(status_data)
        else:
            return FlextResult.fail(f"Status monitoring failed: {response.error}")

async def flexcore_integration_demo():
    """Demonstrate complete FlexCore integration workflow."""
    print("🚀 FlexCore Integration Demo")

    try:
        # Initialize integration
        integration = FlexCoreIntegrationExample()

        # Step 1: Health check
        print("\n=== Step 1: FlexCore Health Check ===")
        health_result = integration.health_check()
        if health_result.is_success:
            print(f"✅ FlexCore is healthy: {health_result.data}")
        else:
            print(f"❌ FlexCore health check failed: {health_result.error}")
            return

        # Step 2: List available plugins
        print("\n=== Step 2: Available Plugins ===")
        plugins_result = integration.list_available_plugins()
        if plugins_result.is_success:
            plugins = plugins_result.data
            print(f"✅ Found {len(plugins)} plugins:")
            for plugin in plugins[:3]:  # Show first 3 plugins
                print(f"  - {plugin.get('name')}: {plugin.get('description')}")
        else:
            print(f"❌ Plugin listing failed: {plugins_result.error}")

        # Step 3: Execute pipeline
        print("\n=== Step 3: Execute Meltano Pipeline ===")
        pipeline_config = {
            "name": "oracle-to-postgres",
            "tap": "tap-oracle",
            "target": "target-postgres",
            "config": {
                "tap_oracle": {
                    "host": "localhost",
                    "port": 1521,
                    "sid": "ORCL"
                },
                "target_postgres": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "warehouse"
                }
            }
        }

        execution_result = integration.execute_meltano_pipeline(pipeline_config)
        if execution_result.is_success:
            execution_id = execution_result.data
            print(f"✅ Pipeline execution started: {execution_id}")

            # Step 4: Monitor execution
            print("\n=== Step 4: Monitor Execution ===")
            for i in range(3):  # Monitor for 3 iterations
                await asyncio.sleep(2)  # Wait 2 seconds
                status_result = integration.monitor_execution(execution_id)
                if status_result.is_success:
                    status = status_result.data
                    print(f"📊 Status: {status.get('status')} "
                          f"({status.get('progress', 0)}% complete)")

                    if status.get('status') in ['completed', 'failed']:
                        break
        else:
            print(f"❌ Pipeline execution failed: {execution_result.error}")

        print("\n✅ FlexCore integration demo completed!")

    except Exception as e:
        logger.exception("FlexCore integration demo failed")
        print(f"❌ Demo failed: {e}")

# Run the demo
if __name__ == "__main__":
    asyncio.run(flexcore_integration_demo())
```

---

## 🔐 Authentication Service Integration

### **JWT Token-Based Authentication**

Complete example of integrating with flext-auth for distributed authentication.

```python
#!/usr/bin/env python3
"""
Authentication Integration Example
Demonstrates JWT-based authentication with flext-auth service.
"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

@dataclass
class AuthToken:
    """Authentication token data structure."""
    access_token: str
    refresh_token: str
    expires_at: float
    token_type: str = "Bearer"

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return time.time() >= self.expires_at

    def expires_in_seconds(self) -> int:
        """Get seconds until token expires."""
        return max(0, int(self.expires_at - time.time()))

class AuthenticatedApiClient:
    """API client with comprehensive authentication integration."""

    def __init__(self, auth_service_url: str = "http://localhost:8082"):
        self.auth_service_url = auth_service_url
        self.api = create_flext_api()
        self.auth_token: Optional[AuthToken] = None
        self._create_auth_client()

    def _create_auth_client(self) -> None:
        """Create HTTP client for authentication service."""
        client_result = self.api.flext_api_create_client({
            "base_url": self.auth_service_url,
            "timeout": 15,
            "headers": {
                "Content-Type": "application/json",
                "User-Agent": "FLEXT-API-Auth/0.9.0"
            }
        })

        if client_result.is_success:
            self.auth_client = client_result.data
            logger.info("Authentication client initialized")
        else:
            logger.error("Auth client creation failed", error=client_result.error)
            raise RuntimeError(f"Auth client creation failed: {client_result.error}")

    def authenticate(self, username: str, password: str) -> FlextResult[AuthToken]:
        """Authenticate user and obtain JWT tokens."""
        logger.info("Authenticating user", username=username)

        response = self.auth_client.post("/auth/login", json={
            "username": username,
            "password": password,
            "grant_type": "password",
            "scope": "read write"
        })

        if response.is_success:
            token_data = response.data

            # Calculate expiration time
            expires_in = token_data.get("expires_in", 3600)  # Default 1 hour
            expires_at = time.time() + expires_in

            auth_token = AuthToken(
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token", ""),
                expires_at=expires_at,
                token_type=token_data.get("token_type", "Bearer")
            )

            self.auth_token = auth_token
            logger.info("Authentication successful",
                       username=username,
                       expires_in=expires_in)
            return FlextResult.ok(auth_token)
        else:
            logger.warning("Authentication failed", username=username)
            return FlextResult.fail(f"Authentication failed: {response.error}")

    def refresh_token(self) -> FlextResult[AuthToken]:
        """Refresh expired access token using refresh token."""
        if not self.auth_token or not self.auth_token.refresh_token:
            return FlextResult.fail("No refresh token available")

        logger.info("Refreshing access token")

        response = self.auth_client.post("/auth/refresh", json={
            "refresh_token": self.auth_token.refresh_token,
            "grant_type": "refresh_token"
        })

        if response.is_success:
            token_data = response.data
            expires_in = token_data.get("expires_in", 3600)
            expires_at = time.time() + expires_in

            # Update existing token
            self.auth_token.access_token = token_data["access_token"]
            self.auth_token.expires_at = expires_at

            logger.info("Token refreshed successfully", expires_in=expires_in)
            return FlextResult.ok(self.auth_token)
        else:
            logger.error("Token refresh failed", error=response.error)
            return FlextResult.fail(f"Token refresh failed: {response.error}")

    def ensure_valid_token(self) -> FlextResult[str]:
        """Ensure we have a valid access token, refreshing if necessary."""
        if not self.auth_token:
            return FlextResult.fail("Not authenticated")

        # Check if token is expired or expires soon (within 60 seconds)
        if self.auth_token.is_expired() or self.auth_token.expires_in_seconds() < 60:
            logger.info("Token expired or expiring soon, refreshing")
            refresh_result = self.refresh_token()
            if not refresh_result.is_success:
                return FlextResult.fail("Token refresh failed")

        return FlextResult.ok(self.auth_token.access_token)

    def create_authenticated_client(self, base_url: str, additional_headers: Dict[str, str] = None) -> FlextResult[object]:
        """Create HTTP client with authentication headers."""
        # Ensure we have a valid token
        token_result = self.ensure_valid_token()
        if not token_result.is_success:
            return FlextResult.fail(f"Authentication required: {token_result.error}")

        access_token = token_result.data

        # Prepare headers
        headers = {
            "Authorization": f"{self.auth_token.token_type} {access_token}",
            "X-Auth-Service": "flext-auth",
            "X-Token-Expires": str(int(self.auth_token.expires_at))
        }

        # Add any additional headers
        if additional_headers:
            headers.update(additional_headers)

        client_result = self.api.flext_api_create_client({
            "base_url": base_url,
            "timeout": 30,
            "headers": headers
        })

        if client_result.is_success:
            logger.info("Authenticated client created",
                       base_url=base_url,
                       token_expires_in=self.auth_token.expires_in_seconds())

        return client_result

    def logout(self) -> FlextResult[bool]:
        """Logout and invalidate tokens."""
        if not self.auth_token:
            return FlextResult.ok(data=True)  # Already logged out

        logger.info("Logging out and invalidating tokens")

        response = self.auth_client.post("/auth/logout", json={
            "access_token": self.auth_token.access_token,
            "refresh_token": self.auth_token.refresh_token
        })

        # Clear local token regardless of server response
        self.auth_token = None

        if response.is_success:
            logger.info("Logout successful")
            return FlextResult.ok(data=True)
        else:
            logger.warning("Server logout failed, but local token cleared",
                          error=response.error)
            return FlextResult.ok(data=True)  # Still consider it successful

def authentication_integration_demo():
    """Demonstrate complete authentication integration workflow."""
    print("🔐 Authentication Integration Demo")

    try:
        # Initialize authenticated client
        auth_client = AuthenticatedApiClient()

        # Step 1: Authenticate
        print("\n=== Step 1: User Authentication ===")
        auth_result = auth_client.authenticate("demo_user", "demo_password")
        if auth_result.is_success:
            token = auth_result.data
            print(f"✅ Authentication successful")
            print(f"   Token expires in: {token.expires_in_seconds()} seconds")
        else:
            print(f"❌ Authentication failed: {auth_result.error}")
            return

        # Step 2: Create authenticated client for API calls
        print("\n=== Step 2: Create Authenticated API Client ===")
        api_client_result = auth_client.create_authenticated_client(
            "http://localhost:8081",  # FLEXT Service
            {"X-Client-Type": "integration-demo"}
        )

        if api_client_result.is_success:
            api_client = api_client_result.data
            print("✅ Authenticated API client created")

            # Step 3: Make authenticated API calls
            print("\n=== Step 3: Authenticated API Calls ===")

            # Call protected endpoint
            response = api_client.get("/api/v1/user/profile")
            if response.is_success:
                profile = response.data
                print(f"✅ Profile retrieved: {profile.get('username')}")
            else:
                print(f"❌ Profile retrieval failed: {response.error}")

            # Call another protected endpoint
            response = api_client.get("/api/v1/pipelines")
            if response.is_success:
                pipelines = response.data
                print(f"✅ Pipelines retrieved: {len(pipelines.get('pipelines', []))} found")
            else:
                print(f"❌ Pipeline retrieval failed: {response.error}")
        else:
            print(f"❌ Authenticated client creation failed: {api_client_result.error}")

        # Step 4: Token refresh demonstration
        print("\n=== Step 4: Token Refresh ===")
        # Simulate token near expiration
        if auth_client.auth_token:
            # Force token to be considered expiring soon
            original_expires_at = auth_client.auth_token.expires_at
            auth_client.auth_token.expires_at = time.time() + 30  # Expires in 30 seconds

            refresh_result = auth_client.ensure_valid_token()
            if refresh_result.is_success:
                print("✅ Token refresh successful")
            else:
                print(f"❌ Token refresh failed: {refresh_result.error}")
                # Restore original expiration for demo
                auth_client.auth_token.expires_at = original_expires_at

        # Step 5: Logout
        print("\n=== Step 5: Logout ===")
        logout_result = auth_client.logout()
        if logout_result.is_success:
            print("✅ Logout successful")
        else:
            print(f"❌ Logout failed: {logout_result.error}")

        print("\n✅ Authentication integration demo completed!")

    except Exception as e:
        logger.exception("Authentication integration demo failed")
        print(f"❌ Demo failed: {e}")

# Run the demo
if __name__ == "__main__":
    authentication_integration_demo()
```

---

## 🎵 Singer Pipeline Integration

### **Complete ETL Pipeline Example**

End-to-end data pipeline integration with Singer taps, targets, and DBT transformations.

```python
#!/usr/bin/env python3
"""
Singer Pipeline Integration Example
Demonstrates complete ETL pipeline orchestration with Singer ecosystem.
"""

import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PipelineExecution:
    """Pipeline execution tracking data."""
    execution_id: str
    pipeline_name: str
    status: PipelineStatus = PipelineStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    error_message: Optional[str] = None
    logs: List[str] = field(default_factory=list)

    def duration_seconds(self) -> Optional[float]:
        """Calculate execution duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class SingerPipelineOrchestrator:
    """Complete Singer pipeline orchestration client."""

    def __init__(self):
        self.api = create_flext_api()
        self._initialize_clients()
        self.executions: Dict[str, PipelineExecution] = {}

    def _initialize_clients(self) -> None:
        """Initialize HTTP clients for different services."""
        # FLEXT Service client (main orchestration)
        flext_client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8081",
            "timeout": 300,  # 5 minutes for long-running operations
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "singer-orchestrator",
                "X-Version": "0.9.0"
            }
        })

        if flext_client_result.is_success:
            self.flext_client = flext_client_result.data
            logger.info("FLEXT Service client initialized")
        else:
            raise RuntimeError(f"FLEXT Service client failed: {flext_client_result.error}")

        # FlexCore client (plugin management)
        flexcore_client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8080",
            "timeout": 120,
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "singer-orchestrator"
            }
        })

        if flexcore_client_result.is_success:
            self.flexcore_client = flexcore_client_result.data
            logger.info("FlexCore client initialized")
        else:
            logger.warning("FlexCore client initialization failed")
            self.flexcore_client = None

    def list_available_taps(self) -> FlextResult[List[Dict[str, Any]]]:
        """List all available Singer taps."""
        logger.info("Retrieving available Singer taps")

        response = self.flext_client.get("/api/v1/singer/taps")

        if response.is_success:
            taps = response.data.get("taps", [])
            logger.info("Retrieved taps list", tap_count=len(taps))
            return FlextResult.ok(taps)
        else:
            return FlextResult.fail(f"Taps retrieval failed: {response.error}")

    def list_available_targets(self) -> FlextResult[List[Dict[str, Any]]]:
        """List all available Singer targets."""
        logger.info("Retrieving available Singer targets")

        response = self.flext_client.get("/api/v1/singer/targets")

        if response.is_success:
            targets = response.data.get("targets", [])
            logger.info("Retrieved targets list", target_count=len(targets))
            return FlextResult.ok(targets)
        else:
            return FlextResult.fail(f"Targets retrieval failed: {response.error}")

    def execute_tap_to_target(self,
                             tap_name: str,
                             target_name: str,
                             tap_config: Dict[str, Any],
                             target_config: Dict[str, Any],
                             catalog: Optional[Dict[str, Any]] = None,
                             state: Optional[Dict[str, Any]] = None) -> FlextResult[str]:
        """Execute complete tap-to-target data pipeline."""

        pipeline_name = f"{tap_name}-to-{target_name}"
        logger.info("Executing Singer pipeline",
                   pipeline=pipeline_name,
                   tap=tap_name,
                   target=target_name)

        # Prepare pipeline configuration
        pipeline_config = {
            "name": pipeline_name,
            "tap": {
                "name": tap_name,
                "config": tap_config,
                "catalog": catalog
            },
            "target": {
                "name": target_name,
                "config": target_config
            },
            "state": state,
            "async": True,
            "options": {
                "log_level": "INFO",
                "buffer_size": 1000,
                "batch_size": 100
            }
        }

        response = self.flext_client.post(
            "/api/v1/singer/execute",
            json=pipeline_config
        )

        if response.is_success:
            execution_id = response.data.get("execution_id")

            # Track execution
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_name=pipeline_name,
                status=PipelineStatus.RUNNING,
                started_at=datetime.now()
            )
            self.executions[execution_id] = execution

            logger.info("Pipeline execution started",
                       execution_id=execution_id,
                       pipeline=pipeline_name)
            return FlextResult.ok(execution_id)
        else:
            logger.error("Pipeline execution failed",
                        pipeline=pipeline_name,
                        error=response.error)
            return FlextResult.fail(f"Pipeline execution failed: {response.error}")

    def get_execution_status(self, execution_id: str) -> FlextResult[PipelineExecution]:
        """Get detailed execution status and metrics."""
        logger.info("Retrieving execution status", execution_id=execution_id)

        response = self.flext_client.get(f"/api/v1/singer/executions/{execution_id}")

        if response.is_success:
            status_data = response.data
            status_str = status_data.get("status", "unknown")

            # Update local tracking
            if execution_id in self.executions:
                execution = self.executions[execution_id]
                execution.status = PipelineStatus(status_str)
                execution.records_processed = status_data.get("records_processed", 0)
                execution.error_message = status_data.get("error_message")

                if status_str in ["completed", "failed"] and not execution.completed_at:
                    execution.completed_at = datetime.now()

                # Add new logs
                new_logs = status_data.get("logs", [])
                execution.logs.extend(new_logs)

                logger.info("Execution status updated",
                           execution_id=execution_id,
                           status=status_str,
                           records=execution.records_processed)

                return FlextResult.ok(execution)
            else:
                # Create new tracking entry
                execution = PipelineExecution(
                    execution_id=execution_id,
                    pipeline_name=status_data.get("pipeline_name", "unknown"),
                    status=PipelineStatus(status_str),
                    records_processed=status_data.get("records_processed", 0),
                    error_message=status_data.get("error_message")
                )
                self.executions[execution_id] = execution
                return FlextResult.ok(execution)
        else:
            return FlextResult.fail(f"Status retrieval failed: {response.error}")

    def execute_dbt_transformation(self,
                                  project_path: str,
                                  models: List[str],
                                  vars: Dict[str, Any] = None) -> FlextResult[str]:
        """Execute DBT transformations after data loading."""
        logger.info("Executing DBT transformation",
                   project=project_path,
                   models=models)

        transformation_config = {
            "type": "dbt",
            "project_path": project_path,
            "models": models,
            "vars": vars or {},
            "target": "prod",
            "options": {
                "full_refresh": False,
                "fail_fast": True,
                "threads": 4
            }
        }

        response = self.flext_client.post(
            "/api/v1/transformations/execute",
            json=transformation_config
        )

        if response.is_success:
            execution_id = response.data.get("execution_id")
            logger.info("DBT transformation started", execution_id=execution_id)
            return FlextResult.ok(execution_id)
        else:
            logger.error("DBT transformation failed", error=response.error)
            return FlextResult.fail(f"DBT execution failed: {response.error}")

    async def wait_for_completion(self,
                                execution_id: str,
                                max_wait_seconds: int = 3600,
                                poll_interval: int = 10) -> FlextResult[PipelineExecution]:
        """Wait for pipeline execution to complete with periodic status updates."""
        logger.info("Waiting for execution completion",
                   execution_id=execution_id,
                   max_wait=max_wait_seconds)

        total_waited = 0

        while total_waited < max_wait_seconds:
            status_result = self.get_execution_status(execution_id)

            if not status_result.is_success:
                return FlextResult.fail(f"Status check failed: {status_result.error}")

            execution = status_result.data

            if execution.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                logger.info("Execution completed",
                           execution_id=execution_id,
                           status=execution.status.value,
                           duration=execution.duration_seconds(),
                           records=execution.records_processed)
                return FlextResult.ok(execution)

            # Still running, wait and check again
            await asyncio.sleep(poll_interval)
            total_waited += poll_interval

            logger.debug("Execution still running",
                        execution_id=execution_id,
                        status=execution.status.value,
                        waited=total_waited)

        # Timeout reached
        logger.warning("Execution timeout reached",
                      execution_id=execution_id,
                      max_wait=max_wait_seconds)
        return FlextResult.fail(f"Execution timeout after {max_wait_seconds} seconds")

async def singer_pipeline_integration_demo():
    """Demonstrate complete Singer pipeline integration."""
    print("🎵 Singer Pipeline Integration Demo")

    try:
        # Initialize orchestrator
        orchestrator = SingerPipelineOrchestrator()

        # Step 1: List available taps and targets
        print("\n=== Step 1: Available Singer Components ===")

        taps_result = orchestrator.list_available_taps()
        if taps_result.is_success:
            taps = taps_result.data
            print(f"✅ Available taps: {len(taps)}")
            for tap in taps[:3]:  # Show first 3
                print(f"  - {tap.get('name')}: {tap.get('description')}")
        else:
            print(f"❌ Taps listing failed: {taps_result.error}")
            return

        targets_result = orchestrator.list_available_targets()
        if targets_result.is_success:
            targets = targets_result.data
            print(f"✅ Available targets: {len(targets)}")
            for target in targets[:3]:  # Show first 3
                print(f"  - {target.get('name')}: {target.get('description')}")
        else:
            print(f"❌ Targets listing failed: {targets_result.error}")
            return

        # Step 2: Execute Oracle to PostgreSQL pipeline
        print("\n=== Step 2: Execute Oracle → PostgreSQL Pipeline ===")

        tap_config = {
            "host": "localhost",
            "port": 1521,
            "sid": "ORCL",
            "username": "hr",
            "password": "hr_password",
            "filter_schemas": ["HR"]
        }

        target_config = {
            "host": "localhost",
            "port": 5432,
            "database": "warehouse",
            "username": "postgres",
            "password": "postgres_password",
            "default_target_schema": "hr_data"
        }

        catalog = {
            "streams": [
                {
                    "tap_stream_id": "employees",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "employee_id": {"type": "integer"},
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "email": {"type": "string"},
                            "hire_date": {"type": "string", "format": "date"}
                        }
                    },
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "replication-method": "INCREMENTAL",
                                "replication-key": "hire_date",
                                "selected": True
                            }
                        }
                    ]
                }
            ]
        }

        execution_result = orchestrator.execute_tap_to_target(
            tap_name="tap-oracle",
            target_name="target-postgres",
            tap_config=tap_config,
            target_config=target_config,
            catalog=catalog
        )

        if execution_result.is_success:
            execution_id = execution_result.data
            print(f"✅ Pipeline execution started: {execution_id}")

            # Step 3: Monitor execution
            print("\n=== Step 3: Monitor Pipeline Execution ===")

            completion_result = await orchestrator.wait_for_completion(
                execution_id,
                max_wait_seconds=300,  # 5 minutes
                poll_interval=5
            )

            if completion_result.is_success:
                execution = completion_result.data

                if execution.status == PipelineStatus.COMPLETED:
                    print(f"✅ Pipeline completed successfully!")
                    print(f"   Records processed: {execution.records_processed}")
                    print(f"   Duration: {execution.duration_seconds():.1f} seconds")

                    # Step 4: Execute DBT transformations
                    print("\n=== Step 4: Execute DBT Transformations ===")

                    dbt_result = orchestrator.execute_dbt_transformation(
                        project_path="/workspace/dbt/hr_analytics",
                        models=["staging", "marts.employee_metrics"],
                        vars={"refresh_date": "2024-01-01"}
                    )

                    if dbt_result.is_success:
                        dbt_execution_id = dbt_result.data
                        print(f"✅ DBT transformation started: {dbt_execution_id}")

                        # Monitor DBT execution
                        dbt_completion = await orchestrator.wait_for_completion(
                            dbt_execution_id,
                            max_wait_seconds=600,  # 10 minutes for transformations
                            poll_interval=10
                        )

                        if dbt_completion.is_success:
                            dbt_exec = dbt_completion.data
                            if dbt_exec.status == PipelineStatus.COMPLETED:
                                print("✅ DBT transformations completed successfully!")
                            else:
                                print(f"❌ DBT transformations failed: {dbt_exec.error_message}")
                        else:
                            print(f"❌ DBT monitoring failed: {dbt_completion.error}")
                    else:
                        print(f"❌ DBT execution failed: {dbt_result.error}")

                elif execution.status == PipelineStatus.FAILED:
                    print(f"❌ Pipeline failed: {execution.error_message}")
                    if execution.logs:
                        print("📋 Recent logs:")
                        for log in execution.logs[-5:]:  # Show last 5 logs
                            print(f"   {log}")
                else:
                    print(f"⚠️  Pipeline ended with status: {execution.status.value}")
            else:
                print(f"❌ Pipeline monitoring failed: {completion_result.error}")
        else:
            print(f"❌ Pipeline execution failed: {execution_result.error}")

        print("\n✅ Singer pipeline integration demo completed!")

    except Exception as e:
        logger.exception("Singer pipeline integration demo failed")
        print(f"❌ Demo failed: {e}")

# Run the demo
if __name__ == "__main__":
    asyncio.run(singer_pipeline_integration_demo())
```

---

## 📊 Observability Integration

### **Comprehensive Monitoring Example**

Complete observability integration with metrics, tracing, and health monitoring.

```python
#!/usr/bin/env python3
"""
Observability Integration Example
Demonstrates comprehensive monitoring, metrics, and tracing integration.
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from dataclasses import dataclass, field
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

@dataclass
class MetricDataPoint:
    """Metric data point structure."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: str = "gauge"  # gauge, counter, histogram

@dataclass
class TraceSpan:
    """Distributed tracing span structure."""
    span_id: str
    trace_id: str
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    tags: Dict[str, str] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    parent_span_id: Optional[str] = None

    def duration_ms(self) -> Optional[float]:
        """Calculate span duration in milliseconds."""
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return None

class ObservabilityIntegration:
    """Complete observability integration client."""

    def __init__(self):
        self.api = create_flext_api()
        self.metrics: List[MetricDataPoint] = []
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_spans: List[TraceSpan] = []
        self._initialize_clients()

    def _initialize_clients(self) -> None:
        """Initialize observability service clients."""

        # Metrics client (Prometheus/InfluxDB endpoint)
        metrics_client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:9090",  # Prometheus
            "timeout": 10,
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "flext-observability"
            }
        })

        if metrics_client_result.is_success:
            self.metrics_client = metrics_client_result.data
            logger.info("Metrics client initialized")
        else:
            logger.warning("Metrics client initialization failed")
            self.metrics_client = None

        # Tracing client (Jaeger endpoint)
        tracing_client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:14268",  # Jaeger collector
            "timeout": 5,
            "headers": {
                "Content-Type": "application/json",
                "X-Client": "flext-tracing"
            }
        })

        if tracing_client_result.is_success:
            self.tracing_client = tracing_client_result.data
            logger.info("Tracing client initialized")
        else:
            logger.warning("Tracing client initialization failed")
            self.tracing_client = None

        # Health monitoring client
        health_client_result = self.api.flext_api_create_client({
            "base_url": "http://localhost:8080",  # FlexCore health
            "timeout": 5,
            "headers": {"X-Client": "health-monitor"}
        })

        if health_client_result.is_success:
            self.health_client = health_client_result.data
            logger.info("Health client initialized")
        else:
            logger.warning("Health client initialization failed")
            self.health_client = None

    def record_metric(self,
                     name: str,
                     value: float,
                     metric_type: str = "gauge",
                     tags: Dict[str, str] = None) -> None:
        """Record a metric data point."""
        metric = MetricDataPoint(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {},
            metric_type=metric_type
        )

        self.metrics.append(metric)
        logger.debug("Metric recorded",
                    name=name,
                    value=value,
                    type=metric_type)

    def start_span(self,
                   operation_name: str,
                   trace_id: Optional[str] = None,
                   parent_span_id: Optional[str] = None,
                   tags: Dict[str, str] = None) -> str:
        """Start a new tracing span."""
        span_id = str(uuid.uuid4())
        trace_id = trace_id or str(uuid.uuid4())

        span = TraceSpan(
            span_id=span_id,
            trace_id=trace_id,
            operation_name=operation_name,
            start_time=time.time(),
            tags=tags or {},
            parent_span_id=parent_span_id
        )

        self.active_spans[span_id] = span
        logger.debug("Span started",
                    operation=operation_name,
                    span_id=span_id,
                    trace_id=trace_id)

        return span_id

    def finish_span(self, span_id: str, tags: Dict[str, str] = None) -> None:
        """Finish an active tracing span."""
        if span_id in self.active_spans:
            span = self.active_spans.pop(span_id)
            span.end_time = time.time()

            if tags:
                span.tags.update(tags)

            self.completed_spans.append(span)
            logger.debug("Span finished",
                        operation=span.operation_name,
                        span_id=span_id,
                        duration_ms=span.duration_ms())

    def add_span_log(self, span_id: str, message: str, fields: Dict[str, Any] = None) -> None:
        """Add a log entry to an active span."""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            log_entry = {
                "timestamp": time.time(),
                "message": message,
                "fields": fields or {}
            }
            span.logs.append(log_entry)

    @contextmanager
    def trace_operation(self, operation_name: str, tags: Dict[str, str] = None):
        """Context manager for tracing operations."""
        span_id = self.start_span(operation_name, tags=tags)
        try:
            yield span_id
        except Exception as e:
            self.add_span_log(span_id, f"Operation failed: {e}", {"error": True})
            self.finish_span(span_id, {"error": "true", "error.message": str(e)})
            raise
        else:
            self.finish_span(span_id, {"success": "true"})

    def send_metrics_batch(self) -> FlextResult[int]:
        """Send accumulated metrics to monitoring system."""
        if not self.metrics_client or not self.metrics:
            return FlextResult.ok(0)

        logger.info("Sending metrics batch", count=len(self.metrics))

        # Convert metrics to Prometheus format
        metrics_data = []
        for metric in self.metrics:
            metric_dict = {
                "name": metric.name,
                "value": metric.value,
                "timestamp": int(metric.timestamp * 1000),  # Convert to milliseconds
                "type": metric.metric_type,
                "tags": metric.tags
            }
            metrics_data.append(metric_dict)

        response = self.metrics_client.post("/api/v1/metrics", json={
            "metrics": metrics_data
        })

        if response.is_success:
            sent_count = len(self.metrics)
            self.metrics.clear()  # Clear sent metrics
            logger.info("Metrics sent successfully", count=sent_count)
            return FlextResult.ok(sent_count)
        else:
            logger.error("Metrics send failed", error=response.error)
            return FlextResult.fail(f"Metrics send failed: {response.error}")

    def send_traces_batch(self) -> FlextResult[int]:
        """Send completed traces to tracing system."""
        if not self.tracing_client or not self.completed_spans:
            return FlextResult.ok(0)

        logger.info("Sending traces batch", count=len(self.completed_spans))

        # Convert spans to Jaeger format
        traces_data = []
        for span in self.completed_spans:
            span_dict = {
                "traceID": span.trace_id,
                "spanID": span.span_id,
                "parentSpanID": span.parent_span_id,
                "operationName": span.operation_name,
                "startTime": int(span.start_time * 1000000),  # Microseconds
                "duration": int((span.end_time - span.start_time) * 1000000),
                "tags": [{"key": k, "value": v} for k, v in span.tags.items()],
                "logs": [
                    {
                        "timestamp": int(log["timestamp"] * 1000000),
                        "fields": [{"key": k, "value": v} for k, v in log["fields"].items()]
                    }
                    for log in span.logs
                ]
            }
            traces_data.append(span_dict)

        response = self.tracing_client.post("/api/traces", json={
            "data": [{
                "traceID": traces_data[0]["traceID"] if traces_data else "unknown",
                "spans": traces_data
            }]
        })

        if response.is_success:
            sent_count = len(self.completed_spans)
            self.completed_spans.clear()  # Clear sent spans
            logger.info("Traces sent successfully", count=sent_count)
            return FlextResult.ok(sent_count)
        else:
            logger.error("Traces send failed", error=response.error)
            return FlextResult.fail(f"Traces send failed: {response.error}")

    def health_check_all_services(self) -> FlextResult[Dict[str, Any]]:
        """Perform health checks on all ecosystem services."""
        logger.info("Performing comprehensive health checks")

        services = {
            "flexcore": "http://localhost:8080/health",
            "flext-service": "http://localhost:8081/health",
            "flext-auth": "http://localhost:8082/health",
            "flext-web": "http://localhost:8083/health"
        }

        health_results = {}

        for service_name, health_url in services.items():
            with self.trace_operation(f"health_check_{service_name}") as span_id:
                try:
                    # Create temporary client for each health check
                    client_result = self.api.flext_api_create_client({
                        "base_url": health_url.rsplit('/', 1)[0],
                        "timeout": 5
                    })

                    if client_result.is_success:
                        client = client_result.data
                        response = client.get("/health")

                        if response.is_success:
                            health_data = response.data
                            health_results[service_name] = {
                                "status": "healthy",
                                "response_time_ms": None,  # Would need timing
                                "details": health_data
                            }

                            # Record health metric
                            self.record_metric(
                                f"service_health_{service_name}",
                                1.0,  # 1 = healthy, 0 = unhealthy
                                "gauge",
                                {"service": service_name}
                            )
                        else:
                            health_results[service_name] = {
                                "status": "unhealthy",
                                "error": response.error
                            }
                            self.record_metric(
                                f"service_health_{service_name}",
                                0.0,
                                "gauge",
                                {"service": service_name}
                            )
                    else:
                        health_results[service_name] = {
                            "status": "unreachable",
                            "error": client_result.error
                        }
                        self.record_metric(
                            f"service_health_{service_name}",
                            0.0,
                            "gauge",
                            {"service": service_name}
                        )

                except Exception as e:
                    logger.exception("Health check failed", service=service_name)
                    health_results[service_name] = {
                        "status": "error",
                        "error": str(e)
                    }
                    self.add_span_log(span_id, f"Health check error: {e}")

        # Calculate overall health score
        healthy_count = sum(1 for result in health_results.values()
                          if result["status"] == "healthy")
        total_count = len(health_results)
        health_score = (healthy_count / total_count) * 100

        self.record_metric("ecosystem_health_score", health_score, "gauge")

        logger.info("Health checks completed",
                   healthy=healthy_count,
                   total=total_count,
                   score=health_score)

        return FlextResult.ok({
            "overall_health_score": health_score,
            "services": health_results,
            "healthy_services": healthy_count,
            "total_services": total_count
        })

def observability_integration_demo():
    """Demonstrate comprehensive observability integration."""
    print("📊 Observability Integration Demo")

    try:
        # Initialize observability
        obs = ObservabilityIntegration()

        # Step 1: Health monitoring
        print("\n=== Step 1: Ecosystem Health Monitoring ===")

        with obs.trace_operation("ecosystem_health_check"):
            health_result = obs.health_check_all_services()

            if health_result.is_success:
                health_data = health_result.data
                score = health_data["overall_health_score"]
                healthy = health_data["healthy_services"]
                total = health_data["total_services"]

                print(f"✅ Health Score: {score:.1f}% ({healthy}/{total} services healthy)")

                for service, status in health_data["services"].items():
                    status_icon = "✅" if status["status"] == "healthy" else "❌"
                    print(f"   {status_icon} {service}: {status['status']}")
            else:
                print(f"❌ Health check failed: {health_result.error}")

        # Step 2: Metrics collection
        print("\n=== Step 2: Metrics Collection ===")

        # Simulate API operations with metrics
        operations = ["create_client", "http_request", "plugin_execution"]

        for operation in operations:
            with obs.trace_operation(f"simulate_{operation}") as span_id:
                # Simulate operation duration
                duration_ms = time.time() * 1000
                time.sleep(0.1)  # Simulate work
                duration_ms = (time.time() * 1000) - duration_ms

                # Record metrics
                obs.record_metric(f"operation_duration_{operation}", duration_ms, "histogram")
                obs.record_metric(f"operation_count_{operation}", 1, "counter")

                obs.add_span_log(span_id, f"Operation {operation} completed")

                print(f"📈 Recorded metrics for {operation} (duration: {duration_ms:.1f}ms)")

        # Step 3: Custom business metrics
        print("\n=== Step 3: Business Metrics ===")

        business_metrics = [
            ("pipelines_executed_today", 42, "counter"),
            ("data_volume_gb", 156.7, "gauge"),
            ("error_rate_percent", 0.5, "gauge"),
            ("active_connections", 23, "gauge")
        ]

        for name, value, metric_type in business_metrics:
            obs.record_metric(name, value, metric_type, {"environment": "production"})
            print(f"📊 Business metric: {name} = {value} ({metric_type})")

        # Step 4: Send observability data
        print("\n=== Step 4: Send Observability Data ===")

        # Send metrics
        metrics_result = obs.send_metrics_batch()
        if metrics_result.is_success:
            print(f"✅ Sent {metrics_result.data} metrics to monitoring system")
        else:
            print(f"❌ Metrics send failed: {metrics_result.error}")

        # Send traces
        traces_result = obs.send_traces_batch()
        if traces_result.is_success:
            print(f"✅ Sent {traces_result.data} trace spans to tracing system")
        else:
            print(f"❌ Traces send failed: {traces_result.error}")

        # Step 5: Summary
        print("\n=== Step 5: Observability Summary ===")
        print(f"✅ Active spans: {len(obs.active_spans)}")
        print(f"✅ Completed spans: {len(obs.completed_spans)}")
        print(f"✅ Pending metrics: {len(obs.metrics)}")

        print("\n✅ Observability integration demo completed!")

    except Exception as e:
        logger.exception("Observability integration demo failed")
        print(f"❌ Demo failed: {e}")

# Run the demo
if __name__ == "__main__":
    observability_integration_demo()
```

---

## 🏢 Enterprise Patterns

### **Circuit Breaker and Fault Tolerance**

Enterprise-grade fault tolerance patterns for production deployments.

```python
#!/usr/bin/env python3
"""
Enterprise Fault Tolerance Example
Demonstrates circuit breaker, retry logic, and fault tolerance patterns.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered

@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: int = 5          # Failures before opening
    recovery_timeout: int = 60          # Seconds before trying half-open
    success_threshold: int = 3          # Successes needed to close from half-open
    timeout_threshold: int = 30         # Request timeout in seconds

class EnterpriseCircuitBreaker:
    """Production-grade circuit breaker implementation."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.last_request_time = 0

        logger.info("Circuit breaker initialized",
                   name=name,
                   failure_threshold=config.failure_threshold)

    def can_execute(self) -> FlextResult[bool]:
        """Check if request can be executed based on circuit state."""
        current_time = time.time()
        self.last_request_time = current_time

        if self.state == CircuitState.CLOSED:
            return FlextResult.ok(data=True)

        elif self.state == CircuitState.OPEN:
            # Check if enough time has passed to try half-open
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN", name=self.name)
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return FlextResult.ok(data=True)
            else:
                return FlextResult.fail("Circuit breaker OPEN - service unavailable")

        elif self.state == CircuitState.HALF_OPEN:
            # Allow limited requests to test service health
            return FlextResult.ok(data=True)

        return FlextResult.fail("Invalid circuit breaker state")

    def record_success(self) -> None:
        """Record successful request."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            logger.debug("Half-open success recorded",
                        name=self.name,
                        success_count=self.success_count)

            if self.success_count >= self.config.success_threshold:
                logger.info("Circuit breaker CLOSED - service recovered", name=self.name)
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0

        elif self.state == CircuitState.CLOSED:
            # Reset failure count on successful request
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self) -> None:
        """Record failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        logger.warning("Circuit breaker failure recorded",
                      name=self.name,
                      failure_count=self.failure_count,
                      threshold=self.config.failure_threshold)

        if self.state == CircuitState.HALF_OPEN:
            # Immediately return to OPEN on any failure during half-open
            logger.warning("Circuit breaker OPEN - half-open test failed", name=self.name)
            self.state = CircuitState.OPEN
            self.success_count = 0

        elif (self.state == CircuitState.CLOSED and
              self.failure_count >= self.config.failure_threshold):
            logger.error("Circuit breaker OPEN - failure threshold exceeded",
                        name=self.name,
                        failures=self.failure_count)
            self.state = CircuitState.OPEN

    def get_status(self) -> Dict[str, Any]:
        """Get current circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "last_request_time": self.last_request_time
        }

class EnterpriseHttpClient:
    """HTTP client with enterprise fault tolerance patterns."""

    def __init__(self):
        self.api = create_flext_api()
        self.circuit_breakers: Dict[str, EnterpriseCircuitBreaker] = {}
        self.clients: Dict[str, Any] = {}

    def get_or_create_circuit_breaker(self, service_name: str) -> EnterpriseCircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self.circuit_breakers:
            config = CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                success_threshold=3,
                timeout_threshold=30
            )
            self.circuit_breakers[service_name] = EnterpriseCircuitBreaker(
                service_name, config
            )

        return self.circuit_breakers[service_name]

    def get_or_create_client(self, service_name: str, base_url: str) -> FlextResult[Any]:
        """Get or create HTTP client for service."""
        if service_name not in self.clients:
            client_result = self.api.flext_api_create_client({
                "base_url": base_url,
                "timeout": 30,
                "headers": {
                    "X-Circuit-Breaker": service_name,
                    "X-Client": "enterprise-fault-tolerant"
                }
            })

            if client_result.is_success:
                self.clients[service_name] = client_result.data
                logger.info("HTTP client created", service=service_name)
                return FlextResult.ok(client_result.data)
            else:
                return FlextResult.fail(f"Client creation failed: {client_result.error}")

        return FlextResult.ok(self.clients[service_name])

    async def request_with_fault_tolerance(self,
                                         service_name: str,
                                         base_url: str,
                                         method: str,
                                         path: str,
                                         max_retries: int = 3,
                                         backoff_factor: float = 2.0,
                                         **kwargs) -> FlextResult[Dict[str, Any]]:
        """Make HTTP request with comprehensive fault tolerance."""

        circuit_breaker = self.get_or_create_circuit_breaker(service_name)

        # Check circuit breaker
        can_execute = circuit_breaker.can_execute()
        if not can_execute.is_success:
            logger.warning("Request blocked by circuit breaker",
                          service=service_name,
                          reason=can_execute.error)
            return FlextResult.fail(can_execute.error)

        # Get HTTP client
        client_result = self.get_or_create_client(service_name, base_url)
        if not client_result.is_success:
            circuit_breaker.record_failure()
            return FlextResult.fail(client_result.error)

        client = client_result.data

        # Retry loop with exponential backoff
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                logger.debug("Making HTTP request",
                           service=service_name,
                           method=method,
                           path=path,
                           attempt=attempt + 1)

                # Make request based on method
                if method.upper() == "GET":
                    response = client.get(path, **kwargs)
                elif method.upper() == "POST":
                    response = client.post(path, **kwargs)
                elif method.upper() == "PUT":
                    response = client.put(path, **kwargs)
                elif method.upper() == "DELETE":
                    response = client.delete(path, **kwargs)
                else:
                    return FlextResult.fail(f"Unsupported HTTP method: {method}")

                if response.is_success:
                    circuit_breaker.record_success()
                    logger.info("Request successful",
                               service=service_name,
                               method=method,
                               path=path,
                               attempt=attempt + 1)
                    return FlextResult.ok(response.data)
                else:
                    last_error = response.error
                    logger.warning("Request failed",
                                  service=service_name,
                                  method=method,
                                  path=path,
                                  attempt=attempt + 1,
                                  error=response.error)

            except Exception as e:
                last_error = str(e)
                logger.exception("Request exception",
                               service=service_name,
                               attempt=attempt + 1)

            # Don't retry on last attempt
            if attempt < max_retries:
                # Exponential backoff
                delay = backoff_factor ** attempt
                logger.info("Retrying request",
                           service=service_name,
                           delay=delay,
                           next_attempt=attempt + 2)
                await asyncio.sleep(delay)

        # All retries failed
        circuit_breaker.record_failure()
        error_msg = f"Request failed after {max_retries + 1} attempts: {last_error}"
        logger.error("Request failed permanently",
                    service=service_name,
                    method=method,
                    path=path,
                    error=error_msg)

        return FlextResult.fail(error_msg)

    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: cb.get_status()
                for name, cb in self.circuit_breakers.items()}

async def enterprise_fault_tolerance_demo():
    """Demonstrate enterprise fault tolerance patterns."""
    print("🏢 Enterprise Fault Tolerance Demo")

    try:
        # Initialize enterprise client
        enterprise_client = EnterpriseHttpClient()

        # Step 1: Normal operations
        print("\n=== Step 1: Normal Operations ===")

        # Test with reliable service (httpbin.org)
        result = await enterprise_client.request_with_fault_tolerance(
            service_name="httpbin",
            base_url="https://httpbin.org",
            method="GET",
            path="/json"
        )

        if result.is_success:
            print("✅ Normal request successful")
        else:
            print(f"❌ Normal request failed: {result.error}")

        # Step 2: Fault tolerance with unreliable service
        print("\n=== Step 2: Fault Tolerance Testing ===")

        # Test with unreliable service (simulate with delays/errors)
        unreliable_requests = [
            ("/delay/1", "Normal request"),
            ("/status/500", "Server error"),
            ("/status/503", "Service unavailable"),
            ("/status/404", "Not found"),
            ("/delay/5", "Timeout request")
        ]

        for path, description in unreliable_requests:
            print(f"\n--- Testing: {description} ---")

            result = await enterprise_client.request_with_fault_tolerance(
                service_name="unreliable-service",
                base_url="https://httpbin.org",
                method="GET",
                path=path,
                max_retries=2,
                backoff_factor=1.5
            )

            if result.is_success:
                print(f"✅ {description}: Request successful")
            else:
                print(f"❌ {description}: {result.error}")

            # Show circuit breaker status
            cb_status = enterprise_client.get_circuit_breaker_status()
            if "unreliable-service" in cb_status:
                status = cb_status["unreliable-service"]
                print(f"   Circuit Breaker: {status['state']} "
                      f"(failures: {status['failure_count']})")

            # Small delay between requests
            await asyncio.sleep(0.5)

        # Step 3: Circuit breaker behavior
        print("\n=== Step 3: Circuit Breaker Behavior ===")

        # Force circuit breaker to open with multiple failures
        print("Forcing circuit breaker to OPEN with multiple failures...")

        for i in range(6):  # Exceed failure threshold
            result = await enterprise_client.request_with_fault_tolerance(
                service_name="failing-service",
                base_url="https://httpbin.org",
                method="GET",
                path="/status/500",
                max_retries=1,
                backoff_factor=1.0
            )

            cb_status = enterprise_client.get_circuit_breaker_status()
            if "failing-service" in cb_status:
                status = cb_status["failing-service"]
                print(f"   Attempt {i+1}: Circuit state = {status['state']} "
                      f"(failures: {status['failure_count']})")

        # Try request when circuit is open
        print("\nTrying request with circuit breaker OPEN...")
        result = await enterprise_client.request_with_fault_tolerance(
            service_name="failing-service",
            base_url="https://httpbin.org",
            method="GET",
            path="/json",
            max_retries=1
        )

        if result.is_failure:
            print(f"✅ Circuit breaker correctly blocked request: {result.error}")

        # Step 4: Circuit breaker recovery simulation
        print("\n=== Step 4: Circuit Breaker Recovery ===")
        print("Simulating recovery timeout...")

        # Manually set recovery time for demo (normally would wait 60 seconds)
        if "failing-service" in enterprise_client.circuit_breakers:
            cb = enterprise_client.circuit_breakers["failing-service"]
            cb.last_failure_time = time.time() - 65  # Simulate 65 seconds ago
            print("Recovery timeout simulated")

        # Try request to trigger half-open state
        result = await enterprise_client.request_with_fault_tolerance(
            service_name="failing-service",
            base_url="https://httpbin.org",
            method="GET",
            path="/json",  # Use successful endpoint
            max_retries=1
        )

        if result.is_success:
            print("✅ Service recovered, circuit breaker should close")

        # Final status
        print("\n=== Final Circuit Breaker Status ===")
        final_status = enterprise_client.get_circuit_breaker_status()
        for service, status in final_status.items():
            print(f"🔧 {service}: {status['state']} "
                  f"(failures: {status['failure_count']}, "
                  f"successes: {status['success_count']})")

        print("\n✅ Enterprise fault tolerance demo completed!")

    except Exception as e:
        logger.exception("Enterprise fault tolerance demo failed")
        print(f"❌ Demo failed: {e}")

# Run the demo
if __name__ == "__main__":
    asyncio.run(enterprise_fault_tolerance_demo())
```

---

## 📋 Integration Best Practices

### **Service Discovery and Configuration Management**

```python
#!/usr/bin/env python3
"""
Service Discovery and Configuration Example
Demonstrates dynamic service discovery and configuration management.
"""

import os
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from flext_api import create_flext_api
from flext_core import get_logger, FlextResult

logger = get_logger(__name__)

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    name: str
    url: str
    health_path: str = "/health"
    timeout: int = 30
    tags: Dict[str, str] = field(default_factory=dict)
    priority: int = 1  # Lower number = higher priority

class FlextServiceRegistry:
    """Dynamic service discovery and registry."""

    def __init__(self):
        self.api = create_flext_api()
        self.services: Dict[str, List[ServiceEndpoint]] = {}
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load service configuration from environment and files."""

        # Default FLEXT ecosystem services
        default_services = {
            "flexcore": [
                ServiceEndpoint("flexcore-primary", "http://localhost:8080", tags={"role": "primary"}),
                ServiceEndpoint("flexcore-secondary", "http://localhost:8081", priority=2, tags={"role": "secondary"})
            ],
            "flext-service": [
                ServiceEndpoint("flext-service", "http://localhost:8081")
            ],
            "flext-auth": [
                ServiceEndpoint("flext-auth", "http://localhost:8082")
            ],
            "flext-web": [
                ServiceEndpoint("flext-web", "http://localhost:8083")
            ],
            "flext-cli": [
                ServiceEndpoint("flext-cli", "http://localhost:8084")
            ]
        }

        self.services.update(default_services)

        # Load from environment variables
        self._load_from_environment()

        # Load from configuration file
        config_file = os.getenv("FLEXT_SERVICES_CONFIG", "services.json")
        if os.path.exists(config_file):
            self._load_from_file(config_file)

        logger.info("Service registry initialized",
                   services=list(self.services.keys()),
                   total_endpoints=sum(len(endpoints) for endpoints in self.services.values()))

    def _load_from_environment(self) -> None:
        """Load service endpoints from environment variables."""
        # Pattern: FLEXT_SERVICE_<NAME>_URL=http://host:port
        for key, value in os.environ.items():
            if key.startswith("FLEXT_SERVICE_") and key.endswith("_URL"):
                # Extract service name: FLEXT_SERVICE_AUTH_URL -> auth
                service_name = key[14:-4].lower().replace("_", "-")  # Remove prefix/suffix

                endpoint = ServiceEndpoint(
                    name=f"{service_name}-env",
                    url=value,
                    tags={"source": "environment"}
                )

                if service_name not in self.services:
                    self.services[service_name] = []

                self.services[service_name].append(endpoint)
                logger.info("Service loaded from environment",
                           service=service_name,
                           url=value)

    def _load_from_file(self, config_file: str) -> None:
        """Load service configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            for service_name, endpoints_config in config.get("services", {}).items():
                if not isinstance(endpoints_config, list):
                    endpoints_config = [endpoints_config]

                for endpoint_config in endpoints_config:
                    endpoint = ServiceEndpoint(
                        name=endpoint_config.get("name", f"{service_name}-file"),
                        url=endpoint_config["url"],
                        health_path=endpoint_config.get("health_path", "/health"),
                        timeout=endpoint_config.get("timeout", 30),
                        tags=endpoint_config.get("tags", {"source": "file"}),
                        priority=endpoint_config.get("priority", 1)
                    )

                    if service_name not in self.services:
                        self.services[service_name] = []

                    self.services[service_name].append(endpoint)

            logger.info("Services loaded from file",
                       file=config_file,
                       services=list(config.get("services", {}).keys()))

        except Exception as e:
            logger.warning("Failed to load services from file",
                          file=config_file,
                          error=str(e))

    def discover_service(self, service_name: str) -> FlextResult[ServiceEndpoint]:
        """Discover healthy service endpoint with load balancing."""
        if service_name not in self.services:
            return FlextResult.fail(f"Service not found: {service_name}")

        endpoints = self.services[service_name]

        # Sort by priority (lower number = higher priority)
        sorted_endpoints = sorted(endpoints, key=lambda x: x.priority)

        # Try each endpoint in priority order
        for endpoint in sorted_endpoints:
            health_result = self._check_endpoint_health(endpoint)
            if health_result.is_success:
                logger.info("Service discovered",
                           service=service_name,
                           endpoint=endpoint.name,
                           url=endpoint.url)
                return FlextResult.ok(endpoint)

        # No healthy endpoints found
        return FlextResult.fail(f"No healthy endpoints found for service: {service_name}")

    def _check_endpoint_health(self, endpoint: ServiceEndpoint) -> FlextResult[Dict[str, Any]]:
        """Check if endpoint is healthy."""
        try:
            client_result = self.api.flext_api_create_client({
                "base_url": endpoint.url,
                "timeout": 5  # Quick health check timeout
            })

            if not client_result.is_success:
                return FlextResult.fail(f"Client creation failed: {client_result.error}")

            client = client_result.data
            response = client.get(endpoint.health_path)

            if response.is_success:
                return FlextResult.ok(response.data)
            else:
                return FlextResult.fail(f"Health check failed: {response.error}")

        except Exception as e:
            return FlextResult.fail(f"Health check exception: {e}")

    def create_service_client(self, service_name: str, **client_options) -> FlextResult[Any]:
        """Create HTTP client for discovered service."""
        discovery_result = self.discover_service(service_name)
        if not discovery_result.is_success:
            return FlextResult.fail(discovery_result.error)

        endpoint = discovery_result.data

        # Merge endpoint settings with client options
        config = {
            "base_url": endpoint.url,
            "timeout": endpoint.timeout,
            "headers": {
                "X-Service-Discovery": "flext-registry",
                "X-Endpoint": endpoint.name
            }
        }
        config.update(client_options)

        client_result = self.api.flext_api_create_client(config)

        if client_result.is_success:
            logger.info("Service client created",
                       service=service_name,
                       endpoint=endpoint.name)

        return client_result

    def list_services(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all registered services and their endpoints."""
        result = {}
        for service_name, endpoints in self.services.items():
            result[service_name] = [
                {
                    "name": ep.name,
                    "url": ep.url,
                    "health_path": ep.health_path,
                    "timeout": ep.timeout,
                    "priority": ep.priority,
                    "tags": ep.tags
                }
                for ep in endpoints
            ]
        return result

def service_discovery_demo():
    """Demonstrate service discovery and configuration management."""
    print("🔍 Service Discovery and Configuration Demo")

    try:
        # Create sample configuration file for demo
        sample_config = {
            "services": {
                "custom-api": [
                    {
                        "name": "custom-api-prod",
                        "url": "https://httpbin.org",
                        "health_path": "/status/200",
                        "timeout": 10,
                        "priority": 1,
                        "tags": {"environment": "production"}
                    },
                    {
                        "name": "custom-api-staging",
                        "url": "https://httpbin.org",
                        "health_path": "/status/200",
                        "timeout": 5,
                        "priority": 2,
                        "tags": {"environment": "staging"}
                    }
                ]
            }
        }

        with open("services.json", "w") as f:
            json.dump(sample_config, f, indent=2)

        # Initialize service registry
        registry = FlextServiceRegistry()

        # Step 1: List all services
        print("\n=== Step 1: Service Registry Overview ===")
        services = registry.list_services()

        for service_name, endpoints in services.items():
            print(f"🔧 {service_name}: {len(endpoints)} endpoint(s)")
            for endpoint in endpoints:
                print(f"   - {endpoint['name']}: {endpoint['url']} "
                      f"(priority: {endpoint['priority']})")

        # Step 2: Service discovery
        print("\n=== Step 2: Service Discovery ===")

        test_services = ["flexcore", "flext-auth", "custom-api"]

        for service_name in test_services:
            print(f"\n--- Discovering {service_name} ---")

            discovery_result = registry.discover_service(service_name)
            if discovery_result.is_success:
                endpoint = discovery_result.data
                print(f"✅ Discovered: {endpoint.name} at {endpoint.url}")
                print(f"   Tags: {endpoint.tags}")
            else:
                print(f"❌ Discovery failed: {discovery_result.error}")

        # Step 3: Create service clients
        print("\n=== Step 3: Service Client Creation ===")

        # Create client for discovered service
        client_result = registry.create_service_client(
            "custom-api",
            headers={"X-Demo": "service-discovery"}
        )

        if client_result.is_success:
            print("✅ Service client created successfully")

            # Test the client
            client = client_result.data
            response = client.get("/json")

            if response.is_success:
                print("✅ Service client test successful")
                print(f"   Response keys: {list(response.data.keys())}")
            else:
                print(f"❌ Service client test failed: {response.error}")
        else:
            print(f"❌ Service client creation failed: {client_result.error}")

        # Step 4: Load balancing demonstration
        print("\n=== Step 4: Load Balancing ===")

        # Add environment variable service for testing
        os.environ["FLEXT_SERVICE_DEMO_API_URL"] = "https://httpbin.org"

        # Reload registry to pick up environment changes
        registry = FlextServiceRegistry()

        # Test load balancing by calling service multiple times
        for i in range(3):
            discovery_result = registry.discover_service("demo-api")
            if discovery_result.is_success:
                endpoint = discovery_result.data
                print(f"Request {i+1}: Using {endpoint.name} ({endpoint.url})")
            else:
                print(f"Request {i+1}: Discovery failed")

        # Cleanup
        if os.path.exists("services.json"):
            os.remove("services.json")

        print("\n✅ Service discovery demo completed!")

    except Exception as e:
        logger.exception("Service discovery demo failed")
        print(f"❌ Demo failed: {e}")

        # Cleanup on error
        if os.path.exists("services.json"):
            os.remove("services.json")

# Run the demo
if __name__ == "__main__":
    service_discovery_demo()
```

---

## 📚 Next Steps

### **Advanced Integration Topics**

After mastering these integration examples, explore:

- **[Advanced Patterns](advanced-patterns.md)** - Complex integration patterns and optimization
- **[Basic Usage](basic-usage.md)** - Fundamental FLEXT API usage patterns
- **[Architecture Guide](../architecture.md)** - Understanding the integration architecture
- **[Development Guide](../development.md)** - Contributing to integration patterns

### **Related Documentation**

- **[Configuration](../configuration.md)** - Advanced configuration for integrations
- **[Troubleshooting](../troubleshooting.md)** - Debugging integration issues
- **[Main Documentation Hub](../../../docs/NAVIGATION.md)** - Complete FLEXT ecosystem

### **Production Deployment**

- **Circuit Breaker Patterns** - Implement fault tolerance in production
- **Service Mesh Integration** - Istio/Linkerd integration patterns
- **Observability Stack** - Prometheus, Grafana, Jaeger integration
- **Security Patterns** - mTLS, JWT tokens, and RBAC integration

---

**Integration Examples v0.9.0** - Real-world integration patterns for FLEXT API HTTP foundation library.
