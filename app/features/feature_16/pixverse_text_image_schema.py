from pydantic import BaseModel

class PixverseTextImageRequest(BaseModel):
    """Schema for Pixverse text-to-video generation request"""
    prompt: str

class PixverseTextImageResponse(BaseModel):
    """Schema for Pixverse text-to-video generation response"""
    video_url: str
    success_message: str
