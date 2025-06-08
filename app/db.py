# app/db.py
from sqlmodel import SQLModel, create_engine, Session
from app.config import Settings

settings = Settings()

DATABASE_URL = f"sqlite:///{settings.database_file}"

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

def init_db():
    from app.models import SessionModel, MessageModel
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
