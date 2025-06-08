# app/models.py
from typing import Optional
from datetime import datetime
from uuid import uuid4
from sqlmodel import SQLModel, Field, Relationship

class SessionModel(SQLModel, table=True):
    id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    selected_recipe_id: Optional[str] = None

    messages: list["MessageModel"] = Relationship(back_populates="session")

class MessageModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessionmodel.id")
    role: str  # 'system' | 'user' | 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    session: SessionModel = Relationship(back_populates="messages")
