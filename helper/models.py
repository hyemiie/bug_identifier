from typing import Optional
from pydantic import BaseModel


class BugResponse(BaseModel):
    language: str
    bug_type: str
    description: str
    suggestion: Optional[str] = None

