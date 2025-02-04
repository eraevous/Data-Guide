import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import missingno as msno
from scipy.stats import entropy
import os
import re
import textwrap

class DataProfilerPlots:
    def __init__(self, df):
        self.df = df

    def _wrap_text(self, text, width=12):
        """
        Helper function to wrap text for axis labels and titles.
        """
        wrapped_lines = textwrap.wrap(text, width)
        return "\n".join(wrapped_lines)
    
    def wrap_xtick_labels(ax, wrap_width=20):
        """
        Wrap the x-axis tick labels on a Matplotlib Axes object.

        Args:
            ax (matplotlib.axes.Axes): The Axes object containing the plot.
            wrap_width (int): The width at which to wrap the labels.
        """
        labels = [label.get_text() for label in ax.get_xticklabels()]
        wrapped_labels = [_wrap_text(label, wrap_width) for label in labels]

        # Set the ticks explicitly
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(wrapped_labels, rotation=60, ha="center")

    def bar_or_column_chart(self, column, output_path, wrap_width=20, top_n=12, include_other=True, transpose=False):
        # Compute value counts
        value_counts = self.df[column].value_counts()
        other_count = value_counts.iloc[top_n:].sum() if len(value_counts) > top_n else 0

        # Create a dictionary for the top values and append 'Other'
        top_values = value_counts.head(top_n).to_dict()
        if other_count > 0 and include_other:
            top_values["Other"] = other_count

        # Convert to pandas Series for plotting
        top_values_series = pd.Series(top_values)

        # Plot column chart
        if transpose:
            ax = top_values_series.plot(kind='barh', color='skyblue')
            ax.set_xlabel(self._wrap_text(column, wrap_width))
            ax.set_ylabel("Count")
            labels = [label.get_text() for label in ax.get_yticklabels()]
            wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(wrapped_labels, ha="right")  # Adjust alignment if needed
            ax.set_title(f"Column Chart for {column}")
            ax.invert_yaxis()  # Reverse the Y-axis sort order

        else:
            ax = top_values_series.plot(kind='bar', color='skyblue')
            ax.set_xlabel(self._wrap_text(column, wrap_width))
            ax.set_ylabel("Count")
            labels = [label.get_text() for label in ax.get_xticklabels()]
            wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(wrapped_labels, rotation=90, ha="center")  # Adjust rotation and alignment if needed
            ax.set_title(f"Bar Chart for {column}")

        # Add data labels for the % of the grand total
        total = value_counts.sum()
        for p in ax.patches:
            percentage = f'{(p.get_height() / total) * 100:.1f}%' if not transpose else f'{(p.get_width() / total) * 100:.1f}%'
            ax.annotate(percentage, (p.get_x() + p.get_width() / 2. + 0.1, p.get_height()) if not transpose else (p.get_width() + 0.1, p.get_y() + p.get_height() / 2.),
                        ha='center', va='center', xytext=(0, 10) if not transpose else (10, 0), textcoords='offset points')

        # Increase bottom margin
        plt.subplots_adjust(bottom=0.40, top=0.90) if not transpose else plt.subplots_adjust(left=0.25, top=0.90)  # Adjust the margin
        # Save the plot
        plt.savefig(output_path)
        plt.close()

    def donut_chart(self, column, output_path, top_n=6):
        # Compute value counts
        value_counts = self.df[column].value_counts()
        top_values = value_counts.head(top_n)
        other_values = value_counts.iloc[top_n:]

        # Create labels for the top values and leave the rest unlabeled
        labels = top_values.index.tolist() + [''] * len(other_values)
        sizes = top_values.tolist() + other_values.tolist()

        # Plot donut chart
        plt.figure(figsize=(8, 8))
        wedges, texts = plt.pie(sizes, labels=labels, startangle=90, wedgeprops=dict(width=0.3))

        # Add a circle at the center to make it a donut chart
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        plt.title(f"Donut Chart for {column}")
        plt.savefig(output_path)
        plt.close()

    # Histogram: Numerical Variable
    def histogram(self, column, output_path, wrap_width=20):
        ax = self.df[column].plot(kind="hist", bins=20, color="lightgreen", edgecolor="black")
        ax.set_title(f"Histogram for {column}")
        ax.set_xlabel(self._wrap_text(column, wrap_width))
        ax.set_ylabel("Frequency")
        # labels = [label.get_text() for label in ax.get_xticklabels()]
        # wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
        # ax.set_xticks(range(len(labels)))
        # ax.set_xticklabels(wrapped_labels, rotation=60, ha="center")  # Adjust rotation and alignment if needed
        plt.subplots_adjust(bottom=0.2, top = 0.85)  # Increase bottom margin
        plt.savefig(output_path)
        plt.close()

    # KDE Plot
    def kde_plot(self, column, output_path, wrap_width=20):
        ax = sns.kdeplot(self.df[column], fill=True, color="blue")
        ax.set_title(f"KDE Plot for {column}")
        ax.set_xlabel(self._wrap_text(column, wrap_width))
        ax.set_ylabel("Density")
        # labels = [label.get_text() for label in ax.get_xticklabels()]
        # wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
        # ax.set_xticks(range(len(labels)))
        # ax.set_xticklabels(wrapped_labels, rotation=60, ha="center")  # Adjust rotation and alignment if needed
        plt.subplots_adjust(bottom=0.2, top = 0.85)  # Increase bottom margin
        plt.savefig(output_path)
        plt.close()

    # Box Plot: Outliers and Spread
    def box_plot(self, column, output_path, wrap_width=20):
        col_data = self.df[column].dropna()
        if col_data.empty:
            print(f"No data available for box plot of {column}")
            return
        ax = sns.boxplot(y=col_data, color="coral")
        ax.set_title(f"Box Plot for {column}")
        ax.set_ylabel(self._wrap_text(column, wrap_width))
        # labels = [label.get_text() for label in ax.get_xticklabels()]
        # wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
        # ax.set_xticks(range(len(labels)))
        # ax.set_xticklabels(wrapped_labels, rotation=60, ha="center")  # Adjust rotation and alignment if needed
        plt.subplots_adjust(bottom=0.2, top = 0.85)  # Increase bottom margin
        plt.savefig(output_path)
        plt.close()

    # Missing Value Matrix
    def missing_value_matrix(self, output_path, wrap_width=20):
        fig, ax = plt.subplots(figsize=(15, 10))  # Set larger dimensions for clarity
        msno.matrix(self.df, ax=ax)
        ax.set_title("Missing Value Matrix")
        # labels = [label.get_text() for label in ax.get_xticklabels()]
        # wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
        # ax.set_xticklabels(wrapped_labels, rotation=0, ha="center")  # Adjust rotation and alignment if needed
        plt.subplots_adjust(top=0.80, right=0.9)  # Slightly adjust top and right margins
        plt.savefig(output_path)
        plt.close()

class TemporalAnalyzer:
    def __init__(self, dataframe, output_dir, window=3):
        self.df = dataframe
        self.output_dir = output_dir
        self.window = window

    def analyze_temporal_column(self, column):
        """
        Perform temporal analysis for a single column.
        """
        col_data = self.df[column].dropna()
        earliest = col_data.min()
        latest = col_data.max()
        analysis = {
            "earliest": earliest.strftime("%Y-%m-%d") if pd.notna(earliest) else "N/A",
            "latest": latest.strftime("%Y-%m-%d") if pd.notna(latest) else "N/A",
            "time_span": f"{(latest - earliest).days} days" if pd.notna(earliest) and pd.notna(latest) else "N/A",
            "temporal_gaps": self._summarize_temporal_gaps(col_data),
            "day_of_week_distribution": self._format_day_of_week_distribution(col_data.dt.dayofweek.value_counts().to_dict()),
            "monthly_trends": self._format_monthly_trends(col_data.dt.month.value_counts().sort_index().to_dict())
        }
        self._plot_temporal_gaps_distribution(col_data, column)
        self._plot_weekly_aggregate_time_series(col_data, column)
        return analysis

    def _summarize_temporal_gaps(self, col_data):
        """
        Summarize temporal gaps with human-friendly descriptions.
        """
        # Ensure the data is sorted chronologically
        col_data = col_data.sort_values()
        gaps = col_data.diff().describe()
        summary = {
            "count": int(gaps["count"]),
            "mean": f"{gaps['mean'].days} days" if pd.notna(gaps["mean"]) else "N/A",
            "std": f"{gaps['std'].days} days" if pd.notna(gaps["std"]) else "N/A",
            "min": f"{gaps['min'].days} days" if pd.notna(gaps["min"]) else "N/A",
            "25%": f"{gaps['25%'].days} days" if pd.notna(gaps["25%"]) else "N/A",
            "50%": f"{gaps['50%'].days} days" if pd.notna(gaps["50%"]) else "N/A",
            "75%": f"{gaps['75%'].days} days" if pd.notna(gaps["75%"]) else "N/A",
            "max": f"{gaps['max'].days} days" if pd.notna(gaps["max"]) else "N/A"
        }
        return summary

    def _format_day_of_week_distribution(self, day_of_week_counts):
        """
        Convert day-of-week counts to labels like Monday, Tuesday, etc.
        """
        day_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return {day_labels[int(k)]: v for k, v in day_of_week_counts.items()}

    def _format_monthly_trends(self, monthly_counts):
        """
        Convert month numbers to names like January, February, etc.
        """
        month_labels = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return {month_labels[int(k) - 1]: v for k, v in monthly_counts.items()}

    def _plot_temporal_gaps_distribution(self, col_data, column):
        """
        Plot histogram and KDE for temporal gaps.
        """
        # Ensure the data is sorted chronologically
        col_data = col_data.sort_values()

        column_name = re.sub(r'[^\w\-_]', '_', column)
        column_name = re.sub(r'__+', '_', column_name)
        temporal_gaps = col_data.diff().dropna()
        plt.figure(figsize=(12, 6))
        sns.histplot(temporal_gaps.dt.days, kde=True, color="blue", bins=30)
        plt.title(f"Temporal Gaps Distribution for {column}")
        plt.xlabel("Gap (days)")
        plt.ylabel("Frequency")
        plt.savefig(f"{self.output_dir}/{column_name}_temporal_gaps_distribution.png")
        plt.close()

    def _plot_weekly_aggregate_time_series(self, col_data, column):
        """
        Plot weekly aggregated time series.
        """
        window = self.window
        column_name = re.sub(r'[^\w\-_]', '_', column)
        column_name = re.sub(r'__+', '_', column_name)

        # Compute weekly aggregated counts
        weekly_counts = col_data.dt.to_period("W").value_counts().sort_index()

        # Apply a moving average for smoothing
        weekly_counts_smooth = weekly_counts.rolling(window=window, center=True).mean()

        plt.figure(figsize=(14, 8))  # Increase figure size for better clarity

        # Plot original data for context
        plt.plot(
            weekly_counts.index.to_timestamp(),
            weekly_counts,
            marker="o",
            color="lightgray",
            alpha=0.6,
            label="Original Data",
            linewidth=1
        )

        # Plot the smoothed moving average
        plt.plot(
            weekly_counts_smooth.index.to_timestamp(),
            weekly_counts_smooth,
            marker="o",
            color="blue",
            linewidth=2,
            label=f"{window}-Week Moving Average"
        )

        plt.title(f"Weekly Time Series for {column}", fontsize=16, fontweight="bold")
        plt.xlabel("Week", fontsize=12, labelpad=10)
        plt.ylabel("Count", fontsize=12, labelpad=10)

        # Add gridlines for readability
        plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.7)

        # Add legend
        plt.legend(fontsize=10)

        # Rotate x-axis labels for better readability
        plt.xticks(fontsize=10, rotation=45)
        plt.yticks(fontsize=10)

        # Add padding around the plot
        plt.tight_layout()

        # Save the plot
        plt.savefig(f"{self.output_dir}/{column_name}_weekly_time_series.png", dpi=300)
        plt.close()

class StringProfiler:
    def __init__(self, column_data):
        """
        Initialize the profiler for a specific string column.

        Args:
            column_data (pd.Series): The column to profile.
        """
        self.col_data = column_data

    def profile(self):
        """
        Profiles the string column, including entropy, dominance, and special character analysis.

        Returns:
            dict: A dictionary containing the profiling results.
        """
        suspicious_patterns = [
            r"Z{2,}",  # Two or more Z's in a row
            r"9{2,}",  # Two or more 9's in a row
            r"\d{4,}",  # Sequential numbers, 6 or more digits
            r"(?i)test",  # Case-insensitive 'test'
            r"(?i)none"  # Case-insensitive 'none'
        ]
        empty_patterns = ['(?i)None', '(?i)nan', '(?i)', '(?i)N/A', '(?i)Not Available', '(?i)Unknown', '(?i)blank', '(?i)missing', '(?i)null']
        suspicious_data = self._identify_invalid_patterns_regex(suspicious_patterns)
        special_characters = self._count_special_characters()
        entropy_value = entropy(self.col_data.value_counts(normalize=True), base=2)
        top_dominance = self.col_data.value_counts(normalize=True).head(1).values[0] * 100 if not self.col_data.empty else 0

        return {
            "distinct_values": self.col_data.nunique(),
            "string_lengths": {
                "min": self.col_data.str.len().min(),
                "max": self.col_data.str.len().max(),
                "mean": self.col_data.str.len().mean()
            },
            "most_common": self.col_data.value_counts().head(4).to_dict(),
            "least_common": self.col_data.value_counts().tail(4).to_dict(),
            "duplicates_count": self.col_data.duplicated().sum(),
            "all_uppercase_count": self.col_data.str.isupper().sum(),
            "all_lowercase_count": self.col_data.str.islower().sum(),
            "empty_vals": self.col_data.isna().sum() + self.col_data.str.strip().isin(empty_patterns).sum(),
            "entropy": entropy_value,
            "dominance": top_dominance,
            "special_character_count": special_characters,
            "suspicious_data": suspicious_data
        }

    def _count_special_characters(self):
        """
        Count occurrences of special characters like hashtags and mentions.

        Returns:
            dict: A dictionary containing counts of special characters.
        """
        special_chars = {
            "hashtags": self.col_data.str.count(r"#").sum(),
            "mentions": self.col_data.str.count(r"@").sum()
        }
        return special_chars

    def profile_phone_numbers(self):
        """
        Placeholder for profiling phone numbers (requires phonenumbers library).

        Returns:
            dict: A dictionary containing counts of valid and invalid phone numbers.
        """
        valid_count = 0
        invalid_count = 0
        try:
            import phonenumbers
            for number in self.col_data:
                try:
                    parsed = phonenumbers.parse(number, "US")
                    if phonenumbers.is_valid_number(parsed):
                        valid_count += 1
                except:
                    invalid_count += 1
        except ImportError:
            print("phonenumbers library not installed.")
            return {"valid_phone_numbers": "N/A", "invalid_phone_numbers": "N/A"}

        return {"valid_phone_numbers": valid_count, "invalid_phone_numbers": invalid_count}

    def _identify_invalid_patterns_regex(self, patterns):
        """
        Identify suspicious patterns in a column using regex.

        Args:
            patterns (list): A list of regex patterns to check for.

        Returns:
            dict: A dictionary containing counts of suspicious patterns.
        """
        suspicious_counts = {}
        for pattern in patterns:
            matches = self.col_data.str.contains(pattern, na=False, regex=True)
            suspicious_counts[pattern] = int(matches.sum())
        return suspicious_counts

class NumericProfiler:
    def __init__(self, column_data):
        """
        Initialize the profiler for a specific numeric column.

        Args:
            column_data (pd.Series): The numeric column to profile.
        """
        self.col_data = column_data

    def profile(self):
        """
        Profiles the numeric column, including additional percentiles and outlier detection.

        Returns:
            dict: A dictionary containing the profiling results.
        """
        
        stats = self.col_data.describe(percentiles=[0.01, 0.05, 0.33, 0.5, 0.66, 0.95, 0.99]).to_dict()
        outliers = self.detect_outliers()
        return {
            "distinct_values": self.col_data.nunique(),
            "statistics": {k: round(v, 2) for k, v in stats.items()},
            "skewness": round(self.col_data.skew(), 2),
            "kurtosis": round(self.col_data.kurt(), 2),
            "most_common": self.col_data.value_counts().head(4).round(2).to_dict(),
            "least_common": self.col_data.value_counts().tail(4).round(2).to_dict(),
            "outliers": outliers.tolist(),
            "count_negative": self.col_data[self.col_data < 0].count(),
            "count_zero": (self.col_data == 0).sum(),
            "avg_nonzero": self.col_data[self.col_data != 0].mean(),
            "count_blank" : self.col_data.isna().sum()
        }

    def detect_outliers(self, method='iqr'):
        """
        Detect outliers using IQR or Z-score.

        Args:
            method (str): The method to use for detecting outliers ('iqr' or 'zscore').

        Returns:
            pd.Series: A Series containing the outlier values.
        """
        if method == 'iqr':
            q1 = self.col_data.quantile(0.25)
            q3 = self.col_data.quantile(0.75)
            iqr = q3 - q1
            return self.col_data[(self.col_data < (q1 - 1.5 * iqr)) | (self.col_data > (q3 + 1.5 * iqr))]
        elif method == 'zscore':
            z_scores = (self.col_data - self.col_data.mean()) / self.col_data.std()
            return self.col_data[(z_scores < -3) | (z_scores > 3)]
        else:
            raise ValueError("Invalid method. Use 'iqr' or 'zscore'.")
class DataProfiler:
    def __init__(self, dataframe, custom_types=None, output_dir="."):
        self.df = dataframe
        self.output_dir = output_dir
        self.custom_types = custom_types
        self._initialize_custom_types()
        self.results = {}
        self._preprocess_data()

    def _initialize_custom_types(self):
        """
        Initialize the custom_types dictionary by merging provided types with defaults.
        """
        # Infer default types from the dataframe
        default_types = {col: str(self.df[col].dtype) for col in self.df.columns}

        # Merge provided custom_types with defaults
        if self.custom_types:
            self.custom_types = {**default_types, **self.custom_types}
        else:
            self.custom_types = default_types

    def _preprocess_data(self):
        """
        Apply custom data type mappings.
        """

        for column, dtype in self.custom_types.items():
            if dtype == 'phone_number':
                self.df[column] = self.df[column].apply(self._parse_phone_number)
            elif dtype == 'id':
                self.df[column] = self.df[column].astype(str)
            elif dtype == 'bool':
                self.df[column] = self.df[column].astype(str)
            elif dtype == 'category':
                self.df[column] = self.df[column].astype(str)
            elif dtype == 'unix_timestamp':
                self.df[column] = self.convert_unix_timestamps(self.df, column, in_milliseconds=True)
            elif dtype == 'currency':
                self.df[column] = self._treat_currency(self.df, column)
            elif dtype == 'date':
                col = self.df[column].replace("Not Available", pd.NaT)
                col = pd.to_datetime(col, errors='coerce', infer_datetime_format=True)
                self.df[column] = col

    def _treat_currency(self, df, column):
        """
        Placeholder for currency treatment logic.
        """
        coll = pd.to_numeric(df[column].replace(r'[\$,]', '', regex=True).replace('-', np.nan), errors='coerce').astype(float)
        coll = coll.fillna(0)
        return coll         
    
    def convert_unix_timestamps(self, df, column, in_milliseconds=True):
        """
        Convert Unix timestamps in a specified column to datetime.

        Args:
            df (pd.DataFrame): The input DataFrame.
            column (str): The name of the column containing Unix timestamps.
            in_milliseconds (bool): Whether the timestamps are in milliseconds. Default is True.

        Returns:
            pd.DataFrame: The DataFrame with the converted datetime column.
        """
        try:
            factor = 1000 if in_milliseconds else 1
            coll = pd.to_datetime(df[column] / factor, unit='s', errors='coerce')
            print(f"Successfully converted {column} to datetime.")
        except Exception as e:
            coll = df[column]
            print(f"Error converting column {column}: {e}")
        return coll

    def _parse_phone_number(self, value):
        """
        Placeholder for phone number parsing logic.
        """
        return value
    

    def profile_dataset(self):
        """
        Generate dataset-level profiles.
        """
        print(self.custom_types)
        
        metadata = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "missing_values": self.df.isnull().sum().sum(),
            "duplicates": self.df.duplicated().sum(),
            "columns": self.df.columns.tolist()
        }
        
        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        plots_dir = os.path.join(self.output_dir, "plots")
        if not os.path.exists(plots_dir):
            os.makedirs(plots_dir)

        temporal_analyzer = TemporalAnalyzer(self.df, plots_dir)

        # Perform analysis

        temporal_analyses = {}
        string_profiles = {}
        numeric_profiles = {}
        phone_profiles = {}
        for col, dtype in self.custom_types.items():
            print(f"Profiling column {col} with type {dtype}")
            if dtype in ['date', 'datetime64[ns]', 'timestamp', 'datetime', 'unix_timestamp']:
                temporal_analyses[col] = temporal_analyzer.analyze_temporal_column(col)     
            elif dtype in ['object', 'category', 'str', 'bool']:
                string_profiler = StringProfiler(self.df[col])
                string_profiles[col] = string_profiler.profile()    
            elif dtype == 'phone_number':
                string_profiler = StringProfiler(self.df[col])
                phone_profiles[col] = string_profiler.profile_phone_numbers() 
            elif dtype in ['int64', 'float64', 'numeric', 'currency']:
                numeric_profiler = NumericProfiler(self.df[col])
                numeric_profiles[col] = numeric_profiler.profile()
            else:
                print(f"Skipping column {col} with unsupported type {dtype}")

        
        profiler_plotter = DataProfilerPlots(self.df)

        # Generate missing value matrix
        profiler_plotter.missing_value_matrix(f"{plots_dir}/missing_value_matrix.png")

        # Generate column visuals
        for column in string_profiles.keys():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            profiler_plotter.bar_or_column_chart(column, f"{plots_dir}/{column_name}_columnchart_all.png", transpose=True)
            profiler_plotter.bar_or_column_chart(column, f"{plots_dir}/{column_name}_columnchart_top.png", include_other=False, transpose=True)
            profiler_plotter.donut_chart(column, f"{plots_dir}/{column_name}_donut.png")

        for column in numeric_profiles.keys():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            profiler_plotter.histogram(column, f"{plots_dir}/{column_name}_histogram.png")
            profiler_plotter.kde_plot(column, f"{plots_dir}/{column_name}_kde_plot.png")
            profiler_plotter.box_plot(column, f"{plots_dir}/{column_name}_boxplot.png")

        self.results['temporal_analyses'] = temporal_analyses
        self.results['metadata'] = metadata
        self.results['string_profiles'] = string_profiles
        self.results['phone_profiles'] = phone_profiles
        self.results['numeric_profiles'] = numeric_profiles

    def generate_report(self, format='markdown', output_filename="data_profile.md"):
        if format == 'md':
            return self._generate_markdown_report(output_filename)
        elif format == 'html':
            return self._generate_html_report(output_filename)
        elif format == 'csv':
            return self._generate_csv_report(output_filename)
        else:
            raise ValueError("Unsupported format: {}".format(format))

    def _generate_markdown_report(self, output_filename):
        """
        Generate a Markdown report with a section per column.
        """
        plots_dir = "plots"

        toc = []
        toc.append("Metadata")
        
        report = f"# Data Profile Report\n\n"
        metadata = self.results.get("metadata", {})
        report += "## Metadata\n"
        for key, value in metadata.items():
            report += f"- **{key}**: {value}\n"
          
        toc.append("Missing Value Matrix")
        # Missing value matrix
        report += "\n"
        report += "## Missing Value Matrix"
        report += "\n"
        report += f"![Missing Value Matrix](./{plots_dir}/missing_value_matrix.png)\n"

        report += "\n"
        report += "## Temporal Analyses\n"
        
        toc.append("Temporal Analyses")

        temporal_analyses = self.results.get("temporal_analyses", {})
        for column, analysis in temporal_analyses.items():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"## Temporal Analysis for {column}\n\n"
            for key, value in analysis.items():
                report += f"- **{key}**: {value}\n"
            report += f"![Temporal Gaps Distribution](./{plots_dir}/{column_name}_temporal_gaps_distribution.png)\n"
            report += f"![Weekly Time Series](./{plots_dir}/{column_name}_weekly_time_series.png)\n\n"

        toc.append("Numeric Columns")

        report += "\n"
        report += "## Numeric Columns\n"
        numeric_profiles = self.results.get("numeric_profiles", {})
        for column, profile in numeric_profiles.items():
            #toc.append(f"[{column} Profile](#{column})")
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"### {column}\n"
            stats = profile.get("statistics", {})
            for stat, value in stats.items():
                report += f"- **{stat}**: {value}\n"
            report += f"- **Skewness**: {profile.get('skewness')}\n"
            report += f"- **Kurtosis**: {profile.get('kurtosis')}\n"
            report += f"- **Outliers**: {len(profile.get('outliers', []))} detected\n"
            report += f"- **Average (Nonzero)**: {profile.get('avg_nonzero'):.2f}\n"
            report += f"- **Number of Distinct Values**: {profile.get('distinct_values')}\n"
            report += f"- **Most Common Values**: {profile.get('most_common')}\n"
            report += f"- **Least Common Values**: {profile.get('least_common')}\n"
            report += f"- **Negative Values**: {profile.get('count_negative')}\n"
            report += f"- **Zero Values**: {profile.get('count_zero')}\n"
            report += f"- **Blank Values**: {profile.get('count_blank')}\n"
            report += f"![Histogram for {column}](./{plots_dir}/{column_name}_histogram.png)\n"
            report += f"![KDE Plot for {column}](./{plots_dir}/{column_name}_kde_plot.png)\n"
            report += f"![Box Plot for {column}](./{plots_dir}/{column_name}_boxplot.png)\n"

        toc.append("String Columns")

        report += "\n"
        report += "## String Columns\n"
        string_profiles = self.results.get("string_profiles", {})
        for column, profile in string_profiles.items():
            #toc.append(f"[{column} Profile](#{column})")
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"### {column}\n"
            report += f"- **Distinct Values**: {profile.get('distinct_values')}\n"
            report += f"- **Most Common**: {profile.get('most_common')}\n"
            report += f"- **Least Common**: {profile.get('least_common')}\n"
            lengths = profile.get("string_lengths", {})
            report += f"- **String Lengths**: min: {lengths.get('min')}, max: {lengths.get('max')}, mean: {lengths.get('mean'):.2f}\n"
            report += f"- **Duplicates Count**: {profile.get('duplicates_count')}\n"
            report += f"- **Entropy**: {profile.get('entropy'):.2f}\n"
            report += f"- **Dominance**: {profile.get('dominance'):.2f}%\n"
            special_chars = profile.get("special_character_count", {})
            for char_type, count in special_chars.items():
                report += f"- **{char_type.capitalize()}**: {count}\n"
            suspicious = profile.get("suspicious_data", {})
            if suspicious:
                report += f"- **Suspicious Data**: {suspicious}\n"
            report += f"- **All Uppercase**: {profile.get('all_uppercase_count')}\n"
            report += f"- **All Lowercase**: {profile.get('all_lowercase_count')}\n"
            report += f"- **Special Characters**: {profile.get('special_character_count')}\n"
            report += f"- **Empty Values**: {profile.get('empty_vals')}\n"
            report += f"![Chart for {column} - Top Values](./{plots_dir}/{column_name}_columnchart_top.png)\n"
            report += f"![Chart for {column} - With Other](./{plots_dir}/{column_name}_columnchart_all.png)\n"
            report += f"![Donut Chart for {column} - With Other](./{plots_dir}/{column_name}_donut.png)\n"
        """ 
        toc.append("Row Examples")
        report += "\n"
        report += "## Row Examples\n"
        report += "\n### First 10 Rows\n"
        report += self.df.head(10).to_markdown(index=False) + "\n"

        report += "\n### Last 10 Rows\n"
        report += self.df.tail(10).to_markdown(index=False) + "\n"

        report += "\n### Random 20 Rows\n"
        report += self.df.sample(n=20, random_state=42).to_markdown(index=False) + "\n" 
        """

        toc_md = "\n".join([f"- [{item}](#{item.lower().replace(' ', '-').strip()})" 
                            for item in toc])
        
        report = f"# Table of Contents\n{toc_md}\n\n" + report

        output_file = os.path.join(self.output_dir, output_filename)

        with open(output_file, "w") as file:
            file.write(report)
            file.close()

        return report

    def append_markdown_section(file_path, section_title, content):
        """
        Append a new section to an existing markdown file.
        
        Args:
            file_path (str): Path to the markdown file.
            section_title (str): Title of the new section.
            content (str): Content to append.
        """
        with open(file_path, "a") as file:
            file.write(f"\n\n## {section_title}\n")
            file.write(content)


    def _generate_html_report(self, output_filename):
        # Implement HTML report generation
        """
        Generate an HTML report with a section per column.
        """
        plots_dir = "plots"

        # Start HTML report
        report = """<!DOCTYPE html>
        <html>
        <head>
            <title>Data Profile Report</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0 20px; }
                h1, h2, h3 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f4f4f4; }
                img { max-width: 100%; height: auto; margin: 10px 0; }
                ul { margin: 0; padding: 0; list-style-type: none; }
                li { margin: 5px 0; }
                a { text-decoration: none; color: #0066cc; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
        <h1>Data Profile Report</h1>
        """

        # Metadata
        report += "<h2>Metadata</h2><ul>"
        metadata = self.results.get("metadata", {})
        for key, value in metadata.items():
            report += f"<li><strong>{key}:</strong> {value}</li>"
        report += "</ul>"

        # Missing Value Matrix
        report += "<h2>Missing Value Matrix</h2>"
        report += f"<img src='{plots_dir}/missing_value_matrix.png' alt='Missing Value Matrix'>"

        # Temporal Analyses
        report += "<h2>Temporal Analyses</h2>"
        temporal_analyses = self.results.get("temporal_analyses", {})
        for column, analysis in temporal_analyses.items():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"<h3>Temporal Analysis for {column}</h3><ul>"
            for key, value in analysis.items():
                report += f"<li><strong>{key}:</strong> {value}</li>"
            report += "</ul>"
            report += f"<img src='{plots_dir}/{column_name}_temporal_gaps_distribution.png' alt='Temporal Gaps Distribution'>"
            report += f"<img src='{plots_dir}/{column_name}_weekly_time_series.png' alt='Weekly Time Series'>"

        # Numeric Columns
        report += "<h2>Numeric Columns</h2>"
        numeric_profiles = self.results.get("numeric_profiles", {})
        for column, profile in numeric_profiles.items():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"<h3>{column}</h3><ul>"
            stats = profile.get("statistics", {})
            for stat, value in stats.items():
                report += f"<li><strong>{stat}:</strong> {value}</li>"
            report += f"<li><strong>Skewness:</strong> {profile.get('skewness')}</li>"
            report += f"<li><strong>Kurtosis:</strong> {profile.get('kurtosis')}</li>"
            report += f"<li><strong>Outliers:</strong> {len(profile.get('outliers', []))} detected</li>"
            report += f"<li><strong>Average (Nonzero):</strong> {profile.get('avg_nonzero'):.2f}</li>"
            report += f"<li><strong>Number of Distinct Values:</strong> {profile.get('distinct_values')}</li>"
            report += f"<li><strong>Most Common Values:</strong> {profile.get('most_common')}</li>"
            report += f"<li><strong>Least Common Values:</strong> {profile.get('least_common')}</li>"
            report += f"<li><strong>Negative Values:</strong> {profile.get('count_negative')}</li>"
            report += f"<li><strong>Zero Values:</strong> {profile.get('count_zero')}</li>"
            report += f"<li><strong>Blank Values:</strong> {profile.get('count_blank')}</li>"
            report += "</ul>"
            report += f"<img src='{plots_dir}/{column_name}_histogram.png' alt='Histogram for {column}'>"
            report += f"<img src='{plots_dir}/{column_name}_kde_plot.png' alt='KDE Plot for {column}'>"
            report += f"<img src='{plots_dir}/{column_name}_boxplot.png' alt='Box Plot for {column}'>"

        # String Columns
        report += "<h2>String Columns</h2>"
        string_profiles = self.results.get("string_profiles", {})
        for column, profile in string_profiles.items():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"<h3>{column}</h3><ul>"
            report += f"<li><strong>Distinct Values:</strong> {profile.get('distinct_values')}</li>"
            report += f"<li><strong>Most Common:</strong> {profile.get('most_common')}</li>"
            report += f"<li><strong>Least Common:</strong> {profile.get('least_common')}</li>"
            lengths = profile.get("string_lengths", {})
            report += f"<li><strong>String Lengths:</strong> min: {lengths.get('min')}, max: {lengths.get('max')}, mean: {lengths.get('mean'):.2f}</li>"
            report += f"<li><strong>Duplicates Count:</strong> {profile.get('duplicates_count')}</li>"
            report += f"<li><strong>Entropy:</strong> {profile.get('entropy'):.2f}</li>"
            report += f"<li><strong>Dominance:</strong> {profile.get('dominance'):.2f}%</li>"
            special_chars = profile.get("special_character_count", {})
            for char_type, count in special_chars.items():
                report += f"<li><strong>{char_type.capitalize()}:</strong> {count}</li>"
            suspicious = profile.get("suspicious_data", {})
            if suspicious:
                report += f"<li><strong>Suspicious Data:</strong> {suspicious}</li>"
            report += f"<li><strong>All Uppercase:</strong> {profile.get('all_uppercase_count')}</li>"
            report += f"<li><strong>All Lowercase:</strong> {profile.get('all_lowercase_count')}</li>"
            report += f"<li><strong>Special Characters:</strong> {profile.get('special_character_count')}</li>"
            report += f"<li><strong>Empty Values:</strong> {profile.get('empty_vals')}</li>"
            report += "</ul>"
            report += f"<img src='{plots_dir}/{column_name}_columnchart_top.png' alt='Chart for {column} - Top Values'>"
            report += f"<img src='{plots_dir}/{column_name}_columnchart_all.png' alt='Chart for {column} - With Other'>"
            report += f"<img src='{plots_dir}/{column_name}_donut.png' alt='Donut Chart for {column} - With Other'>"

        # Row Examples
        report += "<h2>Row Examples</h2>"
        report += "<h3>First 10 Rows</h3>"
        report += self.df.head(10).to_html(index=False, border=1)

        report += "<h3>Last 10 Rows</h3>"
        report += self.df.tail(10).to_html(index=False, border=1)

        report += "<h3>Random 20 Rows</h3>"
        report += self.df.sample(n=20, random_state=42).to_html(index=False, border=1)

        # End HTML report
        report += "</body></html>"

        # Write HTML file
        output_file = os.path.join(self.output_dir, output_filename)
        with open(output_file, "w") as file:
            file.write(report)

        return report

    def _generate_csv_report(self, output_filename):
        # Implement CSV report generation
        pass

# Example Usage
if __name__ == "__main__":
    # Sample dataset
    df = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "Bob", "Alice"],
        "Age": [25, 30, 35, 30, 25],
        "JoinDate": ["2022-01-01", "2022-02-15", "2022-03-10", "2022-02-15", "2022-01-01"],
        "Comments": ["#Hello", "@Bob", "Test123", "ZZZZ", "None"]
    })

    profiler = DataProfiler(df, custom_types={"JoinDate": "date"})
    profiler.profile_dataset()
    profiler.generate_report("data_profile.md")
