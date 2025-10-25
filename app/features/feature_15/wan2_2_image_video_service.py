import logging
import os
import requests
from datetime import datetime
import fal_client
import base64
from fastapi import UploadFile
from app.core.config import config
import mimetypes
from google.cloud import storage
from PIL import Image
import io

logger = logging.getLogger(__name__)

class Wan22ImageVideoService:
    """Service for generating videos using WAN 2.2 Image-to-Video from FAL.ai"""
    
    def __init__(self):
        self.api_key = config.FAL_API_KEY
        if not self.api_key:
            raise ValueError("FAL_API_KEY is required in .env file")
        
        # Configure FAL client
        os.environ["FAL_KEY"] = self.api_key
        fal_client.api_key = self.api_key
        
        self.videos_folder = "generated_videos"
        # Create the folder if it doesn't exist
        os.makedirs(self.videos_folder, exist_ok=True)
        
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
        
    async def generate_video(self, prompt: str, image_file: UploadFile, shape: str) -> str:
        """
        Generate a video using WAN 2.2 Image-to-Video and save it locally
        
        Args:
            prompt (str): The video description prompt
            image_file (UploadFile): The input image file
            shape (str): The video aspect ratio shape (square, portrait, landscape)
            
        Returns:
            str: Local video URL (similar to feature_14)
        """
        try:
            logger.info(f"Generating video with WAN 2.2 Image-to-Video for prompt: {prompt[:50]}...")
            
            # Map shape to width/height (WAN 2.2 may use width/height instead of aspect_ratio)
            dimension_mapping = {
                "square": {"width": 512, "height": 512},
                "portrait": {"width": 512, "height": 768}, 
                "landscape": {"width": 768, "height": 512}
            }
            dimensions = dimension_mapping.get(shape, {"width": 768, "height": 512})
            
            # Read the uploaded image
            image_content = await image_file.read()
            
            # Resize image if it exceeds FAL.ai limits (4000x4000)
            resized_content = self._resize_image_if_needed(image_content)
            
            # Convert image to base64 for FAL.ai
            image_base64 = base64.b64encode(resized_content).decode('utf-8')
            image_data_url = f"data:{image_file.content_type};base64,{image_base64}"
            
            # Submit the request to FAL.ai
            handler = fal_client.submit(
                "fal-ai/wan/v2.2-a14b/image-to-video",
                arguments={
                    "prompt": prompt,
                    "image_url": image_data_url,
                    "width": dimensions["width"],
                    "height": dimensions["height"],
                    "duration": 5,  # 5 seconds for simplicity
                    "fps": 24,
                    "num_videos": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 25
                }
            )
            
            # Get the result
            result = handler.get()
            
            if not result or "video" not in result or not result["video"]:
                raise Exception("No video generated by FAL.ai")
            
            # Get the video URL
            video_url = result["video"]["url"]

            # Download video bytes
            response = requests.get(video_url)
            response.raise_for_status()
            data = response.content

            # Build filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"wan22_img2vid_{timestamp}_{safe_prompt}.mp4"

            # Try upload to GCS
            try:
                destination_blob_name = f"video/{filename}"
                storage_client = storage.Client()
                bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                content_type = mimetypes.guess_type(filename)[0] or 'video/mp4'
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_string(data, content_type=content_type)
                video_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                logger.info(f"Video uploaded to GCS: {video_url}")
                return video_url
            except Exception as e:
                logger.error(f"Error uploading video to GCS: {e}")

            # Fallback to local save
            local_video_url = await self._download_and_save_video(video_url, prompt)
            
            logger.info(f"Successfully generated video for prompt: {prompt}")
            return local_video_url
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _download_and_save_video(self, video_url: str, prompt: str) -> str:
        """
        Download video from URL and save it locally (like feature_14)
        
        Args:
            video_url (str): URL of the generated video
            prompt (str): Original prompt (for filename)
            
        Returns:
            str: Local video URL (BASE_URL + filename)
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"wan22_img2vid_{timestamp}_{safe_prompt}.mp4"
            
            # Full path for the video
            file_path = os.path.join(self.videos_folder, filename)
            
            # Download the video
            response = requests.get(video_url)
            response.raise_for_status()
            
            # Save the video
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Return URL like feature_14
            local_video_url = f"{config.BASE_URL}/videos/{filename}"
            
            logger.info(f"Video saved to: {file_path}")
            logger.info(f"Video URL: {local_video_url}")
            return local_video_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving video: {str(e)}")
            raise

# Create a singleton instance
wan22_image_video_service = Wan22ImageVideoService()
