import pandas as pd
import numpy as np
from scipy.stats import entropy
import matplotlib.pyplot as plt
import seaborn as sns

class DataProfiler:
    """
    A modular data profiling class to generate comprehensive insights into datasets.
    
    Attributes:
        df (pd.DataFrame): The dataset to be profiled.
        results (dict): A dictionary to store profiling results.
    """
    
    def __init__(self, dataframe, custom_types=None):
        """
        Initialize the profiler with the given dataset and custom data type mappings.
        
        Args:
            dataframe (pd.DataFrame): The dataset to profile.
            custom_types (dict): Optional dictionary to specify custom data type mappings.
        """
        self.df = dataframe
        self.results = {}
        self.custom_types = custom_types if custom_types else {}
        self._preprocess_data()

    def _preprocess_data(self):
        """
        Preprocess the data by applying custom data type mappings and transformations.
        """
        for column, dtype in self.custom_types.items():
            if dtype == 'phone_number':
                self.df[column] = self.df[column].apply(self._parse_phone_number)
            elif dtype == 'id':
                self.df[column] = self.df[column].astype(str)
            elif dtype == 'date':
                self.df[column] = pd.to_datetime(self.df[column], errors='coerce')
            # Add more custom types as needed
    
    def _parse_phone_number(self, value):
        """
        Parse and standardize phone numbers.
        
        Args:
            value (str): The phone number to parse.
        
        Returns:
            str: The standardized phone number.
        """
        # Implement phone number parsing logic here
        return value  # Placeholder implementation   

    def profile_dataset(self):
        """
        Profiles the entire dataset, including high-level metadata and duplicate analysis.
        
        Stores the results in the `results` attribute under the key `dataset_metadata`.
        """
        try:
            self.results["dataset_metadata"] = profile_dataset(self.df)
        except Exception as e:
            self.results["dataset_metadata"] = {"error": str(e)}
    
    def profile_columns(self):
        """
        Profiles each column in the dataset based on its data type.
        
        Stores the results in the `results` attribute under the key `columns`.
        """
        self.results["columns"] = {}
        for column in self.df.columns:
            try:
                if self.df[column].dtype == "object":
                    self.results["columns"][column] = profile_column_as_string(self.df, column)
                else:
                    self.results["columns"][column] = profile_column_as_numeric(self.df, column)
            except Exception as e:
                self.results["columns"][column] = {"error": str(e)}
    
    def generate_report(self, format='markdown'):
        """
        Generates a report in the specified format (markdown, HTML, or CSV).
        
        Args:
            format (str): The format of the report (default is 'markdown').
        
        Returns:
            str: The generated report.
        """
        if format == 'markdown':
            return self._generate_markdown_report()
        elif format == 'html':
            return self._generate_html_report()
        elif format == 'csv':
            return self._generate_csv_report()
        else:
            raise ValueError("Unsupported format: {}".format(format))
    
    def _generate_markdown_report(self):
        # Implement markdown report generation
        report = "# Data Profile Report\n\n"
        report += "## Dataset Metadata\n"
        for key, value in self.results["dataset_metadata"]["metadata"].items():
            report += f"- **{key}**: {value}\n"
        report += "\n## Duplicate Analysis\n"
        report += f"- **Duplicates**: {self.results['dataset_metadata']['duplicates']}\n"
        report += "\n## Temporal Analysis\n"
        for column, analysis in self.results["dataset_metadata"]["temporal_analysis"].items():
            report += f"### {column}\n"
            for key, value in analysis.items():
                report += f"- **{key}**: {value}\n"
        report += "\n## Column Profiles\n"
        for column, profile in self.results["columns"].items():
            report += f"### {column}\n"
            for key, value in profile.items():
                if key == "string_lengths":
                    report += f"- **{key}**: min: {int(value['min'])}, max: {int(value['max'])}, mean: {value['mean']:.2f}\n"
                else: 
                    report += f"- **{key}**: {value}\n"
        return report

    def _generate_html_report(self):
        # Implement HTML report generation
        pass

    def _generate_csv_report(self):
        # Implement CSV report generation
        pass

def profile_dataset(df):
    """
    Profiles the entire dataset, providing high-level metadata and duplicate analysis.
    
    Args:
        df (pd.DataFrame): The dataset to profile.
    
    Returns:
        dict: A dictionary containing dataset metadata and duplicate analysis results.
    """
    metadata = {
        "row_count": df.shape[0],
        "column_count": df.shape[1],
        "column_names": df.columns.tolist(),
        "column_types": df.dtypes.to_dict()
    }
    duplicates = df.duplicated().sum()
    temporal_data = profile_temporal_data(df)  # Call temporal profiling function
    return {"metadata": metadata, "duplicates": duplicates, "temporal_analysis": temporal_data}

def count_empty_values(series):
    empty_vals = (series.isna().sum() + series.isnan().sum() + (series == '').sum() + 
    (series.str.strip() == '').sum() + (series.str.strip() == 'None').sum() + (series.str.strip() == 'nan').sum() 
    )
    return empty_vals

def profile_column_as_string(df, column):
    """
    Profiles a column as a string, including statistics on distinct values, string lengths,
    most/least common values, count of duplicates, count of all upper and all lower cases,
    and detection of suspicious data patterns.
    
    Args:
        df (pd.DataFrame): The dataset containing the column.
        column (str): The name of the column to profile.
    
    Returns:
        dict: A dictionary containing string-based profiling statistics.
    """
    col_data = df[column]
    distinct_values = col_data.nunique()
    string_lengths = col_data.str.len()
    most_common = col_data.value_counts().head(10).to_dict()
    least_common = col_data.value_counts().tail(10).to_dict()
    duplicates_count = col_data.duplicated().sum()
    all_uppercase_count = col_data.str.isupper().sum()
    all_lowercase_count = col_data.str.islower().sum()
    
    # Suspicious data patterns
    suspicious_patterns = ["ZZZZ", "9999", "-1", "test", "none", "123456789"]
    suspicious_data = identify_invalid_patterns(df, column, suspicious_patterns)

    # Count of blanks
    empty_patterns = ['None', 'nan', '']
    empty_vals = col_data.isna().sum() + col_data.str.strip().isin(empty_patterns).sum()
    
    return {
        "distinct_values": distinct_values,
        "string_lengths": {
            "min": string_lengths.min(),
            "max": string_lengths.max(),
            "mean": string_lengths.mean()
        },
        "most_common": most_common,
        "least_common": least_common,
        "duplicates_count": duplicates_count,
        "all_uppercase_count": all_uppercase_count,
        "all_lowercase_count": all_lowercase_count,
        "suspicious_data": suspicious_data,
        "empty_vals": empty_vals
    }

def profile_column_as_numeric(df, column):
    """
    Profiles a column as a numeric, including statistics on distribution and common values.
    
    Args:
        df (pd.DataFrame): The dataset containing the column.
        column (str): The name of the column to profile.
    
    Returns:
        dict: A dictionary containing numeric-based profiling statistics.
    """
    col_data = df[column]
    stats = col_data.describe().to_dict()
    most_common = col_data.value_counts().head(10).to_dict()
    least_common = col_data.value_counts().tail(10).to_dict()
    return {
        "statistics": stats,
        "most_common": most_common,
        "least_common": least_common
    }

def profile_temporal_data(df):
    """
    Profiles temporal data, providing insights into time coverage, gaps, and trends.
    
    Args:
        df (pd.DataFrame): The dataset to profile.
    
    Returns:
        dict: A dictionary containing temporal analysis results.
    """
    temporal_columns = df.select_dtypes(include=['datetime']).columns
    temporal_analysis = {}
    for column in temporal_columns:
        col_data = df[column]
        temporal_analysis[column] = {
            "earliest": col_data.min(),
            "latest": col_data.max(),
            "time_span": col_data.max() - col_data.min(),
            "temporal_gaps": col_data.diff().describe().to_dict(),
            "trends": col_data.value_counts().sort_index().to_dict()
        }
    return temporal_analysis

def identify_invalid_patterns(df, column, patterns):
    """
    Identifies invalid or suspicious patterns in a column.
    
    Args:
        df (pd.DataFrame): The dataset containing the column.
        column (str): The name of the column to profile.
        patterns (list): A list of patterns to check for.
    
    Returns:
        dict: A dictionary containing the counts of each suspicious pattern found.
    """
    col_data = df[column]
    invalid_values = col_data[col_data.isin(patterns)]
    return invalid_values.value_counts().to_dict()

if __name__ == "__main__":
    # Example dataset
    data = pd.DataFrame({
        "A": [1, 2, 2, 4, 5],
        "B": [1, 2, 2, 4, 5],
        "C": ["NA", "hello", "world", "hello", "hello"],
        "D": pd.date_range(start="2021-01-01", periods=5),
    })

    # Custom data type mappings
    custom_types = {
        "C": "string",
        "D": "date"
    }

    # Initialize profiler
    profiler = DataProfiler(data, custom_types)

    # Profile dataset and columns
    profiler.profile_dataset()
    profiler.profile_columns()

    # Generate Markdown report
    markdown_report = profiler.generate_report(format="markdown")
    print(markdown_report)