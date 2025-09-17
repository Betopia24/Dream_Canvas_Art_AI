from fastapi import APIRouter, HTTPException
from .prompt_enhancer_schema import PromptEnhancerRequest, PromptEnhancerResponse
from .prompt_enhancer_service import prompt_enhancer_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/prompt-enhancer",
    tags=["Prompt Enhancer"]
)


@router.post("/enhance", response_model=PromptEnhancerResponse)
async def enhance_prompt(request: PromptEnhancerRequest):
    """
    Enhance a text prompt for better AI image generation
    
    - **prompt**: The original text prompt to enhance
    """
    try:
        logger.info(f"Received prompt enhancement request")
        
        # Enhance the prompt
        enhanced_prompt = prompt_enhancer_service.enhance_prompt(request.prompt)
        
        return PromptEnhancerResponse(
            status=200,
            success_message="Prompt enhanced successfully",
            enhanced_prompt=enhanced_prompt
        )
        
    except Exception as e:
        logger.error(f"Error in prompt enhancement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to enhance prompt: {str(e)}"
        )