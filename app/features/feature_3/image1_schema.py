# from pydantic import BaseModel, Field
# from enum import Enum

# class StyleEnum(str, Enum):
#     """Available styles for image generation"""
#     PHOTO = "Photo"
#     ILLUSTRATION = "Illustration"
#     COMIC = "Comic"
#     ANIME = "Anime"
#     ABSTRACT = "Abstract"
#     FANTASY = "Fantasy"
#     POP_ART = "PopArt"

# class ShapeEnum(str, Enum):
#     """Available shapes for image generation"""
#     SQUARE = "square"
#     PORTRAIT = "portrait"
#     LANDSCAPE = "landscape"

# class Image1Response(BaseModel):
#     """Schema for GPT-Image-1 generation response"""
#     image_url: str = Field(description="URL to the generated image")
#     success_message: str = Field(description="Success message with style info")
#     shape: str = Field(description="The shape used for generation")
