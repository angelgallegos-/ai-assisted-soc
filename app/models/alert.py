from pydantic import BaseModel

class Alert(BaseModel):
    id: str
    title: str
    severity: str
    user: str
    host: str
    description: str
