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
    success_message: str = Field(description="Success message with style info")
    image_url: str = Field(description="URL to the edited image")
    style: str = Field(description="The style used for editing")
