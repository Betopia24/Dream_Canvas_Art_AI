from fastapi import APIRouter, HTTPException, Query,Header
from .dalle_schema import DalleRequest, DalleResponse, StyleEnum, ShapeEnum
from .dalle_service import DalleService
from ...core.error_handlers import handle_service_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dalle"], prefix="/dalle")
dalle_service = DalleService()

@router.post("/generate", response_model=DalleResponse)
async def generate_image(
    request: DalleRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    user_id: str = Header(None)
):
    """
    Generate an image using DALL-E 3 with specified style and shape as query parameters
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
        
        image_path = await dalle_service.generate_image(
            prompt=request.prompt,
            user_id=user_id,
            style=style,
            shape=shape
        )
        
        success_message = f"Successfully generated and saved {style} style image in {shape} format"
        
        return DalleResponse(
            status=200,
            success_message=success_message,
            image_url=image_path,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle OpenAI/DALL-E service errors
        logger.error(f"Error in DALL-E image generation: {str(e)}")
        raise handle_service_error(e, "OpenAI DALL-E", "generate image")
