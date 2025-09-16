from fastapi import APIRouter, HTTPException, File, UploadFile
import logging
from .ai_avatar_service import ai_avatar_service
from .ai_avatar_schema import AIAvatarResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/ai-avatar", response_model=AIAvatarResponse)
async def generate_ai_avatar_video(
    image_file: UploadFile = File(..., description="Image file for the avatar"),
    audio_file: UploadFile = File(..., description="Audio file for the avatar speech")
):
    """
    Generate an AI Avatar video using ByteDance OmniHuman model from FAL.ai
    
    Args:
        image_file: Image file for the avatar
        audio_file: Audio file for the avatar speech
        
    Returns:
        AIAvatarResponse with success message and video URL
    """
    try:
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(status_code=400, detail="Image file is required")
        
        # Check image file type
        allowed_image_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if image_file.content_type not in allowed_image_types:
            raise HTTPException(status_code=400, detail=f"Invalid image file type. Allowed types: {', '.join(allowed_image_types)}")
        
        # Validate audio file
        if not audio_file or not audio_file.filename:
            raise HTTPException(status_code=400, detail="Audio file is required")
        
        # Check audio file type
        allowed_audio_types = ["audio/mpeg", "audio/mp3", "audio/wav", "audio/ogg", "audio/m4a"]
        if audio_file.content_type not in allowed_audio_types:
            raise HTTPException(status_code=400, detail=f"Invalid audio file type. Allowed types: {', '.join(allowed_audio_types)}")
        
        logger.info(f"Generating AI Avatar video from image {image_file.filename} and audio {audio_file.filename}...")
        
        # Generate the video
        video_url = await ai_avatar_service.generate_video(
            image_file=image_file,
            audio_file=audio_file
        )
        
        return AIAvatarResponse(
            video_url=video_url,
            success_message="AI Avatar video generated successfully with ByteDance OmniHuman"
        )
        
    except Exception as e:
        logger.error(f"Error in AI Avatar video generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate video: {str(e)}"
        )
