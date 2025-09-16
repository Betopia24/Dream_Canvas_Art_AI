from fastapi import APIRouter, HTTPException, Query
import logging
from .qwen_service import qwen_service
from .qwen_schema import QwenRequest, QwenResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/qwen-image", response_model=QwenResponse)
async def generate_qwen_image(
    request: QwenRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape")
):
    """
    Generate an image using Qwen Image model from FAL.ai with style and shape as query parameters
    
    Args:
        request: QwenRequest with prompt
        style: Image style as query parameter
        shape: Image shape as query parameter
        
    Returns:
        QwenResponse with success message and image URL
    """
    try:
        logger.info(f"Received Qwen image request for {style} style {shape} image: {request.prompt[:50]}...")
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
        # Generate the image with style and shape
        image_url = await qwen_service.generate_image(
            prompt=request.prompt,
            style=style,
            shape=shape
        )
        
        return QwenResponse(
            success_message="Image generated successfully with Qwen",
            image_url=image_url,
            style=style
        )
        
    except Exception as e:
        logger.error(f"Error in Qwen image generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate image: {str(e)}"
        )
