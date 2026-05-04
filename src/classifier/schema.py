from pydantic import BaseModel
from typing import List, Optional, Dict


class ClassifiedIntent(BaseModel):
    intent: str
    agent: str
    entities: Dict[str, List[str]]
    safety_verdict: Optional[str] = None