from pydantic import BaseModel, Field
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

class FluxKontextEditResponse(BaseModel):
    """Response schema for Flux Kontext image editing"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message with shape info")
    image_url: str = Field(description="URL to the edited image")
    shape: str = Field(description="The shape used for editing")
    

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str = Field(description="Error message")
