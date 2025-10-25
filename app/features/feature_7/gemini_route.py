from fastapi import APIRouter, HTTPException, Query
import logging

from .gemini_schema import GeminiImageRequest, GeminiImageResponse, ErrorResponse, StyleEnum, ShapeEnum
from .gemini_service import gemini_service
from ...core.error_handlers import handle_service_error

# Setup logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/iamgen",
    tags=["Gemini Image Generation"]
)


@router.post("/generate", response_model=GeminiImageResponse)
async def generate_image(
    request: GeminiImageRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape")
):
    """
    Generate an image from a text prompt using Google's Gemini Imagen model with specified style and shape
    
    Takes a text prompt and returns a URL to the generated image.
    Uses Gemini's imagen-4.0-generate-001 model with style and shape parameters.
    """
    try:
        # Validate prompt
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )
        
        logger.info(f"Generating image with Gemini for prompt: {request.prompt[:50]}...")
        
        # Generate the image with style and shape
        filename, image_url = gemini_service.generate_image(
            prompt=request.prompt,
            style=style,
            shape=shape
        )
        
        success_message = f"Successfully generated {style} style image in {shape} format using Gemini"
        
        return GeminiImageResponse(
            status=200,
            success_message=success_message,
            image_url=image_url,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle Google AI/Gemini service errors
        logger.error(f"Error in Gemini image generation: {str(e)}")
        raise handle_service_error(e, "Google AI", "generate image")