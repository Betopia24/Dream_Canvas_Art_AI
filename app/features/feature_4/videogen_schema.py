from pydantic import BaseModel

class VideoGenRequest(BaseModel):
    """Schema for video generation request"""
    prompt: str

class VideoGenResponse(BaseModel):
    """Schema for video generation response"""
    video_path: str
    success_message: str
