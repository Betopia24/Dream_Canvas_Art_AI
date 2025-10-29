from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form, Header
from typing import Optional
import logging
from .flux_kontext_dev_edit_service import flux_kontext_edit_service
from .flux_kontext_dev_edit_schema import FluxKontextEditResponse
from ...core.error_handlers import handle_service_error, validate_file_types

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/flux-kontext-edit", response_model=FluxKontextEditResponse)
async def edit_image_with_flux_kontext(
    prompt: str = Form(..., description="Text prompt describing how to edit the image"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_file: UploadFile = File(..., description="Image file to edit"),
    user_id: str = Header(None)
):
    """
    Edit an image using Flux Kontext with specified style and shape as query parameters.
    Prompt is sent as form data. Image file is required for editing.
    """
    try:
        # Validate prompt
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )
        
        # Validate image file
        if not image_file or not image_file.filename:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Image file is required for editing",
                    "field": "image_file"
                }
            )
        
        # Check file type using utility function
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        validate_file_types([image_file], allowed_types, "image_file")
        
        logger.info(f"Editing image {image_file.filename} with {style} style in {shape} format")
        
        # Edit the image
        image_path = await flux_kontext_edit_service.edit_image(
            prompt=prompt,
            image_file=image_file,
            user_id=user_id,
            style=style,
            shape=shape           
        )       

        success_message = f"Successfully edited image with {style} style in {shape} format using Flux Kontext"
        
        return FluxKontextEditResponse(
            status=200,
            success_message=success_message,
            image_url=image_path,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle fal.ai service errors
        logger.error(f"Error in Flux Kontext image editing: {str(e)}")
        raise handle_service_error(e, "fal.ai", "edit image")
