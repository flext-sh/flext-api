"""Tests for FlextApi thin facade."""

from flext_api import (
    FlextApi,
    FlextApiApp,
    FlextApiClient,
    FlextApiConfig,
    FlextApiConstants,
    FlextApiExceptions,
    FlextApiModels,
    FlextApiProtocols,
    FlextApiStorage,
    FlextApiTypes,
    FlextApiUtilities,
)


class TestFlextApiFacade:
    """Tests for FlextApi thin facade - verifies all modules are properly exposed."""

    def test_facade_exposes_app(self) -> None:
        """Test that FlextApi.App references FlextApiApp."""
        assert FlextApi.App is FlextApiApp
        assert hasattr(FlextApi, "App")

    def test_facade_exposes_client(self) -> None:
        """Test that FlextApi.Client references FlextApiClient."""
        assert FlextApi.Client is FlextApiClient
        assert hasattr(FlextApi, "Client")

    def test_facade_exposes_config(self) -> None:
        """Test that FlextApi.Config references FlextApiConfig."""
        assert FlextApi.Config is FlextApiConfig
        assert hasattr(FlextApi, "Config")

    def test_facade_exposes_constants(self) -> None:
        """Test that FlextApi.Constants references FlextApiConstants."""
        assert FlextApi.Constants is FlextApiConstants
        assert hasattr(FlextApi, "Constants")

    def test_facade_exposes_exceptions(self) -> None:
        """Test that FlextApi.Exceptions references FlextApiExceptions."""
        assert FlextApi.Exceptions is FlextApiExceptions
        assert hasattr(FlextApi, "Exceptions")

    def test_facade_exposes_models(self) -> None:
        """Test that FlextApi.Models references FlextApiModels."""
        assert FlextApi.Models is FlextApiModels
        assert hasattr(FlextApi, "Models")

    def test_facade_exposes_protocols(self) -> None:
        """Test that FlextApi.Protocols references FlextApiProtocols."""
        assert FlextApi.Protocols is FlextApiProtocols
        assert hasattr(FlextApi, "Protocols")

    def test_facade_exposes_storage(self) -> None:
        """Test that FlextApi.Storage references FlextApiStorage."""
        assert FlextApi.Storage is FlextApiStorage
        assert hasattr(FlextApi, "Storage")

    def test_facade_exposes_types(self) -> None:
        """Test that FlextApi.Types references FlextApiTypes."""
        assert FlextApi.Types is FlextApiTypes
        assert hasattr(FlextApi, "Types")

    def test_facade_exposes_utilities(self) -> None:
        """Test that FlextApi.Utilities references FlextApiUtilities."""
        assert FlextApi.Utilities is FlextApiUtilities
        assert hasattr(FlextApi, "Utilities")

    def test_facade_constant_shortcuts(self) -> None:
        """Test that FlextApi provides constant shortcuts."""
        assert FlextApi.HttpMethod is FlextApiConstants.HttpMethod
        assert FlextApi.ClientStatus is FlextApiConstants.ClientStatus
        assert FlextApi.RequestStatus is FlextApiConstants.RequestStatus
        assert FlextApi.ServiceStatus is FlextApiConstants.ServiceStatus
        assert FlextApi.ContentType is FlextApiConstants.ContentType
        assert FlextApi.StorageBackend is FlextApiConstants.StorageBackend
        assert FlextApi.AuthenticationType is FlextApiConstants.AuthenticationType
        assert FlextApi.CacheStrategy is FlextApiConstants.CacheStrategy
        assert FlextApi.LoggingConstants is FlextApiConstants.LoggingConstants

    def test_facade_provides_unified_access(self) -> None:
        """Test that facade provides unified access to all components."""
        # Verify all expected attributes exist
        expected_attributes = [
            "App",
            "Client",
            "Config",
            "Constants",
            "Exceptions",
            "Models",
            "Protocols",
            "Storage",
            "Types",
            "Utilities",
            "HttpMethod",
            "ClientStatus",
            "RequestStatus",
            "ServiceStatus",
            "ContentType",
            "StorageBackend",
            "AuthenticationType",
            "CacheStrategy",
            "LoggingConstants",
        ]

        for attr in expected_attributes:
            assert hasattr(FlextApi, attr), f"FlextApi missing attribute: {attr}"

    def test_client_instantiation_through_facade(self) -> None:
        """Test that client can be instantiated through facade."""
        # This should work - direct instantiation
        client = FlextApi.Client(base_url="https://api.example.com")
        assert client is not None
        assert isinstance(client, FlextApiClient)

    def test_config_instantiation_through_facade(self) -> None:
        """Test that config can be instantiated through facade."""
        # This should work - direct instantiation
        config = FlextApi.Config()
        assert config is not None
        assert isinstance(config, FlextApiConfig)

    def test_storage_instantiation_through_facade(self) -> None:
        """Test that storage can be instantiated through facade."""
        # This should work - direct instantiation
        storage = FlextApi.Storage()
        assert storage is not None
        assert isinstance(storage, FlextApiStorage)

    def test_models_access_through_facade(self) -> None:
        """Test that models can be accessed through facade."""
        # Models is a class with nested classes
        assert hasattr(FlextApi.Models, "HttpRequest")
        assert hasattr(FlextApi.Models, "HttpResponse")
        assert hasattr(FlextApi.Models, "ClientConfig")

    def test_constants_access_through_facade(self) -> None:
        """Test that constants can be accessed through facade."""
        # Constants is a class with constant values
        assert hasattr(FlextApi.Constants, "HTTP_OK")
        assert FlextApi.Constants.HTTP_OK == 200
        assert hasattr(FlextApi.Constants, "DEFAULT_TIMEOUT")

    def test_exceptions_access_through_facade(self) -> None:
        """Test that exceptions can be accessed through facade."""
        # Exceptions is a class with nested exception classes
        assert hasattr(FlextApi.Exceptions, "ValidationError")
        assert hasattr(FlextApi.Exceptions, "AuthenticationError")
        assert hasattr(FlextApi.Exceptions, "NotFoundError")

    def test_facade_is_thin_no_logic(self) -> None:
        """Test that facade contains no logic - only references."""
        # Verify that all class attributes are direct references
        assert FlextApi.Client is FlextApiClient
        assert FlextApi.Config is FlextApiConfig
        assert FlextApi.Constants is FlextApiConstants

        # Verify no instance methods exist (only class references)
        import inspect

        methods = [
            name
            for name, method in inspect.getmembers(FlextApi, predicate=inspect.ismethod)
            if not name.startswith("_")
        ]
        assert len(methods) == 0, f"Facade should have no methods, found: {methods}"
