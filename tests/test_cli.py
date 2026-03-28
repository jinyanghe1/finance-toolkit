import json

from click.testing import CliRunner

import finance_toolkit.config as config_module
from finance_toolkit.__version__ import __version__
from finance_toolkit.cli import main


def reset_config() -> None:
    config_module._config = None


def test_cli_help() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Finance Toolkit CLI" in result.output
    assert "config" in result.output
    assert "version" in result.output


def test_cli_version_command() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_config_paths_respect_env_override(monkeypatch, tmp_path) -> None:
    runner = CliRunner()
    data_root = tmp_path / "finance-data"

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FINANCE_DATA_ROOT", str(data_root))
    reset_config()

    result = runner.invoke(main, ["config", "paths", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["root"] == str(data_root)
    assert payload["company"] == str(data_root / "company")
    assert payload["exports"] == str(data_root / "exports")

    reset_config()
