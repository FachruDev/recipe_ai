# app/services/context_service.py
import json
from typing import List, Optional
from sqlmodel import Session as DbSession, select
from app.models import SessionModel, MessageModel
from app.schemas.recipe import RecipeSummary

class ContextService:
    def __init__(self, db: DbSession):
        self.db = db

    def create_context(self, recipes: List[RecipeSummary]) -> str:
        sess = SessionModel(
            recipes_json=[r.dict() for r in recipes]
        )
        self.db.add(sess)
        self.db.commit()
        self.db.refresh(sess)

        prompt = {
            "role": "system",
            "content": f"Available recipes: {[r['title'] for r in sess.recipes_json]}"
        }
        msg = MessageModel(session_id=sess.id, **prompt)
        self.db.add(msg)
        self.db.commit()

        return sess.id

    def select_recipe(self, context_id: str, recipe_id: str):
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            raise KeyError("Context ID tidak ditemukan.")
        recipes = sess.recipes_json or []
        if not any(r["id"] == recipe_id for r in recipes):
            raise KeyError("Recipe ID tidak ada di context.")
        sess.selected_recipe_id = recipe_id
        self.db.add(sess)
        self.db.commit()

    def get_selected_recipe(self, context_id: str) -> Optional[RecipeSummary]:
        sess = self.db.get(SessionModel, context_id)
        if not sess or not sess.selected_recipe_id:
            return None
        for r in sess.recipes_json:
            if r["id"] == sess.selected_recipe_id:
                return RecipeSummary(**r)
        return None

    def append_message(self, context_id: str, role: str, content: str):
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            raise KeyError("Context ID tidak ditemukan.")
        msg = MessageModel(session_id=context_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()

    def get_history(self, context_id: str) -> List[dict]:
        statement = select(MessageModel).where(
            MessageModel.session_id == context_id
        ).order_by(MessageModel.timestamp)
        msgs = self.db.exec(statement).all()
        return [{"role": m.role, "content": m.content} for m in msgs]

    def end_context(self, context_id: str):
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            return
        statement = select(MessageModel).where(
            MessageModel.session_id == context_id
        )
        for m in self.db.exec(statement).all():
            self.db.delete(m)
            
        self.db.delete(sess)
        self.db.commit()
