from fastapi import APIRouter, HTTPException, Query
from .dalle_schema import DalleRequest, DalleResponse, StyleEnum, ShapeEnum
from .dalle_service import DalleService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["dalle"], prefix="/dalle")
dalle_service = DalleService()

@router.post("/generate", response_model=DalleResponse)
async def generate_image(
    request: DalleRequest,
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape")
):
    """
    Generate an image using DALL-E 3 with specified style and shape as query parameters
    """
    try:
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
        image_path = await dalle_service.generate_image(
            prompt=request.prompt,
            style=style,
            shape=shape
        )
        
        success_message = f"Successfully generated and saved {style} style image in {shape} format"
        
        return DalleResponse(
            status=200,
            success_message=success_message,
            image_path=image_path,
            shape=shape
        )
        
    except Exception as e:
        logger.error(f"Error in image generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
