from fastapi import APIRouter, HTTPException, Query, Header
from .videogen_schema import VideoGenRequest, VideoGenResponse, ShapeEnum
from .videogen_service import VideoGenService
from ...core.error_handlers import handle_service_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    # prefix="/videogen",
    tags=["videogen"]
    )
videogen_service = VideoGenService()

@router.post("/videogen", response_model=VideoGenResponse)
async def generate_video(
    request: VideoGenRequest,
    shape: ShapeEnum = Query(default=ShapeEnum.LANDSCAPE, description="Video aspect ratio shape: square, portrait, landscape"),
    user_id: str = Header(None)
):
    """
    Generate a video using Gemini Veo 3
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
        
        video_url = await videogen_service.generate_video(request.prompt, user_id, shape)
        
        success_message = f"Successfully generated video for prompt: {request.prompt}"
        
        return VideoGenResponse(
            status=200,
            success_message=success_message,
            video_url=video_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle video generation service errors
        logger.error(f"Error in video generation: {str(e)}")
        raise handle_service_error(e, "VideoGen", "generate video")
