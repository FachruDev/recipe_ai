# app/services/recipe_service.py
from typing import Optional
from fastapi import UploadFile, HTTPException
from app.services.ai_service import ai_client
from app.services.context_service import ContextService
from app.schemas.recipe import RecipeSummary

class RecipeService:
    def __init__(self):
        self.ai = ai_client

    async def handle_initial(
        self,
        context_service: ContextService,
        text: Optional[str],
        image: Optional[UploadFile]
    ) -> tuple[str, list[RecipeSummary]]:
        # ekstrak bahan
        if text:
            ingredients = await self.ai.extract_ingredients_from_text(text)
        elif image:
            ingredients = await self.ai.extract_ingredients_from_image(image)
        else:
            raise HTTPException(status_code=400, detail="Berikan `text` atau `image`.")
        # generate resep
        recipes = await self.ai.generate_recipes(ingredients)
        # buat context di DB
        context_id = context_service.create_context(recipes)
        return context_id, recipes

    def handle_select(
        self,
        context_service: ContextService,
        context_id: str,
        recipe_id: str
    ):
        context_service.select_recipe(context_id, recipe_id)

    async def chat(
        self,
        context_service: ContextService,
        context_id: str,
        message: str
    ) -> str:
        context_service.append_message(context_id, "user", message)
        history = context_service.get_history(context_id)
        reply = await self.ai._chat(history, model="mistralai/mistral-7b-instruct")
        context_service.append_message(context_id, "assistant", reply)
        return reply

    def end(
        self,
        context_service: ContextService,
        context_id: str
    ):
        context_service.end_context(context_id)

# singleton instance
recipe_service = RecipeService()
