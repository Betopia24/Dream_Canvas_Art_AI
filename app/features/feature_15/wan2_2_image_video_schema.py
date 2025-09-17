from pydantic import BaseModel, Field

class Wan22ImageVideoRequest(BaseModel):
    """Schema for WAN 2.2 image-to-video generation request"""
    prompt: str

class Wan22ImageVideoResponse(BaseModel):
    """Schema for WAN 2.2 image-to-video generation response"""
    video_url: str
    success_message: str
    status: int = Field(description="HTTP status code", example=200)
