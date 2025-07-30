from typing import Optional
from fastapi import APIRouter, Request
from helper.core import receive_code_snippet
from starlette.responses import JSONResponse
from config.config import limiter
from helper.models import BugRequest  

router = APIRouter()

@router.post("/find-bug")
@limiter.limit("10/minute") 
async def find_bug(request: Request, bug_request: BugRequest):
    try:
        if bug_request.tone.lower !=  "dev" or "casual":
            bug_request.tone = "dev"
        #     return JSONResponse(
        #     status_code=422,
        #     content="Please choose either dev or casual for the tone input"
        # )
        code_response = await receive_code_snippet(
                code_snippet=bug_request.code_snippet, 
                language=bug_request.language, 
                tone=bug_request.tone
            )

        print('response', code_response)
        return {"status": "success", "data": code_response}
    
    except Exception as e:
        print(f"Error occurred: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
   

sample_snippets = [
    {
        "language": "Python",
        "code": "if x = 5:\n    print('x is 5')"
    },
    {
        "language": "Python",
        "code": "for i in range(1, len(arr)):\n    print(arr[i-1])"
    },
    {
        "language": "Python",
        "code": "return x / y"
    }
]

@router.get("/sample-cases")
async def get_sample_cases():
    results = []

    for snippet in sample_snippets:
        language = snippet["language"]
        code = snippet["code"]

        try:
            ai_response = await receive_code_snippet(code_snippet=code, language=language, tone="casual")
            results.append({
                "code": code,
                "language": language,
                "ai_analysis": ai_response
            })
        except Exception as e:
            results.append({
                "code": code,
                "language": language,
                "ai_analysis": {"error": str(e)}
            })

    return results