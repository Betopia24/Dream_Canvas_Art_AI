from fastapi import APIRouter, HTTPException, Query, Header
import logging
from .qwen_service import qwen_service
from .qwen_schema import QwenRequest, QwenResponse
from ...core.error_handlers import handle_service_error

router = APIRouter(
    prefix="/qwen-image"
)
logger = logging.getLogger(__name__)

@router.post("/generate", response_model=QwenResponse)
async def generate_qwen_image(
    request: QwenRequest,
    user_id: str = Header(None),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    
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
        
        print(user_id)
        logger.info(f"Received Qwen image request for {style} style {shape} image: {request.prompt[:50]}...")
        
        # Generate the image with style and shape
        image_url = await qwen_service.generate_image(
            prompt=request.prompt,
            user_id=user_id,
            style=style,
            shape=shape
            
        )
        
        logger.info(f"Qwen image generation completed successfully: {image_url}")
        
        return QwenResponse(
            status=200,
            success_message="Image generated successfully with Qwen",
            image_url=image_url,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle fal.ai service errors
        logger.error(f"Error in Qwen image generation: {str(e)}")
        raise handle_service_error(e, "fal.ai", "generate image")
