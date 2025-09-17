from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
import logging
from .flux_kontext_dev_service import flux_kontext_dev_service
from .flux_kontext_dev_schema import FluxKontextDevRequest, FluxKontextDevResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/flux-kontext-dev", response_model=FluxKontextDevResponse)
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
        logger.info(f"Received Flux Kontext Dev request for {style} style {shape} image: {request.prompt[:50]}...")
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
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
            image_path=image_path,
            shape=shape
            
        )
        
    except Exception as e:
        logger.error(f"Error in Flux Kontext Dev generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image: {str(e)}"
        )
