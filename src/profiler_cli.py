import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
import typer

from data_profiler import DataProfiler
from data_pipeline.bivariate_profiler import BivariateProfiler

app = typer.Typer(help="Data Profiler command line interface")


def _load_config(path: Path) -> dict:
    """Load a JSON or YAML config file."""
    with path.open() as f:
        if path.suffix.lower() in {".yml", ".yaml"}:
            try:
                import yaml  # type: ignore
            except Exception as exc:
                raise typer.BadParameter("PyYAML required for YAML configs") from exc
            return yaml.safe_load(f)
        return json.load(f)


@app.command()
def profile(
    config: List[Path] = typer.Option(..., "--config", "-c", help="Path(s) to config file(s)"),
    output_dir: Path = typer.Option(Path("output"), "--output-dir", "-o", help="Directory for reports"),
    analyses: List[str] = typer.Option(["univariate"], "--analysis", "-a", help="Analyses to run"),
    report_format: str = typer.Option("markdown", "--format", "-f", help="Report format: markdown or html"),
) -> None:
    """Run profiling using the provided configuration."""

    for cfg_path in config:
        cfg = _load_config(cfg_path)
        api_key = cfg.get("api_key")  # currently unused but parsed for future use
        datasets = cfg.get("datasets", {})
        bivariate_pairs = cfg.get("bivariate_pairs", [])

        for name, ds in datasets.items():
            csv_path = Path(ds["path"]).resolve()
            df = pd.read_csv(csv_path)

            if "fields" in ds:
                df = df[ds["fields"]]

            output_subdir = output_dir / name
            output_subdir.mkdir(parents=True, exist_ok=True)

            profiler = DataProfiler(df, custom_types=ds.get("types"), output_dir=str(output_subdir))

            if "univariate" in analyses:
                profiler.profile_dataset()
                profiler.profile_columns()
                ext = "md" if report_format == "markdown" else report_format
                report = profiler.generate_report(report_format, output_filename=f"{name}_profile.{ext}")
                (output_subdir / f"{name}_profile.{ext}").write_text(report)

            if "bivariate" in analyses and bivariate_pairs:
                bivariate = BivariateProfiler(df, output_dir=str(output_subdir / "bivariate"))
                bivariate.correlation_analysis()
                for pair in bivariate_pairs:
                    if len(pair) != 2:
                        continue
                    x, y = pair
                    if x in df.columns and y in df.columns:
                        bivariate.scatter_plot(x, y)


if __name__ == "__main__":
    app()

