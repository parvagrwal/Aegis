from pydantic import BaseModel
from typing import Optional, Any
from aegis.chain.simulate import SimResult

class CaseContext(BaseModel):
    case_id: str
    tx: dict
    decoded: dict
    sim: Optional[SimResult]
    effects: list[dict]
    sig_effects: list[dict]
    net_flows: dict[str, dict[str, int]]
    subject: str
    initiator: str
    profiles: dict[str, dict]
    labels: dict[str, dict]

class Feature(BaseModel):
    id: str
    weight: int
    data: dict[str, Any]
