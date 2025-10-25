from fastapi import APIRouter, HTTPException, Query
from .videogen3_schema import VideoGen3Request, VideoGen3Response, ShapeEnum
from .videogen3_service import VideoGen3Service
from ...core.error_handlers import handle_service_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    # prefix="/videogen3",
    tags=["videogen3"]
)
videogen3_service = VideoGen3Service()

@router.post("/videogen3", response_model=VideoGen3Response)
async def generate_video(
    request: VideoGen3Request,
    shape: ShapeEnum = Query(default=ShapeEnum.LANDSCAPE, description="Video aspect ratio shape: square, portrait, landscape")
):
    """
    Generate a video using Veo 3.0 Fast and save it locally
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
        
        logger.info(f"Generating video with Veo 3.0 Fast for prompt: {request.prompt[:50]}... shape: {shape}")
        
        video_url = await videogen3_service.generate_video(request.prompt, shape)
        
        success_message = f"Successfully generated and saved video using Veo 3.0 Fast for prompt: {request.prompt}"
        
        logger.info(f"Video generation completed successfully: {video_url}")
        
        return VideoGen3Response(
            status=200,
            success_message=success_message,
            video_url=video_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle video generation service errors
        logger.error(f"Error in Veo 3 video generation: {str(e)}")
        raise handle_service_error(e, "Google AI Veo", "generate video")
