from pydantic import BaseModel, Field
from enum import Enum

class ShapeEnum(str, Enum):
    """Available shapes for video generation"""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class Wan22ImageVideoRequest(BaseModel):
    """Schema for WAN 2.2 image-to-video generation request"""
    prompt: str

class Wan22ImageVideoResponse(BaseModel):
    """Schema for WAN 2.2 image-to-video generation response"""
    success_message: str = Field(description="Success message")
    status: int = Field(description="HTTP status code", example=200)
    video_url: str = Field(description="URL to the generated video")

