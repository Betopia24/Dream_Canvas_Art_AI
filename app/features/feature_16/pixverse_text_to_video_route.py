from fastapi import APIRouter, HTTPException
import logging

from .pixverse_text_to_video_service import pixverse_text_image_service
from .pixverse_text_to_video_schema import PixverseTextImageRequest, PixverseTextImageResponse, ShapeEnum

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/pixverse-text-video", response_model=PixverseTextImageResponse)
async def generate_pixverse_video(request: PixverseTextImageRequest):
    """
    Generate a video using Pixverse text-to-video model from FAL.ai
    Args:
        request: PixverseTextImageRequest with prompt and shape
    Returns:
        PixverseTextImageResponse with success message and video URL
    """
    try:
        logger.info(f"Received Pixverse video request for prompt: {request.prompt[:50]}... shape: {request.shape}")
        # Generate the video
        video_url = await pixverse_text_image_service.generate_video(request.prompt, request.shape)
        return PixverseTextImageResponse(
            status=200,
            success_message="Video generated successfully with Pixverse",
            video_url=video_url
        )
    except Exception as e:
        logger.error(f"Error in Pixverse video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
