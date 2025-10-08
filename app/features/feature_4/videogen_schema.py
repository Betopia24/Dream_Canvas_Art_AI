from pydantic import BaseModel
from enum import Enum

class ShapeEnum(str, Enum):
    """Available shapes for video generation"""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class VideoGenRequest(BaseModel):
    """Schema for video generation request"""
    prompt: str

class VideoGenResponse(BaseModel):
    """Schema for video generation response"""
    status: int = 200
    success_message: str
    video_url: str
