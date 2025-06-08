from pydantic import BaseModel
from typing import List

class RecipeSummary(BaseModel):
    id: str
    title: str
    ingredients: List[str]
    instructions_preview: str
