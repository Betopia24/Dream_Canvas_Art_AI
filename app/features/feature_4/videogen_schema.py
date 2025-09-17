from pydantic import BaseModel

class VideoGenRequest(BaseModel):
    """Schema for video generation request"""
    prompt: str

class VideoGenResponse(BaseModel):
    """Schema for video generation response"""
    status: int = 200
    video_path: str
    success_message: str
