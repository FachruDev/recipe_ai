from pydantic import BaseModel
from typing import List
from app.schemas.recipe import RecipeSummary

class ParseResponse(BaseModel):
    context_id: str
    recipes: List[RecipeSummary]
