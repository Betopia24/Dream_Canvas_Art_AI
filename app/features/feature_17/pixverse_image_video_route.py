from fastapi import APIRouter, HTTPException, File, UploadFile, Form
import logging
from .pixverse_image_video_service import pixverse_image_video_service
from .pixverse_image_video_schema import PixverseImageVideoResponse, ShapeEnum

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/pixverse-image-video", response_model=PixverseImageVideoResponse)
async def generate_pixverse_image_video(
    prompt: str = Form(..., description="Text prompt describing the video transformation"),
    image_file: UploadFile = File(..., description="Image file to convert to video"),
    shape: ShapeEnum = Form(default=ShapeEnum.LANDSCAPE, description="Video aspect ratio shape")
):
    """
    Generate a video from an image using Pixverse Image-to-Video model from FAL.ai
    
    Args:
        prompt: Text prompt as form data
        image_file: Image file to convert to video
        
    Returns:
        PixverseImageVideoResponse with success message and video URL
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
        video_url = await pixverse_image_video_service.generate_video(
            prompt=prompt,
            image_file=image_file,
            shape=shape
        )
        
        return PixverseImageVideoResponse(
            status=200,
            success_message="Video generated successfully from image with Pixverse",
            video_url=video_url
        )

        
    except Exception as e:
        logger.error(f"Error in Pixverse image-to-video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
