from __future__ import annotations

import itertools
import os
from pathlib import Path
from typing import Any, Dict, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import (
    chi2_contingency,
    f_oneway,
    gaussian_kde,
    kendalltau,
    ks_2samp,
    pearsonr,
    pointbiserialr,
    spearmanr,
)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import LabelEncoder
from statsmodels.graphics.mosaicplot import mosaic
from statsmodels.stats.outliers_influence import variance_inflation_factor

from data_profiler import TypeResolver, slugify


class BivariateProfiler:
    """Analyse pairwise relationships using type-aware routing."""

    def __init__(
        self,
        dataframe: pd.DataFrame,
        custom_types: Optional[Dict[str, str]] = None,
        output_dir: str = "bivariate_analysis",
    ) -> None:
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir = self.output_dir / "plots"
        self.plots_dir.mkdir(parents=True, exist_ok=True)

        self.type_resolver = TypeResolver(dataframe, custom_types)
        self.column_types = self.type_resolver.resolved_types
        self.df = self.type_resolver.transform(dataframe)
        self.numeric_columns = [
            column
            for column, info in self.column_types.items()
            if info.semantic == "numeric" or info.semantic == "datetime"
        ]
        self.categorical_columns = [
            column
            for column, info in self.column_types.items()
            if info.semantic in {"string", "boolean"} or info.logical in {"id", "phone_number"}
        ]
        self.results: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def profile(
        self,
        include_plots: bool = True,
        correlations: tuple[str, ...] = ("pearson", "spearman", "kendall"),
    ) -> Dict[str, Any]:
        """Run automated bivariate analysis across column type combinations."""

        results: Dict[str, Any] = {
            "column_types": self.type_resolver.as_dict(),
            "numeric_numeric": {},
            "numeric_categorical": {},
            "categorical_categorical": {},
            "correlation_matrices": {},
            "plots": {},
        }

        # Correlation matrices and VIF for numeric columns
        if len(self.numeric_columns) >= 2:
            for method in correlations:
                matrix, plot_path = self.correlation_analysis(method=method, include_plot=include_plots)
                results["correlation_matrices"][method] = matrix.round(4).fillna(0).to_dict()
                if include_plots and plot_path:
                    results["plots"][f"correlation_{method}"] = plot_path
            vif_table = self.compute_vif()
            if vif_table is not None:
                results["vif"] = vif_table.to_dict("records")
            else:
                results["vif"] = []
        else:
            results["vif"] = []

        # Numeric vs numeric pairs
        for x, y in itertools.combinations(self.numeric_columns, 2):
            metrics = self._analyze_numeric_pair(x, y)
            if include_plots:
                scatter = self.scatter_plot(x, y)
                hexbin = self.hexbin_plot(x, y) if len(self.df) > 500 else None
                plots = {"scatter": scatter, "hexbin": hexbin}
                metrics["plots"] = {k: v for k, v in plots.items() if v}
            results["numeric_numeric"][f"{x}|{y}"] = metrics

        # Categorical vs categorical pairs
        for cat1, cat2 in itertools.combinations(self.categorical_columns, 2):
            metrics = self._analyze_categorical_pair(cat1, cat2)
            if include_plots:
                mosaic_path = self.mosaic_plot(cat1, cat2)
                if mosaic_path:
                    metrics["plots"] = {"mosaic": mosaic_path}
            results["categorical_categorical"][f"{cat1}|{cat2}"] = metrics

        # Numeric vs categorical pairs
        for num in self.numeric_columns:
            for cat in self.categorical_columns:
                metrics = self._analyze_numeric_categorical(num, cat)
                if include_plots:
                    box_path = self.box_plot(num, cat)
                    density_path = self.stacked_density_plot(num, cat)
                    metrics["plots"] = {
                        key: value
                        for key, value in {
                            "box_plot": box_path,
                            "stacked_density": density_path,
                        }.items()
                        if value
                    }
                results["numeric_categorical"][f"{num}|{cat}"] = metrics

        self.results = results
        return results

    def automated_bivariate_analysis(
        self,
        include_plots: bool = True,
        correlations: tuple[str, ...] = ("pearson", "spearman", "kendall"),
    ) -> Dict[str, Any]:
        """Backward-compatible alias for :meth:`profile`."""

        return self.profile(include_plots=include_plots, correlations=correlations)

    # ------------------------------------------------------------------
    # Pairwise metric helpers
    # ------------------------------------------------------------------
    def correlation_analysis(self, method: str = "pearson", include_plot: bool = True):
        numeric_df = self._numeric_frame()
        if numeric_df.shape[1] < 2:
            return numeric_df.corr(method=method), None
        corr_matrix = numeric_df.corr(method=method)
        plot_path = None
        if include_plot and not corr_matrix.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
            ax.set_title(f"{method.title()} Correlation Matrix")
            plot_path = self._save_plot(fig, f"correlation_matrix_{method}.png")
        return corr_matrix, plot_path

    def scatter_plot(self, x: str, y: str) -> Optional[str]:
        data = self._numeric_frame([x, y]).dropna()
        if data.empty:
            return None
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.regplot(x=data[x], y=data[y], scatter_kws={"alpha": 0.5}, line_kws={"color": "red"}, ax=ax)
        ax.set_title(f"Scatter Plot: {x} vs {y}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        filename = f"scatter_{slugify(x)}_vs_{slugify(y)}.png"
        return self._save_plot(fig, filename)

    def chi_square_test(self, cat1: str, cat2: str) -> Dict[str, float]:
        contingency = pd.crosstab(self.df[cat1], self.df[cat2])
        if contingency.empty:
            return {"chi2": np.nan, "p_value": np.nan}
        chi2, p, _, _ = chi2_contingency(contingency)
        return {"chi2": float(chi2), "p_value": float(p)}

    def mosaic_plot(self, cat1: str, cat2: str) -> Optional[str]:
        contingency = pd.crosstab(self.df[cat1], self.df[cat2])
        if contingency.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        mosaic(self.df[[cat1, cat2]].dropna(), [cat1, cat2], ax=ax)
        ax.set_title(f"Mosaic Plot: {cat1} vs {cat2}")
        filename = f"mosaic_{slugify(cat1)}_vs_{slugify(cat2)}.png"
        return self._save_plot(fig, filename)

    def box_plot(self, num: str, cat: str) -> Optional[str]:
        frame = self.df[[num, cat]].dropna()
        if frame.empty or frame[cat].nunique() < 2:
            return None
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(x=frame[cat], y=frame[num], ax=ax)
        ax.set_title(f"Box Plot: {num} by {cat}")
        ax.set_xlabel(cat)
        ax.set_ylabel(num)
        filename = f"boxplot_{slugify(num)}_by_{slugify(cat)}.png"
        return self._save_plot(fig, filename)

    def anova_test(self, num: str, cat: str) -> Dict[str, float]:
        frame = self.df[[num, cat]].dropna()
        groups = [frame[frame[cat] == level][num] for level in frame[cat].unique()]
        if len(groups) < 2 or any(len(group) < 2 for group in groups):
            return {"f_stat": np.nan, "p_value": np.nan}
        f_stat, p_value = f_oneway(*groups)
        return {"f_stat": float(f_stat), "p_value": float(p_value)}

    def compute_vif(self) -> Optional[pd.DataFrame]:
        numeric_df = self._numeric_frame().dropna()
        if numeric_df.shape[1] < 2:
            return None
        vif_values = []
        try:
            for i in range(numeric_df.shape[1]):
                vif = variance_inflation_factor(numeric_df.values, i)
                vif_values.append(vif)
        except np.linalg.LinAlgError:
            return None
        return pd.DataFrame({"variable": numeric_df.columns, "vif": vif_values})

    def cramers_v(self, cat1: str, cat2: str) -> float:
        contingency = pd.crosstab(self.df[cat1], self.df[cat2])
        if contingency.empty:
            return float("nan")
        chi2 = chi2_contingency(contingency)[0]
        n = contingency.to_numpy().sum()
        r, k = contingency.shape
        return float(np.sqrt(chi2 / (n * (min(r - 1, k - 1) or 1))))

    def logistic_regression_effect(self, cat: str, num: str) -> Optional[Dict[str, float]]:
        frame = self.df[[cat, num]].dropna()
        if frame.empty or frame[cat].nunique() < 2:
            return None
        encoder = LabelEncoder()
        y = encoder.fit_transform(frame[cat])
        X = frame[[num]]
        try:
            model = LogisticRegression(max_iter=200).fit(X, y)
        except Exception:
            return None
        return {"coef": float(model.coef_[0][0]), "intercept": float(model.intercept_[0])}

    def pairplot(self) -> Optional[str]:
        if len(self.numeric_columns) < 2:
            return None
        numeric_df = self._numeric_frame()
        if numeric_df.empty:
            return None
        grid = sns.pairplot(numeric_df.dropna())
        filename = self.plots_dir / "pairplot.png"
        grid.fig.savefig(filename)
        plt.close(grid.fig)
        return self._relative_path(filename)

    def point_biserial_corr(self, numeric_col: str, categorical_col: str) -> Optional[float]:
        frame = self.df[[numeric_col, categorical_col]].dropna()
        if frame[categorical_col].nunique() != 2 or frame.empty:
            return None
        encoded = LabelEncoder().fit_transform(frame[categorical_col])
        return float(pointbiserialr(frame[numeric_col], encoded)[0])

    def tukey_hsd_test(self, numeric_col: str, category_col: str) -> Dict[str, Any]:
        frame = self.df[[numeric_col, category_col]].dropna()
        groups = [group for _, group in frame.groupby(category_col)[numeric_col]]
        if len(groups) < 2:
            return {"f_stat": np.nan, "p_value": np.nan}
        f_stat, p_value = f_oneway(*groups)
        return {"f_stat": float(f_stat), "p_value": float(p_value)}

    def mutual_information(self, categorical_col: str, target_col: str) -> Optional[float]:
        frame = self.df[[categorical_col, target_col]].dropna()
        if frame.empty:
            return None
        return float(mutual_info_score(frame[categorical_col], frame[target_col]))

    def kolmogorov_smirnov_test(self, numeric_col: str, group_col: str) -> Optional[Dict[str, float]]:
        frame = self.df[[numeric_col, group_col]].dropna()
        if frame[group_col].nunique() < 2:
            return None
        groups = [values[numeric_col].values for _, values in frame.groupby(group_col)]
        if len(groups) < 2:
            return None
        stat, p_value = ks_2samp(groups[0], groups[1])
        return {"statistic": float(stat), "p_value": float(p_value)}

    def stacked_density_plot(self, numeric_col: str, category_col: str) -> Optional[str]:
        frame = self.df[[numeric_col, category_col]].dropna()
        categories = frame[category_col].unique()
        if len(categories) < 2:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        for category in categories:
            subset = frame[frame[category_col] == category][numeric_col].dropna()
            if subset.empty:
                continue
            if subset.nunique() < 2:
                continue
            density = gaussian_kde(subset)
            x_vals = np.linspace(subset.min(), subset.max(), 100)
            ax.plot(x_vals, density(x_vals), label=str(category))
        if not ax.lines:
            plt.close(fig)
            return None
        ax.set_title(f"Stacked Density Plot: {numeric_col} by {category_col}")
        ax.set_xlabel(numeric_col)
        ax.set_ylabel("Density")
        ax.legend()
        filename = f"stacked_density_{slugify(numeric_col)}_by_{slugify(category_col)}.png"
        return self._save_plot(fig, filename)

    def hexbin_plot(self, x: str, y: str) -> Optional[str]:
        data = self._numeric_frame([x, y]).dropna()
        if data.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        hb = ax.hexbin(data[x], data[y], gridsize=40, cmap="Blues", mincnt=1)
        ax.figure.colorbar(hb, ax=ax, label="Density")
        ax.set_title(f"Hexbin Plot: {x} vs {y}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        filename = f"hexbin_{slugify(x)}_vs_{slugify(y)}.png"
        return self._save_plot(fig, filename)

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _analyze_numeric_pair(self, x: str, y: str) -> Dict[str, Any]:
        data = self._numeric_frame([x, y]).dropna()
        if data.empty:
            return {"n": 0}
        return {
            "n": int(len(data)),
            "pearson": float(data[x].corr(data[y], method="pearson")),
            "spearman": float(data[x].corr(data[y], method="spearman")),
            "kendall": float(data[x].corr(data[y], method="kendall")),
        }

    def _analyze_categorical_pair(self, cat1: str, cat2: str) -> Dict[str, Any]:
        contingency = pd.crosstab(self.df[cat1], self.df[cat2])
        if contingency.shape[0] < 2 or contingency.shape[1] < 2:
            return {"error": "Insufficient variation"}
        chi2, p_value, dof, _ = chi2_contingency(contingency)
        return {
            "chi2": float(chi2),
            "p_value": float(p_value),
            "degrees_of_freedom": int(dof),
            "cramers_v": float(self.cramers_v(cat1, cat2)),
            "mutual_information": float(mutual_info_score(self.df[cat1], self.df[cat2])),
        }

    def _analyze_numeric_categorical(self, num: str, cat: str) -> Dict[str, Any]:
        frame = self.df[[num, cat]].dropna()
        if frame.empty or frame[cat].nunique() < 2:
            return {"error": "Insufficient variation"}
        metrics: Dict[str, Any] = {
            "anova": self.anova_test(num, cat),
            "logistic_regression": self.logistic_regression_effect(cat, num),
            "point_biserial": self.point_biserial_corr(num, cat),
        }
        return metrics

    def _numeric_frame(self, columns: Optional[list[str]] = None) -> pd.DataFrame:
        cols = columns or self.numeric_columns
        data: Dict[str, pd.Series] = {}
        for column in cols:
            series = self.df[column]
            if pd.api.types.is_datetime64_any_dtype(series):
                values = series.view("int64").astype(float)
                values[series.isna()] = np.nan
                data[column] = values / 1e9
            else:
                data[column] = pd.to_numeric(series, errors="coerce")
        return pd.DataFrame(data)

    def _save_plot(self, fig: plt.Figure, filename: str) -> str:
        path = self.plots_dir / filename
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        return self._relative_path(path)

    def _relative_path(self, path: Path) -> str:
        return os.path.relpath(path, self.output_dir)


__all__ = ["BivariateProfiler"]
