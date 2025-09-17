from pydantic import BaseModel, Field

class PixverseImageVideoResponse(BaseModel):
    """Schema for Pixverse image-to-video generation response"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    video_url: str = Field(description="URL to the generated video")
    