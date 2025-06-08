from pydantic import BaseModel

class SelectRequest(BaseModel):
    context_id: str
    recipe_id: str
