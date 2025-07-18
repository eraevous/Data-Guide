import pandas as pd
import seaborn as sns
from data_profiler import DataProfiler
from data_transform import DataTransform

if __name__ == "__main__":
    # Load sample dataset
    df_raw = sns.load_dataset("titanic")

    # Step 1: Profile the raw data
    print("Profiling raw data...")
    raw_profiler = DataProfiler(df_raw)
    raw_profiler.profile_dataset()
    raw_profiler.generate_markdown_report("raw_data_profile.md")

    # Step 2: Clean and transform data
    print("Transforming data...")
    df_cleaned = DataTransform.handle_nulls(df_raw, strategy="fill", fill_value="Unknown")
    df_cleaned = DataTransform.convert_dates(df_cleaned, ["age", "fare"])  # Replace with actual date columns if available

    # Example transformation: Add external data
    external_data = pd.DataFrame({
        "ID": [1, 2, 3],
        "Additional_Info": ["Info1", "Info2", "Info3"]
    })
    df_cleaned["ID"] = range(1, len(df_cleaned) + 1)  # Simulate ID column for join
    df_transformed = DataTransform.join_datasets(df_cleaned, external_data, on_key="ID", how="left")

    # Step 3: Profile the transformed data
    print("Profiling transformed data...")
    transformed_profiler = DataProfiler(df_transformed)
    transformed_profiler.profile_dataset()
    transformed_profiler.generate_markdown_report("transformed_data_profile.md")

    # Final output
    print("Pipeline execution complete. Reports generated.")
