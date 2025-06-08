# app/routers/ingredients.py

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from starlette.datastructures import UploadFile as StarletteUploadFile
from io import BytesIO
from PIL import Image

from app.schemas.parse_response import ParseResponse
from app.services.recipe_service import recipe_service
from app.deps import get_context_service, rate_limit
from app.services.context_service import ContextService

router = APIRouter()

@router.post(
    "/ingredients",
    response_model=ParseResponse,
    dependencies=[Depends(rate_limit)]
)
async def parse_ingredients(
    text: str | None = Form(None),
    image: UploadFile | None = File(None),
    context_service: ContextService = Depends(get_context_service)
):
    if not text and not image:
        raise HTTPException(400, "Berikan `text` atau `image`.")

    if image:
        # Read & preprocess
        raw = await image.read()
        try:
            img = Image.open(BytesIO(raw)).convert("RGB")
        except Exception:
            raise HTTPException(400, "Gagal membaca file gambar.")
        img.thumbnail((1024, 1024))
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=85)
        buf.seek(0)

        wrapped = StarletteUploadFile(buf)        
        wrapped.filename = image.filename        
        object.__setattr__(wrapped, "_content_type", "image/jpeg")
        image = wrapped

    try:
        context_id, recipes = await recipe_service.handle_initial(
            context_service, text, image
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    return ParseResponse(context_id=context_id, recipes=recipes)
