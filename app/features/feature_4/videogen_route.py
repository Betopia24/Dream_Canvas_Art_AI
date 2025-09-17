from fastapi import APIRouter, HTTPException
from .videogen_schema import VideoGenRequest, VideoGenResponse
from .videogen_service import VideoGenService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["videogen"], prefix="/videogen")
videogen_service = VideoGenService()

@router.post("/generate", response_model=VideoGenResponse)
async def generate_video(request: VideoGenRequest):
    """
    Generate a video using Gemini Veo 3
    """
    try:
        video_path = await videogen_service.generate_video(request.prompt)
        
        success_message = f"Successfully generated video for prompt: {request.prompt}"
        
        return VideoGenResponse(
            status=200,
            success_message=success_message,
            video_path=video_path
            
        )
        
    except Exception as e:
        logger.error(f"Error in video generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
