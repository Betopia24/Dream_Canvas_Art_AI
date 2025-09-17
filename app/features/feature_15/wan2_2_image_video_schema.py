from pydantic import BaseModel, Field

class Wan22ImageVideoRequest(BaseModel):
    """Schema for WAN 2.2 image-to-video generation request"""
    prompt: str

class Wan22ImageVideoResponse(BaseModel):
    """Schema for WAN 2.2 image-to-video generation response"""
    success_message: str = Field(description="Success message")
    status: int = Field(description="HTTP status code", example=200)
    video_url: str = Field(description="URL to the generated video")

