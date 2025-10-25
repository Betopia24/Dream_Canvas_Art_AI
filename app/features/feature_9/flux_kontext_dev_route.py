from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging
from .flux_kontext_dev_service import flux_kontext_dev_service
from .flux_kontext_dev_schema import FluxKontextDevRequest, FluxKontextDevResponse
from ...core.error_handlers import handle_service_error

router = APIRouter(
    prefix="/flux-kontext-dev"
)
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=FluxKontextDevResponse)
async def generate_flux_kontext_dev_image(
    request: FluxKontextDevRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape")
):
    """
    Generate an image using Flux Kontext Dev model from FAL.ai with style and shape as query parameters
    
    Args:
        request: FluxKontextDevRequest with prompt
        style: Image style as query parameter
        shape: Image shape as query parameter
        
    Returns:
        FluxKontextDevResponse with success message and image path
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
        
        logger.info(f"Received Flux Kontext Dev request for {style} style {shape} image: {request.prompt[:50]}...")
        
        # Generate the image with style and shape
        image_path = await flux_kontext_dev_service.generate_image(
            prompt=request.prompt,
            style=style,
            shape=shape
        )
        
        success_message = f"Successfully generated {style} style image in {shape} format using Flux Kontext Dev"
        
        return FluxKontextDevResponse(
            status=200,
            success_message=success_message,
            image_url=image_path,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle fal.ai service errors
        logger.error(f"Error in Flux Kontext Dev generation: {str(e)}")
        raise handle_service_error(e, "fal.ai", "generate image")
