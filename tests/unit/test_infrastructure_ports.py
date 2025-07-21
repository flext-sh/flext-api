"""Tests for FLEXT API infrastructure ports implementations."""

from __future__ import annotations

from uuid import uuid4

import pytest

from flext_api.infrastructure.config import APIConfig
from flext_api.infrastructure.ports import JWTAuthService

# COMMENTED OUT - These test classes are for non-existent port implementations
# Once the actual infrastructure port implementations are added, these tests can be
# uncommented

# class TestMemoryCacheBackend:
#     """Test MemoryCacheBackend implementation."""
#     # ... tests commented out until MemoryCacheBackend is implemented

# class TestJWTSecurityService:
#     """Test JWTSecurityService implementation."""
#     # ... tests commented out until JWTSecurityService is implemented


class TestJWTAuthService:
    """Test REAL JWTAuthService implementation."""

    @pytest.fixture
    def real_config(self) -> APIConfig:
        """Create REAL API config for testing - NO MOCKS."""
        return APIConfig()

    def test_jwt_auth_service_initialization(self, real_config: APIConfig) -> None:
        """Test JWT auth service initializes correctly with REAL config."""
        service = JWTAuthService(real_config)
        # Check that token manager is properly initialized (SRP compliance)
        assert service.token_manager is not None
        assert len(service.token_manager.secret_key) >= 16  # Reasonable minimum length
        assert service.token_manager.algorithm == "HS256"
        assert service.token_manager.expire_minutes == 30
        # Check that authorization strategy is initialized (DIP compliance)
        assert service.authorization_strategy is not None
        assert service.authorization_strategy.get_strategy_name() == "basic"

    @pytest.mark.asyncio
    async def test_generate_and_authenticate_token(
        self,
        real_config: APIConfig,
    ) -> None:
        """Test generating REAL JWT token and authenticating it."""
        service = JWTAuthService(real_config)

        # Generate a real JWT token
        user_data = {
            "user_id": "test_user_123",
            "username": "test_user",
            "email": "test@example.com",
        }
        token = await service.generate_token(user_data)

        # Token should be a real JWT string
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        assert "." in token  # JWT has dots

        # Authenticate the token
        result = await service.authenticate(token)
        assert result is not None
        assert result["user_id"] == "test_user_123"
        assert result["username"] == "test_user"
        assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_authenticate_invalid_token(self, real_config: APIConfig) -> None:
        """Test authenticating with invalid token."""
        service = JWTAuthService(real_config)

        result = await service.authenticate("invalid_token")
        assert result is None

    @pytest.mark.asyncio
    async def test_authorize_user(self, real_config: APIConfig) -> None:
        """Test authorizing user access."""
        service = JWTAuthService(real_config)

        user_id = uuid4()
        result = await service.authorize(user_id, "resource", "read")
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_token_same_as_authenticate(
        self,
        real_config: APIConfig,
    ) -> None:
        """Test that validate_token returns same as authenticate."""
        service = JWTAuthService(real_config)

        # Generate a real token
        user_data = {"user_id": "test_user_456", "username": "test_validate"}
        token = await service.generate_token(user_data)

        # Both methods should return the same result
        auth_result = await service.authenticate(token)
        validate_result = await service.validate_token(token)

        assert auth_result == validate_result
        if auth_result is not None and isinstance(auth_result, dict):
            assert auth_result["user_id"] == "test_user_456"


# COMMENTED OUT - These infrastructure implementations don't exist yet
#
# class TestRedisCache:
#     """Test RedisCache implementation."""
#     # ... tests commented out until RedisCache is implemented


# COMMENTED OUT - All remaining infrastructure implementations don't exist yet
# Once infrastructure ports are implemented, these test classes can be uncommented:
#
# class TestPrometheusMetricsService:
# class TestPostgreSQLHealthCheck:
# class TestMemoryRateLimitService:
# class TestFastAPIMiddleware:
# class TestUvicornServer:
# class TestPydanticValidationService:
#
# All these tests are waiting for the actual infrastructure implementations
