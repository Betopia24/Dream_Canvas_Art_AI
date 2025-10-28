from fastapi import APIRouter, HTTPException, Query, Header
from .dream_interpreter import dream_interpreter_service
from .dream_interpreter_schema import DreamInterpreterRequest, DreamInterpreterResponse
from ...core.error_handlers import handle_service_error

router = APIRouter()

@router.post("/dream-interpreter/generate", response_model=DreamInterpreterResponse)
async def interpret_dream(request: DreamInterpreterRequest, user_id: str = Header(None), style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"), shape: str = Query(..., description="Image shape: square, portrait, landscape")):
    """
    Simple dream interpretation endpoint
    - Takes a dream description
    - Returns interpretation and dream image
    """
    try:
        # Validate prompt
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Dream prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )

        result = await dream_interpreter_service.interpret_dream(request.prompt, user_id, style, shape)
        
        if not isinstance(result, dict):
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Service Error",
                    "message": "Dream interpretation service returned invalid response format",
                    "details": {"expected": "dict", "received": type(result).__name__}
                }
            )

        image_url = result.get("image_url")
        success_message = result.get("success_message", "")
        dream_interpretation = result.get("dream_interpretation", "")

        if not image_url or image_url == "No image generated":
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Image Generation Failed",
                    "message": "Failed to generate dream image. Please try again with a different prompt.",
                    "details": {"service": "dream_interpreter", "operation": "image_generation"}
                }
            )

        return DreamInterpreterResponse(
            status=200,
            success_message=success_message,
            image_url=image_url,
            dream_interpretation=dream_interpretation
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are our custom validation errors)
        raise
    except Exception as e:
        # Handle unexpected service errors
        raise handle_service_error(e, "DreamInterpreter", "interpret dream")
