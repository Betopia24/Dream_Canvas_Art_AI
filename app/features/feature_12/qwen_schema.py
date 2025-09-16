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

class QwenRequest(BaseModel):
    """Request schema for Qwen image generation"""
    prompt: str = Field(
        ...,
        description="Text prompt describing the image to generate",
        min_length=1,
        max_length=1000,
        example="A beautiful landscape with mountains and a lake"
    )

class QwenResponse(BaseModel):
    """Response schema for Qwen image generation"""
    success_message: str = Field(description="Success message")
    image_url: str = Field(description="URL to the generated image")
    style: str = Field(description="The style used for generation")
