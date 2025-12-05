from pydantic import BaseModel

class HealthCheck(BaseModel):
    name: str
    status: str
    version: str

