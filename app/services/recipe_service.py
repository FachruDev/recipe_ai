# app/services/recipe_service.py
from typing import Optional, Tuple, List, Dict, Any
from fastapi import UploadFile, HTTPException
from app.services.ai_service import ai_client
from app.services.context_service import ContextService

class RecipeService:
    """
    Orkestrator utama untuk alur resep.
    Menggabungkan ai_service untuk logika AI dan context_service untuk manajemen state.
    """
    def __init__(self):
        self.ai = ai_client

    async def handle_initial_request(
        self,
        context_service: ContextService,
        text: Optional[str],
        image: Optional[UploadFile]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Menangani permintaan awal dari pengguna (teks/gambar), mengekstrak bahan,
        membuat resep, dan memulai sesi konteks baru.
        """
        # Menggunakan satu fungsi terpadu dari ai_service
        ingredients = await self.ai.extract_ingredients(text_input=text, image_file=image)
        if not ingredients:
            # Jika tidak ada bahan valid yang ditemukan, kita bisa berhenti di sini.
            raise HTTPException(status_code=400, detail="Tidak ada bahan makanan valid yang dapat ditemukan dari input Anda.")
        
        recipes = await self.ai.generate_recipes(ingredients)
        if not recipes:
            raise HTTPException(status_code=404, detail="Maaf, tidak ada resep yang bisa dibuat dari bahan-bahan tersebut.")

        # Memulai sesi konteks dengan resep yang dihasilkan
        context_id = context_service.create_context(recipes)
        return context_id, recipes

    def select_recipe(
        self,
        context_service: ContextService,
        context_id: str,
        recipe_id: str
    ):
        """Meneruskan permintaan pemilihan resep ke context_service."""
        context_service.select_recipe(context_id, recipe_id)

    async def handle_chat_message(
        self,
        context_service: ContextService,
        context_id: str,
        message: str
    ) -> str:
        """
        Menangani pesan chat dari pengguna secara kontekstual.
        """
        recipe = context_service.get_selected_recipe(context_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Resep belum dipilih atau ID konteks tidak valid.")
        
        # PERBAIKAN URUTAN: Simpan pesan pengguna terlebih dahulu.
        context_service.append_message(context_id, "user", message)

        # PERUBAHAN KRUSIAL: Ambil riwayat chat untuk diberikan ke AI sebagai memori.
        chat_history = context_service.get_chat_history(context_id)
        
        # Panggil AI dengan konteks resep, pertanyaan baru, DAN riwayat chat.
        reply = await self.ai.answer_question(
            recipe=recipe, 
            question=message, 
            chat_history=chat_history
        )
        
        # Simpan balasan dari AI ke dalam database.
        context_service.append_message(context_id, "assistant", reply)
        return reply

    def end_session(
        self,
        context_service: ContextService,
        context_id: str
    ):
        """Meneruskan permintaan penghentian sesi ke context_service."""
        context_service.end_context(context_id)


# Singleton instance
recipe_service = RecipeService()