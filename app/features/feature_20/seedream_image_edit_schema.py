from pydantic import BaseModel, Field
from enum import Enum

class StyleEnum(str, Enum):
    """Available styles for image editing"""
    PHOTO = "Photo"
    ILLUSTRATION = "Illustration"
    COMIC = "Comic"
    ANIME = "Anime"
    ABSTRACT = "Abstract"
    FANTASY = "Fantasy"
    POP_ART = "PopArt"

class ShapeEnum(str, Enum):
    """Available shapes for image editing"""
    SQUARE = "square"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

class SeedreamImageEditResponse(BaseModel):
    """Response schema for SeeDream image editing"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message with shape info")
    image_url: str = Field(description="URL to the edited image")
    shape: str = Field(description="The shape used for editing")
    