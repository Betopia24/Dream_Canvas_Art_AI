from pydantic import BaseModel

class KlingTextVideoRequest(BaseModel):
    """Schema for Kling text-to-video generation request"""
    prompt: str

class KlingTextVideoResponse(BaseModel):
    """Schema for Kling text-to-video generation response"""
    video_url: str
    success_message: str
