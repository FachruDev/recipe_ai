# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Settings
from app.db import init_db
from app.routers.ingredients import router as ingr_router
from app.routers.recipes import router as rec_router

settings = Settings()
app = FastAPI(
    title="Recipe AI Backend",
    description="Backend untuk ekstraksi bahan, generate resep, dan chat resep",
    version="0.1.0"
)

# Inisialization database SQLite
init_db()

# Pasang CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Daftarkan router di bawah prefix /api
app.include_router(ingr_router, prefix="/api")
app.include_router(rec_router, prefix="/api")
