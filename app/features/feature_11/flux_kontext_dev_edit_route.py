from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import Optional
import logging
from .flux_kontext_dev_edit_service import flux_kontext_edit_service
from .flux_kontext_dev_edit_schema import FluxKontextEditResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/flux-kontext-edit", response_model=FluxKontextEditResponse)
async def edit_image_with_flux_kontext(
    prompt: str = Form(..., description="Text prompt describing how to edit the image"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_file: UploadFile = File(..., description="Image file to edit")
):
    """
    Edit an image using Flux Kontext with specified style and shape as query parameters.
    Prompt is sent as form data. Image file is required for editing.
    """
    try:
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(status_code=400, detail="Image file is required for editing")
        
        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        if image_file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed types: {', '.join(allowed_types)}")
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
        logger.info(f"Editing image {image_file.filename} with {style} style in {shape} format")
        
        # Edit the image
        image_path = await flux_kontext_edit_service.edit_image(
            prompt=prompt,
            image_file=image_file,
            style=style,
            shape=shape
        )
        
        success_message = f"Successfully edited image with {style} style in {shape} format using Flux Kontext"
        
        return FluxKontextEditResponse(
            success_message=success_message,
            image_path=image_path,
            style=style
        )
        
    except Exception as e:
        logger.error(f"Error in Flux Kontext image editing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit image: {str(e)}"
        )
