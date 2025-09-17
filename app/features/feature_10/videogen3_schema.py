from pydantic import BaseModel, Field

class VideoGen3Request(BaseModel):
    """Schema for Veo 3 video generation request"""
    prompt: str

class VideoGen3Response(BaseModel):
    """Schema for Veo 3 video generation response"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    video_path: str = Field(description="Local path to the generated video")
