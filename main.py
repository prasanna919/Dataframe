import os
import pandas as pd
import argparse
from agents.profiler import profile_csv
from agents.recommender import get_cleaning_suggestions
from agents.cleaner import clean_data
from tools.mcp_tool import get_csv_stats

def print_header(title):
    print("\n" + "=" * 60)
    print(f" {title.upper()} ".center(60, "="))
    print("=" * 60)

def safe_input(prompt, default=""):
    try:
        val = input(prompt)
        return val
    except EOFError:
        return default

def main():
    parser = argparse.ArgumentParser(description="CSV Clean Dataframe Agent")
    parser.add_argument("--file", help="Path to the messy CSV file")
    parser.add_argument("--yes", action="store_true", help="Auto-approve all recommended cleaning steps")
    args = parser.parse_args()

    print_header("CSV Clean Dataframe Agent")
    
    # 1. Ask for file path
    default_path = "samples/employees.csv"
    if args.file:
        file_path = args.file
    else:
        file_path = safe_input(f"Enter path to messy CSV file [default: {default_path}]: ", default="").strip()
        if not file_path:
            file_path = default_path
        
    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return
        
    # Get stats from MCP tool
    stats = get_csv_stats(file_path)
    print("\n[Stats Overview]")
    print(f"Columns: {', '.join(stats['column_names'])}")
    print(f"Total Rows: {stats['rows']} | Total Columns: {stats['columns']}")
    
    # STEP 1: Profile
    print("\nProfiling dataset...")
    profile = profile_csv(file_path)
    
    print_header("CSV Profile Results")
    print(f"File Name:  {profile['file_name']}")
    print(f"Encoding:   {profile['encoding']}")
    print(f"Rows:       {profile['rows']}")
    print(f"Columns:    {profile['columns']}")
    print(f"Duplicates: {profile['duplicates']}")
    
    print("\nColumn breakdown:")
    for col, analysis in profile["column_analysis"].items():
        issues_str = f" | Issues: {', '.join(analysis['detected_issues'])}" if analysis['detected_issues'] else " | Clean"
        print(f" - {col} ({analysis['pandas_dtype']}): Missing: {analysis['missing_values']} ({analysis['missing_percentage']}%){issues_str}")
        print(f"   Samples: {', '.join(analysis['sample_values'])}")

    # STEP 2: AI Suggestions
    print("\nQuerying AI Agent for cleaning suggestions...")
    suggestions = get_cleaning_suggestions(profile)
    steps = suggestions.get("cleaning_steps", [])
    
    if not steps:
        print("\nNo cleaning suggestions recommended by the AI. The dataset looks clean!")
        return

    print_header("AI Recommended Cleaning Steps")
    approved_operations = []
    
    for idx, step in enumerate(steps, 1):
        desc = step.get("description", "No description provided.")
        print(f"\n[Step {idx}] {desc}")
        print(f"Operation: {step.get('operation')} | Target: {step.get('column', 'Dataset')}")
        
        if args.yes:
            choice = "y"
            print("Auto-approved (--yes enabled).")
        else:
            choice = safe_input("Apply this step? (Y/n): ", default="y").strip().lower()
            
        if choice in ["", "y", "yes"]:
            approved_operations.append(step)
            print("=> Approved.")
        else:
            print("=> Skipped.")

    if not approved_operations:
        print("\nNo cleaning steps were approved. Exiting without modifying the file.")
        return

    # STEP 3: Clean Data
    print("\nApplying approved cleaning transformations...")
    cleaned_df, logs = clean_data(file_path, approved_operations)
    
    # Ensure folders exist
    os.makedirs("output", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    output_path = "output/cleaned.csv"
    cleaned_df.to_csv(output_path, index=False)
    
    # Create Markdown Report
    report_path = "reports/cleaning_report.md"
    
    applied_logs_md = "\n".join([f"- {log}" for log in logs])
    
    report_content = f"""# CSV Cleaning Report

**Processed File:** `{file_path}`  
**Output File:** `{output_path}`  
**Execution Date:** 2026-06-13 (Agent Local Time)

## Summary Metrics
| Metric | Before | After | Change |
| --- | --- | --- | --- |
| **Rows** | {profile['rows']} | {len(cleaned_df)} | {len(cleaned_df) - profile['rows']} |
| **Columns** | {profile['columns']} | {len(cleaned_df.columns)} | {len(cleaned_df.columns) - profile['columns']} |
| **Duplicates** | {profile['duplicates']} | {int(cleaned_df.duplicated().sum())} | -{profile['duplicates'] - int(cleaned_df.duplicated().sum())} |

## Applied Cleaning Operations
{applied_logs_md}

## Original Dataset Profile
- **Encoding:** {profile['encoding']}
- **Total Columns:** {profile['columns']}
- **Columns Details:**
"""
    for col, analysis in profile["column_analysis"].items():
        issues_str = f" ({', '.join(analysis['detected_issues'])})" if analysis['detected_issues'] else ""
        report_content += f"  - `{col}` ({analysis['pandas_dtype']}){issues_str}: Missing {analysis['missing_values']} rows. Samples: {analysis['sample_values']}\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print_header("Cleaning Done")
    print(f"Saved cleaned CSV at:  {output_path}")
    print(f"Saved summary report at: {report_path}")
    print("\nApplied transformations:")
    for log in logs:
        print(f" - {log}")

if __name__ == "__main__":
    main()