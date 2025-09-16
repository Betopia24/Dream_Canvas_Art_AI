from pydantic import BaseModel
from enum import Enum

class StyleEnum(str, Enum):
    """Available styles for image generation"""
    PHOTO = "Photo"
    ILLUSTRATION = "Illustration"
    COMIC = "Comic"
    ANIME = "Anime"
    ABSTRACT = "Abstract"
    FANTASY = "Fantasy"
    POP_ART = "PopArt"

class ShapeEnum(str, Enum):
    """Available shapes for image generation"""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class DalleRequest(BaseModel):
    """Schema for DALL-E image generation request"""
    prompt: str

class DalleResponse(BaseModel):
    """Schema for DALL-E image generation response"""
    image_path: str
    success_message: str
    shape: str
