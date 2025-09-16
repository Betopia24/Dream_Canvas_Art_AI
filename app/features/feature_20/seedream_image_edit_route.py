from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import List
import logging
from .seedream_image_edit_service import seedream_image_edit_service
from .seedream_image_edit_schema import SeedreamImageEditResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/seedream-image-edit", response_model=SeedreamImageEditResponse)
async def edit_images_with_seedream(
    prompt: str = Form(..., description="Text prompt describing how to edit the images"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_files: List[UploadFile] = File(..., description="Image files to edit (maximum 4 images)")
):
    """
    Edit multiple images (max 4) using SeeDream with specified style and shape as query parameters.
    Prompt is sent as form data. Multiple image files are required for editing.
    """
    try:
        # Validate image files
        if not image_files or len(image_files) == 0:
            raise HTTPException(status_code=400, detail="At least one image file is required for editing")
        
        if len(image_files) > 4:
            raise HTTPException(status_code=400, detail="Maximum 4 images allowed")
        
        # Check each file
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        for i, image_file in enumerate(image_files):
            if not image_file or not image_file.filename:
                raise HTTPException(status_code=400, detail=f"Image file {i+1} is empty or invalid")
            
            if image_file.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail=f"Invalid file type for image {i+1}. Allowed types: {', '.join(allowed_types)}")
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        if style not in valid_styles:
            raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
        # Validate shape parameter
        valid_shapes = ["square", "portrait", "landscape"]
        if shape not in valid_shapes:
            raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
        logger.info(f"Editing {len(image_files)} images with {style} style in {shape} format")
        
        # Edit the images
        image_url = await seedream_image_edit_service.edit_images(
            prompt=prompt,
            image_files=image_files,
            style=style,
            shape=shape
        )
        
        return SeedreamImageEditResponse(
            success_message=f"Images edited successfully with SeeDream in {style} style",
            image_url=image_url,
            style=style
        )
        
    except Exception as e:
        logger.error(f"Error in SeeDream image editing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to edit images: {str(e)}"
        )
