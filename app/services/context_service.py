# app/services/context_service.py

import json
from typing import List, Optional, Dict, Any
from sqlmodel import Session as DbSession, select
from app.models import SessionModel, MessageModel

class ContextService:
    """
    Mengelola state dan konteks percakapan yang disimpan di database.
    Disesuaikan untuk bekerja dengan format data baru dari ai_service.
    """
    def __init__(self, db: DbSession):
        self.db = db

    def create_context(self, recipes: List[Dict[str, Any]]) -> str:
        """Membuat sesi baru dan menyimpan daftar resep yang dihasilkan AI."""
        sess = SessionModel(recipes_json=recipes)
        self.db.add(sess)
        self.db.commit()
        self.db.refresh(sess)
        
        initial_message = {
            "role": "system_internal", 
            "content": f"Session created with recipes: {[r.get('title', 'N/A') for r in recipes]}"
        }
        msg = MessageModel(session_id=sess.id, **initial_message)
        self.db.add(msg)
        self.db.commit()

        return sess.id

    def select_recipe(self, context_id: str, recipe_id: str):
        """Menandai resep yang dipilih pengguna dalam sebuah sesi."""
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            raise KeyError("Context ID tidak ditemukan.")
        
        recipes = sess.recipes_json or []
        if not any(r.get("id") == recipe_id for r in recipes):
            raise KeyError("Recipe ID tidak ada di dalam konteks sesi ini.")
        
        sess.selected_recipe_id = recipe_id
        self.db.add(sess)
        self.db.commit()

    def get_selected_recipe(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Mengambil data resep lengkap yang telah dipilih dari DB."""
        sess = self.db.get(SessionModel, context_id)
        if not sess or not sess.selected_recipe_id:
            return None
        
        for r in sess.recipes_json:
            if r.get("id") == sess.selected_recipe_id:
                return r
        return None

    def append_message(self, context_id: str, role: str, content: str):
        """Menyimpan pesan baru (dari user atau AI) ke dalam riwayat chat."""
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            raise KeyError("Context ID tidak ditemukan.")
        
        msg = MessageModel(session_id=context_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()

    def get_chat_history(self, context_id: str) -> List[Dict[str, str]]:
        """
        Mengambil riwayat percakapan yang relevan untuk diberikan sebagai konteks ke AI.
        Hanya mengambil pesan dari 'user' dan 'assistant'.
        """
        statement = select(MessageModel).where(
            MessageModel.session_id == context_id,
            MessageModel.role.in_(['user', 'assistant'])
        ).order_by(MessageModel.timestamp)
        
        msgs = self.db.exec(statement).all()
        return [{"role": m.role, "content": m.content} for m in msgs]

    def end_context(self, context_id: str):
        """Menghapus sesi dan semua pesan terkait dari database."""
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            return
        
        # Hapus semua pesan yang terkait dengan sesi ini
        messages_to_delete = self.db.exec(
            select(MessageModel).where(MessageModel.session_id == context_id)
        ).all()
        for m in messages_to_delete:
            self.db.delete(m)
        
        # Hapus sesi itu sendiri
        self.db.delete(sess)
        self.db.commit()