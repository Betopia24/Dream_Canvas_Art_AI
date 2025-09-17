from fastapi import APIRouter, HTTPException, File, UploadFile, Form
import logging
from .kling_image_video_service import kling_image_video_service
from .kling_image_video_schema import KlingImageVideoResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/kling-image-video", response_model=KlingImageVideoResponse)
async def generate_kling_image_video(
    prompt: str = Form(..., description="Text prompt describing the video transformation"),
    image_file: UploadFile = File(..., description="Image file to convert to video")
):
    """
    Generate a video from an image using Kling Image-to-Video model from FAL.ai
    
    Args:
        prompt: Text prompt as form data
        image_file: Image file to convert to video
        
    Returns:
        KlingImageVideoResponse with success message and video URL
    """
    try:
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(status_code=400, detail="Image file is required for video generation")
        
        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if image_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        logger.info(f"Generating video from image {image_file.filename} with prompt: {prompt[:50]}...")
        
        # Generate the video
        video_url = await kling_image_video_service.generate_video(
            prompt=prompt,
            image_file=image_file
        )
        
        return KlingImageVideoResponse(
            status=200,
            success_message="Video generated successfully from image with Kling",
            video_url=video_url
        )
        
    except Exception as e:
        logger.error(f"Error in Kling image-to-video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
