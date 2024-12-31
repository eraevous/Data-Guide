import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import missingno as msno
from scipy.stats import entropy

class DataProfiler:
    def __init__(self, dataframe, custom_types=None, output_dir="."):
        self.df = dataframe
        self.output_dir = output_dir
        self.custom_types = custom_types or {col: str(self.df[col].dtype) for col in self.df.columns}
        self.results = {}
        self._preprocess_data()

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
                self.df = self.convert_unix_timestamps(self.df, column, errors='coerce')
            elif dtype == 'date':
                self.df[column] = pd.to_datetime(self.df[column], errors='coerce')

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
            df[column] = pd.to_datetime(df[column] / factor, unit='s', errors='coerce')
            print(f"Successfully converted {column} to datetime.")
        except Exception as e:
            print(f"Error converting column {column}: {e}")
        return df

    def _parse_phone_number(self, value):
        """
        Placeholder for phone number parsing logic.
        """
        return value

    def profile_column_as_string(self, column):
        """
        Profiles string columns, including entropy, dominance, and special character analysis.
        """
        col_data = self.df[column]
        suspicious_patterns = [
            r"Z{2,}",  # Two or more Z's in a row
            r"9{2,}",  # Two or more 9's in a row
            r"\d{6,}",  # Sequential numbers, 6 or more digits
            r"(?i)test",  # Case-insensitive 'test'
            r"(?i)none"  # Case-insensitive 'none'
        ]
        suspicious_data = self._identify_invalid_patterns_regex(col_data, suspicious_patterns)
        special_characters = self._count_special_characters(col_data)
        entropy_value = entropy(col_data.value_counts(normalize=True), base=2)
        top_dominance = col_data.value_counts(normalize=True).head(1).values[0] * 100 if not col_data.empty else 0

        return {
            "distinct_values": col_data.nunique(),
            "string_lengths": {
                "min": col_data.str.len().min(),
                "max": col_data.str.len().max(),
                "mean": col_data.str.len().mean()
            },
            "most_common": col_data.value_counts().head(4).to_dict(),
            "least_common": col_data.value_counts().tail(4).to_dict(),
            "duplicates_count": col_data.duplicated().sum(),
            "all_uppercase_count": col_data.str.isupper().sum(),
            "all_lowercase_count": col_data.str.islower().sum(),
            "empty_vals" : col_data.isna().sum() + col_data.str.strip().isin(empty_patterns).sum(),
            "entropy": entropy_value,
            "dominance": top_dominance,
            "special_character_count": special_characters,
            "suspicious_data": suspicious_data
        }

    def _count_special_characters(self, col_data):
        """
        Count occurrences of special characters like hashtags and mentions.
        """
        special_chars = {
            "hashtags": col_data.str.count(r"#").sum(),
            "mentions": col_data.str.count(r"@").sum()
        }
        return special_chars

    def profile_column_as_numeric(self, column):
        """
        Profiles numeric columns, including additional percentiles.
        """
        col_data = self.df[column]
        stats = col_data.describe(percentiles=[0.01, 0.05, 0.33, 0.5, 0.66, 0.95, 0.99]).to_dict()
        outliers = self.detect_outliers(col_data)
        return {
            "statistics": stats,
            "skewness": col_data.skew(),
            "kurtosis": col_data.kurt(),
            "most_common": col_data.value_counts().head(4).round(2).to_dict(),
            "least_common": col_data.value_counts().tail(4).round(2).to_dict(),
            "outliers": outliers.tolist()
        }
      
    def profile_phone_numbers(df, phone_column):
        valid_count = 0
        invalid_count = 0
        for number in df[phone_column]:
            try:
                parsed = phonenumbers.parse(number, "US")
                if phonenumbers.is_valid_number(parsed):
                    valid_count += 1
            except:
                invalid_count += 1
        return {"valid_phone_numbers": valid_count, "invalid_phone_numbers": invalid_count}

    def profile_temporal_data(df):
        """
        Profiles temporal data, providing insights into time coverage, gaps, and trends.
        
        Args:
            df (pd.DataFrame): The dataset to profile.
        
        Returns:
            dict: A dictionary containing temporal analysis results.
        """
        temporal_columns = [col for col, dtype in self.custom_types.items() if dtype == 'date']
        temporal_analysis = {}
        for column in temporal_columns:
            col_data = df[column]
            temporal_analysis[column] = {
                "earliest": col_data.min(),
                "latest": col_data.max(),
                "time_span": col_data.max() - col_data.min(),
                "temporal_gaps": col_data.diff().describe().to_dict(),
                "day_of_week_distribution": col_data.dt.dayofweek.value_counts().to_dict(),
                "monthly_trends": col_data.dt.month.value_counts().sort_index().to_dict(),
                "day_trends": col_data.value_counts().sort_index().to_dict()
            }
        return temporal_analysis

    def detect_outliers(self, series, method='iqr'):
        """
        Detect outliers using IQR or Z-score.
        """
        if method == 'iqr':
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            return series[(series < (q1 - 1.5 * iqr)) | (series > (q3 + 1.5 * iqr))]
        elif method == 'zscore':
            z_scores = (series - series.mean()) / series.std()
            return series[(z_scores < -3) | (z_scores > 3)]

    def _identify_invalid_patterns_regex(self, col_data, patterns):
        """
        Identify suspicious patterns in a column using regex.
        """
        suspicious_counts = {}
        for pattern in patterns:
            matches = col_data.str.contains(pattern, na=False, regex=True)
            suspicious_counts[pattern] = matches.sum()
        return suspicious_counts

    # Bar Chart: Categorical Variable
    def bar_chart(data, column, output_path, top_n=10):

        value_counts = data[column].value_counts()
        top_values = value_counts.head(top_n)
        
        if len(value_counts) > top_n:
            other_count = value_counts.iloc[top_n:].sum()
            top_values["Other"] = other_count
            
        top_values.plot(kind='bar', color='skyblue')
        plt.title(f"Bar Chart for {column}")
        plt.xlabel(column)
        plt.savefig(output_path)
        plt.close()
    
    # Histogram: Numerical Variable
    def histogram(self, column, output_path):
        self.df[column].plot(kind="hist", bins=20, color="lightgreen", edgecolor="black")
        plt.title(f"Histogram for {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.savefig(output_path)
        plt.close()

    def kde_plot(self, column, output_path):
        sns.kdeplot(self.df[column], shade=True, color="blue")
        plt.title(f"KDE Plot for {column}")
        plt.xlabel(column)
        plt.ylabel("Density")
        plt.savefig(output_path)
        plt.close()
      
    # Box Plot: Outliers and Spread
    def box_plot(self, column, output_path):
        sns.boxplot(y=self.df[column], color="coral")
        plt.title(f"Box Plot for {column}")
        plt.ylabel(column)
        plt.savefig(output_path)
        plt.close()
    
    # Missing Value Matrix
    def missing_value_matrix(data):
        msno.matrix(self.df)
        plt.title("Missing Value Matrix")
        plt.savefig(output_path)
        plt.close()		

    def profile_dataset(self):
        """
        Generate dataset-level profiles.
        """
        metadata = {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "missing_values": self.df.isnull().sum().sum(),
            "duplicates": self.df.duplicated().sum()
        }
        temporal_analyses = self.profile_temporal_data(self.df)

        phone_profiles = {
            col: self.profile_phone_numbers(self.df, col)
            for col, dtype in self.custom_types.items() if dtype == 'phone_number'
        }

        string_profiles = {
            col: self.profile_column_as_string(col)
            for col, dtype in self.custom_types.items() if dtype in ['object', 'category', 'str']
        }

        numeric_profiles = {
            col: self.profile_column_as_numeric(col)
            for col, dtype in self.custom_types.items() if dtype in ['int64', 'float64', 'numeric']
        }

        # Generate missing value matrix
        self.missing_value_matrix(f"{self.output_dir}/plots/missing_value_matrix.png")

        # Generate column visuals
        for column in string_profiles.keys():
            self.bar_chart(self.df, column, f"Bar Chart for {column}")
            plt.savefig(f"{self.output_dir}/plots/{column}_barchart.png")
            plt.close()

        for column in numeric_profiles.keys():
            self.histogram(column, f"{self.output_dir}/plots/{column}_histogram.png")
            self.kde_plot(column, f"{self.output_dir}/plots/{column}_kde_plot.png")
            self.box_plot(column, f"{self.output_dir}/plots/{column}_boxplot.png")

        self.results['temportal_analyses'] = temporal_analyses
        self.results['metadata'] = metadata
        self.results['string_profiles'] = string_profiles
        self.results['numeric_profiles'] = numeric_profiles

    def generate_report(self, format='markdown', output_path="./data_profile.md"):
        if format == 'markdown':
            return self._generate_markdown_report(output_path)
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
        report = "# Data Profile Report\n\n"
        metadata = self.results.get("metadata", {})
        report += "## Metadata\n"
        for key, value in metadata.items():
            report += f"- **{key}**: {value}\n"

        # Missing value matrix
        report += "\n## Missing Value Matrix\n"
        report += "![Missing Value Matrix](plots/missing_value_matrix.png)\n"

        report += "\n## Temporal Analysis\n"
        for column, analysis in self.results["temporal_analyses"].items():
            report += f"### {column}\n"
            for key, value in analysis.items():
                report += f"- **{key}**: {value}\n"

        report += "\n## Numeric Columns\n"
        numeric_profiles = self.results.get("numeric_profiles", {})
        for column, profile in numeric_profiles.items():
            report += f"### {column}\n"
            stats = profile.get("statistics", {})
            for stat, value in stats.items():
                report += f"- **{stat}**: {value}\n"
            report += f"- **Skewness**: {profile.get('skewness')}\n"
            report += f"- **Kurtosis**: {profile.get('kurtosis')}\n"
            report += f"- **Outliers**: {len(profile.get('outliers', []))} detected\n"
            report += f"- ![Histogram](plots/{column}_histogram.png)\n"
            report += f"- ![KDE Plot](plots/{column}_kde_plot.png)\n"
            report += f"- ![Box Plot](plots/{column}_boxplot.png)\n"

        report += "\n## String Columns\n"
        string_profiles = self.results.get("string_profiles", {})
        for column, profile in string_profiles.items():
            report += f"### {column}\n"
            report += f"- **Distinct Values**: {profile.get('distinct_values')}\n"
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
            report += f"- **Distinct Values**: {profile.get('distinct_values')}\n"
            report += f"- ![Bar Chart](plots/{column}_barchart.png)\n"

        output_file = os.path.join(self.output_dir, output_filename)
        with open(output_file, "w") as file:
            file.write(report)

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
