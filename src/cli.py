from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
import yaml

from core.models import SchemaContract
from outputs.static_report import StaticReportRenderer
from profilers.univariate import profile as run_profile

app = typer.Typer(help="Data Guide — general-purpose EDA tool.")

_VERSION = "0.1.0"

_EXT_TO_CONNECTOR = {
    ".csv": "csv",
    ".xlsx": "excel",
    ".xls": "excel",
    ".json": "json",
    ".db": "sqlite",
    ".sqlite": "sqlite",
    ".sqlite3": "sqlite",
}


def _build_connector(connector_type: str, cfg: dict, credentials_path: str | None = None):
    """Instantiate the right connector from a config dict."""
    sc_cfg = cfg.get("schema_contract", {})
    sc = SchemaContract(
        mode=sc_cfg.get("mode", "unknown"),
        metric_col=sc_cfg.get("metric_col", "metric"),
        value_col=sc_cfg.get("value_col", "value"),
        type_col=sc_cfg.get("type_col"),
        key_cols=sc_cfg.get("key_cols", []),
        context_cols=sc_cfg.get("context_cols", []),
    )

    if connector_type == "csv":
        from connectors.csv_connector import CSVConnector
        return CSVConnector(path=cfg["path"], schema=sc)
    elif connector_type == "excel":
        from connectors.excel_connector import ExcelConnector
        return ExcelConnector(path=cfg["path"], schema=sc, sheet=cfg.get("sheet", 0))
    elif connector_type == "json":
        from connectors.json_connector import JSONConnector
        return JSONConnector(path=cfg["path"], schema=sc)
    elif connector_type == "sqlite":
        from connectors.sqlite_connector import SQLiteConnector
        return SQLiteConnector(path=cfg["path"], query=cfg["query"], schema=sc)
    elif connector_type == "sql":
        from connectors.sql_connector import SQLConnector
        return SQLConnector(
            connection_string=cfg["connection_string"],
            query=cfg["query"],
            schema=sc,
        )
    elif connector_type == "snowflake":
        from connectors.credentials import load_credentials
        from connectors.snowflake_connector import SnowflakeConnector
        creds = load_credentials(
            "snowflake",
            credentials_path=credentials_path or cfg.get("credentials"),
        )
        return SnowflakeConnector(credentials=creds, query=cfg["query"], schema=sc)
    else:
        raise ValueError(f"Unknown connector type: '{connector_type}'")


def _auto_detect_connector(file: Path) -> str:
    ext = file.suffix.lower()
    connector = _EXT_TO_CONNECTOR.get(ext)
    if connector is None:
        raise typer.BadParameter(
            f"Cannot auto-detect connector for extension '{ext}'. "
            f"Supported: {sorted(_EXT_TO_CONNECTOR.keys())}. "
            "Use --connector to specify one explicitly."
        )
    return connector


@app.command()
def version() -> None:
    """Show the current version."""
    typer.echo(f"data-guide {_VERSION}")


@app.command()
def validate(
    file: Path = typer.Argument(..., help="Path to data file to validate."),
    metric_col: str = typer.Option("metric", help="Name of the metric column."),
    value_col: str = typer.Option("value", help="Name of the value column."),
    type_col: Optional[str] = typer.Option(None, help="Name of the data_type column (optional)."),
) -> None:
    """Validate that a file matches the expected schema contract."""
    import pandas as pd
    df = pd.read_csv(file)
    errors = []
    if metric_col not in df.columns:
        errors.append(f"metric column '{metric_col}' not found in {list(df.columns)}")
    if value_col not in df.columns:
        errors.append(f"value column '{value_col}' not found in {list(df.columns)}")
    if type_col and type_col not in df.columns:
        errors.append(f"type column '{type_col}' not found in {list(df.columns)}")

    if errors:
        for err in errors:
            typer.echo(f"ERROR: {err}", err=True)
        raise typer.Exit(code=1)
    typer.echo(f"Valid: schema contract satisfied for '{file.name}'.")


@app.command()
def profile(
    file: Path = typer.Argument(..., help="Path to data file to profile."),
    output: Path = typer.Option(Path("reports/report.html"), help="Output HTML report path."),
    connector: str = typer.Option("auto", help="Connector type: auto|csv|excel|json|sqlite|snowflake"),
    metric_col: str = typer.Option("metric", help="Name of the metric column."),
    value_col: str = typer.Option("value", help="Name of the value column."),
    type_col: Optional[str] = typer.Option(None, help="Name of the data_type column (optional)."),
    mode: str = typer.Option("unknown", help="Schema mode: long, wide, or unknown."),
    query: Optional[str] = typer.Option(None, help="SQL query (required for snowflake/sqlite/sql connectors)."),
    credentials: Optional[str] = typer.Option(None, help="Path to credentials file (for snowflake/sql)."),
) -> None:
    """Profile a data file and generate a static HTML report."""
    connector_type = connector
    if connector_type == "auto":
        try:
            connector_type = _auto_detect_connector(file)
        except typer.BadParameter as e:
            typer.echo(f"ERROR: {e}", err=True)
            raise typer.Exit(code=1)

    cfg: dict = {
        "path": str(file),
        "schema_contract": {
            "mode": mode,
            "metric_col": metric_col,
            "value_col": value_col,
            "type_col": type_col,
        },
    }
    if query:
        cfg["query"] = query

    try:
        conn = _build_connector(connector_type, cfg, credentials_path=credentials)
    except ValueError as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(code=1)

    conn.connect()
    gdf = conn.load()

    result = run_profile(gdf, output_dir=str(output.parent))

    renderer = StaticReportRenderer()
    renderer.render(result, output_path=str(output))
    typer.echo(f"Report written to {output}")


@app.command()
def run(
    config: Path = typer.Option(..., "--config", help="Path to YAML config file."),
) -> None:
    """Run profiling from a YAML config file."""
    if not config.exists():
        typer.echo(f"ERROR: Config file not found: {config}", err=True)
        raise typer.Exit(code=1)

    with config.open() as f:
        cfg = yaml.safe_load(f)

    connector_type = cfg.get("connector")
    if not connector_type:
        typer.echo("ERROR: Config must specify 'connector' field.", err=True)
        raise typer.Exit(code=1)

    typer.echo("Loading data...")
    try:
        conn = _build_connector(connector_type, cfg, credentials_path=cfg.get("credentials"))
    except (ValueError, Exception) as e:
        typer.echo(f"ERROR: {e}", err=True)
        raise typer.Exit(code=1)

    conn.connect()
    gdf = conn.load()

    typer.echo("Profiling...")
    outputs_cfg = cfg.get("outputs", [])
    if not outputs_cfg:
        typer.echo("ERROR: Config must specify at least one output.", err=True)
        raise typer.Exit(code=1)

    for out_cfg in outputs_cfg:
        out_type = out_cfg.get("type")
        out_path = out_cfg.get("path", "reports/report.html")

        if out_type == "static_report":
            result = run_profile(gdf, output_dir=str(Path(out_path).parent))
            renderer = StaticReportRenderer()
            renderer.render(result, output_path=out_path)
            typer.echo(f"Writing report to {out_path}")
        else:
            typer.echo(f"WARNING: Unknown output type '{out_type}', skipping.")


if __name__ == "__main__":
    app()
