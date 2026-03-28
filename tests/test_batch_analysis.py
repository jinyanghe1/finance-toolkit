import json

from click.testing import CliRunner

import finance_toolkit.config as config_module
from finance_toolkit.analyzer.company import CompanyAnalyzer
from finance_toolkit.cli import main
from finance_toolkit.data.db import CompanyDB, reset_db_instance
from finance_toolkit.exceptions import CompanyNotFoundError


def reset_runtime_state() -> None:
    config_module._config = None
    reset_db_instance()


def seed_company_data(data_root, code: str = "600519", name: str = "贵州茅台") -> None:
    analyzer = CompanyAnalyzer(CompanyDB(data_root=data_root / "company"))
    analyzer.create_profile(code=code, name=name, full_name=name)


def test_analyze_batch_empty_list(test_db) -> None:
    analyzer = CompanyAnalyzer(test_db)

    result = analyzer.analyze_batch([])

    assert result == {}


def test_analyze_batch_success_and_failure(test_db) -> None:
    analyzer = CompanyAnalyzer(test_db)
    analyzer.create_profile(code="600519", name="贵州茅台", full_name="贵州茅台酒股份有限公司")

    result = analyzer.analyze_batch(["600519", "999999"])

    assert result["600519"]["success"] is True
    assert result["600519"]["name"] == "贵州茅台"
    assert result["999999"]["success"] is False
    assert "CompanyNotFoundError" in result["999999"]["error"]


def test_analyze_batch_fail_fast(test_db) -> None:
    analyzer = CompanyAnalyzer(test_db)

    try:
        analyzer.analyze_batch(["999999"], skip_errors=False)
    except CompanyNotFoundError:
        return

    raise AssertionError("Expected CompanyNotFoundError when fail-fast is enabled")


def test_batch_cli_help() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["batch", "analyze", "--help"])

    assert result.exit_code == 0
    assert "--input" in result.output
    assert "--skip-errors" in result.output


def test_batch_cli_direct_codes(monkeypatch, tmp_path) -> None:
    runner = CliRunner()
    data_root = tmp_path / "finance-data"

    monkeypatch.setenv("FINANCE_DATA_ROOT", str(data_root))
    reset_runtime_state()
    seed_company_data(data_root)

    result = runner.invoke(main, ["batch", "analyze", "600519", "999999", "--format", "json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["summary"]["success_count"] == 1
    assert payload["summary"]["failed_count"] == 1
    assert payload["results"]["600519"]["success"] is True
    assert payload["results"]["999999"]["success"] is False

    reset_runtime_state()


def test_batch_cli_input_file_and_output(monkeypatch, tmp_path) -> None:
    runner = CliRunner()
    data_root = tmp_path / "finance-data"
    input_file = tmp_path / "codes.txt"
    output_file = tmp_path / "batch-results.yaml"

    input_file.write_text("600519\n999999\n", encoding="utf-8")
    monkeypatch.setenv("FINANCE_DATA_ROOT", str(data_root))
    reset_runtime_state()
    seed_company_data(data_root)

    result = runner.invoke(
        main,
        [
            "batch",
            "analyze",
            "--input",
            str(input_file),
            "--format",
            "yaml",
            "--output",
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "success_count: 1" in content
    assert "failed_count: 1" in content

    reset_runtime_state()
