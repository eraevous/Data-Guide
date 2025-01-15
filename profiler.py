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

    def bar_chart(self, column, output_path, wrap_width=20, top_n=12):
        #print("DEBUG: Column being plotted -", column)
        
        # Compute value counts
        value_counts = self.df[column].value_counts()
        other_count = value_counts.iloc[top_n:].sum() if len(value_counts) > top_n else 0
        
        # Create a dictionary for the top values and append 'Other'
        top_values = value_counts.head(top_n).to_dict()
        if other_count > 0:
            top_values["Other"] = other_count
        
        # Convert to pandas Series for plotting
        top_values_series = pd.Series(top_values)
        #print("DEBUG: Top values for bar chart -", top_values_series)
        
        # Plot bar chart
        ax = top_values_series.plot(kind='bar', color='skyblue')
        ax.set_title(f"Bar Chart for {column}")
        ax.set_xlabel(self._wrap_text(column, wrap_width))
        labels = [label.get_text() for label in ax.get_xticklabels()]
        wrapped_labels = [self._wrap_text(label, wrap_width) for label in labels]
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(wrapped_labels, rotation=90, ha="center")  # Adjust rotation and alignment if needed
        ax.set_ylabel("Count")
        # Increase bottom margin
        plt.subplots_adjust(bottom=0.40, top = 0.90)  # Adjust the bottom margin
        # Save the plot
        plt.savefig(output_path)
        plt.close()
        #print(f"DEBUG: Bar chart saved at {output_path}")

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
            r"\d{6,}",  # Sequential numbers, 6 or more digits
            r"(?i)test",  # Case-insensitive 'test'
            r"(?i)none"  # Case-insensitive 'none'
        ]
        empty_patterns = ['None', 'nan', '']
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
            "statistics": {k: round(v, 2) for k, v in stats.items()},
            "skewness": round(self.col_data.skew(), 2),
            "kurtosis": round(self.col_data.kurt(), 2),
            "most_common": self.col_data.value_counts().head(4).round(2).to_dict(),
            "least_common": self.col_data.value_counts().tail(4).round(2).to_dict(),
            "outliers": outliers.tolist(),
            "avg_nonzero": self.col_data[self.col_data != 0].mean(),
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
        coll = pd.to_numeric(df[column].replace('[\$,]', '', regex=True).replace('-', np.nan), errors='coerce').astype(float)
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
            "duplicates": self.df.duplicated().sum()
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
            elif dtype in ['object', 'category', 'str']:
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
            profiler_plotter.bar_chart(column, f"{plots_dir}/{column_name}_barchart.png")

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
        if format == 'markdown':
            return self._generate_markdown_report(output_filename)
        elif format == 'html':
            return self._generate_html_report()
        elif format == 'csv':
            return self._generate_csv_report()
        else:
            raise ValueError("Unsupported format: {}".format(format))

    def _generate_markdown_report(self, output_filename):
        """
        Generate a Markdown report with a section per column.
        """
        plots_dir = "plots"

        report = f"# Data Profile Report\n\n"
        metadata = self.results.get("metadata", {})
        report += "## Metadata\n"
        for key, value in metadata.items():
            report += f"- **{key}**: {value}\n"

        # Missing value matrix
        report += "\n## Missing Value Matrix\n"
        report += f"![Missing Value Matrix](./{plots_dir}/missing_value_matrix.png)\n"

        report += "\n## Temporal Analyses\n"
        
        temporal_analyses = self.results.get("temporal_analyses", {})
        for column, analysis in temporal_analyses.items():
            column_name = re.sub(r'[^\w\-_]', '_', column)
            column_name = re.sub(r'__+', '_', column_name)
            report += f"## Temporal Analysis for {column}\n\n"
            for key, value in analysis.items():
                report += f"- **{key}**: {value}\n"
            report += f"![Temporal Gaps Distribution](./{plots_dir}/{column_name}_temporal_gaps_distribution.png)\n"
            report += f"![Weekly Time Series](./{plots_dir}/{column_name}_weekly_time_series.png)\n\n"

        report += "\n## Numeric Columns\n"
        numeric_profiles = self.results.get("numeric_profiles", {})
        for column, profile in numeric_profiles.items():
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
            report += f"![Histogram for {column}](./{plots_dir}/{column_name}_histogram.png)\n"
            report += f"![KDE Plot for {column}](./{plots_dir}/{column_name}_kde_plot.png)\n"
            report += f"![Box Plot for {column}](./{plots_dir}/{column_name}_boxplot.png)\n"

        report += "\n## String Columns\n"
        string_profiles = self.results.get("string_profiles", {})
        for column, profile in string_profiles.items():
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
            report += f"- **Empty Values**: {profile.get('empty_vals')}\n"
            report += f"![Bar Chart for {column}](./{plots_dir}/{column_name}_barchart.png)\n"

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


    def _generate_html_report(self):
        # Implement HTML report generation
        pass

    def _generate_csv_report(self):
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
