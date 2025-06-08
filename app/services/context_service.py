# app/services/context_service.py
from typing import List
from sqlmodel import Session as DbSession, select
from app.models import SessionModel, MessageModel
from app.schemas.recipe import RecipeSummary
from app.db import get_db

class ContextService:
    def __init__(self, db: DbSession):
        self.db = db

    def create_context(self, recipes: List[RecipeSummary]) -> str:
        sess = SessionModel()
        # Simpan ke DB
        self.db.add(sess)
        self.db.commit()
        self.db.refresh(sess)
        # store recipes list as first system prompt?
        prompt = {
            "role": "system",
            "content": f"Available recipes: {[(r.id, r.title) for r in recipes]}"
        }
        msg = MessageModel(session_id=sess.id, **prompt)
        self.db.add(msg)
        self.db.commit()
        return sess.id

    def select_recipe(self, context_id: str, recipe_id: str):
        sess = self.db.get(SessionModel, context_id)
        if not sess:
            raise KeyError("Context ID tidak ditemukan.")
        sess.selected_recipe_id = recipe_id
        # add system prompt with selected recipe detail if needed...
        self.db.add(sess)
        self.db.commit()

    def append_message(self, context_id: str, role: str, content: str):
        if not self.db.get(SessionModel, context_id):
            raise KeyError("Context ID tidak ditemukan.")
        msg = MessageModel(session_id=context_id, role=role, content=content)
        self.db.add(msg)
        self.db.commit()

    def get_history(self, context_id: str) -> List[dict]:
        statement = select(MessageModel).where(MessageModel.session_id == context_id).order_by(MessageModel.timestamp)
        msgs = self.db.exec(statement).all()
        return [{"role": m.role, "content": m.content} for m in msgs]

    def end_context(self, context_id: str):
        sess = self.db.get(SessionModel, context_id)
        if sess:
            # delete messages first
            stmt = select(MessageModel).where(MessageModel.session_id == context_id)
            msgs = self.db.exec(stmt).all()
            for m in msgs:
                self.db.delete(m)
            self.db.delete(sess)
            self.db.commit()
