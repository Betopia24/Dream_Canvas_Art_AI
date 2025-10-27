from pydantic import BaseModel, Field
from typing import Optional
class MinimaxMusicRequest(BaseModel):
    """Request schema for MiniMax Music generation"""
    verse_prompt: str = Field(
        ...,
        description="The actual lyrics content/text for the song",
        min_length=1,
        example="A song about nature and peaceful moments"
    )
    lyrics_prompt: Optional[str] = Field(
        default=None,
        description="Music style description (optional)",
        example="Folk acoustic guitar with soft melody"
    )
    user_id:str 

class MinimaxMusicResponse(BaseModel):
    """Response schema for MiniMax Music generation"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    audio_url: str = Field(description="URL to the generated audio file")

