"""FLEXT API - Example of using FlextConfig as source of truth.

This example demonstrates how to use FlextConfig singleton pattern
in the flext-api module, showing how parameters can change behavior
and how FlextConfig serves as the single source of truth.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from collections.abc import Mapping

from flext_api import FlextApiClient, FlextApiConfig


def _demonstrate_basic_singleton() -> None:
    """Demonstrate basic singleton usage."""
    print("\n📋 1. Basic Singleton Usage")
    print("-" * 30)

    config = FlextApiConfig.get_global_instance()
    print(f"Global config instance: {config}")
    print(f"API Host: {config.api_host}")
    print(f"API Port: {config.api_port}")
    print(f"Workers: {config.workers}")
    print(f"Debug Mode: {config.api_debug}")


def _demonstrate_environment_overrides() -> None:
    """Demonstrate environment variable overrides."""
    print("\n🌍 2. Environment Variable Overrides")
    print("-" * 40)

    # Set environment variables to override configuration
    os.environ["FLEXT_API_HOST"] = "127.0.0.1"
    os.environ["FLEXT_API_PORT"] = "9000"
    os.environ["FLEXT_API_WORKERS"] = "8"
    os.environ["FLEXT_API_DEBUG"] = "true"

    # Clear global instance to force reload from environment
    FlextApiConfig.clear_global_instance()

    # Get new instance with environment overrides
    env_config = FlextApiConfig.get_global_instance()
    print("Environment overridden config:")
    print(f"  API Host: {env_config.api_host}")
    print(f"  API Port: {env_config.api_port}")
    print(f"  Workers: {env_config.workers}")
    print(f"  Debug Mode: {env_config.api_debug}")


def _create_configurations() -> tuple[FlextApiConfig, FlextApiConfig]:
    """Create production and development configurations.

    Returns:
        Tuple of (production_config, development_config).

    Raises:
        RuntimeError: If configuration creation fails.

    """
    print("\n⚙️ 3. Parameter Overrides - Change Behavior")
    print("-" * 45)

    # Create configuration with specific parameter overrides
    prod_config_result = FlextApiConfig.create_with_overrides(
        api_host="prod-api.example.com",
        api_port=443,
        workers=16,
        api_debug=False,
    )

    if not prod_config_result.success:
        print(f"❌ Configuration creation failed: {prod_config_result.error}")
        msg = "Failed to create production config"
        raise RuntimeError(msg)

    prod_config = prod_config_result.value
    print("Production config created:")
    print(f"  API Host: {prod_config.api_host}")
    print(f"  API Port: {prod_config.api_port}")
    print(f"  Workers: {prod_config.workers}")
    print(f"  Debug Mode: {prod_config.api_debug}")
    print("  Environment: production")

    # Create development configuration with different parameters
    dev_config_result = FlextApiConfig.create_with_overrides(
        api_host="localhost",
        api_port=8000,
        workers=2,
        api_debug=True,
    )

    if not dev_config_result.success:
        print(
            f"❌ Development configuration creation failed: {dev_config_result.error}"
        )
        msg = "Failed to create development config"
        raise RuntimeError(msg)

    dev_config = dev_config_result.value
    print("\nDevelopment config created:")
    print(f"  API Host: {dev_config.api_host}")
    print(f"  API Port: {dev_config.api_port}")
    print(f"  Workers: {dev_config.workers}")
    print(f"  Debug Mode: {dev_config.api_debug}")
    print("  Environment: development")

    return prod_config, dev_config


def _demonstrate_service_usage(
    prod_config: FlextApiConfig, dev_config: FlextApiConfig
) -> None:
    """Demonstrate using config in services."""
    print("\n🔧 4. Using Config in Services")
    print("-" * 35)

    # Create API client using FlextConfig as source of truth
    # Method 1: Use global singleton
    client1 = FlextApiClient()  # Uses global FlextConfig automatically
    print(f"Client 1 (global config): {client1.base_url}")

    # Method 2: Use specific configuration
    client2 = FlextApiClient(config=prod_config)
    print(f"Client 2 (production config): {client2.base_url}")

    # Method 3: Use configuration with additional overrides
    client3 = FlextApiClient(
        config=dev_config,
        timeout=60.0,  # Override timeout
        max_retries=5,  # Override retries
    )
    print(f"Client 3 (dev config + overrides): {client3.base_url}")
    print(f"  Timeout: {client3.timeout}")
    print(f"  Max Retries: {client3.max_retries}")


def _demonstrate_validation(
    prod_config: FlextApiConfig, dev_config: FlextApiConfig
) -> None:
    """Demonstrate configuration validation."""
    print("\n✅ 5. Configuration Validation")
    print("-" * 35)

    # Validate production configuration
    validation_result = prod_config.validate_business_rules()
    if validation_result.is_success:
        print("✅ Production configuration is valid")
    else:
        print(
            f"❌ Production configuration validation failed: {validation_result.error}"
        )

    # Validate development configuration
    validation_result = dev_config.validate_business_rules()
    if validation_result.is_success:
        print("✅ Development configuration is valid")
    else:
        print(
            f"❌ Development configuration validation failed: {validation_result.error}"
        )


def _demonstrate_export(prod_config: FlextApiConfig) -> None:
    """Demonstrate configuration export."""
    print("\n📤 6. Configuration Export")
    print("-" * 30)

    # Export server configuration
    server_config_result = prod_config.get_server_config()
    if server_config_result.is_success:
        print("Server Configuration:")
        for key, value in server_config_result.value.items():
            print(f"  {key}: {value}")

    # Export client configuration
    client_config_result = prod_config.get_client_config()
    if client_config_result.is_success:
        print("\nClient Configuration:")
        client_config_dict: Mapping[str, object] = client_config_result.value
        for key in client_config_dict:
            config_value: object = client_config_dict[key]
            print(f"  {key}: {config_value}")

    # Export CORS configuration
    cors_config_result = prod_config.get_cors_config()
    if cors_config_result.is_success:
        print("\nCORS Configuration:")
        cors_config_dict: Mapping[str, object] = cors_config_result.value
        for key in cors_config_dict:
            cors_value: object = cors_config_dict[key]
            print(f"  {key}: {cors_value}")


def _demonstrate_global_management(dev_config: FlextApiConfig) -> None:
    """Demonstrate global instance management."""
    print("\n🌐 7. Global Instance Management")
    print("-" * 40)

    # Set a specific configuration as global
    FlextApiConfig.set_global_instance(dev_config)
    print("✅ Development configuration set as global instance")

    # Verify global instance
    global_config = FlextApiConfig.get_global_instance()
    print(f"Global instance API Host: {global_config.api_host}")
    print(f"Global instance Debug Mode: {global_config.api_debug}")

    # Clear global instance
    FlextApiConfig.clear_global_instance()
    print("✅ Global instance cleared")


def main() -> None:
    """Demonstrate FlextConfig usage in flext-api."""
    print("🚀 FLEXT API - FlextConfig Singleton Usage Example")
    print("=" * 60)

    try:
        _demonstrate_basic_singleton()
        _demonstrate_environment_overrides()
        prod_config, dev_config = _create_configurations()
        _demonstrate_service_usage(prod_config, dev_config)
        _demonstrate_validation(prod_config, dev_config)
        _demonstrate_export(prod_config)
        _demonstrate_global_management(dev_config)

        print("\n🎉 FlextConfig usage example completed!")
        print("=" * 60)
    except RuntimeError as e:
        print(f"❌ Example failed: {e}")
        return


if __name__ == "__main__":
    main()
