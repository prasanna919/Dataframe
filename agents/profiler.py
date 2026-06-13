import pandas as pd
import numpy as np
import re

def load_csv(file_path):
    """Loads CSV with auto-detection of common encodings."""
    encodings = ["utf-8", "latin-1", "cp1252", "utf-16"]
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df, enc
        except (UnicodeDecodeError, LookupError):
            continue
    # Fallback
    return pd.read_csv(file_path), "utf-8"

def detect_date_like(series):
    """Simple check if a string column might contain dates."""
    if not pd.api.types.is_object_dtype(series):
        return False
    # Drop nulls and take non-empty samples
    samples = series.dropna().astype(str).str.strip()
    samples = samples[samples != ""]
    if len(samples) == 0:
        return False
    
    # Check if samples match common date formats (e.g. YYYY-MM-DD, DD/MM/YYYY, MM-DD-YYYY)
    date_patterns = [
        r"^\d{4}[-/]\d{2}[-/]\d{2}", # 2023-01-01
        r"^\d{2}[-/]\d{2}[-/]\d{4}", # 01/01/2023 or 01-01-2023
    ]
    
    matches = 0
    test_samples = samples.head(10)
    for sample in test_samples:
        if any(re.match(pat, sample) for pat in date_patterns):
            matches += 1
            
    return (matches / len(test_samples)) >= 0.5 if len(test_samples) > 0 else False

def detect_numeric_like(series):
    """Check if a string column should be numeric but contains symbols like $, ,, %."""
    if not pd.api.types.is_object_dtype(series):
        return False
    
    samples = series.dropna().astype(str).str.strip()
    samples = samples[samples != ""]
    if len(samples) == 0:
        return False
        
    numeric_pattern = r"^[\$\€\£]?\s*-?\d+[\.,]?\d*\s*\%?$"
    
    matches = 0
    test_samples = samples.head(10)
    for sample in test_samples:
        if re.match(numeric_pattern, sample):
            matches += 1
            
    return (matches / len(test_samples)) >= 0.5 if len(test_samples) > 0 else False

def profile_csv(file_path):
    """Profiles a CSV file to identify structure, types, missing values, duplicates, and issues."""
    df, encoding = load_csv(file_path)
    
    profile = {
        "file_name": file_path.split("/")[-1].split("\\")[-1],
        "encoding": encoding,
        "rows": len(df),
        "columns": len(df.columns),
        "duplicates": int(df.duplicated().sum()),
        "column_analysis": {}
    }
    
    for col in df.columns:
        series = df[col]
        missing_count = int(series.isnull().sum())
        missing_percentage = round((missing_count / len(df)) * 100, 2) if len(df) > 0 else 0.0
        
        # Get sample values (non-null, unique)
        samples = series.dropna().unique()
        samples_list = [str(x) for x in samples[:5]]
        
        detected_issues = []
        # Check for potential data quality issues
        if missing_count > 0:
            detected_issues.append(f"Has missing values ({missing_count} rows, {missing_percentage}%)")
        
        if detect_date_like(series):
            detected_issues.append("Stored as text but looks like date format")
        
        if detect_numeric_like(series):
            detected_issues.append("Stored as text but looks like numeric (contains currency or percentage symbols)")
            
        profile["column_analysis"][col] = {
            "pandas_dtype": str(series.dtype),
            "missing_values": missing_count,
            "missing_percentage": missing_percentage,
            "unique_values_count": len(samples),
            "sample_values": samples_list,
            "detected_issues": detected_issues
        }
        
    return profile