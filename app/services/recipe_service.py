# app/services/recipe_service.py
from typing import Optional, Tuple, List
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
    ) -> Tuple[str, List[RecipeSummary]]:
        if text:
            ingredients = await self.ai.extract_ingredients_from_text(text)
        elif image:
            ingredients = await self.ai.extract_ingredients_from_image(image)
        else:
            raise HTTPException(400, "Berikan `text` atau `image`.")
        recipes = await self.ai.generate_recipes(ingredients)
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
        recipe = context_service.get_selected_recipe(context_id)
        if not recipe:
            raise HTTPException(400, "Belum memilih resep atau context tidak valid.")
        reply = await self.ai.answer_question(recipe, message)
        context_service.append_message(context_id, "user", message)
        context_service.append_message(context_id, "assistant", reply)
        return reply

    def end(
        self,
        context_service: ContextService,
        context_id: str
    ):
        context_service.end_context(context_id)

recipe_service = RecipeService()
