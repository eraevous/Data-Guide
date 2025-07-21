import os
import sys
import pandas as pd

from data_profiler import DataProfiler
from data_transform import DataTransform
from data_pipeline.bivariate_profiler import BivariateProfiler
from data_pipeline.config import (
    get_csv_paths,
    CUSTOM_TYPES,
    INPUT_DIR,
    OUTPUT_DIR,
)

def load_csv_files(file_paths):
    """Load multiple CSV files into a dictionary keyed by filename."""
    dataframes = {}
    for file_path in file_paths:
        df_name = os.path.basename(file_path).replace(".csv", "")
        dataframes[df_name] = pd.read_csv(file_path)
    return dataframes

def save_report(report, output_dir, file_name):
    with open(os.path.join(output_dir, file_name), "w") as f:
        f.write(report)

if __name__ == "__main__":
    # Define CSV files, custom types, and output directory

    if len(sys.argv) < 2:
        print("Usage: main.py <input_dif> (optional) <output_dir> (optional)")
        sys.exit(1)

    input_dir = sys.argv[1] if len(sys.argv) > 1 else INPUT_DIR
    output_dir = sys.argv[2] if len(sys.argv) > 2 else OUTPUT_DIR

    csv_files = get_csv_paths(input_dir)
    custom_types = CUSTOM_TYPES

    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load datasets
    dataframes = {dataset: pd.read_csv(file_path) for dataset, file_path in csv_files.items()}

    for df_name, df in dataframes.items():
        print(f"Processing {df_name}...")

        print(df.head())

        # Step 1: Profile raw data
        print("Profiling raw data...")
        profiler = DataProfiler(
            df,
            custom_types=custom_types.get(df_name, {}),
            output_dir=f"{output_dir}/{df_name}/",
        )
        profiler.profile_dataset()
        raw_report = profiler.generate_report("markdown", f"{df_name} raw data.md")

        # Bivariate analysis
        bivariate = BivariateProfiler(df, output_dir=f"{output_dir}/{df_name}/bivariate")
        bivariate.correlation_analysis()

        # # Step 2: Transform data
        # print("Transforming data...")
        # df_cleaned = DataTransform.handle_nulls(df, strategy="fill", fill_value="Unknown")
        # date_columns = [col for col, dtype in custom_types.get(df_name, {}).items() if dtype == "date"]
        # df_cleaned = DataTransform.convert_dates(df_cleaned, date_columns)

        # # Step 3: Profile transformed data
        # print("Profiling transformed data...")
        # transformed_profiler = DataProfiler(df_cleaned)
        # transformed_profiler.profile_dataset()
        # transformed_report = transformed_profiler.generate_report("markdown", f"{df_name} transformed data")
        # save_report(transformed_report, output_dir, f"{df_name}_transformed_data_profile.md")

    print("Pipeline execution complete.")
