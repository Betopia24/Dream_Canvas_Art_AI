from fastapi import APIRouter, HTTPException, Query
from .dream_interpreter import dream_interpreter_service
from .dream_interpreter_schema import DreamInterpreterRequest, DreamInterpreterResponse

router = APIRouter()

@router.post("/dream-interpreter/generate", response_model=DreamInterpreterResponse)
async def interpret_dream(request: DreamInterpreterRequest, style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"), shape: str = Query(..., description="Image shape: square, portrait, landscape") ):
    """
    Simple dream interpretation endpoint
    - Takes a dream description
    - Returns interpretation and dream image
    """
    try:
        if not request.prompt.strip():
            raise HTTPException(status_code=400, detail="Dream prompt is required")
        
        result = await dream_interpreter_service.interpret_dream(request.prompt, style, shape)
        if not isinstance(result, dict):
            raise HTTPException(status_code=500, detail="Image generation failed")

        image_url = result.get("image_url")
        success_message = result.get("success_message", "")
        dream_interpretation = result.get("dream_interpretation", "")

        if not image_url:
            raise HTTPException(status_code=500, detail="Image generation failed")

        return DreamInterpreterResponse(
            status=200,
            success_message=success_message,
            image_url=image_url,
            dream_interpretation=dream_interpretation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process dream: {str(e)}")
