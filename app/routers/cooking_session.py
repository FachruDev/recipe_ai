# app/routers/cooking_session.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status, 
)
from typing import Optional
from io import BytesIO
from PIL import Image
from app.schemas import (
    GenerateRecipesResponse,
    SelectRecipeRequest,
    ChatRequest,
    ChatResponse,
)
from app.services.recipe_service import recipe_service
from app.services.context_service import ContextService
from app.deps import get_context_service, rate_limit

# Create a router with prefixes and tags for better API documentation
router = APIRouter(
    prefix="/session",
    tags=["Cooking Session"],
)


@router.post(
    "/",
    response_model=GenerateRecipesResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Memulai Sesi Memasak Baru",
    description="Kirim teks atau gambar bahan untuk mendapatkan daftar resep dan memulai sesi baru.",
    dependencies=[Depends(rate_limit)],
)
async def start_new_session(
    context_service: ContextService = Depends(get_context_service),
    text: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    """
    Endpoint untuk memulai sesi. Menerima input bahan (teks/gambar),
    menghasilkan resep, dan mengembalikan context_id untuk interaksi selanjutnya.
    """
    if not text and not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Harus menyediakan input 'text' atau 'image' dalam form data.",
        )

    # Processing Image
    if image:
        # Validation content type
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File yang diunggah bukan gambar.")
        try:
            raw_content = await image.read()
            # Resize and compression for efisiensi
            processed_image = Image.open(BytesIO(raw_content)).convert("RGB")
            processed_image.thumbnail((1024, 1024)) # Max 1024px
            
            buffer = BytesIO()
            processed_image.save(buffer, format="JPEG", quality=85)
            buffer.seek(0)
            
            image = UploadFile(file=buffer, filename=image.filename, media_type="image/jpeg")
        except Exception:
            raise HTTPException(status_code=400, detail="Gagal memproses file gambar.")

    context_id, recipes = await recipe_service.handle_initial_request(
        context_service=context_service, text=text, image=image
    )
    
    return GenerateRecipesResponse(context_id=context_id, recipes=recipes)


@router.post(
    "/{context_id}/select",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Memilih Resep",
    description="Setelah resep dibuat, endpoint ini digunakan untuk memilih salah satu resep yang akan dibahas.",
)
def select_a_recipe(
    context_id: str,
    request: SelectRecipeRequest,
    context_service: ContextService = Depends(get_context_service),
):
    """
    Menandai resep yang dipilih pengguna berdasarkan context_id dan recipe_id.
    """
    try:
        recipe_service.select_recipe(
            context_service=context_service,
            context_id=context_id,
            recipe_id=request.recipe_id,
        )
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{context_id}/chat",
    response_model=ChatResponse,
    summary="Mengirim Pesan Chat ke AI",
    description="Berinteraksi dengan Chef AI mengenai resep yang telah dipilih.",
    dependencies=[Depends(rate_limit)],
)
async def chat_with_assistant(
    context_id: str,
    request: ChatRequest,
    context_service: ContextService = Depends(get_context_service),
):
    """
    Mengirim pesan pengguna ke AI dan mengembalikan balasannya.
    Menggunakan context_id dari path URL untuk menjaga state.
    """
    try:
        reply = await recipe_service.handle_chat_message(
            context_service=context_service, context_id=context_id, message=request.message
        )
        return ChatResponse(reply=reply)
    except (KeyError, HTTPException) as e:
        status_code = e.status_code if isinstance(e, HTTPException) else status.HTTP_404_NOT_FOUND
        detail = e.detail if isinstance(e, HTTPException) else str(e)
        raise HTTPException(status_code=status_code, detail=detail)


@router.delete(
    "/{context_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Mengakhiri Sesi Memasak",
    description="Menghapus sesi dan semua riwayat percakapan dari database.",
)
def end_a_session(
    context_id: str,
    context_service: ContextService = Depends(get_context_service),
):
    """
    Membersihkan data sesi setelah pengguna selesai.
    Menggunakan metode HTTP DELETE yang lebih sesuai secara semantik.
    """
    recipe_service.end_session(context_service, context_id)