from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import List
import logging
from .seedream_image_edit_service import seedream_image_edit_service
from .seedream_image_edit_schema import SeedreamImageEditResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/seedream-image-edit", response_model=SeedreamImageEditResponse)
async def edit_images_with_seedream(
    prompt: str = Form(..., description="Text prompt describing how to edit the images or generate new images"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_files: List[UploadFile] = File(None, description="Image files to edit (maximum 4 images). Optional - if not provided, will generate new images")
):
    """
    Edit multiple images (max 4) using SeeDream with specified style and shape as query parameters.
    Prompt is sent as form data. Image files are optional - if not provided, will generate new images instead of editing.
    """
    try:
        # Check if image files are provided
        is_editing_mode = image_files and len(image_files) > 0 and image_files[0].filename
        
        if is_editing_mode:
            # Validate image files for editing mode
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
        
        if is_editing_mode:
            logger.info(f"Editing {len(image_files)} images with {style} style in {shape} format")
            action_message = f"Images edited successfully with SeeDream in {style} style"
        else:
            logger.info(f"Generating new image with {style} style in {shape} format")
            action_message = f"Image generated successfully with SeeDream in {style} style"
        
        # Process the images (edit or generate)
        image_url = await seedream_image_edit_service.process_images(
            prompt=prompt,
            image_files=image_files if is_editing_mode else None,
            style=style,
            shape=shape
        )
        
        return SeedreamImageEditResponse(
            status=200,
            success_message=action_message,
            image_url=image_url,
            shape=shape
            
        )
        
    except Exception as e:
        logger.error(f"Error in SeeDream image processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process images: {str(e)}"
        )
