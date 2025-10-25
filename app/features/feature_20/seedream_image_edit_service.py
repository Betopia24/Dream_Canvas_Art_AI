import logging
import os
import requests
from datetime import datetime
import fal_client
import base64
from typing import List
from fastapi import UploadFile
from app.core.config import config
from PIL import Image
import io

logger = logging.getLogger(__name__)
from google.cloud import storage

class SeedreamImageEditService:
    """Service for editing images and generating new images using ByteDance SeeDream from FAL.ai"""
    
    def __init__(self):
        self.api_key = config.FAL_API_KEY
        if not self.api_key:
            raise ValueError("FAL_API_KEY is required in .env file")
        
        # Configure FAL client
        os.environ["FAL_KEY"] = self.api_key
        fal_client.api_key = self.api_key
        
        self.images_folder = "generated_images"
        # Create the folder if it doesn't exist
        os.makedirs(self.images_folder, exist_ok=True)
        
    def _resize_image_if_needed(self, image_content: bytes, max_dimension: int = 4000) -> bytes:
        """
        Resize image if it exceeds FAL.ai's maximum dimensions (4000x4000)
        
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
        
    async def process_images(self, prompt: str, image_files: List[UploadFile] = None, style: str = "Photo", shape: str = "square") -> str:
        """
        Process images - either edit existing images or generate new images
        
        Args:
            prompt (str): The edit description prompt or generation prompt
            image_files (List[UploadFile], optional): List of image files to edit (max 4). If None, generates new images
            style (str): Style of the image (Photo, Illustration, etc.)
            shape (str): Shape/aspect ratio (square, portrait, landscape)
            
        Returns:
            str: Local image URL of the processed image
        """
        if image_files and len(image_files) > 0 and image_files[0].filename:
            # Edit mode - process existing images
            return await self.edit_images(prompt, image_files, style, shape)
        else:
            # Generation mode - create new images
            return await self.generate_images(prompt, style, shape)
    
    async def edit_images(self, prompt: str, image_files: List[UploadFile], style: str = "Photo", shape: str = "square") -> str:
        """
        Edit images using SeeDream and save it locally
        
        Args:
            prompt (str): The edit description prompt
            image_files (List[UploadFile]): List of image files to edit (max 4)
            style (str): Style of the edited image (Photo, Illustration, etc.)
            shape (str): Shape/aspect ratio (square, portrait, landscape)
            
        Returns:
            str: Local image URL of the edited image
        """
        try:
            logger.info(f"Editing {len(image_files)} images in {style} style with {shape} format using SeeDream for prompt: {prompt[:50]}...")
            
            # Validate number of images
            if len(image_files) > 4:
                raise ValueError("Maximum 4 images allowed")
            
            # Process all uploaded images
            image_data_urls = []
            for i, image_file in enumerate(image_files):
                # Read the uploaded image
                image_content = await image_file.read()
                
                # Resize image if it exceeds FAL.ai limits (4000x4000)
                resized_content = self._resize_image_if_needed(image_content)
                
                # Convert image to base64 for FAL.ai
                image_base64 = base64.b64encode(resized_content).decode('utf-8')
                image_data_url = f"data:{image_file.content_type};base64,{image_base64}"
                image_data_urls.append(image_data_url)
            
            # Create styled prompt
            styled_prompt = f"{style} style: {prompt}"
            
            # Map shape to image_size
            shape_mapping = {
                "square": "square",
                "portrait": "portrait", 
                "landscape": "landscape"
            }
            image_size = shape_mapping.get(shape, "square")
            
            # Prepare arguments for SeeDream
            arguments = {
                "prompt": styled_prompt,
                "image_urls": image_data_urls,
                "aspect_ratio": image_size,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "num_images": 1
            }
            
            # Submit the request to FAL.ai for image editing
            handler = fal_client.submit(
                "fal-ai/bytedance/seedream/v4/edit",
                arguments=arguments
            )
            
            # Get the result
            result = handler.get()
            
            if not result or "images" not in result or not result["images"]:
                raise Exception("No images generated by FAL.ai")
            
            # Get the image URL
            image_url = result["images"][0]["url"]
            
            # Download and save the edited image locally
            local_image_url = await self._download_and_save_image(image_url, prompt, style, shape, len(image_files))
            
            logger.info(f"Successfully edited and saved {style} style image in {shape} format for prompt: {prompt}")
            return local_image_url
            
        except Exception as e:
            logger.error(f"Error editing images: {str(e)}")
            raise
    
    async def generate_images(self, prompt: str, style: str = "Photo", shape: str = "square") -> str:
        """
        Generate new images using SeeDream and save them locally
        
        Args:
            prompt (str): The generation prompt
            style (str): Style of the generated image (Photo, Illustration, etc.)
            shape (str): Shape/aspect ratio (square, portrait, landscape)
            
        Returns:
            str: Local image URL of the generated image
        """
        try:
            logger.info(f"Generating new image in {style} style with {shape} format using SeeDream for prompt: {prompt[:50]}...")
            
            # Create styled prompt
            styled_prompt = f"{style} style: {prompt}"
            
            # Map shape to image_size
            shape_mapping = {
                "square": "square",
                "portrait": "portrait", 
                "landscape": "landscape"
            }
            image_size = shape_mapping.get(shape, "square")
            
            # Prepare arguments for SeeDream image generation
            arguments = {
                "prompt": styled_prompt,
                "aspect_ratio": image_size,
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
                "num_images": 1
            }
            
            # Submit the request to FAL.ai for image generation
            handler = fal_client.submit(
                "fal-ai/bytedance/seedream/v4",
                arguments=arguments
            )
            
            # Get the result
            result = handler.get()
            
            if not result or "images" not in result or not result["images"]:
                raise Exception("No images generated by FAL.ai")
            
            # Get the image URL
            image_url = result["images"][0]["url"]
            
            # Download and save the generated image locally
            local_image_url = await self._download_and_save_image(image_url, prompt, style, shape, 0)
            
            logger.info(f"Successfully generated and saved {style} style image in {shape} format for prompt: {prompt}")
            return local_image_url
            
        except Exception as e:
            logger.error(f"Error generating images: {str(e)}")
            raise
    
    async def _download_and_save_image(self, image_url: str, prompt: str, style: str, shape: str, num_images: int) -> str:
        """
        Download image from URL and save it locally
        
        Args:
            image_url (str): URL of the generated image
            prompt (str): Original prompt (for filename)
            style (str): Style used for editing
            shape (str): Shape used for editing
            num_images (int): Number of input images
            
        Returns:
            str: Local image URL
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            
            if num_images > 0:
                # Editing mode
                filename = f"seedream_edit_{timestamp}_{style}_{shape}_{num_images}imgs_{safe_prompt}.png"
            else:
                # Generation mode
                filename = f"seedream_gen_{timestamp}_{style}_{shape}_{safe_prompt}.png"
            
            # Download image bytes
            response = requests.get(image_url)
            response.raise_for_status()
            data = response.content

            # Try uploading bytes directly to GCS
            try:
                destination_blob_name = f"image/{filename}"
                storage_client = storage.Client()
                bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                blob = bucket.blob(destination_blob_name)
                import mimetypes
                content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
                blob.upload_from_string(data, content_type=content_type)
                image_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                logger.info(f"Image uploaded to GCS: {image_url}")
                return image_url
            except Exception as e:
                logger.error(f"Error uploading to GCS: {str(e)}")

            # Fallback to local save
            file_path = os.path.join(self.images_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(data)

            local_image_url = f"{config.BASE_URL}/images/{filename}"
            logger.info(f"Image saved to: {file_path}")
            logger.info(f"Image URL: {local_image_url}")
            return local_image_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving image: {str(e)}")
            raise

# Create a singleton instance
seedream_image_edit_service = SeedreamImageEditService()
