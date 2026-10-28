from pydantic import BaseModel

class TriageResult(BaseModel):
    summary: str
    verdict: str
    confidence: int
