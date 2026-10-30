from __future__ import annotations

import os
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple

import matplotlib.pyplot as plt
import missingno as msno
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import entropy

try:  # Optional dependency used for phone-number validation
    import phonenumbers
except ImportError:  # pragma: no cover - optional dependency
    phonenumbers = None


__all__ = [
    "ColumnType",
    "TypeResolver",
    "DataProfiler",
    "DataProfilerPlots",
    "TemporalAnalyzer",
    "StringProfiler",
    "NumericProfiler",
    "slugify",
]


@dataclass
class ColumnType:
    """Normalized representation of a column's semantic type."""

    semantic: str
    logical: str
    source: str
    original_dtype: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "semantic": self.semantic,
            "logical": self.logical,
            "source": self.source,
            "original_dtype": self.original_dtype,
        }


def slugify(label: str) -> str:
    """Return a filesystem-safe slug for column names and section anchors."""

    sanitized = re.sub(r"[^\w\-]+", "_", str(label))
    sanitized = re.sub(r"__+", "_", sanitized)
    sanitized = sanitized.strip("_-")
    return sanitized or "column"


class TypeResolver:
    """Infer and normalise column types, optionally merging custom overrides."""

    _ALIASES: Dict[str, Tuple[str, str]] = {
        "object": ("string", "object"),
        "category": ("string", "category"),
        "str": ("string", "string"),
        "string": ("string", "string"),
        "id": ("string", "id"),
        "phone_number": ("string", "phone_number"),
        "bool": ("boolean", "bool"),
        "boolean": ("boolean", "boolean"),
        "int64": ("numeric", "int64"),
        "int32": ("numeric", "int32"),
        "float64": ("numeric", "float64"),
        "float32": ("numeric", "float32"),
        "numeric": ("numeric", "numeric"),
        "number": ("numeric", "number"),
        "currency": ("numeric", "currency"),
        "date": ("datetime", "date"),
        "datetime": ("datetime", "datetime"),
        "timestamp": ("datetime", "timestamp"),
        "datetime64": ("datetime", "datetime64"),
        "datetime64[ns]": ("datetime", "datetime64[ns]"),
        "unix_timestamp": ("datetime", "unix_timestamp"),
    }

    def __init__(self, dataframe: pd.DataFrame, custom_types: Optional[Dict[str, str]] = None) -> None:
        self._df = dataframe
        self._custom_types = custom_types or {}
        self.resolved_types: Dict[str, ColumnType] = {}
        self._resolve_types()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Coerce dataframe columns to their resolved semantic representations."""

        df = dataframe.copy()
        for column, info in self.resolved_types.items():
            if column not in df.columns:
                continue
            if info.logical == "unix_timestamp":
                numeric = pd.to_numeric(df[column], errors="coerce")
                factor = 1000 if numeric.dropna().abs().gt(1_000_000_000_000).any() else 1
                df[column] = pd.to_datetime(numeric / factor, unit="s", errors="coerce")
            elif info.semantic == "datetime":
                df[column] = pd.to_datetime(df[column], errors="coerce")
            elif info.logical == "currency":
                cleaned = (
                    df[column]
                    .astype(str)
                    .str.replace(r"[\$,]", "", regex=True)
                    .str.replace("(", "-", regex=False)
                    .str.replace(")", "", regex=False)
                )
                df[column] = pd.to_numeric(cleaned, errors="coerce").fillna(0.0)
            elif info.semantic == "numeric":
                df[column] = pd.to_numeric(df[column], errors="coerce")
            elif info.semantic == "boolean":
                df[column] = df[column].astype("boolean")
            else:
                df[column] = df[column].astype("string")
        return df

    def as_dict(self) -> Dict[str, Dict[str, str]]:
        return {column: info.to_dict() for column, info in self.resolved_types.items()}

    def semantic_map(self) -> Dict[str, str]:
        return {column: info.semantic for column, info in self.resolved_types.items()}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _resolve_types(self) -> None:
        for column in self._df.columns:
            original_dtype = str(self._df[column].dtype)
            if column in self._custom_types:
                semantic, logical = self._normalise_custom(self._custom_types[column])
                self.resolved_types[column] = ColumnType(
                    semantic=semantic,
                    logical=logical,
                    source="custom",
                    original_dtype=original_dtype,
                )
            else:
                inferred = self._infer_column_type(self._df[column])
                self.resolved_types[column] = ColumnType(
                    semantic=inferred[0],
                    logical=inferred[1],
                    source="inferred",
                    original_dtype=original_dtype,
                )

    def _normalise_custom(self, dtype: str) -> Tuple[str, str]:
        key = str(dtype).lower()
        if key in self._ALIASES:
            return self._ALIASES[key]
        if key.startswith("datetime64"):
            return "datetime", key
        if "date" in key or "time" in key:
            return "datetime", key
        if key in {"float", "int", "double"}:
            return "numeric", key
        return "string", key

    def _infer_column_type(self, series: pd.Series) -> Tuple[str, str]:
        if pd.api.types.is_datetime64_any_dtype(series):
            return "datetime", str(series.dtype)
        if pd.api.types.is_bool_dtype(series):
            return "boolean", str(series.dtype)
        if pd.api.types.is_numeric_dtype(series):
            return "numeric", str(series.dtype)

        # Attempt heuristic inference for object columns
        sample = series.dropna().astype(str).head(50)
        if not sample.empty:
            parsed_dates = pd.to_datetime(sample, errors="coerce")
            if parsed_dates.notna().mean() > 0.8:
                return "datetime", "datetime"
            cleaned_numeric = pd.to_numeric(
                sample.str.replace(r"[\$,]", "", regex=True), errors="coerce"
            )
            if cleaned_numeric.notna().mean() > 0.8:
                return "numeric", "numeric"
        return "string", "string"


class DataProfilerPlots:
    """Generate and persist column-level visualisations."""

    def __init__(self, dataframe: pd.DataFrame, output_dir: Path) -> None:
        self.df = dataframe
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _wrap_text(self, text: str, width: int = 12) -> str:
        wrapped_lines = textwrap.wrap(str(text), width)
        return "\n".join(wrapped_lines)

    def _save_current_plot(self, filename: str) -> Path:
        file_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()
        return file_path

    def missing_value_matrix(self) -> Path:
        fig, ax = plt.subplots(figsize=(15, 10))
        msno.matrix(self.df, ax=ax)
        ax.set_title("Missing Value Matrix")
        return self._save_current_plot("missing_value_matrix.png")

    def column_chart(
        self,
        column: str,
        include_other: bool = True,
        top_n: int = 12,
    ) -> Path:
        value_counts = self.df[column].value_counts(dropna=False)
        other_count = value_counts.iloc[top_n:].sum() if len(value_counts) > top_n else 0

        plot_values = value_counts.head(top_n).to_dict()
        if include_other and other_count > 0:
            plot_values["Other"] = other_count

        series = pd.Series(plot_values)
        fig, ax = plt.subplots(figsize=(10, 6))
        series.plot(kind="bar", color="skyblue", ax=ax)
        ax.set_title(f"Column Chart for {column}")
        ax.set_xlabel(self._wrap_text(column, 20))
        ax.set_ylabel("Count")

        total = value_counts.sum()
        for patch in ax.patches:
            percentage = (patch.get_height() / total) * 100 if total else 0
            ax.annotate(
                f"{percentage:.1f}%",
                (patch.get_x() + patch.get_width() / 2.0, patch.get_height()),
                ha="center",
                va="center",
                xytext=(0, 10),
                textcoords="offset points",
            )
        filename = f"{slugify(column)}_columnchart_{'all' if include_other else 'top'}.png"
        return self._save_current_plot(filename)

    def histogram(self, column: str) -> Path:
        fig, ax = plt.subplots(figsize=(10, 6))
        self.df[column].plot(kind="hist", bins=20, color="lightgreen", edgecolor="black", ax=ax)
        ax.set_title(f"Histogram for {column}")
        ax.set_xlabel(self._wrap_text(column, 20))
        ax.set_ylabel("Frequency")
        filename = f"{slugify(column)}_histogram.png"
        return self._save_current_plot(filename)

    def kde_plot(self, column: str) -> Path:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.kdeplot(self.df[column].dropna(), fill=True, color="blue", ax=ax)
        ax.set_title(f"KDE Plot for {column}")
        ax.set_xlabel(self._wrap_text(column, 20))
        ax.set_ylabel("Density")
        filename = f"{slugify(column)}_kde_plot.png"
        return self._save_current_plot(filename)

    def box_plot(self, column: str) -> Optional[Path]:
        col_data = self.df[column].dropna()
        if col_data.empty:
            return None
        fig, ax = plt.subplots(figsize=(6, 6))
        sns.boxplot(y=col_data, color="coral", ax=ax)
        ax.set_title(f"Box Plot for {column}")
        ax.set_ylabel(self._wrap_text(column, 20))
        filename = f"{slugify(column)}_boxplot.png"
        return self._save_current_plot(filename)


class TemporalAnalyzer:
    def __init__(self, dataframe: pd.DataFrame, output_dir: Path, window: int = 3) -> None:
        self.df = dataframe
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.window = window

    def analyze_temporal_column(self, column: str) -> Dict[str, Any]:
        col_data = self.df[column].dropna().sort_values()
        if col_data.empty:
            return {
                "earliest": None,
                "latest": None,
                "time_span": None,
                "temporal_gaps": {},
                "day_of_week_distribution": {},
                "monthly_trends": {},
                "plots": {},
            }

        earliest = col_data.min()
        latest = col_data.max()
        analysis = {
            "earliest": earliest.strftime("%Y-%m-%d") if pd.notna(earliest) else None,
            "latest": latest.strftime("%Y-%m-%d") if pd.notna(latest) else None,
            "time_span": f"{(latest - earliest).days} days" if pd.notna(earliest) and pd.notna(latest) else None,
            "temporal_gaps": self._summarize_temporal_gaps(col_data),
            "day_of_week_distribution": self._format_day_of_week_distribution(col_data.dt.dayofweek.value_counts().to_dict()),
            "monthly_trends": self._format_monthly_trends(col_data.dt.month.value_counts().sort_index().to_dict()),
        }

        plots = {
            "gaps_distribution": self._plot_temporal_gaps_distribution(col_data, column),
            "weekly_time_series": self._plot_weekly_aggregate_time_series(col_data, column),
        }
        analysis["plots"] = {key: value for key, value in plots.items() if value}
        return analysis

    def _summarize_temporal_gaps(self, col_data: pd.Series) -> Dict[str, Any]:
        gaps = col_data.diff().dropna()
        if gaps.empty:
            return {}
        stats = gaps.describe()
        summary: Dict[str, Any] = {"count": int(stats["count"])}
        for key in ["mean", "std", "min", "25%", "50%", "75%", "max"]:
            value = stats.get(key)
            summary[key] = f"{value.days} days" if isinstance(value, pd.Timedelta) else None
        return summary

    def _format_day_of_week_distribution(self, counts: Dict[int, int]) -> Dict[str, int]:
        labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {labels[int(idx)]: count for idx, count in counts.items() if 0 <= int(idx) < len(labels)}

    def _format_monthly_trends(self, counts: Dict[int, int]) -> Dict[str, int]:
        labels = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        return {labels[int(idx) - 1]: count for idx, count in counts.items() if 1 <= int(idx) <= 12}

    def _plot_temporal_gaps_distribution(self, col_data: pd.Series, column: str) -> Optional[Path]:
        gaps = col_data.diff().dropna()
        if gaps.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        gap_days = gaps.dt.days
        sns.histplot(gap_days, kde=True, ax=ax)
        ax.set_title(f"Temporal Gaps Distribution for {column}")
        ax.set_xlabel("Gap (days)")
        ax.set_ylabel("Frequency")
        filename = f"{slugify(column)}_temporal_gaps_distribution.png"
        return self._save_plot(fig, filename)

    def _plot_weekly_aggregate_time_series(self, col_data: pd.Series, column: str) -> Optional[Path]:
        counts = col_data.dt.to_period("W").value_counts().sort_index()
        if counts.empty:
            return None
        rolling = counts.rolling(window=self.window, min_periods=1).mean()
        fig, ax = plt.subplots(figsize=(12, 6))
        counts.index = counts.index.to_timestamp()
        rolling.index = rolling.index.to_timestamp()
        ax.plot(counts.index, counts.values, marker="o", label="Weekly Count")
        ax.plot(rolling.index, rolling.values, marker="o", label=f"{self.window}-Week Moving Average")
        ax.set_title(f"Weekly Time Series for {column}")
        ax.set_xlabel("Week")
        ax.set_ylabel("Observations")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        filename = f"{slugify(column)}_weekly_time_series.png"
        return self._save_plot(fig, filename)

    def _save_plot(self, fig: plt.Figure, filename: str) -> Path:
        file_path = self.output_dir / filename
        fig.tight_layout()
        fig.savefig(file_path)
        plt.close(fig)
        return file_path


class StringProfiler:
    def __init__(self, column_data: pd.Series) -> None:
        self.col_data = column_data.astype("string")

    def profile(self) -> Dict[str, Any]:
        suspicious_patterns = [
            r"Z{2,}",
            r"9{2,}",
            r"\d{6,}",
            r"(?i)test",
            r"(?i)none",
        ]
        empty_patterns = ["None", "nan", ""]
        suspicious_data = self._identify_invalid_patterns_regex(suspicious_patterns)
        special_characters = self._count_special_characters()
        counts = self.col_data.value_counts()

        if counts.empty:
            entropy_value = 0.0
            dominance = 0.0
        else:
            entropy_value = entropy(counts / counts.sum(), base=2)
            dominance = (counts.iloc[0] / counts.sum()) * 100

        return {
            "distinct_values": int(self.col_data.nunique()),
            "string_lengths": {
                "min": float(self.col_data.str.len().min() or 0),
                "max": float(self.col_data.str.len().max() or 0),
                "mean": float(self.col_data.str.len().mean() or 0),
            },
            "most_common": counts.head(10).to_dict(),
            "least_common": counts.tail(10).to_dict(),
            "duplicates_count": int(self.col_data.duplicated().sum()),
            "all_uppercase_count": int(self.col_data.str.isupper().sum()),
            "all_lowercase_count": int(self.col_data.str.islower().sum()),
            "empty_vals": int(self.col_data.isna().sum() + self.col_data.str.strip().isin(empty_patterns).sum()),
            "entropy": float(entropy_value),
            "dominance": float(dominance),
            "special_character_count": special_characters,
            "suspicious_data": suspicious_data,
        }

    def profile_phone_numbers(self) -> Dict[str, Any]:
        if phonenumbers is None:
            return {"valid_phone_numbers": None, "invalid_phone_numbers": None, "library_available": False}

        valid_count = 0
        invalid_count = 0
        for number in self.col_data.dropna():
            try:
                parsed = phonenumbers.parse(str(number), "US")
                if phonenumbers.is_valid_number(parsed):
                    valid_count += 1
                else:
                    invalid_count += 1
            except phonenumbers.NumberParseException:
                invalid_count += 1
        return {
            "valid_phone_numbers": valid_count,
            "invalid_phone_numbers": invalid_count,
            "library_available": True,
        }

    def _count_special_characters(self) -> Dict[str, int]:
        return {
            "hashtags": int(self.col_data.str.count(r"#").sum()),
            "mentions": int(self.col_data.str.count(r"@").sum()),
        }

    def _identify_invalid_patterns_regex(self, patterns: Iterable[str]) -> Dict[str, int]:
        suspicious_counts: Dict[str, int] = {}
        for pattern in patterns:
            matches = self.col_data.str.contains(pattern, na=False, regex=True)
            suspicious_counts[pattern] = int(matches.sum())
        return suspicious_counts


class NumericProfiler:
    def __init__(self, column_data: pd.Series) -> None:
        self.col_data = pd.to_numeric(column_data, errors="coerce")

    def profile(self) -> Dict[str, Any]:
        data = self.col_data.dropna()
        if data.empty:
            return {
                "distinct_values": 0,
                "statistics": {},
                "skewness": None,
                "kurtosis": None,
                "most_common": {},
                "least_common": {},
                "outliers": [],
                "avg_nonzero": None,
            }

        stats = data.describe(percentiles=[0.01, 0.05, 0.33, 0.5, 0.66, 0.95, 0.99]).to_dict()
        outliers = self.detect_outliers(data)
        nonzero = data[data != 0]
        avg_nonzero = float(nonzero.mean()) if not nonzero.empty else None

        return {
            "distinct_values": int(data.nunique()),
            "statistics": {k: round(v, 3) for k, v in stats.items()},
            "skewness": round(float(data.skew()), 3) if len(data) > 2 else None,
            "kurtosis": round(float(data.kurt()), 3) if len(data) > 3 else None,
            "most_common": data.value_counts().head(10).round(3).to_dict(),
            "least_common": data.value_counts().tail(10).round(3).to_dict(),
            "outliers": outliers.tolist(),
            "avg_nonzero": avg_nonzero,
        }

    def detect_outliers(self, data: Optional[pd.Series] = None, method: str = "iqr") -> pd.Series:
        series = data if data is not None else self.col_data
        if series.empty:
            return pd.Series(dtype=float)
        if method == "iqr":
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            return series[(series < lower) | (series > upper)]
        if method == "zscore":
            z_scores = (series - series.mean()) / series.std(ddof=0)
            return series[(z_scores < -3) | (z_scores > 3)]
        raise ValueError("Invalid method. Use 'iqr' or 'zscore'.")


class DataProfiler:
    """High-level orchestration of dataset and column profiling."""

    def __init__(
        self,
        dataframe: pd.DataFrame,
        custom_types: Optional[Dict[str, str]] = None,
        output_dir: str = ".",
    ) -> None:
        self.original_df = dataframe
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

        self.type_resolver = TypeResolver(dataframe, custom_types)
        self.column_types = self.type_resolver.resolved_types
        self.df = self.type_resolver.transform(dataframe)
        self.results: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Profiling orchestration
    # ------------------------------------------------------------------
    def profile_dataset(self, include_bivariate: bool = False, bivariate_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        metadata = {
            "row_count": int(len(self.df)),
            "column_count": int(self.df.shape[1]),
            "missing_values": int(self.df.isna().sum().sum()),
            "duplicates": int(self.df.duplicated().sum()),
        }

        self.results["metadata"] = metadata
        self.results["column_types"] = self.type_resolver.as_dict()
        self.profile_columns()

        if include_bivariate:
            self.profile_bivariate(**(bivariate_kwargs or {}))

        return self.results

    def profile_columns(self) -> Dict[str, Any]:
        temporal_analyzer = TemporalAnalyzer(self.df, self.plots_dir)
        plotter = DataProfilerPlots(self.df, self.plots_dir)

        temporal_analyses: Dict[str, Any] = {}
        string_profiles: Dict[str, Any] = {}
        numeric_profiles: Dict[str, Any] = {}
        phone_profiles: Dict[str, Any] = {}

        for column, info in self.column_types.items():
            semantic = info.semantic
            logical = info.logical

            if semantic == "datetime":
                temporal_analyses[column] = temporal_analyzer.analyze_temporal_column(column)
            elif logical == "phone_number":
                profiler = StringProfiler(self.df[column])
                phone_profiles[column] = profiler.profile_phone_numbers()
            elif semantic == "numeric":
                profiler = NumericProfiler(self.df[column])
                profile_result = profiler.profile()
                profile_result["logical_type"] = logical
                numeric_profiles[column] = profile_result
            else:
                profiler = StringProfiler(self.df[column])
                profile_result = profiler.profile()
                profile_result["logical_type"] = logical
                string_profiles[column] = profile_result

        plots: Dict[str, Any] = {}
        plots["missing_value_matrix"] = self._relative_path(plotter.missing_value_matrix())

        for column, profile in string_profiles.items():
            all_path = plotter.column_chart(column, include_other=True)
            top_path = plotter.column_chart(column, include_other=False)
            profile["plots"] = {
                "column_chart_all": self._relative_path(all_path),
                "column_chart_top": self._relative_path(top_path),
            }

        for column, profile in numeric_profiles.items():
            histogram_path = plotter.histogram(column)
            kde_path = plotter.kde_plot(column)
            box_path = plotter.box_plot(column)
            profile["plots"] = {
                "histogram": self._relative_path(histogram_path),
                "kde": self._relative_path(kde_path),
            }
            if box_path:
                profile["plots"]["box_plot"] = self._relative_path(box_path)

        for column, analysis in temporal_analyses.items():
            plots_info = analysis.get("plots", {})
            analysis["plots"] = {key: self._relative_path(path) for key, path in plots_info.items()}

        self.results["temporal_analyses"] = temporal_analyses
        self.results["string_profiles"] = string_profiles
        self.results["numeric_profiles"] = numeric_profiles
        self.results["phone_profiles"] = phone_profiles
        self.results.setdefault("plots", {}).update(plots)
        return self.results

    def profile_bivariate(self, **kwargs: Any) -> Dict[str, Any]:
        from data_pipeline.bivariate_profiler import BivariateProfiler

        custom_types = {column: info.logical for column, info in self.column_types.items()}
        output_dir = self.output_dir / "bivariate"
        profiler = BivariateProfiler(self.df, custom_types=custom_types, output_dir=str(output_dir))
        bivariate_results = profiler.profile(**kwargs)
        self.results["bivariate"] = bivariate_results
        return bivariate_results

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def generate_report(self, format: str = "markdown", output_filename: str = "data_profile.md") -> str:
        if not self.results:
            raise RuntimeError("Call profile_dataset() before generating a report.")
        if format == "markdown":
            return self._generate_markdown_report(output_filename)
        if format == "html":
            raise NotImplementedError("HTML report generation is not implemented yet.")
        if format == "csv":
            raise NotImplementedError("CSV report generation is not implemented yet.")
        raise ValueError(f"Unsupported format: {format}")

    def _generate_markdown_report(self, output_filename: str) -> str:
        report_lines = ["# Data Profile Report", ""]
        toc: list[str] = []

        # Metadata
        toc.append("[Metadata](#metadata)")
        report_lines.append("## Metadata")
        for key, value in self.results.get("metadata", {}).items():
            report_lines.append(f"- **{key}**: {value}")
        report_lines.append("")

        # Column type summary
        toc.append("[Column Types](#column-types)")
        report_lines.append("## Column Types")
        type_map = self.results.get("column_types", {})
        if type_map:
            type_rows = ["| Column | Semantic | Logical | Source | Original Dtype |", "| --- | --- | --- | --- | --- |"]
            for column, info in type_map.items():
                type_rows.append(
                    f"| {column} | {info['semantic']} | {info['logical']} | {info['source']} | {info['original_dtype']} |"
                )
            report_lines.extend(type_rows)
        report_lines.append("")

        # Missing value matrix
        missing_path = self.results.get("plots", {}).get("missing_value_matrix")
        if missing_path:
            toc.append("[Missing Value Matrix](#missing-value-matrix)")
            report_lines.append("## Missing Value Matrix")
            report_lines.append(f"![Missing Value Matrix]({missing_path})")
            report_lines.append("")

        # Temporal analyses
        temporal_analyses = self.results.get("temporal_analyses", {})
        if temporal_analyses:
            toc.append("[Temporal Analyses](#temporal-analyses)")
            report_lines.append("## Temporal Analyses")
            for column, analysis in temporal_analyses.items():
                anchor = slugify(column)
                report_lines.append(f"### {column}")
                for key, value in analysis.items():
                    if key == "plots":
                        continue
                    report_lines.append(f"- **{key}**: {value}")
                plots = analysis.get("plots", {})
                for plot_name, path in plots.items():
                    report_lines.append(f"![{plot_name.replace('_', ' ').title()}]({path})")
                report_lines.append("")

        # Numeric profiles
        numeric_profiles = self.results.get("numeric_profiles", {})
        if numeric_profiles:
            toc.append("[Numeric Columns](#numeric-columns)")
            report_lines.append("## Numeric Columns")
            for column, profile in numeric_profiles.items():
                report_lines.append(f"### {column}")
                report_lines.append(f"- **Logical Type**: {profile.get('logical_type')}")
                for stat, value in profile.get("statistics", {}).items():
                    report_lines.append(f"- **{stat}**: {value}")
                report_lines.append(f"- **Skewness**: {profile.get('skewness')}")
                report_lines.append(f"- **Kurtosis**: {profile.get('kurtosis')}")
                report_lines.append(f"- **Outliers**: {len(profile.get('outliers', []))}")
                report_lines.append(f"- **Average (Nonzero)**: {profile.get('avg_nonzero')}")
                report_lines.append(f"- **Distinct Values**: {profile.get('distinct_values')}")
                plots = profile.get("plots", {})
                for plot_name, path in plots.items():
                    report_lines.append(f"![{plot_name.replace('_', ' ').title()}]({path})")
                report_lines.append("")

        # String profiles
        string_profiles = self.results.get("string_profiles", {})
        if string_profiles:
            toc.append("[String Columns](#string-columns)")
            report_lines.append("## String Columns")
            for column, profile in string_profiles.items():
                report_lines.append(f"### {column}")
                report_lines.append(f"- **Logical Type**: {profile.get('logical_type')}")
                report_lines.append(f"- **Distinct Values**: {profile.get('distinct_values')}")
                report_lines.append(f"- **Most Common**: {profile.get('most_common')}")
                report_lines.append(f"- **Least Common**: {profile.get('least_common')}")
                lengths = profile.get("string_lengths", {})
                report_lines.append(
                    "- **String Lengths**: "
                    f"min: {lengths.get('min')}, max: {lengths.get('max')}, mean: {lengths.get('mean')}"
                )
                report_lines.append(f"- **Duplicates Count**: {profile.get('duplicates_count')}")
                report_lines.append(f"- **Entropy**: {profile.get('entropy')}")
                report_lines.append(f"- **Dominance**: {profile.get('dominance')}%")
                report_lines.append(f"- **All Uppercase**: {profile.get('all_uppercase_count')}")
                report_lines.append(f"- **All Lowercase**: {profile.get('all_lowercase_count')}")
                report_lines.append(f"- **Empty Values**: {profile.get('empty_vals')}")
                suspicious = profile.get("suspicious_data")
                if suspicious:
                    report_lines.append(f"- **Suspicious Data**: {suspicious}")
                special_chars = profile.get("special_character_count", {})
                for char_type, value in special_chars.items():
                    report_lines.append(f"- **{char_type.title()}**: {value}")
                plots = profile.get("plots", {})
                for plot_name, path in plots.items():
                    report_lines.append(f"![{plot_name.replace('_', ' ').title()}]({path})")
                report_lines.append("")

        # Phone number profiles
        phone_profiles = self.results.get("phone_profiles", {})
        if phone_profiles:
            toc.append("[Phone Numbers](#phone-numbers)")
            report_lines.append("## Phone Numbers")
            for column, profile in phone_profiles.items():
                report_lines.append(f"### {column}")
                for key, value in profile.items():
                    report_lines.append(f"- **{key}**: {value}")
                report_lines.append("")

        # Row examples
        toc.append("[Row Examples](#row-examples)")
        report_lines.append("## Row Examples")
        report_lines.append("### First 10 Rows")
        report_lines.append(self.df.head(10).to_markdown(index=False))
        report_lines.append("")
        report_lines.append("### Last 10 Rows")
        report_lines.append(self.df.tail(10).to_markdown(index=False))
        report_lines.append("")
        sample_size = min(20, len(self.df))
        if sample_size:
            report_lines.append(f"### Random {sample_size} Rows")
            report_lines.append(self.df.sample(n=sample_size, random_state=42).to_markdown(index=False))
            report_lines.append("")

        toc_lines = ["# Table of Contents", ""] + [f"- {item}" for item in toc] + [""]
        report_content = "\n".join(toc_lines + report_lines)

        """         
        output_path = self.output_dir / output_filename
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(report_content)
        """
        return report_content

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _relative_path(self, path: Path) -> str:
        return os.path.relpath(path, self.output_dir)


if __name__ == "__main__":  # pragma: no cover
    data = pd.DataFrame(
        {
            "A": [1, 2, 2, 4, 5],
            "B": [1.2, 2.5, 2.0, 4.1, 5.3],
            "C": ["NA", "hello", "world", "hello", "hello"],
            "D": pd.date_range(start="2021-01-01", periods=5),
        }
    )

    profiler = DataProfiler(data, custom_types={"C": "string", "D": "date"}, output_dir="./profile_output")
    profiler.profile_dataset()
    profiler.generate_report("markdown", "sample_profile.md")
