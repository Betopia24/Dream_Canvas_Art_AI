from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import Optional
import logging

from .gemini_nanobanana_schema import GeminiNanoBananaResponse, StyleEnum, ShapeEnum
from .gemini_nanobanana_service import gemini_nanobanana_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/nanobanana",
    tags=["Gemini NanoBanana"]
)


@router.post("/generate", response_model=GeminiNanoBananaResponse)
async def generate_banana_costume(
    prompt: str = Form(..., description="Text prompt describing the image to generate"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_file: Optional[UploadFile] = File(None, description="Optional image file (temporarily disabled to avoid errors)")
):
    """
    Generate a banana costume image using Gemini NanoBanana with specified style and shape.
    Prompt is sent as form data. Image upload is optional but temporarily disabled to avoid errors.
    """
    try:
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
        # Note about image file if provided
        if image_file and image_file.filename:
            logger.warning(f"Image file {image_file.filename} provided but image support is temporarily disabled")
        
        filename, image_url = await gemini_nanobanana_service.generate_banana_costume_image(
            prompt=prompt,
            style=style,
            shape=shape,
            image_file=image_file
        )
        
        success_message = f"Successfully generated {style} style banana model image in {shape} format using Gemini NanoBanana"
        
        return GeminiNanoBananaResponse(
            success_message=success_message,
            image_url=image_url,
            shape=shape
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))