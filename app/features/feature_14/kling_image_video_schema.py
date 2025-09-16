from pydantic import BaseModel

class KlingImageVideoRequest(BaseModel):
    """Schema for Kling image-to-video generation request"""
    prompt: str

class KlingImageVideoResponse(BaseModel):
    """Schema for Kling image-to-video generation response"""
    video_url: str
    success_message: str
