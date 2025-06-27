import asyncio
import json
import logging
from pathlib import Path
from typing import List

import typer

from core import aggregator
from core.exporter import export_data
from core.scanner import EVENT_BUS, run_scanner
from core.utils import setup_logging
from external_api import shodan_lookup, wigle_lookup
from mqtt_client import setup as mqtt_setup
from plugins import install_plugin, load_plugins

app = typer.Typer(help="BLE Scanner Suite CLI")

setup_logging()
logger = logging.getLogger(__name__)


@app.command()
def scan(
    interval: int = 5,
    workers: int = 1,
    threads: int = 1,
    processes: int = 0,
    threaded_scan: bool = False,
):
    """Run BLE scanner."""
    load_plugins()
    mqtt_setup()
    stop_event = asyncio.Event()

    async def runner() -> None:
        task = asyncio.create_task(
            run_scanner(
                interval,
                workers,
                threads,
                processes,
                stop_event=stop_event,
                threaded_scan=threaded_scan,
            )
        )
        try:
            await task
        finally:
            stop_event.set()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        logger.info("Scanner stopped by user")


@app.command()
def listen():
    """Consume events from the bus and print them."""

    async def _listen():
        while True:
            event = await EVENT_BUS.get()
            logger.info("%s", event)

    asyncio.run(_listen())


@app.command()
def shodan(query: str):
    """Query Shodan."""
    res = shodan_lookup(query)
    typer.echo(res)


@app.command()
def wigle(ssid: str):
    """Query Wigle for a Wi-Fi SSID."""
    res = wigle_lookup(ssid)
    typer.echo(res)


@app.command()
def plugin_install(package: str, manager: str = "apt"):
    """Install a system plugin via apt or brew."""
    success = install_plugin(package, manager)
    if success:
        typer.echo("Installed successfully")
    else:
        typer.echo("Installation failed")


@app.command()
def aggregate(
    endpoints: List[str] = typer.Option([], "--endpoint", help="Remote dashboard URLs")
):
    """Aggregate device results from remote dashboards."""
    if not endpoints:
        typer.echo("No endpoints provided", err=True)
        raise typer.Exit(code=1)
    results = aggregator.aggregate(endpoints)
    typer.echo(json.dumps(results, indent=2))


@app.command()
def export(
    fmt: str = typer.Option("json", "--format", "-f", help="json, csv, sqlite"),
    output: Path = typer.Argument(Path("export.out")),
    limit: int = 100,
):
    """Export the local database."""
    from core.db import init_db

    init_db()
    export_data(fmt, output, limit)
    typer.echo(f"Exported to {output}")


if __name__ == "__main__":
    app()
