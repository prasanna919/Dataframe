import pandas as pd
import numpy as np

def clean_data(file_path_or_df, operations):
    """
    Applies a list of structured cleaning operations to a dataframe.
    Accepts a file path or a pandas DataFrame.
    Returns the cleaned DataFrame and a list of operation execution logs.
    """
    if isinstance(file_path_or_df, str):
        from agents.profiler import load_csv
        df, _ = load_csv(file_path_or_df)
    else:
        df = file_path_or_df.copy()
        
    applied_logs = []
    
    for op in operations:
        operation = op.get("operation")
        column = op.get("column")
        
        if operation == "drop_duplicates":
            initial_rows = len(df)
            df = df.drop_duplicates()
            rows_removed = initial_rows - len(df)
            applied_logs.append(f"Dropped duplicate rows. Removed {rows_removed} row(s).")
            
        elif operation == "fill_missing":
            if column in df.columns:
                strategy = op.get("strategy")
                null_count = int(df[column].isnull().sum())
                
                if null_count > 0:
                    if strategy == "median":
                        val = df[column].median()
                    elif strategy == "mean":
                        val = df[column].mean()
                    elif strategy == "mode":
                        val = df[column].mode()[0] if not df[column].mode().empty else ""
                    else:
                        val = strategy
                    
                    df[column] = df[column].fillna(val)
                    applied_logs.append(f"Filled {null_count} missing value(s) in '{column}' using strategy '{strategy}' (value: {val}).")
                else:
                    applied_logs.append(f"Skipped fill_missing for '{column}' (no missing values found).")
                    
        elif operation == "replace_value":
            if column in df.columns:
                old_val = op.get("old")
                new_val = op.get("new")
                
                # Sanitize LLM single/double quotes around string values
                if isinstance(old_val, str) and old_val not in df[column].values:
                    cleaned_old = old_val.strip("'\"")
                    if cleaned_old in df[column].values:
                        old_val = cleaned_old
                if isinstance(new_val, str):
                    new_val = new_val.strip("'\"")
                
                # Count matches
                match_count = int((df[column] == old_val).sum())
                df[column] = df[column].replace(old_val, new_val)
                applied_logs.append(f"Replaced {match_count} occurrence(s) of '{old_val}' with '{new_val}' in '{column}'.")
                
        elif operation == "to_datetime":
            if column in df.columns:
                df[column] = pd.to_datetime(df[column], errors="coerce")
                applied_logs.append(f"Converted '{column}' to datetime objects.")
                
        elif operation == "convert_type":
            if column in df.columns:
                target_type = op.get("type")
                # Clean currency and percentage signs first if column is string (object)
                if target_type in ["float", "int"] and df[column].dtype == "object":
                    df[column] = df[column].astype(str).str.replace(r'[\$\,\€\£\%\s]', '', regex=True)
                    df[column] = df[column].replace('', np.nan)
                
                if target_type == "float":
                    df[column] = pd.to_numeric(df[column], errors="coerce")
                elif target_type == "int":
                    df[column] = pd.to_numeric(df[column], errors="coerce").round().astype("Int64")
                elif target_type == "str":
                    df[column] = df[column].astype(str)
                    
                applied_logs.append(f"Converted column '{column}' to type '{target_type}'.")
                
        elif operation == "drop_column":
            if column in df.columns:
                df = df.drop(columns=[column])
                applied_logs.append(f"Dropped column '{column}'.")

        elif operation == "trim_whitespace":
            # Trim leading/trailing whitespace from a specific column or all string columns
            if column and column in df.columns:
                if df[column].dtype == "object":
                    before = df[column].copy()
                    df[column] = df[column].str.strip()
                    changed = int((before != df[column]).sum())
                    applied_logs.append(f"Trimmed whitespace in '{column}'. Fixed {changed} value(s).")
                else:
                    applied_logs.append(f"Skipped trim_whitespace for '{column}' (not a string column).")
            else:
                # Apply to all object (string) columns
                total_changed = 0
                for col in df.select_dtypes(include=["object"]).columns:
                    before = df[col].copy()
                    df[col] = df[col].str.strip()
                    total_changed += int((before != df[col]).sum())
                applied_logs.append(f"Trimmed whitespace across all string columns. Fixed {total_changed} value(s).")

        elif operation == "standardize_case":
            if column and column in df.columns:
                case_type = op.get("case", "title")  # title | lower | upper
                if df[column].dtype == "object":
                    if case_type == "lower":
                        df[column] = df[column].str.lower()
                    elif case_type == "upper":
                        df[column] = df[column].str.upper()
                    else:
                        df[column] = df[column].str.title()
                    applied_logs.append(f"Standardized case of '{column}' to '{case_type}'.")
                else:
                    applied_logs.append(f"Skipped standardize_case for '{column}' (not a string column).")

    return df, applied_logs