from fastapi import APIRouter, HTTPException
import logging
from .dream_interpreter import dream_interpreter_service
from .dream_interpreter_schema import DreamInterpreterRequest, DreamInterpreterResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/dream-interpreter", response_model=DreamInterpreterResponse)
async def interpret_dream(request: DreamInterpreterRequest):
    """
    Simple dream interpretation endpoint
    - Takes a dream description
    - Returns interpretation and dream image
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Dream prompt is required")
        
        logger.info(f"Dream request: {request.prompt[:30]}...")
        
        # Process dream
        result = await dream_interpreter_service.interpret_dream(request.prompt)
        
        return DreamInterpreterResponse(
            success_message=result["success_message"],
            image_url=result["image_url"],
            dream_interpretation=result["dream_interpretation"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process dream: {str(e)}")
