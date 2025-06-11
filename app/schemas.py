# app/schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# ==============================================================================
# Scheme for Initiation Process & Recipe Creation
# ==============================================================================

class GenerateRecipesResponse(BaseModel):
    """
    Respons yang dikirim ke user setelah resep berhasil dibuat.
    """
    context_id: str = Field(..., description="ID unik untuk sesi percakapan ini.")
    recipes: List[Dict[str, Any]] = Field(..., description="Daftar 3 resep yang dihasilkan oleh AI.")
    

# ==============================================================================
# Scheme for Recipe Selection Process
# ==============================================================================

class SelectRecipeRequest(BaseModel):
    """
    Request body yang dikirim user untuk memilih resep dari daftar.
    """
    recipe_id: str = Field(..., description="ID dari resep yang dipilih oleh pengguna.")


# ==============================================================================
# Scheme for Chat Process
# ==============================================================================

class ChatRequest(BaseModel):
    """
    Request body yang dikirim user saat mengirim pesan chat.
    """
    message: str = Field(..., min_length=1, description="Pesan atau pertanyaan dari pengguna.")


class ChatResponse(BaseModel):
    """
    Respons yang dikirim ke user setelah AI membalas chat.
    """
    reply: str = Field(..., description="Balasan dari Chef AI.")