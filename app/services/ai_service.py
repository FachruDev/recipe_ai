# app/services/ai_service.py

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
    GENERATE_RECIPES_PROMPT_EN,
    GENERATE_RECIPES_PROMPT_ID,
    CHAT_SYSTEM_PROMPT_EN,
    CHAT_SYSTEM_PROMPT_ID
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
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={"model": model, "messages": messages}
            )
        if resp.status_code != 200:
            raise HTTPException(resp.status_code, f"OpenRouter API Error: {resp.text}")
        return resp.json()["choices"][0]["message"]["content"]

    def _extract_json_array(self, text: str) -> str:
        # Greedy match from first [ to last ]
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return match.group(0)
        start, end = text.find('['), text.rfind(']')
        if start != -1 and end > start:
            return text[start:end+1]
        raise ValueError("JSON array not found")

    def _balance_json(self, s: str) -> str:
        # Close any unbalanced brackets/braces
        ob, cb = s.count('['), s.count(']')
        if ob > cb:
            s += ']' * (ob - cb)
        oB, cB = s.count('{'), s.count('}')
        if oB > cB:
            s += '}' * (oB - cB)
        return s

    def _normalize_ingredients(self, data: List[Union[str, dict]]) -> List[str]:
        out: List[str] = []
        for i in data:
            if isinstance(i, str):
                out.append(i)
            elif isinstance(i, dict):
                for k in ("nama_bahan", "ingredient"):
                    if k in i and isinstance(i[k], str):
                        out.append(i[k])
                        break
        return out

    def _detect_indonesian(self, text: str) -> bool:
        # Simple keyword-based detection
        keywords = ["apa", "bagaimana", "saya", "kamu", "ini", "itu", "kalo", "sambal", "bumbu"]
        lower = text.lower()
        return any(kw in lower for kw in keywords)

    async def extract_ingredients_from_text(self, text: str) -> List[str]:
        prompt = EXTRACT_TEXT_PROMPT.format(text=text)
        content = await self._chat(
            messages=[{"role": "user", "content": prompt}],
            model="opengvlab/internvl3-14b:free"
        )
        try:
            arr = self._extract_json_array(content)
            data = json.loads(arr)
        except Exception:
            raise HTTPException(502, f"Gagal parse JSON (text): {content}")
        return self._normalize_ingredients(data)

    async def extract_ingredients_from_image(self, image_file: UploadFile) -> List[str]:
        raw = await image_file.read()
        b64 = base64.b64encode(raw).decode()
        messages = [
            {"role": "user", "content": EXTRACT_IMAGE_PROMPT},
            {"role": "user", "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{image_file.content_type};base64,{b64}",
                        "detail": "auto"
                    }
                }
            ]}
        ]
        content = await self._chat(
            messages=messages,
            model="opengvlab/internvl3-14b:free"
        )
        try:
            arr = self._extract_json_array(content)
            data = json.loads(arr)
        except Exception:
            raise HTTPException(502, f"Gagal parse JSON (image): {content}")

        ingredients = self._normalize_ingredients(data)
        return ingredients

    async def generate_recipes(self, ingredients: List[str]) -> List[RecipeSummary]:
        key = tuple(sorted(ingredients))
        if key in self._recipes_cache:
            return [RecipeSummary(**r.dict()) for r in self._recipes_cache[key]]

        is_id = self._detect_indonesian(" ".join(ingredients))
        prompt = (
            GENERATE_RECIPES_PROMPT_ID if is_id else GENERATE_RECIPES_PROMPT_EN
        ).format(ingredients=ingredients)

        content = await self._chat(
            messages=[{"role": "user", "content": prompt}],
            model="opengvlab/internvl3-14b:free"
        )
        try:
            arr = self._extract_json_array(content)
            arr = self._balance_json(arr)
            raw = json.loads(arr)
            recipes = [RecipeSummary(**r) for r in raw]
        except Exception as e:
            raise HTTPException(502, f"Parse recipes error: {e}\nAI: {content}")

        self._recipes_cache[key] = recipes
        return recipes

    async def answer_question(self, recipe: RecipeSummary, question: str) -> str:
        is_id = self._detect_indonesian(question)
        system_prompt = (
            CHAT_SYSTEM_PROMPT_ID if is_id else CHAT_SYSTEM_PROMPT_EN
        ).format(
            title=recipe.title,
            ingredients=recipe.ingredients,
            instructions_preview=recipe.instructions_preview
        )

        reply = await self._chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": question}
            ],
            model="opengvlab/internvl3-14b:free"
        )
        return reply

# Singleton instance
ai_client = AIClient()