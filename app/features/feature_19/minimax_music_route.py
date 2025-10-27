from fastapi import APIRouter, HTTPException
import logging
from .minimax_music_service import minimax_music_service
from .minimax_music_schema import MinimaxMusicRequest, MinimaxMusicResponse
from ...core.error_handlers import handle_service_error

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/minimax-music", response_model=MinimaxMusicResponse)
async def generate_minimax_music(request: MinimaxMusicRequest):
    """
    Generate music using MiniMax Music model from FAL.ai
    
    Args:
        request: MinimaxMusicRequest with verse_prompt and lyrics_prompt
        
    Returns:
        MinimaxMusicResponse with success message and audio URL
    """
    try:
        # Validate verse_prompt
        if not request.verse_prompt or not request.verse_prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Verse prompt is required and cannot be empty",
                    "field": "verse_prompt"
                }
            )
        
        # Log the request (lyrics_prompt is optional)
        if request.lyrics_prompt and request.lyrics_prompt.strip():
            logger.info(f"Received MiniMax Music request for verse: {request.verse_prompt[:50]}... and lyrics: {request.lyrics_prompt[:50]}...")
        else:
            logger.info(f"Received MiniMax Music request for verse: {request.verse_prompt[:50]}... (no lyrics)")
        
        # Generate the audio
        audio_url = await minimax_music_service.generate_audio(
            verse_prompt=request.verse_prompt,
            lyrics_prompt=request.lyrics_prompt
        )
        
        logger.info(f"MiniMax Music generation completed successfully: {audio_url}")
        
        return MinimaxMusicResponse(
            status=200,
            success_message="Music generated successfully with MiniMax Music",
            audio_url=audio_url
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle MiniMax Music service errors
        logger.error(f"Error in MiniMax Music generation: {str(e)}")
        raise handle_service_error(e, "MiniMax Music", "generate music")
