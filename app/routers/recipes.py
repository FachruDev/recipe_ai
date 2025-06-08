# app/routers/recipes.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.schemas.select_request import SelectRequest
from app.schemas.select_response import SelectResponse
from app.schemas.question_request import QuestionRequest
from app.schemas.question_response import QuestionResponse
from app.services.recipe_service import recipe_service
from app.deps import get_context_service, rate_limit
from app.services.context_service import ContextService

router = APIRouter()

class ChatRequest(BaseModel):
    context_id: str
    message: str

class ChatResponse(BaseModel):
    reply: str

class EndRequest(BaseModel):
    context_id: str

@router.post("/recipes/select", response_model=SelectResponse)
def select_recipe(
    req: SelectRequest,
    context_service: ContextService = Depends(get_context_service)
):
    try:
        recipe_service.handle_select(
            context_service, req.context_id, req.recipe_id
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return SelectResponse(message="Resep berhasil dipilih.")

@router.post(
    "/recipes/chat",
    response_model=ChatResponse,
    dependencies=[Depends(rate_limit)]  # <-- pasang rate limit
)
async def chat(
    req: ChatRequest,
    context_service: ContextService = Depends(get_context_service)
):
    try:
        reply = await recipe_service.chat(
            context_service, req.context_id, req.message
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ChatResponse(reply=reply)

@router.post("/recipes/end")
def end_session(
    req: EndRequest,
    context_service: ContextService = Depends(get_context_service)
):
    recipe_service.end(context_service, req.context_id)
    return {"message": "Session selesai dan context dihapus."}
