import pandas as pd
from datetime import datetime

class DataTransform:
    @staticmethod
    def validate_columns(df, columns):
        """
        Validate that the specified columns exist in the DataFrame.

        Args:
            df (pd.DataFrame): The input dataframe.
            columns (list): List of columns to validate.

        Raises:
            ValueError: If any column is missing from the DataFrame.
        """
        missing = [col for col in columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")

    @staticmethod
    def handle_nulls(df, strategy="drop", fill_value=None, column_strategies=None):
        """
        Handle missing values in the dataset with optional column-specific strategies.

        Args:
            df (pd.DataFrame): The input dataframe.
            strategy (str): Default strategy: "drop" or "fill".
            fill_value: Default value to fill nulls if strategy is "fill".
            column_strategies (dict): Column-specific strategies (e.g., {"col1": "median", "col2": "mode"}).

        Returns:
            pd.DataFrame: DataFrame with nulls handled.
        """
        if column_strategies:
            for col, strat in column_strategies.items():
                DataTransform.validate_columns(df, [col])
                if strat == "median":
                    df[col] = df[col].fillna(df[col].median())
                elif strat == "mode":
                    df[col] = df[col].fillna(df[col].mode()[0])
        else:
            if strategy == "drop":
                return df.dropna()
            elif strategy == "fill":
                return df.fillna(fill_value)
        return df

    @staticmethod
    def convert_dates(df, date_columns):
        """
        Convert specified columns to datetime format.

        Args:
            df (pd.DataFrame): The input dataframe.
            date_columns (list): List of columns to convert.

        Returns:
            pd.DataFrame: DataFrame with date columns converted.
        """
        DataTransform.validate_columns(df, date_columns)
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    @staticmethod
    def anonymize_columns(df, columns):
        """
        Anonymize specified columns by replacing values with hashes.

        Args:
            df (pd.DataFrame): The input dataframe.
            columns (list): List of columns to anonymize.

        Returns:
            pd.DataFrame: DataFrame with anonymized columns.
        """
        DataTransform.validate_columns(df, columns)
        for col in columns:
            df[col] = df[col].apply(lambda x: hash(x) if pd.notnull(x) else x)
        return df

    @staticmethod
    def join_datasets(df1, df2, on_key, how="inner", suffixes=("_left", "_right")):
        """
        Join two datasets on a specified key with default suffixes for overlapping columns.

        Args:
            df1 (pd.DataFrame): Left dataframe.
            df2 (pd.DataFrame): Right dataframe.
            on_key (str): Column name to join on.
            how (str): Type of join ("inner", "left", etc.).
            suffixes (tuple): Suffixes for overlapping columns.

        Returns:
            pd.DataFrame: Joined dataframe.
        """
        return df1.merge(df2, on=on_key, how=how, suffixes=suffixes)

    @staticmethod
    def handle_nulls_with_log(df, strategy="drop", fill_value=None, log=None):
        """
        Handle nulls and track changes in a log.

        Args:
            df (pd.DataFrame): The input dataframe.
            strategy (str): Strategy for handling nulls.
            fill_value: Value to fill nulls if strategy is "fill".
            log (list): Optional log to store transformation details.

        Returns:
            pd.DataFrame: Transformed DataFrame.
        """
        original_shape = df.shape
        df = DataTransform.handle_nulls(df, strategy=strategy, fill_value=fill_value)
        if log is not None:
            log.append(f"Null handling: {original_shape[0] - df.shape[0]} rows affected.")
        return df

# Example Usage
if __name__ == "__main__":
    # Example datasets
    df1 = pd.DataFrame({
        "ID": [1, 2, 3],
        "Name": ["Alice", "Bob", "Charlie"],
        "JoinDate": ["2022-01-01", "2022-02-15", "2022-03-10"]
    })

    df2 = pd.DataFrame({
        "ID": [2, 3, 4],
        "Amount": [100, 150, 200]
    })

    # Handle nulls with column-specific strategies
    df1 = DataTransform.handle_nulls(df1, column_strategies={"Name": "mode"})

    # Convert dates
    df1 = DataTransform.convert_dates(df1, ["JoinDate"])

    # Anonymize columns
    df1 = DataTransform.anonymize_columns(df1, ["Name"])

    # Join datasets
    merged_df = DataTransform.join_datasets(df1, df2, on_key="ID", how="inner")
    print(merged_df)
