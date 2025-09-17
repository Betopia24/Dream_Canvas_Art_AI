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


class GeminiImageRequest(BaseModel):
    """Request schema for Gemini image generation"""
    prompt: str = Field(
        ..., 
        description="Text prompt describing the image to generate",
        min_length=1,
        max_length=1000,
        example="A beautiful chocolate lady dancing in the kitchen"
    )


class GeminiImageResponse(BaseModel):
    """Response schema for Gemini image generation"""
    status: int = Field(description="HTTP status code", example=200)
    success_message: str = Field(description="Whether the generation was successful")
    image_url: str = Field(description="URL to the generated image")
    shape: str = Field(description="The shape used for generation")


class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str = Field(description="Error message")