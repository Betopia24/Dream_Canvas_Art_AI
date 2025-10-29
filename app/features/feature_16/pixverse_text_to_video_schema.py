from pydantic import BaseModel, Field


from enum import Enum

class ShapeEnum(str, Enum):
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class PixverseTextImageRequest(BaseModel):
    """Schema for Pixverse text-to-video generation request"""
    prompt: str


class PixverseTextImageResponse(BaseModel):
    """Schema for Pixverse text-to-video generation response"""
    success_message: str = Field(description="Success message")
    status: int = Field(description="HTTP status code", example=200)
    video_url: str = Field(description="URL to the generated video")

