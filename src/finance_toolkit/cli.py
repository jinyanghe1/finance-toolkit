"""Finance Toolkit CLI."""

from __future__ import annotations

import json
from typing import Any

import click
import yaml

from .__version__ import __title__, __version__
from .config import get_config


def _emit_payload(payload: dict[str, Any], output_format: str) -> None:
    """Emit a payload in the requested format."""
    if output_format == "json":
        click.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    click.echo(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        nl=False,
    )


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="ftk")
def main() -> None:
    """Finance Toolkit CLI."""


@main.command("version")
def version_command() -> None:
    """Show the installed version."""
    click.echo(f"{__title__} {__version__}")


@main.group("config")
def config_group() -> None:
    """Inspect runtime configuration."""


@config_group.command("show")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    show_default=True,
)
def show_config(output_format: str) -> None:
    """Show the configured values."""
    config = get_config()
    _emit_payload(config.to_dict(), output_format.lower())


@config_group.command("paths")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["yaml", "json"], case_sensitive=False),
    default="yaml",
    show_default=True,
)
def show_paths(output_format: str) -> None:
    """Show resolved filesystem paths after env overrides."""
    config = get_config()
    payload = {
        "root": str(config.data.root),
        "company": str(config.data.company),
        "exports": str(config.data.exports),
    }
    _emit_payload(payload, output_format.lower())
