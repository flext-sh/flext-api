# PATTERNS.md - FLEXT-API CODING PATTERNS

**Reference**: Consolidated patterns from flext-core integration
**Status**: ACTIVE REFERENCE

---

## 🏗️ ARCHITECTURAL PATTERNS

### Clean Architecture Layers
```
┌─────────────────────────────────────┐
│          routes/                    │ ← FastAPI HTTP layer
├─────────────────────────────────────┤
│       application/services/         │ ← Business logic (Use Cases)
├─────────────────────────────────────┤
│          domain/                    │ ← Entities, Value Objects
├─────────────────────────────────────┤
│      infrastructure/                │ ← External systems, DB
└─────────────────────────────────────┘
```

### Dependency Flow (ALWAYS inward)
- Routes → Application Services
- Application → Domain
- Infrastructure → Domain (via ports/interfaces)

---

## 🔧 CORE PATTERNS

### 1. FlextLoggerFactory Pattern
```python
from flext_core import get_logger

# ✅ ALWAYS use this pattern
logger = get_logger(__name__)

# ✅ Available methods (ALL VALID):
logger.info("Operation successful", extra={"user_id": user.id})
logger.warning("Potential issue detected") 
logger.error("Operation failed", exc_info=True)
logger.exception("Critical error occurred")  # ← VALID METHOD!
logger.debug("Debug information")
```

### 2. FlextResult Pattern
```python
from flext_core import FlextResult

async def service_operation() -> FlextResult[DataType]:
    try:
        # Business logic here
        result = await some_operation()
        
        logger.info("Operation completed successfully")
        return FlextResult.ok(result)
        
    except SomeSpecificError as e:
        logger.warning(f"Expected error: {e}")
        return FlextResult.fail(f"Operation failed: {e}")
        
    except Exception as e:
        logger.exception("Unexpected error in operation")
        return FlextResult.fail(f"Unexpected error: {e}")
```

### 3. Service Class Pattern
```python
from flext_core import FlextResult, FlextServiceError, get_logger

logger = get_logger(__name__)

class FlextApiService(BaseService):
    """FLEXT API service following core patterns.
    
    - NO fallbacks or legacy code
    - Uses FlextResult for all operations  
    - Proper exception hierarchy
    - Clean architecture compliance
    """
    
    def __init__(self, dependency: DependencyType) -> None:
        """Initialize with strict dependencies."""
        super().__init__(dependency)
        # Real dependencies only - no mocks in production
```

---

## 🎯 NAMING CONVENTIONS

### Classes
```python
# ✅ CORRECT
class FlextAuthService(AuthenticationService):
class FlextPipelineRepository(PipelineRepository):
class FlextApiError(FlextServiceError):

# ❌ WRONG  
class AuthService:        # Missing Flext prefix
class MockAuthService:    # No mocks in production
class LegacyService:      # No legacy code
```

### Files
```python
# ✅ CORRECT
flext_auth_service.py
flext_pipeline_repository.py
flext_api_handlers.py

# ❌ WRONG
mock_service.py          # No mock files
legacy_handler.py        # No legacy files
temp_fix.py             # No temporary files
```

### Methods
```python
# ✅ CORRECT
async def authenticate_user(self) -> FlextResult[User]:
async def create_pipeline(self) -> FlextResult[Pipeline]:
async def validate_token(self) -> FlextResult[TokenData]:

# ❌ WRONG
def auth_user_fallback():     # No fallbacks
def create_mock_pipeline():   # No mocks  
def temp_validate():          # No temporary methods
```

---

## 🚀 FASTAPI INTEGRATION PATTERNS

### Route Handler Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from flext_core import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["resource"])

@router.post("/resource")
async def create_resource(
    request: ResourceRequest,
    service: FlextResourceService = Depends(get_resource_service)
) -> ResourceResponse:
    """Create resource with proper error handling."""
    try:
        result = await service.create_resource(request)
        
        if not result.success:
            logger.warning(f"Resource creation failed: {result.error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
            
        logger.info("Resource created successfully")
        return ResourceResponse.from_domain(result.data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in resource creation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e
```

### Dependency Injection Pattern
```python
from fastapi import Depends
from flext_core import get_logger

logger = get_logger(__name__)

def get_flext_auth_service() -> FlextAuthService:
    """Get authentication service - NO FALLBACKS."""
    try:
        # Real service configuration
        return FlextAuthService(
            auth_provider=get_auth_provider(),
            session_manager=get_session_manager()
        )
    except Exception as e:
        logger.exception("Failed to create auth service")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        ) from e
```

---

## 📋 ERROR HANDLING PATTERNS

### Exception Hierarchy
```python
from flext_core import FlextServiceError

# ✅ Use flext-core exception hierarchy
class FlextApiError(FlextServiceError):
    """Base API error."""
    
class FlextAuthenticationError(FlextApiError):
    """Authentication specific error."""
    
class FlextValidationError(FlextApiError):
    """Request validation error."""
```

### Logging with Context
```python
# ✅ CORRECT - Structured logging
logger.info(
    "User authenticated successfully",
    extra={
        "user_id": user.id,
        "session_id": session.id,
        "ip_address": request.client.host
    }
)

# ✅ CORRECT - Exception logging  
logger.exception(
    "Authentication failed",
    extra={
        "username": username,
        "error_type": type(e).__name__
    }
)
```

---

## 🔍 TESTING PATTERNS

### Unit Test Pattern
```python
import pytest
from flext_core import FlextResult
from flext_api.application.services.flext_auth_service import FlextAuthService

class TestFlextAuthService:
    """Test FlextAuthService following patterns."""
    
    @pytest.fixture
    def auth_service(self) -> FlextAuthService:
        """Create auth service for testing."""
        return FlextAuthService(
            auth_provider=MockAuthProvider(),  # ✅ Mocks OK in tests
            session_manager=MockSessionManager()
        )
    
    async def test_authenticate_user_success(self, auth_service):
        """Test successful user authentication."""
        # Arrange
        username = "test_user"
        password = "valid_password"
        
        # Act
        result = await auth_service.authenticate_user(username, password)
        
        # Assert
        assert result.success
        assert result.data is not None
        assert result.data.username == username
```

---

## 🚨 ANTI-PATTERNS (NEVER DO)

### ❌ Fallback Implementations
```python
# ❌ WRONG
def get_auth_service():
    try:
        return RealAuthService()
    except:
        return MockAuthService()  # NO FALLBACKS!
```

### ❌ Suppressed Errors
```python
# ❌ WRONG  
try:
    result = risky_operation()
except:
    pass  # NEVER suppress errors!
    
# ✅ CORRECT
try:
    result = risky_operation()
except SpecificError as e:
    logger.warning(f"Expected error: {e}")
    return FlextResult.fail(f"Operation failed: {e}")
```

### ❌ Legacy Code Patterns
```python
# ❌ WRONG
def legacy_auth():
    """Old authentication method."""
    pass

def auth_v2_fallback():
    """Backup authentication.""" 
    pass

# ✅ CORRECT - Single, modern implementation
async def authenticate_user() -> FlextResult[User]:
    """Modern authentication using flext-core patterns."""
    pass
```

---

**REMEMBER**: These patterns are MANDATORY. No exceptions, no compromises.