import json
import base64
import re
from typing import List, Union, Tuple
import httpx
from fastapi import UploadFile, HTTPException
from app.schemas.recipe import RecipeSummary
from app.config import Settings
from app.prompts import (
    EXTRACT_TEXT_PROMPT,
    EXTRACT_IMAGE_PROMPT,
    GENERATE_RECIPES_PROMPT,
    CHAT_SYSTEM_PROMPT
)

settings = Settings()

class AIClient:
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self._recipes_cache: dict[Tuple[str, ...], List[RecipeSummary]] = {}

    async def _chat(self, messages: List[dict], model: str) -> str:
        payload = {"model": model, "messages": messages}
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, f"OpenRouter API Error: {resp.text}")
        return resp.json()["choices"][0]["message"]["content"]

    def _extract_json_array(self, text: str) -> str:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            raise ValueError("Tidak menemukan JSON array dalam response AI")
        return match.group(0)

    def _normalize_ingredients(self, data: List[Union[str, dict]]) -> List[str]:
        result: List[str] = []
        for item in data:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Prioritaskan key 'nama_bahan' atau 'ingredient'
                if "nama_bahan" in item:
                    result.append(item["nama_bahan"])
                elif "ingredient" in item:
                    result.append(item["ingredient"])
                else:
                    val = next(iter(item.values()), None)
                    if isinstance(val, str):
                        result.append(val)
        return result

    async def extract_ingredients_from_text(self, text: str) -> List[str]:
        prompt = EXTRACT_TEXT_PROMPT.format(text=text)
        content = await self._chat(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/mistral-7b-instruct"
        )
        try:
            json_str = self._extract_json_array(content)
            data = json.loads(json_str)
        except Exception:
            raise HTTPException(502, f"Gagal parse JSON dari AI: {content}")
        return self._normalize_ingredients(data)

    async def extract_ingredients_from_image(self, image_file: UploadFile) -> List[str]:
        raw = await image_file.read()
        b64 = base64.b64encode(raw).decode()
        # Kirim gambar dan prompt
        messages = [
            {"role": "user", "content": EXTRACT_IMAGE_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{image_file.content_type};base64,{b64}",
                            "detail": "auto"
                        }
                    }
                ]
            }
        ]
        content = await self._chat(
            messages=messages,
            model="mistralai/mistral-7b-instruct"
        )
        try:
            json_str = self._extract_json_array(content)
            data = json.loads(json_str)
        except Exception:
            raise HTTPException(502, f"Gagal parse JSON dari AI (image): {content}")
        return self._normalize_ingredients(data)

    async def generate_recipes(self, ingredients: List[str]) -> List[RecipeSummary]:
        key = tuple(sorted(ingredients))
        if key in self._recipes_cache:
            return [RecipeSummary(**r.dict()) for r in self._recipes_cache[key]]

        prompt = GENERATE_RECIPES_PROMPT.format(ingredients=ingredients)
        content = await self._chat(
            messages=[{"role": "user", "content": prompt}],
            model="mistralai/mistral-7b-instruct"
        )
        try:
            raw = json.loads(self._extract_json_array(content))
            recipes = [RecipeSummary(**r) for r in raw]
        except Exception as e:
            raise HTTPException(502, f"Gagal parse JSON resep: {e}\nAI Response: {content}")

        self._recipes_cache[key] = recipes
        return recipes

    async def answer_question(self, recipe: RecipeSummary, question: str) -> str:
        system = CHAT_SYSTEM_PROMPT.format(
            title=recipe.title,
            ingredients=recipe.ingredients,
            instructions_preview=recipe.instructions_preview
        )
        user = question
        return await self._chat(
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": user}
            ],
            model="mistralai/mistral-7b-instruct"
        )

# Singleton client
ai_client = AIClient()
