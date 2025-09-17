from pydantic import BaseModel, Field

class VideoGen3Request(BaseModel):
    """Schema for Veo 3 video generation request"""
    prompt: str

class VideoGen3Response(BaseModel):
    """Schema for Veo 3 video generation response"""
    video_path: str
    success_message: str
    status: int = Field(description="HTTP status code", example=200)
