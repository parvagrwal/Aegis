from pydantic import BaseModel
from typing import Optional, List

class Health(BaseModel):
    status: str
    lag_s: Optional[int] = 0

class CaseResponse(BaseModel):
    id: str
    verdict: str
    risk: str
    features: List[str]
    explanation: str
