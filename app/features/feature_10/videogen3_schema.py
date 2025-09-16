from pydantic import BaseModel

class VideoGen3Request(BaseModel):
    """Schema for Veo 3 video generation request"""
    prompt: str

class VideoGen3Response(BaseModel):
    """Schema for Veo 3 video generation response"""
    video_path: str
    success_message: str
