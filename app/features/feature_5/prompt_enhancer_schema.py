from pydantic import BaseModel, Field


class PromptEnhancerRequest(BaseModel):
    """Request schema for prompt enhancement"""
    prompt: str = Field(
        ..., 
        description="Original text prompt to enhance for image generation",
        min_length=1,
        max_length=500,
        example="a beautiful landscape"
    )


class PromptEnhancerResponse(BaseModel):
    """Response schema for prompt enhancement"""
    success: bool = Field(description="Whether the enhancement was successful")
    message: str = Field(description="Status message")
    enhanced_prompt: str = Field(description="The enhanced prompt optimized for image generation")
