from fastapi import APIRouter, HTTPException
from .videogen3_schema import VideoGen3Request, VideoGen3Response
from .videogen3_service import VideoGen3Service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["videogen3"], prefix="/videogen3")
videogen3_service = VideoGen3Service()

@router.post("/generate", response_model=VideoGen3Response)
async def generate_video(request: VideoGen3Request):
    """
    Generate a video using Veo 3.0 Fast and save it locally
    """
    try:
        video_path = await videogen3_service.generate_video(request.prompt)
        
        success_message = f"Successfully generated and saved video using Veo 3.0 Fast for prompt: {request.prompt}"
        
        return VideoGen3Response(
            video_path=video_path,
            success_message=success_message
        )
        
    except Exception as e:
        logger.error(f"Error in Veo 3 video generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
