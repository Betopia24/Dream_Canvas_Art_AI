from pydantic import BaseModel

class PixverseImageVideoResponse(BaseModel):
    """Schema for Pixverse image-to-video generation response"""
    video_url: str
    success_message: str
