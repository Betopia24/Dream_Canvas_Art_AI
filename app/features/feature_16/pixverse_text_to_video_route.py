from fastapi import APIRouter, HTTPException, Header
import logging

from .pixverse_text_to_video_service import pixverse_text_image_service
from .pixverse_text_to_video_schema import PixverseTextImageRequest, PixverseTextImageResponse, ShapeEnum
from ...core.error_handlers import handle_service_error

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/pixverse-text-video", response_model=PixverseTextImageResponse)
async def generate_pixverse_video(request: PixverseTextImageRequest, user_id: str = Header(None)):
    """
    Generate a video using Pixverse text-to-video model from FAL.ai
    Args:
        request: PixverseTextImageRequest with prompt and shape
    Returns:
        PixverseTextImageResponse with success message and video URL
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
        
        logger.info(f"Received Pixverse video request for prompt: {request.prompt[:50]}... shape: {request.shape}")
        
        # Generate the video
        video_url = await pixverse_text_image_service.generate_video(request.prompt,user_id, request.shape)
        
        return PixverseTextImageResponse(
            status=200,
            success_message="Video generated successfully with Pixverse",
            video_url=video_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle fal.ai service errors
        logger.error(f"Error in Pixverse video generation: {str(e)}")
        raise handle_service_error(e, "fal.ai", "generate video")
