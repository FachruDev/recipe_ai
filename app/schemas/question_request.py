from pydantic import BaseModel

class QuestionRequest(BaseModel):
    context_id: str
    question: str
