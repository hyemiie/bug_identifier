from fastapi import HTTPException
from helper.ai_suggestiosn import get_ai_suggestion
from helper.check_syntax import check_syntax_errors
from helper.models import BugResponse

async def check_code_length(snippet: str) -> bool:
    lines = snippet.strip().split('\n')
    return len(lines) <= 30



async def receive_code_snippet(code_snippet: str, language: str, tone: str):
    print('snippet received')
    if not code_snippet or not isinstance(code_snippet, str) or code_snippet.strip() == "":
        raise HTTPException(status_code=400, detail="No valid snippet was provided, please try again")
    
    snippet_length = await check_code_length(snippet= code_snippet)
    if not snippet_length:
        raise HTTPException(status_code=400, detail="Snippet length's greater than 30")

    
    has_error, error_message = check_syntax_errors(code=code_snippet, language=language)
    if has_error:
        return BugResponse(
            language=language,
            bug_type="Syntax Error",
            description=f"The code contains syntax errors: {error_message}",
            suggestion="Fix syntax errors first, then submit again for logic analysis"
        )
    
    response = get_ai_suggestion(code_snippet= code_snippet, language=language, tone=tone)
    return response


