from pydantic import BaseModel, Field

class PixverseTextImageRequest(BaseModel):
    """Schema for Pixverse text-to-video generation request"""
    prompt: str

class PixverseTextImageResponse(BaseModel):
    """Schema for Pixverse text-to-video generation response"""
    video_url: str
    success_message: str
    status: int = Field(description="HTTP status code", example=200)
