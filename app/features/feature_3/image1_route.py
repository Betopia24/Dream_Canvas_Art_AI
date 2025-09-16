# from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Form
# from typing import List
# import logging
# from .image1_service import image1_service
# from .image1_schema import Image1Response

# router = APIRouter()
# logger = logging.getLogger(__name__)

# @router.post("/gpt-image-1", response_model=Image1Response)
# async def generate_image_with_gpt_image1(
#     prompt: str = Form(..., description="Text prompt describing the image to generate"),
#     style: str = Query(..., description="Image style: Photo, Illustration, Comic, Anime, Abstract, Fantasy, PopArt"),
#     shape: str = Query(..., description="Image shape: square, portrait, landscape"),
#     image_files: List[UploadFile] = File(..., description="Input image files for reference (maximum 5 images)")
# ):
#     """
#     Generate an image using GPT-Image-1 with multiple input images (max 5) and specified style and shape.
#     Prompt is sent as form data. Multiple image files are used as reference.
#     """
#     try:
#         # Validate image files
#         if not image_files or len(image_files) == 0:
#             raise HTTPException(status_code=400, detail="At least one image file is required")
        
#         if len(image_files) > 5:
#             raise HTTPException(status_code=400, detail="Maximum 5 images allowed")
        
#         # Check each file
#         allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
#         for i, image_file in enumerate(image_files):
#             if not image_file or not image_file.filename:
#                 raise HTTPException(status_code=400, detail=f"Image file {i+1} is empty or invalid")
            
#             if image_file.content_type not in allowed_types:
#                 raise HTTPException(status_code=400, detail=f"Invalid file type for image {i+1}. Allowed types: {', '.join(allowed_types)}")
        
#         # Validate style parameter
#         valid_styles = ["Photo", "Illustration", "Comic", "Anime", "Abstract", "Fantasy", "PopArt"]
#         if style not in valid_styles:
#             raise HTTPException(status_code=400, detail=f"Invalid style. Must be one of: {', '.join(valid_styles)}")
        
#         # Validate shape parameter
#         valid_shapes = ["square", "portrait", "landscape"]
#         if shape not in valid_shapes:
#             raise HTTPException(status_code=400, detail=f"Invalid shape. Must be one of: {', '.join(valid_shapes)}")
        
#         logger.info(f"Generating image with {len(image_files)} input images using {style} style in {shape} format")
        
#         # Generate the image
#         image_url = await image1_service.generate_image(
#             prompt=prompt,
#             image_files=image_files,
#             style=style,
#             shape=shape
#         )
        
#         return Image1Response(
#             image_url=image_url,
#             success_message=f"Image generated successfully with GPT-Image-1 in {style} style",
#             shape=shape
#         )
        
#     except Exception as e:
#         logger.error(f"Error in GPT-Image-1 generation: {str(e)}")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to generate image: {str(e)}"
#         )
