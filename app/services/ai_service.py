# app/services/ai_service.py

import json
import base64
import re
import uuid 
from typing import List, Optional, Dict, Any
import httpx
from fastapi import UploadFile, HTTPException
from app.config import Settings
from app.prompts import (
    UNIFIED_EXTRACT_AND_VALIDATE_PROMPT,
    GENERATE_RECIPES_PROMPT_ID,
    GENERATE_RECIPES_PROMPT_EN,
    CHAT_SYSTEM_PROMPT_ID,
    CHAT_SYSTEM_PROMPT_EN,
)

settings = Settings()

class AIClient:
    """
    Klien AI yang telah direfaktor untuk efisiensi, kontrol, dan konsistensi.
    Menggunakan satu model multimodal dan prompt yang kuat.
    """
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        self.base_url = settings.openrouter_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Define a single model that we will use across all services.
        self.model = "openbmb/internvl-chat-v1.5" 

    async def _execute_chat_completion(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Fungsi inti yang mengeksekusi panggilan ke API OpenRouter.
        Dibuat lebih robust dengan timeout yang lebih panjang.
        """
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={"model": self.model, "messages": messages}
            )
        response.raise_for_status()
        return response.json()

    def _extract_json_from_response(self, text: str) -> Any:
        """
        Helper untuk mengekstrak blok JSON dari respons teks AI yang terkadang
        mengandung teks tambahan sebelum atau sesudah blok JSON.
        """
        # Search for JSON blocks enclosed by ```json ... ``` or ``` ... ```
        match = re.search(r"```(json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(2)
        
        # Search from the first to the last curly/square bracket
        start = text.find('[') if text.find('[') != -1 else text.find('{')
        end = text.rfind(']') if text.rfind(']') != -1 else text.rfind('}')
        
        if start != -1 and end != -1:
            json_str = text[start : end + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Gagal mem-parse JSON yang diekstrak: {e}\nString Asli: {json_str}")
        
        raise ValueError("Tidak ada blok JSON yang valid ditemukan dalam respons AI.")

    def _detect_indonesian(self, text: str) -> bool:
        """Deteksi bahasa sederhana untuk memilih prompt yang tepat."""
        keywords = ["apa", "bagaimana", "saya", "resep", "buatkan", "bahan", "nasi", "sambal"]
        return any(kw in text.lower() for kw in keywords)

    # --- PUBLIC FUNCTION FOR ENDPOINT ---

    async def extract_ingredients(
        self,
        text_input: Optional[str] = None,
        image_file: Optional[UploadFile] = None
    ) -> List[str]:
        """
        Fungsi terpadu untuk mengekstrak bahan dari teks atau gambar,
        menggunakan UNIFIED_EXTRACT_AND_VALIDATE_PROMPT.
        """
        if not text_input and not image_file:
            raise HTTPException(status_code=400, detail="Harus menyediakan input teks atau file gambar.")

        user_content = []
        prompt_input_text = ""

        if text_input:
            prompt_input_text += f"Analisis teks berikut: '{text_input}'"
        
        if image_file:
            prompt_input_text += "\nAnalisis juga gambar yang terlampir."
            raw_content = await image_file.read()
            b64_image = base64.b64encode(raw_content).decode('utf-8')
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:{image_file.content_type};base64,{b64_image}"}
            })
        
        user_content.insert(0, {"type": "text", "text": prompt_input_text})
        
        messages = [
            {"role": "system", "content": UNIFIED_EXTRACT_AND_VALIDATE_PROMPT},
            {"role": "user", "content": user_content}
        ]
        
        try:
            response = await self._execute_chat_completion(messages)
            ai_response_text = response["choices"][0]["message"]["content"]
            ingredients = self._extract_json_from_response(ai_response_text)
            if not isinstance(ingredients, list):
                raise ValueError("Respons JSON dari AI bukanlah sebuah list.")
            return ingredients
        except (ValueError, json.JSONDecodeError, IndexError) as e:
            raise HTTPException(status_code=502, detail=f"Gagal memproses respons dari AI: {e}")

    async def generate_recipes(self, ingredients: List[str]) -> List[Dict[str, Any]]:
        """
        Membuat resep berdasarkan daftar bahan yang valid.
        Secara otomatis menambahkan UUID yang aman pada setiap resep.
        """
        is_id = self._detect_indonesian(" ".join(ingredients))
        prompt_template = GENERATE_RECIPES_PROMPT_ID if is_id else GENERATE_RECIPES_PROMPT_EN
        
        messages = [
            {"role": "system", "content": prompt_template},
            {"role": "user", "content": json.dumps(ingredients)}
        ]

        try:
            response = await self._execute_chat_completion(messages)
            ai_response_text = response["choices"][0]["message"]["content"]
            recipes = self._extract_json_from_response(ai_response_text)
            
            if not isinstance(recipes, list):
                raise ValueError("Respons JSON dari AI bukanlah sebuah list resep.")

            # Generate ID on server side, not asking AI.
            for recipe in recipes:
                recipe['id'] = str(uuid.uuid4())
            
            return recipes
        except (ValueError, json.JSONDecodeError, IndexError) as e:
            raise HTTPException(status_code=502, detail=f"Gagal memproses respons resep dari AI: {e}")

    async def answer_question(
        self,
        recipe: Dict[str, Any],
        question: str,
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Menjawab pertanyaan tentang resep secara kontekstual, dengan mempertimbangkan riwayat chat.
        """
        is_id = self._detect_indonesian(question) or self._detect_indonesian(recipe.get('title', ''))
        prompt_template = CHAT_SYSTEM_PROMPT_ID if is_id else CHAT_SYSTEM_PROMPT_EN
        
        # Create recipe context in a neat string format
        recipe_context_str = json.dumps(recipe, indent=2, ensure_ascii=False)
        system_prompt = prompt_template.format(recipe_context=recipe_context_str)
        
        messages = [
            {"role": "system", "content": system_prompt},
            *chat_history,  # Enter all previous conversation history
            {"role": "user", "content": question}
        ]

        response = await self._execute_chat_completion(messages)
        return response["choices"][0]["message"]["content"]


# Singleton instance to use throughout the application
ai_client = AIClient()