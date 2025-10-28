import base64
import mimetypes
import os
import uuid
import logging
import sys
from typing import Optional, List
from fastapi import UploadFile
from google import genai
from google.genai import types
from google.cloud import storage
from PIL import Image
import io

# Add the app directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import config

logger = logging.getLogger(__name__)


class GeminiNanoBananaService:
    def __init__(self):
        """Initialize the Gemini NanoBanana streaming image generation service"""
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required in .env file")
        
        self.client = genai.Client(api_key=self.api_key)
        self.output_dir = config.IMAGES_DIR
        self.model = "gemini-2.5-flash-image-preview"
        
        # Do NOT auto-create runtime folders inside the container. Expect the
        # environment (mounted volume, GCS, or host) to provide this directory.
        # os.makedirs(self.output_dir, exist_ok=True)

    def _resize_image_if_needed(self, image_content: bytes, max_dimension: int = 4000) -> bytes:
        """
        Resize image if it exceeds maximum dimensions to prevent API issues
        
        Args:
            image_content (bytes): Original image content
            max_dimension (int): Maximum width or height allowed
            
        Returns:
            bytes: Resized image content
        """
        try:
            # Open the image
            image = Image.open(io.BytesIO(image_content))
            original_width, original_height = image.size
            
            logger.info(f"Original image dimensions: {original_width}x{original_height}")
            
            # Check if resizing is needed
            if original_width <= max_dimension and original_height <= max_dimension:
                logger.info("Image dimensions are within limits, no resizing needed")
                return image_content
            
            # Calculate new dimensions while maintaining aspect ratio
            if original_width > original_height:
                new_width = max_dimension
                new_height = int((original_height * max_dimension) / original_width)
            else:
                new_height = max_dimension
                new_width = int((original_width * max_dimension) / original_height)
            
            logger.info(f"Resizing image to: {new_width}x{new_height}")
            
            # Resize the image
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save resized image to bytes
            output_buffer = io.BytesIO()
            # Preserve original format, default to JPEG if unknown
            format_to_use = image.format if image.format else 'JPEG'
            resized_image.save(output_buffer, format=format_to_use, quality=95)
            resized_content = output_buffer.getvalue()
            
            logger.info(f"Image resized successfully. Original size: {len(image_content)} bytes, New size: {len(resized_content)} bytes")
            return resized_content
            
        except Exception as e:
            logger.error(f"Error resizing image: {str(e)}")
            # Return original content if resizing fails
            return image_content

    def save_binary_file(self, file_name: str, data: bytes) -> str:
        """
        Save binary data to file
        
        Args:
            file_name: Name of the file to save
            data: Binary data to save
            
        Returns:
            str: Full path to saved file
        """
        filepath = os.path.join(self.output_dir, file_name)
        with open(filepath, "wb") as f:
            f.write(data)
        logger.info(f"File saved to: {filepath}")
        return filepath

    async def generate_banana_costume_image(self, prompt: str = "Generate an image of a banana wearing a costume.", user_id: str = None, style: str = "Photo", shape: str = "square", image_files: Optional[List[UploadFile]] = None) -> tuple[str, str]:
        """
        Generate a banana costume image using Gemini's streaming image generation with style and shape
        
        Args:
            prompt: Text description of the banana costume image to generate
            user_id: The user ID for folder organization
            style: The style for the image (Photo, Illustration, Comic, etc.)
            shape: The shape/aspect ratio of the image (square, portrait, landscape)
            image_files: Optional list of image files to use as reference for guided generation (maximum 4 images)
            
        Returns:
            tuple: (filename, image_url)
        """

        try:
            logger.info(f"Generating banana costume image with Gemini streaming for prompt: {prompt[:50]}...")

            # Create styled prompt by incorporating the style
            styled_prompt = f"{prompt}, in {style.lower()} style"

            # Prepare content parts - start with text prompt
            content_parts = [types.Part.from_text(text=styled_prompt)]

            # Add image references if provided
            if image_files and len(image_files) > 0:
                # Limit to maximum 4 images to avoid API limits
                max_images = min(len(image_files), 4)
                successfully_added = 0
                
                for i, image_file in enumerate(image_files[:max_images]):
                    if image_file and image_file.filename:
                        try:
                            logger.info(f"Adding reference image {i+1}: {image_file.filename}")
                            # Read the image file
                            image_content = await image_file.read()
                            
                            # Resize image if it exceeds reasonable dimensions
                            resized_content = self._resize_image_if_needed(image_content)
                            
                            # Add image as reference to the content
                            content_parts.append(
                                types.Part.from_bytes(
                                    data=resized_content,
                                    mime_type=image_file.content_type or "image/jpeg"
                                )
                            )
                            successfully_added += 1
                        except Exception as e:
                            logger.warning(f"Failed to process reference image {image_file.filename}: {e}. Skipping this image.")
                
                if successfully_added > 0:
                    # Enhance prompt to indicate using reference images
                    styled_prompt = f"{styled_prompt}. Use the provided {successfully_added} reference image{'s' if successfully_added > 1 else ''} as visual reference for style and composition."
                    content_parts[0] = types.Part.from_text(text=styled_prompt)

            # Prepare content for the streaming API
            contents = [
                types.Content(
                    role="user",
                    parts=content_parts,
                ),
            ]

            # Configure generation for image and text response
            generate_content_config = types.GenerateContentConfig(
                response_modalities=[
                    "IMAGE",
                    "TEXT",
                ],
            )

            file_index = 0
            generated_filename = None
            image_url = None
            # Stream the response
            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue

                # Check for image data in the chunk
                if (chunk.candidates[0].content.parts[0].inline_data and 
                    chunk.candidates[0].content.parts[0].inline_data.data):

                    # Generate unique filename with style and shape info
                    base_filename = f"nanobanana_{style}_{shape}_{uuid.uuid4().hex}_{file_index}"
                    file_index += 1

                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    mime_type = inline_data.mime_type
                    file_extension = mimetypes.guess_extension(mime_type)

                    if file_extension is None:
                        file_extension = ".png"  # Default to PNG if can't determine

                    generated_filename = f"{base_filename}{file_extension}"

                    # Try uploading bytes directly to GCS
                    try:
                        destination_blob_name = f"image/{user_id}/{generated_filename}"
                        storage_client = storage.Client()
                        bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                        blob = bucket.blob(destination_blob_name)
                        content_type = mime_type or 'image/png'
                        blob.upload_from_string(data_buffer, content_type=content_type)
                        image_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                        logger.info(f"Banana costume image generated successfully with {style} style in {shape} format: {generated_filename}")
                        return generated_filename, image_url
                    except Exception as e:
                        logger.error(f"Error uploading streamed image to GCS: {e}")
                        # Save locally as fallback
                        self.save_binary_file(generated_filename, data_buffer)
                        image_url = f"{config.BASE_URL}/images/{generated_filename}"
                        logger.info(f"Banana costume image generated successfully (local fallback) with {style} style in {shape} format: {generated_filename}")
                        return generated_filename, image_url

                else:
                    # Log any text response
                    if hasattr(chunk, 'text') and chunk.text:
                        logger.info(f"Text response: {chunk.text}")

            if generated_filename is None or image_url is None:
                raise Exception("No image data received from Gemini streaming API")

        except Exception as e:
            logger.error(f"Error generating banana costume image with Gemini streaming: {str(e)}")
            raise Exception(f"Failed to generate banana costume image: {str(e)}")


# Create a singleton instance
gemini_nanobanana_service = GeminiNanoBananaService()