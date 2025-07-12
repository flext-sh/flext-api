"""FLEXT API CLI - Command Line Interface.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

This module provides CLI commands for API operations.
Uses flext-cli patterns for consistency.
"""

from __future__ import annotations

import click
import httpx
import uvicorn

from flext_api.config import get_api_settings


@click.group()
@click.version_option(version="0.7.0", prog_name="flext-api")
def cli() -> None:
    """FLEXT API CLI - Command Line Interface."""


@cli.command()
def config() -> None:
    """Display the API configuration."""
    settings = get_api_settings()
    click.echo(f"Project: {settings.project_name}")
    click.echo(f"Version: {settings.project_version}")
    click.echo(f"Environment: {settings.environment}")
    click.echo(f"Debug: {settings.debug}")
    click.echo(f"Server: {settings.server.host}:{settings.server.port}")
    click.echo(f"Workers: {settings.server.workers}")
    click.echo(f"Database: {settings.database_url}")
    click.echo(f"Redis: {settings.redis_url}")
    click.echo(f"CORS Origins: {', '.join(settings.cors.origins)}")
    click.echo(
        f"Rate Limiting: {'Enabled' if settings.rate_limit.enabled else 'Disabled'}",
    )


@cli.command()
def test() -> None:
    """Test the API configuration.

    Raises:
        click.Abort: If the configuration fails.

    """
    try:
        settings = get_api_settings()
        click.echo("✅ Configuration loaded successfully")
        click.echo(f"Project: {settings.project_name}")
        click.echo(f"Environment: {settings.environment}")
        click.echo(f"Server: {settings.server.host}:{settings.server.port}")
        click.echo("✅ FLEXT API system is working")
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort from e


@cli.command()
@click.option("--host", default=None, help="Host to bind to")
@click.option("--port", default=None, type=int, help="Port to bind to")
@click.option("--workers", default=None, type=int, help="Number of workers")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(
    host: str | None,
    port: int | None,
    workers: int | None,
    reload: bool,
) -> None:
    """Start the API server.

    Raises:
        click.Abort: If the server fails to start.

    """
    settings = get_api_settings()

    # Use CLI options or fall back to config
    server_host = host or settings.server.host
    server_port = port or settings.server.port
    server_workers = workers or settings.server.workers
    server_reload = reload or settings.server.reload

    click.echo("🚀 Starting FLEXT API server...")
    click.echo(f"Host: {server_host}")
    click.echo(f"Port: {server_port}")
    click.echo(f"Workers: {server_workers}")
    click.echo(f"Reload: {server_reload}")

    try:
        """Start the API server."""
        uvicorn.run(
            "flext_api.app:create_app",
            factory=True,
            host=server_host,
            port=server_port,
            workers=server_workers if not server_reload else 1,
            reload=server_reload,
            log_level=settings.log_level.lower(),
        )
    except Exception as e:
        click.echo(f"❌ Failed to start server: {e}")
        raise click.Abort from e


@cli.command()
def health() -> None:
    """Check the health of the API.

    Raises:
        click.Abort: If the API is not healthy.

    """
    settings = get_api_settings()
    url = f"http://{settings.server.host}:{settings.server.port}/health"

    try:
        with httpx.Client() as client:
            response = client.get(url, timeout=5.0)

        if response.status_code == 200:
            click.echo("✅ API is healthy")
            data = response.json()
            click.echo(f"Status: {data.get('status', 'unknown')}")
            click.echo(f"Version: {data.get('version', 'unknown')}")
        else:
            click.echo(f"❌ API health check failed: {response.status_code}")
            raise click.Abort
    except httpx.RequestError as e:
        click.echo(f"❌ Could not connect to API: {e}")
        click.echo(f"Make sure the server is running on {url}")
        raise click.Abort from e


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
