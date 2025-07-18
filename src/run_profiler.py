import pandas as pd
from data_profiler import DataProfiler  # Ensure this matches the actual file name and class name
import os

# define dataset path and output directory

data_path = "C:/Users/Admin/Documents/GitHub/Data-Guide/data_pipeline/pull_dec_29"
output_dir = "C:/Users/Admin/Documents/GitHub/Data-Guide/data_pipeline/pull_dec_29/profiling_output"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# defined datasets
datasets = ["aged_ar_report.csv", "statement_submission_report.csv", "integrated_payments_report.csv"] 

# Load the CSV file into a DataFrame
for d in datasets:

    df = pd.read_csv(os.path.join(data_path, d))

    # Initialize the DataProfiler with the DataFrame
    profiler = DataProfiler(df)

    # Profile the dataset and columns
    profiler.profile_dataset()
    profiler.profile_columns()

    markdown_report = profiler.generate_report(format="markdown")

    # Generate and print the Markdown report
    with open(os.path.join(output_dir, f"{d}_profiling.md"), "w") as f:
        f.write(markdown_report)

# Optionally, generate and print the HTML report
# html_report = profiler.generate_report(format="html")
# print(html_report)

# Optionally, generate and print the CSV report
# csv_report = profiler.generate_report(format="csv")
# print(csv_report)