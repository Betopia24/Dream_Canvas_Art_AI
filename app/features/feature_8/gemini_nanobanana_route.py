from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import Optional
import logging

from .gemini_nanobanana_schema import GeminiNanoBananaResponse, StyleEnum, ShapeEnum
from .gemini_nanobanana_service import gemini_nanobanana_service
from ...core.error_handlers import handle_service_error, validate_file_types

logger = logging.getLogger(__name__)

router = APIRouter(
    # prefix="/nanobanana",
    tags=["Gemini NanoBanana"]
)


@router.post("/nanobanana",response_model=GeminiNanoBananaResponse)
async def generate_banana_costume(
    prompt: str = Form(..., description="Text prompt describing the image to generate"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_file: Optional[UploadFile] = File(None, description="Optional reference image file. If provided, will use as visual reference for generation.")
):
    """
    Generate a banana costume image using Gemini NanoBanana with specified style and shape.
    
    - **prompt**: Text description sent as form data
    - **style**: Visual style for the generated image
    - **shape**: Aspect ratio/shape of the output image
    - **image_file**: Optional reference image. If provided, the AI will use it as visual reference along with the prompt. If not provided, will generate purely from the text prompt.
    """
    try:
        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )
        
        # Handle optional image file validation
        if image_file and image_file.filename:
            # Validate file type
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            validate_file_types([image_file], allowed_types, "image_file")
            logger.info(f"Reference image file {image_file.filename} provided for guided generation")
            success_message = f"Successfully generated {style} style banana model image in {shape} format using Gemini NanoBanana with reference image"
        else:
            logger.info("No reference image provided, generating from text prompt only")
            success_message = f"Successfully generated {style} style banana model image in {shape} format using Gemini NanoBanana from text prompt"
        
        filename, image_url = await gemini_nanobanana_service.generate_banana_costume_image(
            prompt=prompt,
            style=style,
            shape=shape,
            image_file=image_file
        )
        
        return GeminiNanoBananaResponse(
            status=200,
            success_message=success_message,
            image_url=image_url,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle Google AI service errors
        logger.error(f"Error in Gemini NanoBanana generation: {str(e)}")
        raise handle_service_error(e, "Google AI", "generate banana costume image")