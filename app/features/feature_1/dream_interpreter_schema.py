from pydantic import BaseModel, Field

class DreamInterpreterRequest(BaseModel):
    """Request schema for dream interpretation"""
    prompt: str = Field(description="Description of the dream to interpret and visualize")

class DreamInterpreterResponse(BaseModel):
    """Response schema for dream interpretation"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    image_url: str = Field(description="Local path to the generated dream image")
    dream_interpretation: str = Field(description="AI interpretation of the dream using GPT-4")

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str = Field(description="Error message")
