from fastapi import APIRouter, HTTPException, Query
import logging

from .gemini_schema import GeminiImageRequest, GeminiImageResponse, ErrorResponse, StyleEnum, ShapeEnum
from .gemini_service import gemini_service

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
        logger.info(f"Generating image with Gemini for prompt: {request.prompt[:50]}...")
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
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
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        raise HTTPException(
            status_code=500,
            detail=f"Service configuration error: {str(ve)}"
        )
        
    except Exception as e:
        logger.error(f"Error in Gemini image generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image: {str(e)}"
        )