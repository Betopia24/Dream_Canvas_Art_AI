from fastapi import APIRouter, HTTPException, Query
import logging
from .flux_1_spro_service import flux1_spro_service
from .flux_1_spro_schema import Flux1SproRequest, Flux1SproResponse
from ...core.error_handlers import handle_service_error

router = APIRouter(
    prefix="/flux-1-srpo",
)
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=Flux1SproResponse)
async def generate_flux1_srpo_image(
    request: Flux1SproRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape")
):
    """
    Generate an image using Flux 1 SRPO model from FAL.ai with style and shape as query parameters
    
    Args:
        request: Flux1SproRequest with prompt
        style: Image style as query parameter
        shape: Image shape as query parameter
        
    Returns:
        Flux1SproResponse with success message, image URL, and style
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
        
        logger.info(f"Received Flux 1 SRPO image request for prompt: {request.prompt[:50]}...")
        
        # Generate the image
        image_url = await flux1_spro_service.generate_image(request.prompt, style, shape)
        
        return Flux1SproResponse(
            status=200,
            success_message=f"Image generated successfully with Flux 1 SRPO in {style} style",
            image_url=image_url,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle fal.ai service errors
        logger.error(f"Error in Flux 1 SRPO image generation: {str(e)}")
        raise handle_service_error(e, "fal.ai", "generate image")
