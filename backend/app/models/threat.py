from pydantic import BaseModel


class Threat(BaseModel):
    id: int
    type: str
    source_ip: str
    severity: str
    status: str 