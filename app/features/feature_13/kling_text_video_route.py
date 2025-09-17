from fastapi import APIRouter, HTTPException
import logging
from .kling_text_video_service import kling_text_video_service
from .kling_text_video_schema import KlingTextVideoRequest, KlingTextVideoResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/kling-text-video", response_model=KlingTextVideoResponse)
async def generate_kling_video(request: KlingTextVideoRequest):
    """
    Generate a video using Kling Video model from FAL.ai
    
    Args:
        request: KlingTextVideoRequest with prompt
        
    Returns:
        KlingTextVideoResponse with success message and video URL
    """
    try:
        logger.info(f"Received Kling video request for prompt: {request.prompt[:50]}...")
        
        # Generate the video
        video_url = await kling_text_video_service.generate_video(request.prompt)
        
        return KlingTextVideoResponse(
            success_message="Video generated successfully with Kling",
            status=200,
            video_url=video_url
        )
        
    except Exception as e:
        logger.error(f"Error in Kling video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
