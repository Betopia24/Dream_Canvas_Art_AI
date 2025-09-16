from fastapi import APIRouter, HTTPException, File, UploadFile, Form
import logging
from .wan2_2_image_video_service import wan22_image_video_service
from .wan2_2_image_video_schema import Wan22ImageVideoResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/wan22-image-video", response_model=Wan22ImageVideoResponse)
async def generate_wan22_image_video(
    prompt: str = Form(..., description="Text prompt describing the video transformation"),
    image_file: UploadFile = File(..., description="Image file to convert to video")
):
    """
    Generate a video from an image using WAN 2.2 Image-to-Video model from FAL.ai
    
    Args:
        prompt: Text prompt as form data
        image_file: Image file to convert to video
        
    Returns:
        Wan22ImageVideoResponse with success message and video URL
    """
    try:
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(status_code=400, detail="Image file is required for video generation")
        
        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if image_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        logger.info(f"Generating video from image {image_file.filename} with WAN 2.2 for prompt: {prompt[:50]}...")
        
        # Generate the video
        video_url = await wan22_image_video_service.generate_video(
            prompt=prompt,
            image_file=image_file
        )
        
        return Wan22ImageVideoResponse(
            video_url=video_url,
            success_message="Video generated successfully from image with WAN 2.2"
        )
        
    except Exception as e:
        logger.error(f"Error in WAN 2.2 image-to-video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
