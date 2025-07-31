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


def get_ai_suggestion(code_snippet: str, language : str, tone: str):
    
    prompt = f"""
You are an expert {language} code reviewer and security researcher.

Analyze the following {language} code for bugs using a {tone} tone:


{code_snippet}

Instructions:
1. Identify the bugs or issues in this code
2. Classify as either: "Logical Bug", "Runtime Error", "Edge Case Issue", "Off-by-One Error", or "Syntax Error"
4. Provide a clear and actionable suggestion for fixing the issue

Respond with ONLY a JSON object in this exact format:
{{
    "bug_type": "category from above",
    "description": "clear explanation of what's wrong",
    "suggestion": "specific and actionable fix recommendation"
}}
Skip extra details or long best practices.
"""

    try:
            model = genai.GenerativeModel("gemini-2.5-flash")  
            response = model.generate_content(prompt)
            raw_text = response.text.strip()

            cleaned = re.sub(r"```(?:json)?\s*", "", raw_text)
            cleaned = re.sub(r"\s*```", "", cleaned)

            data = json.loads(cleaned)
            return data

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
    