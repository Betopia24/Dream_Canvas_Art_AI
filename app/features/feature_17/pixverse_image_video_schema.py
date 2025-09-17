from pydantic import BaseModel, Field

class PixverseImageVideoResponse(BaseModel):
    """Schema for Pixverse image-to-video generation response"""
    video_url: str
    success_message: str
    status: int = Field(description="HTTP status code", example=200)
