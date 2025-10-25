from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
from typing import List, Union, Optional
import logging
from .seedream_image_edit_service import seedream_image_edit_service
from .seedream_image_edit_schema import SeedreamImageEditResponse
from ...core.error_handlers import (
    validate_file_types, 
    validate_file_count, 
    validate_parameter_choice,
    validate_required_fields,
    handle_service_error,
    ErrorMessages
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/seedream-image-edit", response_model=SeedreamImageEditResponse)
async def edit_images_with_seedream(
    prompt: str = Form(..., description="Text prompt describing how to edit the images or generate new images"),
    style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
    shape: str = Query(..., description="Image shape: square, portrait, landscape"),
    image_files: Union[List[UploadFile], None] = File(default=None, description="Image files to edit (maximum 4 images). Optional - if not provided, will generate new images")
):
    """
    Edit multiple images (max 4) using SeeDream with specified style and shape as query parameters.
    Prompt is sent as form data. Image files are optional - if not provided, will generate new images instead of editing.
    """
    try:
        # Validate required fields
        if not prompt or not prompt.strip():
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Validation Error",
                    "message": "Prompt is required and cannot be empty",
                    "field": "prompt"
                }
            )
        
        # Validate style parameter
        valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
        validate_parameter_choice(style, valid_styles, "style")
        
        # Validate shape parameter  
        valid_shapes = ["square", "portrait", "landscape"]
        validate_parameter_choice(shape, valid_shapes, "shape")
        
        # Handle and validate image files
        is_editing_mode = False
        valid_image_files = []
        
        if image_files is not None:
            # Handle different input formats
            if isinstance(image_files, list):
                logger.info(f"Processing {len(image_files)} files from list")
                
                # Filter valid UploadFile objects
                for idx, file in enumerate(image_files):
                    if hasattr(file, 'filename') and hasattr(file, 'content_type'):
                        if file.filename and file.filename.strip():
                            valid_image_files.append(file)
                            logger.info(f"Valid file {idx}: {file.filename}")
                        else:
                            logger.warning(f"Empty filename for file {idx}")
                    else:
                        # This handles the case where strings are passed instead of UploadFile
                        if file and str(file).strip():
                            raise HTTPException(
                                status_code=400,
                                detail={
                                    "error": "Invalid File Format", 
                                    "message": "Files must be uploaded as multipart/form-data, not as text strings. Please use the file upload field in your client.",
                                    "field": f"image_files[{idx}]",
                                    "received_type": str(type(file).__name__),
                                    "expected_type": "UploadFile"
                                }
                            )
                
                if valid_image_files:
                    is_editing_mode = True
                    logger.info(f"Found {len(valid_image_files)} valid image files for editing")
                    
            elif hasattr(image_files, 'filename'):
                # Single file case
                if image_files.filename and image_files.filename.strip():
                    valid_image_files = [image_files]
                    is_editing_mode = True
                    logger.info(f"Single valid image file: {image_files.filename}")
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Invalid File Format",
                        "message": "Files must be uploaded as multipart/form-data. Please ensure you're using the correct file upload method.",
                        "field": "image_files",
                        "received_type": str(type(image_files).__name__),
                        "expected_type": "UploadFile or List[UploadFile]"
                    }
                )
        
        if is_editing_mode:
            # Validate file count
            validate_file_count(valid_image_files, 4, "image_files")
            
            # Validate file types
            allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
            validate_file_types(valid_image_files, allowed_types, "image_files")
            
            # Additional file validation
            for i, image_file in enumerate(valid_image_files):
                if not image_file.filename:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Invalid File",
                            "message": f"File {i+1} has no filename or is corrupted",
                            "field": f"image_files[{i}]"
                        }
                    )
            
            logger.info(f"Editing {len(valid_image_files)} images with {style} style in {shape} format")
            action_message = f"Images edited successfully with SeeDream in {style} style"
        else:
            logger.info(f"Generating new image with {style} style in {shape} format")
            action_message = f"Image generated successfully with SeeDream in {style} style"
        
        # Process the images (edit or generate)
        image_url = await seedream_image_edit_service.process_images(
            prompt=prompt,
            image_files=valid_image_files if is_editing_mode else None,
            style=style,
            shape=shape
        )
        
        return SeedreamImageEditResponse(
            status=200,
            success_message=action_message,
            image_url=image_url,
            shape=shape
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (these are our custom validation errors)
        raise
    except Exception as e:
        # Handle unexpected service errors
        logger.error(f"Unexpected error in SeeDream image processing: {str(e)}")
        raise handle_service_error(e, "SeeDream", "process images")
