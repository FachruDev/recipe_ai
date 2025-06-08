from pydantic import BaseModel

class SelectResponse(BaseModel):
    message: str
