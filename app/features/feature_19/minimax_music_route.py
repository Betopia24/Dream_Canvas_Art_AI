from fastapi import APIRouter, HTTPException
import logging
from .minimax_music_service import minimax_music_service
from .minimax_music_schema import MinimaxMusicRequest, MinimaxMusicResponse

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
        logger.info(f"Received MiniMax Music request for verse: {request.verse_prompt[:50]}... and lyrics: {request.lyrics_prompt[:50]}...")
        
        # Generate the audio
        audio_url = await minimax_music_service.generate_audio(
            verse_prompt=request.verse_prompt,
            lyrics_prompt=request.lyrics_prompt
        )
        
        return MinimaxMusicResponse(
            status=200,
            audio_url=audio_url,
            success_message="Music generated successfully with MiniMax Music"
        )
        
    except Exception as e:
        logger.error(f"Error in MiniMax Music generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate music: {str(e)}"
        )
