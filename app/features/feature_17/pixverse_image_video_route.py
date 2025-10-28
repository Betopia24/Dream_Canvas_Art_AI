from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Header
import logging
from .pixverse_image_video_service import pixverse_image_video_service
from .pixverse_image_video_schema import PixverseImageVideoResponse, ShapeEnum
from ...core.error_handlers import handle_service_error

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/pixverse-image-video", response_model=PixverseImageVideoResponse)
async def generate_pixverse_image_video(
    prompt: str = Form(..., description="Text prompt describing the video transformation"),
    image_file: UploadFile = File(..., description="Image file to convert to video"),
    shape: ShapeEnum = Form(default=ShapeEnum.LANDSCAPE, description="Video aspect ratio shape"),
    user_id: str = Header(None)
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
        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )
        
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Image file is required for video generation",
                    "field": "image_file"
                }
            )
        
        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if image_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": f"Invalid file type. Allowed types: {', '.join(allowed_types)}",
                    "field": "image_file"
                }
            )
        
        logger.info(f"Generating video from image {image_file.filename} with prompt: {prompt[:50]}... shape: {shape}")
        
        # Generate the video
        video_url = await pixverse_image_video_service.generate_video(
            prompt=prompt,
            user_id=user_id,
            image_file=image_file,
            shape=shape
        )
        
        logger.info(f"Pixverse image-to-video generation completed successfully: {video_url}")
        
        return PixverseImageVideoResponse(
            status=200,
            success_message="Video generated successfully from image with Pixverse",
            video_url=video_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle Pixverse service errors
        logger.error(f"Error in Pixverse image-to-video generation: {str(e)}")
        raise handle_service_error(e, "Pixverse", "generate video from image")
