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
    theme_prompt: str = Field(
        ...,
        description="Text prompt describing the lyrical theme or instrumental theme",
        min_length=1,
        max_length=1000,
        example="Relaxing ambient music for meditation"
    )

class MinimaxMusicResponse(BaseModel):
    """Response schema for MiniMax Music generation"""
    audio_url: str = Field(description="URL to the generated audio file")
    success_message: str = Field(description="Success message")
