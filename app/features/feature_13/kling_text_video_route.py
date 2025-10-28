from fastapi import APIRouter, HTTPException, Query, Header
import logging
from .kling_text_video_service import kling_text_video_service
from .kling_text_video_schema import KlingTextVideoRequest, KlingTextVideoResponse, ShapeEnum
from ...core.error_handlers import handle_service_error

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/kling-text-video", response_model=KlingTextVideoResponse)
async def generate_kling_video(
    request: KlingTextVideoRequest,
    shape: ShapeEnum = Query(default=ShapeEnum.LANDSCAPE, description="Video aspect ratio shape: square, portrait, landscape"),
    user_id: str = Header(None)
):
    """
    Generate a video using Kling Video model from FAL.ai
    
    Args:
        request: KlingTextVideoRequest with prompt
        
    Returns:
        KlingTextVideoResponse with success message and video URL
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
        
        logger.info(f"Received Kling video request for prompt: {request.prompt[:50]}... shape: {shape}")
        
        # Generate the video
        video_url = await kling_text_video_service.generate_video(request.prompt, user_id, shape)
        
        logger.info(f"Kling video generation completed successfully: {video_url}")
        
        return KlingTextVideoResponse(
            status=200,
            success_message="Video generated successfully with Kling",
            video_url=video_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle Kling service errors
        logger.error(f"Error in Kling video generation: {str(e)}")
        raise handle_service_error(e, "Kling", "generate video")
