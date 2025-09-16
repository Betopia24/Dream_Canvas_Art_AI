from pydantic import BaseModel, Field

class AIAvatarResponse(BaseModel):
    """Schema for AI Avatar video generation response"""
    video_url: str = Field(description="URL to the generated video")
    success_message: str = Field(description="Success message")
