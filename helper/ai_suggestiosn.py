import json
import re
from typing import Optional
from dotenv import load_dotenv
import os
from fastapi.responses import JSONResponse
import google.generativeai as genai
from helper.models import BugResponse

load_dotenv()



GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
genai.configure(api_key= GEMINI_API_KEY)


def get_ai_suggestion(code_snippet: str, language: str, tone: str):
    prompt = f"""
You are an expert {language} code reviewer and security researcher.

Analyze the following {language} code for bugs using a {tone} tone:
{code_snippet}


Instructions:
1. Identify any bugs or issues in this code.
2. Classify as one of: "Logical Bug", "Runtime Error", "Edge Case Issue", "Off-by-One Error", or "Syntax Error".
3. Provide a short, clear, and actionable suggestion for fixing it.
4. Return the fully corrected version of the code, formatted exactly as valid {language} syntax.

Respond with ONLY a JSON object in this exact format:
{{
    "bug_type": "category from above",
    "description": "clear explanation of what's wrong",
    "suggestion": "specific and actionable fix recommendation",
    "corrected_code": "the full corrected code here, escaped as valid JSON string"
}}

Rules:
- The corrected code must be valid {language} code that compiles/runs without syntax errors.
- Do NOT wrap corrected code in backticks or markdown fences.
- Escape all special characters so it’s valid JSON.
- Do not include extra commentary outside the JSON.
"""


    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
        cleaned = re.sub(r"\s*```", "", cleaned)

        data = json.loads(cleaned)

        return {
            "status": "success",
            "data": data
        }

    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": "JSON_PARSE_ERROR",
                "message": f"Failed to parse AI output: {str(e)}",
                "raw_output": raw_text
            }
        )
    except Exception as e:
        error_message = str(e).lower()
        error_code = "AI_QUOTA_EXCEEDED" if "429" in error_message or "quota" in error_message else "AI_FAILURE"
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": error_code,
                "message": f"AI request failed: {str(e)}"
            }
        )