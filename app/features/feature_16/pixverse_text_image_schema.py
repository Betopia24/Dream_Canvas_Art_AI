from pydantic import BaseModel, Field

class PixverseTextImageRequest(BaseModel):
    """Schema for Pixverse text-to-video generation request"""
    prompt: str

class PixverseTextImageResponse(BaseModel):
    """Schema for Pixverse text-to-video generation response"""
    success_message: str = Field(description="Success message")
    status: int = Field(description="HTTP status code", example=200)
    video_url: str = Field(description="URL to the generated video")

