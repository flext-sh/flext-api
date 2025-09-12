"""FLEXT API - Example of using FlextConfig as source of truth.

This example demonstrates how to use FlextConfig singleton pattern
in the flext-api module, showing how parameters can change behavior
and how FlextConfig serves as the single source of truth.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import os

from flext_api import FlextApiClient, FlextApiConfig


async def main() -> None:
    """Demonstrate FlextConfig usage in flext-api."""
    print("🚀 FLEXT API - FlextConfig Singleton Usage Example")
    print("=" * 60)

    # =========================================================================
    # 1. BASIC SINGLETON USAGE - Get global instance
    # =========================================================================
    print("\n📋 1. Basic Singleton Usage")
    print("-" * 30)

    # Get the global singleton instance (source of truth)
    config = FlextApiConfig.get_global_instance()
    print(f"Global config instance: {config}")
    print(f"API Host: {config.api_host}")
    print(f"API Port: {config.api_port}")
    print(f"Workers: {config.workers}")
    print(f"Debug Mode: {config.api_debug}")

    # =========================================================================
    # 2. ENVIRONMENT VARIABLE OVERRIDES
    # =========================================================================
    print("\n🌍 2. Environment Variable Overrides")
    print("-" * 40)

    # Set environment variables to override configuration
    os.environ["FLEXT_API_HOST"] = "0.0.0.0"
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

    # =========================================================================
    # 3. PARAMETER OVERRIDES - Change behavior with parameters
    # =========================================================================
    print("\n⚙️ 3. Parameter Overrides - Change Behavior")
    print("-" * 45)

    # Create configuration with specific parameter overrides
    production_config_result = FlextApiConfig.create_with_overrides(
        api_host="prod-api.example.com",
        api_port=443,
        workers=16,
        api_debug=False,
        environment="production"
    )

    if production_config_result.is_success:
        prod_config = production_config_result.value
        print("Production config created:")
        print(f"  API Host: {prod_config.api_host}")
        print(f"  API Port: {prod_config.api_port}")
        print(f"  Workers: {prod_config.workers}")
        print(f"  Debug Mode: {prod_config.api_debug}")
        print(f"  Environment: {prod_config.environment}")

    # Create development configuration with different parameters
    dev_config_result = FlextApiConfig.create_with_overrides(
        api_host="localhost",
        api_port=8000,
        workers=2,
        api_debug=True,
        environment="development"
    )

    if dev_config_result.is_success:
        dev_config = dev_config_result.value
        print("\nDevelopment config created:")
        print(f"  API Host: {dev_config.api_host}")
        print(f"  API Port: {dev_config.api_port}")
        print(f"  Workers: {dev_config.workers}")
        print(f"  Debug Mode: {dev_config.api_debug}")
        print(f"  Environment: {dev_config.environment}")

    # =========================================================================
    # 4. USING CONFIG IN SERVICES - FlextConfig as source of truth
    # =========================================================================
    print("\n🔧 4. Using Config in Services")
    print("-" * 35)

    # Create API client using FlextConfig as source of truth
    # Method 1: Use global singleton
    client1 = FlextApiClient()  # Uses global FlextConfig automatically
    print(f"Client 1 (global config): {client1.base_url}")

    # Method 2: Use specific configuration
    if production_config_result.is_success:
        client2 = FlextApiClient(config=production_config_result.value)
        print(f"Client 2 (production config): {client2.base_url}")

    # Method 3: Use configuration with additional overrides
    client3 = FlextApiClient(
        config=dev_config_result.value if dev_config_result.is_success else None,
        timeout=60.0,  # Override timeout
        max_retries=5   # Override retries
    )
    print(f"Client 3 (dev config + overrides): {client3.base_url}")
    print(f"  Timeout: {client3.timeout}")
    print(f"  Max Retries: {client3.max_retries}")

    # =========================================================================
    # 5. CONFIGURATION VALIDATION
    # =========================================================================
    print("\n✅ 5. Configuration Validation")
    print("-" * 35)

    # Validate production configuration
    if production_config_result.is_success:
        validation_result = production_config_result.value.validate_business_rules()
        if validation_result.is_success:
            print("✅ Production configuration is valid")
        else:
            print(f"❌ Production configuration validation failed: {validation_result.error}")

    # Validate development configuration
    if dev_config_result.is_success:
        validation_result = dev_config_result.value.validate_business_rules()
        if validation_result.is_success:
            print("✅ Development configuration is valid")
        else:
            print(f"❌ Development configuration validation failed: {validation_result.error}")

    # =========================================================================
    # 6. CONFIGURATION EXPORT AND SERIALIZATION
    # =========================================================================
    print("\n📤 6. Configuration Export")
    print("-" * 30)

    if production_config_result.is_success:
        prod_config = production_config_result.value

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
            for key, value in client_config_result.value.items():
                print(f"  {key}: {value}")

        # Export CORS configuration
        cors_config_result = prod_config.get_cors_config()
        if cors_config_result.is_success:
            print("\nCORS Configuration:")
            for key, value in cors_config_result.value.items():
                print(f"  {key}: {value}")

    # =========================================================================
    # 7. GLOBAL INSTANCE MANAGEMENT
    # =========================================================================
    print("\n🌐 7. Global Instance Management")
    print("-" * 40)

    # Set a specific configuration as global
    if dev_config_result.is_success:
        FlextApiConfig.set_global_instance(dev_config_result.value)
        print("✅ Development configuration set as global instance")

        # Verify global instance
        global_config = FlextApiConfig.get_global_instance()
        print(f"Global instance API Host: {global_config.api_host}")
        print(f"Global instance Debug Mode: {global_config.api_debug}")

    # Clear global instance
    FlextApiConfig.clear_global_instance()
    print("✅ Global instance cleared")

    print("\n🎉 FlextConfig usage example completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
