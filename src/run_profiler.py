"""Command line helper for profiling CSV files in a folder."""

import argparse
import os
from pathlib import Path

import pandas as pd

from data_profiler import DataProfiler


def profile_folder(input_dir: Path, output_dir: Path) -> None:
    """Profile each CSV file in ``input_dir`` and write markdown reports."""

    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = [p for p in input_dir.glob("*.csv")]
    for csv_path in csv_files:
        df = pd.read_csv(csv_path)

        profiler = DataProfiler(df)
        profiler.profile_dataset()
        profiler.profile_columns()
        report = profiler.generate_report(format="markdown")

        report_name = csv_path.stem + "_profiling.md"
        with open(output_dir / report_name, "w") as f:
            f.write(report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile all CSVs in a folder")
    parser.add_argument("input_dir", type=Path, help="Directory containing CSV files")
    parser.add_argument("output_dir", type=Path, help="Directory for markdown reports")
    args = parser.parse_args()

    profile_folder(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()