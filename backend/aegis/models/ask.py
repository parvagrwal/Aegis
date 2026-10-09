from pydantic import BaseModel
from typing import Any, Dict, Optional

class AskRequest(BaseModel):
    question: str
    context: Optional[Dict[str, Any]] = None

class AskResponse(BaseModel):
    answer: str
    citations: list[str]