import os
import json
import requests

def clean_json_string(text):
    text = text.strip()
    if text.startswith("```"):
        # Remove markdown code block fences
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text

def get_cleaning_suggestions(profile):
    prompt = f"""You are a Data Engineering AI Agent.
Analyze the following CSV dataset profile and recommend data cleaning steps.

CSV Profile:
{json.dumps(profile, indent=2)}

You MUST only output a JSON object containing a "cleaning_steps" key, which is a list of steps.
Each step in "cleaning_steps" must have:
1. "step_number": integer
2. "description": string explaining why and what to clean
3. "operation": one of the following exact strings:
   - "drop_duplicates" (no other keys required)
   - "fill_missing" (requires "column" and "strategy": "mean", "median", "mode", or a specific value)
   - "replace_value" (requires "column", "old", "new")
   - "to_datetime" (requires "column")
   - "convert_type" (requires "column", "type": "int", "float", "str")
   - "drop_column" (requires "column")

Only recommend operations that are actually needed based on the profile issues. 
If 'duplicates' is greater than 0 in the profile, you MUST recommend a "drop_duplicates" operation.
If no cleaning is needed, return an empty list.
Do NOT include any markdown formatting or prefix/suffix outside the JSON block. Output ONLY the raw JSON string.

Example JSON output format:
{{
  "cleaning_steps": [
    {{
      "step_number": 1,
      "description": "Remove duplicate rows",
      "operation": "drop_duplicates"
    }}
  ]
}}"""

    # 1. Try Gemini API if key is present
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            headers = {"Content-Type": "application/json"}
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}
            }
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code == 200:
                result = resp.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(clean_json_string(text))
        except Exception:
            pass

    # 2. Try OpenAI API if key is present
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a data cleaning assistant. Always output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            if resp.status_code == 200:
                result = resp.json()
                text = result["choices"][0]["message"]["content"]
                return json.loads(clean_json_string(text))
        except Exception:
            pass

    # 3. Try Ollama (local) if package is installed and server is running
    try:
        # Quick check if Ollama server is running
        resp = requests.get("http://localhost:11434/api/tags", timeout=1.5)
        if resp.status_code == 200:
            import ollama
            response = ollama.chat(
                model="llama3",
                messages=[{"role": "user", "content": prompt}]
            )
            text = response["message"]["content"]
            return json.loads(clean_json_string(text))
    except Exception:
        pass

    # 4. Fallback to Rule-Based Recommender (Deterministic suggestions)
    return get_rule_based_suggestions(profile)

def get_rule_based_suggestions(profile):
    """Rule-based fallback when no LLM API is available."""
    steps = []
    step_num = 1
    
    # 1. Check duplicates
    if profile.get("duplicates", 0) > 0:
        steps.append({
            "step_number": step_num,
            "description": f"Remove {profile['duplicates']} duplicate rows to ensure data uniqueness.",
            "operation": "drop_duplicates"
        })
        step_num += 1
        
    # 2. Check each column
    for col, analysis in profile.get("column_analysis", {}).items():
        # Missing values
        missing_cnt = analysis.get("missing_values", 0)
        if missing_cnt > 0:
            dtype = analysis.get("pandas_dtype", "")
            strategy = "median" if "int" in dtype or "float" in dtype else "mode"
            steps.append({
                "step_number": step_num,
                "description": f"Fill missing values in '{col}' using the column {strategy} (found {missing_cnt} missing rows).",
                "operation": "fill_missing",
                "column": col,
                "strategy": strategy
            })
            step_num += 1
            
        # Typos in samples (specifically Inda -> India)
        samples = analysis.get("sample_values", [])
        if col.lower() == "country" and "Inda" in samples:
            steps.append({
                "step_number": step_num,
                "description": "Standardize 'Inda' values to 'India' in country column.",
                "operation": "replace_value",
                "column": col,
                "old": "Inda",
                "new": "India"
            })
            step_num += 1
            
        # Potential date text format
        issues = analysis.get("detected_issues", [])
        if any("date format" in iss for iss in issues):
            steps.append({
                "step_number": step_num,
                "description": f"Convert '{col}' to proper datetime objects for consistent formatting.",
                "operation": "to_datetime",
                "column": col
            })
            step_num += 1
            
        # Potential numeric format
        if any("numeric" in iss for iss in issues):
            steps.append({
                "step_number": step_num,
                "description": f"Parse numeric values in '{col}' and cast to float.",
                "operation": "convert_type",
                "column": col,
                "type": "float"
            })
            step_num += 1
            
    return {"cleaning_steps": steps}