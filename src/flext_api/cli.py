"""Command-line interface for FLEXT API."""

from __future__ import annotations

import argparse
import sys
from typing import Any


def info_command(args: Any) -> int:
    """Show FLEXT API information."""
    return 0


def serve_command(args: Any) -> int:
    """Start the API server."""
    try:
        host = args.host
        port = args.port
        debug = args.debug

        # Import and start server
        try:
            import uvicorn

            from .app import app

            uvicorn.run(
                app,
                host=host,
                port=port,
                debug=debug,
                reload=debug,
            )

        except ImportError:
            return 1

        return 0

    except KeyboardInterrupt:
        return 0
    except Exception:
        return 1


def routes_command(args: Any) -> int:
    """List available API routes."""
    try:

        # Try to import the app and list routes
        try:
            from .app import app

            routes = []
            for route in app.routes:
                if hasattr(route, 'methods') and hasattr(route, 'path'):
                    methods = list(route.methods)
                    path = route.path
                    name = getattr(route, 'name', 'unnamed')
                    routes.append((methods, path, name))

            if routes:

                for methods, path, name in routes:
                    ", ".join(sorted(methods))
            else:
                pass

        except ImportError:
            pass

        return 0

    except Exception:
        return 1


def validate_command(args: Any) -> int:
    """Validate API configuration."""
    try:

        errors = 0

        # Check imports
        try:
            from .app import app
        except ImportError:
            errors += 1

        # Check dependencies
        try:
            import fastapi
            import uvicorn
        except ImportError:
            errors += 1

        # Check environment variables
        import os
        env_vars = [
            ("FLEXT_API_HOST", "API host"),
            ("FLEXT_API_PORT", "API port"),
            ("FLEXT_API_DEBUG", "Debug mode"),
        ]

        for var_name, _description in env_vars:
            value = os.environ.get(var_name)
            if value:
                pass
            else:
                pass

        if errors == 0:
            return 0
        else:
            return 1

    except Exception:
        return 1


def health_command(args: Any) -> int:
    """Check API health status."""
    try:
        import requests

        host = args.host
        port = args.port
        url = f"http://{host}:{port}/health"

        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            response.json()
            return 0
        else:
            return 1

    except ImportError:
        return 1
    except Exception:
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
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    serve_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with auto-reload"
    )
    serve_parser.set_defaults(func=serve_command)

    # Routes command
    routes_parser = subparsers.add_parser("routes", help="List API routes")
    routes_parser.set_defaults(func=routes_command)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate API configuration")
    validate_parser.set_defaults(func=validate_command)

    # Health command
    health_parser = subparsers.add_parser("health", help="Check API health")
    health_parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="API host to check (default: 127.0.0.1)"
    )
    health_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="API port to check (default: 8000)"
    )
    health_parser.set_defaults(func=health_command)

    # Parse arguments
    args = parser.parse_args()

    # Execute command
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
