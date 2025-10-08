from pydantic import BaseModel, Field
from enum import Enum

class ShapeEnum(str, Enum):
    """Available shapes for video generation"""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class KlingImageVideoRequest(BaseModel):
    """Schema for Kling image-to-video generation request"""
    prompt: str

class KlingImageVideoResponse(BaseModel):
    """Schema for Kling image-to-video generation response"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message")
    video_url: str = Field(description="URL to the generated video")
    
