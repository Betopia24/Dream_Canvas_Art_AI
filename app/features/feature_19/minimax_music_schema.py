from pydantic import BaseModel, Field

class MinimaxMusicRequest(BaseModel):
    """Request schema for MiniMax Music generation"""
    verse_prompt: str = Field(
        ...,
        description="Text prompt describing the verse or main content of the music",
        min_length=1,
        max_length=1000,
        example="A peaceful melody with nature sounds"
    )
    lyrics_prompt: str = Field(
        ...,
        description="Text prompt describing the lyrics or musical theme",
        min_length=1,
        max_length=1000,
        example="Relaxing ambient music for meditation"
    )

class MinimaxMusicResponse(BaseModel):
    """Response schema for MiniMax Music generation"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    audio_url: str = Field(description="URL to the generated audio file")
