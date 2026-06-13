import pandas as pd

def get_csv_stats(file_path):

    df = pd.read_csv(file_path)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns)
    }