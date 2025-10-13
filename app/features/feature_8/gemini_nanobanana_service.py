import base64
import mimetypes
import os
import uuid
import logging
import sys
from typing import Optional
from fastapi import UploadFile
from google import genai
from google.genai import types
from google.cloud import storage

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
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

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

    async def generate_banana_costume_image(self, prompt: str = "Generate an image of a banana wearing a costume.", style: str = "Photo", shape: str = "square", image_file: Optional[UploadFile] = None) -> tuple[str, str]:
        """
        Generate a banana costume image using Gemini's streaming image generation with style and shape
        
        Args:
            prompt: Text description of the banana costume image to generate
            style: The style for the image (Photo, Illustration, Comic, etc.)
            shape: The shape/aspect ratio of the image (square, portrait, landscape)
            image_file: Optional image file to use as reference for guided generation
            
        Returns:
            tuple: (filename, image_url)
        """
        try:
            logger.info(f"Generating banana costume image with Gemini streaming for prompt: {prompt[:50]}...")
            
            # Create styled prompt by incorporating the style
            styled_prompt = f"{prompt}, in {style.lower()} style"
            
            # Prepare content parts - start with text prompt
            content_parts = [types.Part.from_text(text=styled_prompt)]
            
            # Add image reference if provided
            if image_file and image_file.filename:
                try:
                    logger.info(f"Adding reference image: {image_file.filename}")
                    # Read the image file
                    image_content = await image_file.read()
                    # Add image as reference to the content
                    content_parts.append(
                        types.Part.from_bytes(
                            data=image_content,
                            mime_type=image_file.content_type or "image/jpeg"
                        )
                    )
                    # Enhance prompt to indicate using reference
                    styled_prompt = f"{styled_prompt}. Use the provided image as visual reference for style and composition."
                    content_parts[0] = types.Part.from_text(text=styled_prompt)
                except Exception as e:
                    logger.warning(f"Failed to process reference image {image_file.filename}: {e}. Proceeding with text-only generation.")
            
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
                    
                    # Save the image to local directory (same as feature_7)
                    self.save_binary_file(generated_filename, data_buffer)
                    
                else:
                    # Log any text response
                    if hasattr(chunk, 'text') and chunk.text:
                        logger.info(f"Text response: {chunk.text}")

            if generated_filename is None:
                raise Exception("No image data received from Gemini streaming API")
            
            # Try to upload to GCS and return plain storage URL
            try:
                destination_blob_name = f"image/{generated_filename}"
                storage_client = storage.Client()
                bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_filename(os.path.join(self.output_dir, generated_filename))
                image_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
            except Exception as e:
                logger.error(f"Error uploading to GCS: {e}")
                image_url = f"{config.BASE_URL}/images/{generated_filename}"
            
            logger.info(f"Banana costume image generated successfully with {style} style in {shape} format: {generated_filename}")
            return generated_filename, image_url
            
        except Exception as e:
            logger.error(f"Error generating banana costume image with Gemini streaming: {str(e)}")
            raise Exception(f"Failed to generate banana costume image: {str(e)}")


# Create a singleton instance
gemini_nanobanana_service = GeminiNanoBananaService()