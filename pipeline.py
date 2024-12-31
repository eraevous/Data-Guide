import pandas as pd
from data_profiler import DataProfiler
from data_transform import DataTransform

if __name__ == "__main__":
    # Load dataset
    df_raw = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", "Bob", "Alice"],
        "Age": [25, 30, 35, 30, 25],
        "JoinDate": ["2022-01-01", "2022-02-15", "2022-03-10", "2022-02-15", "2022-01-01"]
    })

    # Step 1: Profile raw data
    print("Profiling raw data...")
    profiler = DataProfiler(df_raw, custom_types={"JoinDate": "date"})
    profiler.profile_dataset()
    profiler.generate_report("raw_data_profile.md")

    # Step 2: Transform data
    print("Transforming data...")
    df_cleaned = DataTransform.handle_nulls(df_raw, strategy="fill", fill_value="Unknown")
    df_cleaned = DataTransform.convert_dates(df_cleaned, ["JoinDate"])

    # Step 3: Profile transformed data
    print("Profiling transformed data...")
    transformed_profiler = DataProfiler(df_cleaned)
    transformed_profiler.profile_dataset()
    transformed_profiler.generate_report("transformed_data_profile.md")

    print("Pipeline execution complete.")