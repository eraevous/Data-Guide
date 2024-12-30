import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from markdownify import markdownify

class DataProfiler:
    def __init__(self, dataframe, custom_types=None):
        self.df = dataframe
        self.custom_types = custom_types or {}
        self.numeric_summary = None
        self.categorical_summary = None
        self.results = {}

    def _generate_metadata(self):
        metadata = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "missing_values": self.df.isnull().sum().sum(),
            "duplicates": self.df.duplicated().sum()
        }
        return metadata

    def _detect_duplicates(self):
        return self.df.duplicated().sum()

    def profile_dataset(self):
        """
        Generate summaries for numeric and categorical columns.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number])
        categorical_cols = self.df.select_dtypes(include=["object", "category"])

        self.numeric_summary = numeric_cols.describe().T
        self.numeric_summary["missing_percentage"] = (
            numeric_cols.isnull().mean() * 100
        )
        self.numeric_summary["unique_values"] = numeric_cols.nunique()
        self.numeric_summary["unique_values"] = numeric_cols.nunique()
        self.numeric_summary["skewness"] = numeric_cols.skew()
        self.numeric_summary["kurtosis"] = numeric_cols.kurt()

        self.categorical_summary = categorical_cols.describe().T
        self.categorical_summary["missing_percentage"] = (
            categorical_cols.isnull().mean() * 100
        )
        self.categorical_summary["unique_values"] = categorical_cols.nunique()

        # Store results in the results attribute
        self.results = {
            "numeric_summary": self.numeric_summary,
            "categorical_summary": self.categorical_summary
        }

    def generate_markdown_report(self, output_path):
        """
        Generate a Markdown report summarizing the dataset.
        """
        md_content = "# Data Profile Report\n\n"

        # Add numeric summary
        if self.numeric_summary is not None:
            md_content += "## Numeric Columns\n\n"
            md_content += self.numeric_summary.to_markdown() + "\n\n"

        # Add categorical summary
        if self.categorical_summary is not None:
            md_content += "## Categorical Columns\n\n"
            md_content += self.categorical_summary.to_markdown() + "\n\n"

        # Save the Markdown file
        with open(output_path, "w") as f:
            f.write(md_content)

    def plot_distributions(self, output_dir):
        """
        Generate distribution plots for numeric columns.
        """
        numeric_cols = self.df.select_dtypes(include=[np.number])
        for col in numeric_cols.columns:
            plt.figure()
            sns.histplot(self.df[col].dropna(), kde=True)
            plt.title(f"Distribution for {col}")
            plt.savefig(f"{output_dir}/{col}_distribution.png")
            plt.close()

    def profile_temporal_data(self):
        """
        Analyze temporal columns for trends and gaps.
        """
        temporal_columns = self.df.select_dtypes(include=['datetime']).columns
        temporal_analysis = {}

        for col in temporal_columns:
            col_data = self.df[col]
            temporal_analysis[col] = {
                "earliest": col_data.min(),
                "latest": col_data.max(),
                "time_span": col_data.max() - col_data.min(),
                "temporal_gaps": col_data.diff().describe().to_dict()
            }

        self.results["temporal_analysis"] = temporal_analysis

    def profile_missing_values(self):
        """
        Visualize missing values using a missing value matrix.
        """
        msno.matrix(self.df)
        plt.title("Missing Value Matrix")
        plt.show()

# Example Usage
if __name__ == "__main__":
    # Load a sample dataset
    df = sns.load_dataset("titanic")

    # Initialize the profiler
    profiler = DataProfiler(df)

    # Profile the dataset
    profiler.profile_dataset()

    # Profile temporal data
    profiler.profile_temporal_data()

    # Generate Markdown report
    profiler.generate_markdown_report("data_profile.md")

    # Plot distributions
    profiler.plot_distributions("plots")

    # Visualize missing values
    profiler.profile_missing_values()
