from pydantic import BaseModel

class Wan22ImageVideoRequest(BaseModel):
    """Schema for WAN 2.2 image-to-video generation request"""
    prompt: str

class Wan22ImageVideoResponse(BaseModel):
    """Schema for WAN 2.2 image-to-video generation response"""
    video_url: str
    success_message: str
