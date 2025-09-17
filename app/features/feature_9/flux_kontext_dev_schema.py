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

class FluxKontextDevRequest(BaseModel):
    """Request schema for Flux Kontext Dev image generation"""
    prompt: str = Field(
        ...,
        description="Text prompt describing the image to generate",
        min_length=1,
        max_length=1000,
        example="A beautiful landscape with mountains and a lake"
    )

class FluxKontextDevResponse(BaseModel):
    """Response schema for Flux Kontext Dev image generation"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Success message with shape info")
    image_path: str = Field(description="Local path to the generated image")
    shape: str = Field(description="The shape used for generation")
