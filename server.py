import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np

# Import our agents
from agents.profiler import profile_csv, load_csv
from agents.recommender import get_cleaning_suggestions
from agents.cleaner import clean_data
from database.db import save_session, get_sessions

app = Flask(__name__)
# Enable CORS so the React app running on port 3000 can talk to this port (3003)
CORS(app)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs("output", exist_ok=True)
os.makedirs("reports", exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return """
    <html>
        <head><title>Clean Dataframe Agent API</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #090d16; color: #f1f5f9; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; margin: 0;">
            <h1 style="color: #818cf8; margin-bottom: 10px;">CSV Clean Dataframe Agent API</h1>
            <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 30px;">The backend API server is running successfully on port 3003.</p>
            <div style="background-color: #131b2e; border: 1px solid #24355a; border-radius: 12px; padding: 24px 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                <p style="margin: 0 0 10px 0; color: #94a3b8;">To use the clean data dashboard, open:</p>
                <h2 style="margin: 0;"><a href="http://localhost:3000" style="color: #c084fc; text-decoration: none; font-size: 1.6rem; border-bottom: 2px solid transparent; transition: border-color 0.2s;">http://localhost:3000</a></h2>
            </div>
        </body>
    </html>
    """

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file:
        file_path = os.path.join(TEMP_DIR, file.filename)
        file.save(file_path)
        
        try:
            # 1. Profile the dataset
            profile = profile_csv(file_path)
            
            # 2. Get AI suggestions
            suggestions = get_cleaning_suggestions(profile)
            
            # 3. Load raw data for "before" preview (first 10 rows)
            raw_df, _ = load_csv(file_path)
            raw_preview_df = raw_df.head(10).replace({np.nan: None})
            raw_preview_rows = raw_preview_df.to_dict(orient="records")
            raw_preview_columns = list(raw_df.columns)

            return jsonify({
                "file_path": file_path,
                "profile": profile,
                "suggestions": suggestions,
                "raw_preview_columns": raw_preview_columns,
                "raw_preview_rows": raw_preview_rows
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/clean", methods=["POST"])
def clean_dataset():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    file_path = data.get("file_path")
    operations = data.get("operations", [])
    original_filename = data.get("filename", os.path.basename(file_path or "unknown.csv"))
    
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Valid file_path is required"}), 400
        
    try:
        # Clean the dataset
        cleaned_df, logs = clean_data(file_path, operations)
        
        output_path = "output/cleaned.csv"
        cleaned_df.to_csv(output_path, index=False)
        
        # Save a summary report
        report_path = "reports/cleaning_report.md"
        profile = profile_csv(file_path) # Get original profile for stats
        
        applied_logs_md = "\n".join([f"- {log}" for log in logs])
        
        report_content = f"""# CSV Cleaning Report

**Processed File:** `{file_path}`  
**Output File:** `{output_path}`  

## Summary Metrics
| Metric | Before | After | Change |
| --- | --- | --- | --- |
| **Rows** | {profile['rows']} | {len(cleaned_df)} | {len(cleaned_df) - profile['rows']} |
| **Columns** | {profile['columns']} | {len(cleaned_df.columns)} | {len(cleaned_df.columns) - profile['columns']} |
| **Duplicates** | {profile['duplicates']} | {int(cleaned_df.duplicated().sum())} | -{profile['duplicates'] - int(cleaned_df.duplicated().sum())} |

## Applied Cleaning Operations
{applied_logs_md}
"""
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        # Prepare a small preview of the cleaned dataframe (first 20 rows) for the frontend
        # Replace NaN/Infinity with None/Null for JSON compatibility
        preview_df = cleaned_df.head(20).replace({np.nan: None})
        preview_data = preview_df.to_dict(orient="records")

        summary = {
            "rows_before": profile['rows'],
            "rows_after": len(cleaned_df),
            "columns_before": profile['columns'],
            "columns_after": len(cleaned_df.columns),
            "duplicates_before": profile['duplicates'],
            "duplicates_after": int(cleaned_df.duplicated().sum())
        }

        # Persist session to SQLite history
        try:
            save_session(
                filename=original_filename,
                summary=summary,
                operations=operations,
                logs=logs
            )
        except Exception:
            pass  # History save failure should not break the response

        return jsonify({
            "success": True,
            "message": "Dataset cleaned successfully",
            "logs": logs,
            "summary": summary,
            "preview_columns": list(cleaned_df.columns),
            "preview_rows": preview_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download", methods=["GET"])
def download_file():
    output_path = "output/cleaned.csv"
    if os.path.exists(output_path):
        return send_file(output_path, as_attachment=True, download_name="cleaned_data.csv")
    else:
        return jsonify({"error": "Cleaned file not found. Please clean a file first."}), 404

@app.route("/history", methods=["GET"])
def get_history():
    """Returns the last 20 cleaning sessions from SQLite."""
    try:
        sessions = get_sessions(limit=20)
        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask Clean Dataframe backend server on port 3003...")
    app.run(port=3003, debug=True)
