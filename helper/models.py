from typing import Optional
from pydantic import BaseModel


class BugResponse(BaseModel):
    language: str
    bug_type: str
    description: str
    suggestion: Optional[str] = None
    corrected_code: Optional[str] = None 


class BugRequest(BaseModel):
   code_snippet: str
   language: str
   tone: Optional[str] = "dev"