"""Command-line interface for FLEXT API."""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse as argparse_types

# Constants
HTTP_OK = 200


def info_command(_args: argparse_types.Namespace) -> int:
    """Show FLEXT API information."""
    return 0


def serve_command(args: argparse_types.Namespace) -> int:
    """Start the API server."""
    try:
        host = args.host
        port = args.port
        debug = args.debug

        # Import and start server
        try:
            import uvicorn

            from flext_api.app import app

            uvicorn.run(
                app,
                host=host,
                port=port,
                reload=debug,
                log_level="debug" if debug else "info",
            )

        except ImportError:
            return 1
        else:
            return 0

    except KeyboardInterrupt:
        return 0
    except (ImportError, OSError, RuntimeError):
        return 1


def routes_command(_args: argparse_types.Namespace) -> int:
    """List available API routes."""
    try:
        # Try to import the app and list routes
        try:
            from flext_api.app import app

            routes = []
            for route in app.routes:
                if hasattr(route, "methods") and hasattr(route, "path"):
                    methods = list(route.methods)
                    route_path = route.path
                    route_name = getattr(route, "name", "unnamed")
                    routes.append((methods, route_path, route_name))

            if routes:
                for methods, route_path, route_name in routes:
                    print(f"{', '.join(sorted(methods))} {route_path} ({route_name})")
            else:
                print("No routes found")

        except ImportError:
            print("Failed to import app")
            return 1
        else:
            return 0

    except (ImportError, AttributeError):
        return 1


def validate_command(_args: argparse_types.Namespace) -> int:
    """Validate API configuration."""
    try:
        errors = 0

        # Check imports using find_spec
        import importlib.util

        if importlib.util.find_spec("flext_api.app") is None:
            print("Error: flext_api.app module not found")
            errors += 1

        # Check dependencies using find_spec
        if (
            importlib.util.find_spec("fastapi") is None
            or importlib.util.find_spec("uvicorn") is None
        ):
            print("Error: FastAPI or Uvicorn dependencies not found")
            errors += 1

        # Check environment variables
        import os

        env_vars = [
            ("FLEXT_API_HOST", "API host"),
            ("FLEXT_API_PORT", "API port"),
            ("FLEXT_API_DEBUG", "Debug mode"),
        ]

        for var_name, description in env_vars:
            value = os.environ.get(var_name)
            if value:
                print(f"Found {description}: {value}")
            else:
                print(f"Optional {description} not set")

        if errors == 0:
            print("Validation successful")
            return 0
        print(f"Validation failed with {errors} errors")
        return 1

    except (ImportError, OSError):
        return 1


def health_command(args: argparse_types.Namespace) -> int:
    """Check API health status."""
    try:
        import requests

        host = args.host
        port = args.port
        url = f"http://{host}:{port}/health"

        response = requests.get(url, timeout=5)

        if response.status_code == HTTP_OK:
            health_data = response.json()
            print(f"API is healthy: {health_data}")
            return 0
        print(f"API health check failed with status {response.status_code}")
        return 1

    except ImportError:
        print("requests library not available")
        return 1
    except (requests.RequestException, OSError) as e:
        print(f"Health check failed: {e}")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FLEXT API - REST Gateway CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  flext-api info                           # Show API information
  flext-api serve                          # Start API server
  flext-api serve --host 0.0.0.0 --port 8080  # Custom host/port
  flext-api routes                         # List API routes
  flext-api validate                       # Validate configuration
  flext-api health                         # Check API health
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show API information")
    info_parser.set_defaults(func=info_command)

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start API server")
    serve_parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind to (default: 127.0.0.1)",
    )
    serve_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)",
    )
    serve_parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with auto-reload",
    )
    serve_parser.set_defaults(func=serve_command)

    # Routes command
    routes_parser = subparsers.add_parser("routes", help="List API routes")
    routes_parser.set_defaults(func=routes_command)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate API configuration",
    )
    validate_parser.set_defaults(func=validate_command)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check API health")
    health_parser.add_argument(
        "--host", default="127.0.0.1", help="API host to check (default: 127.0.0.1)",
    )
    health_parser.add_argument(
        "--port", type=int, default=8000, help="API port to check (default: 8000)",
    )
    health_parser.set_defaults(func=health_command)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        result = args.func(args)
        return int(result) if result is not None else 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
