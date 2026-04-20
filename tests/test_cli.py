from pathlib import Path
import yaml
from typer.testing import CliRunner
from cli import app

runner = CliRunner()
FIXTURES = Path(__file__).parent / "fixtures"


def test_profile_command_produces_report(tmp_path):
    result = runner.invoke(app, [
        "profile", str(FIXTURES / "sample.csv"),
        "--output", str(tmp_path / "report.html"),
    ])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "report.html").exists()


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_validate_command_long_format():
    result = runner.invoke(app, [
        "validate", str(FIXTURES / "sample.csv"),
        "--metric-col", "metric",
        "--value-col", "value",
    ])
    assert result.exit_code == 0
    assert "valid" in result.output.lower()


def test_validate_command_missing_col():
    result = runner.invoke(app, [
        "validate", str(FIXTURES / "sample.csv"),
        "--metric-col", "nonexistent",
        "--value-col", "value",
    ])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_run_command_with_config(tmp_path):
    config = {
        "connector": "csv",
        "path": str(FIXTURES / "sample.csv"),
        "schema_contract": {
            "mode": "long",
            "metric_col": "metric",
            "value_col": "value",
            "type_col": "data_type",
        },
        "outputs": [
            {"type": "static_report", "path": str(tmp_path / "run_report.html")}
        ],
    }
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(yaml.dump(config))

    result = runner.invoke(app, ["run", "--config", str(config_path)])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "run_report.html").exists()


def test_run_command_missing_config():
    result = runner.invoke(app, ["run", "--config", "/nonexistent/config.yaml"])
    assert result.exit_code != 0


def test_profile_auto_detects_csv():
    # Profile with explicit connector=auto (same as default)
    result = runner.invoke(app, [
        "profile", str(FIXTURES / "sample.csv"),
        "--output", "/tmp/test_auto.html",
        "--connector", "auto",
    ])
    assert result.exit_code == 0, result.output


def test_profile_unknown_extension_raises():
    result = runner.invoke(app, [
        "profile", "/tmp/fake_file.parquet",
        "--output", "/tmp/test_parquet.html",
        "--connector", "auto",
    ])
    assert result.exit_code != 0
