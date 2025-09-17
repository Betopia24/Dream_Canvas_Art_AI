from pydantic import BaseModel, Field

class AIAvatarResponse(BaseModel):
    """Schema for AI Avatar video generation response"""
    status: int = Field(description="HTTP status code", example=200)
    video_url: str = Field(description="URL to the generated video")
    success_message: str = Field(description="Success message")
