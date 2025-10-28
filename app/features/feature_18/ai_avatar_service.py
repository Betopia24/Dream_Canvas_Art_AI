import logging
import os
import requests
from datetime import datetime
import fal_client

import base64
import uuid
import tempfile
import io
from fastapi import UploadFile
from app.core.config import config
import mimetypes
from google.cloud import storage
from PIL import Image

logger = logging.getLogger(__name__)

class AIAvatarService:
    """Service for generating videos using ByteDance OmniHuman from FAL.ai"""
    
    def __init__(self):
        self.api_key = config.FAL_API_KEY
        if not self.api_key:
            raise ValueError("FAL_API_KEY is required in .env file")
        
        # Configure FAL client
        os.environ["FAL_KEY"] = self.api_key
        fal_client.api_key = self.api_key
        
        self.videos_folder = "generated_videos"
        self.temp_folder = "temp_uploads"
        # Create the folders if they don't exist
        os.makedirs(self.videos_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)

    async def generate_video(self, image_file: UploadFile, audio_file: UploadFile,user_id: str) -> str:
        """
        Generate a video using ByteDance OmniHuman and save it locally
        
        Args:
            image_file (UploadFile): The input image file
            audio_file (UploadFile): The input audio file
            
        Returns:
            str: Local video URL
        """
        try:
            logger.info(f"Generating AI Avatar video with image {image_file.filename} and audio {audio_file.filename}...")
            

            # Read file contents
            image_content = await image_file.read()
            audio_content = await audio_file.read()

            # Resize image if needed (min 512x512, max 4000x4000 for FAL.ai)
            try:
                image_stream = io.BytesIO(image_content)
                with Image.open(image_stream) as img:
                    width, height = img.size
                    logger.info(f"Original image dimensions: {width}x{height}")
                    
                    needs_resize = False
                    new_width, new_height = width, height
                    
                    # Check if image exceeds FAL.ai maximum dimensions (4000x4000)
                    if width > 4000 or height > 4000:
                        logger.info(f"Image exceeds FAL.ai maximum dimensions, resizing from {width}x{height}...")
                        # Scale down while maintaining aspect ratio
                        if width > height:
                            new_width = 4000
                            new_height = int((height * 4000) / width)
                        else:
                            new_height = 4000
                            new_width = int((width * 4000) / height)
                        needs_resize = True
                    
                    # Check if image is below minimum dimensions (512x512)
                    if new_width < 512 or new_height < 512:
                        logger.info(f"Image below minimum dimensions, resizing to at least 512x512...")
                        new_width = max(new_width, 512)
                        new_height = max(new_height, 512)
                        needs_resize = True
                    
                    if needs_resize:
                        logger.info(f"Resizing image to: {new_width}x{new_height}")
                        # Resize the image
                        img = img.convert("RGB")
                        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        
                        # Save resized image
                        out_stream = io.BytesIO()
                        resized_img.save(out_stream, format="JPEG", quality=95)
                        image_content = out_stream.getvalue()
                        logger.info(f"Image resized successfully to {new_width}x{new_height}")
                    else:
                        logger.info("Image dimensions are within acceptable limits, no resizing needed")
                        
            except Exception as e:
                logger.warning(f"Could not resize image: {e}. Proceeding with original image.")

            # Reset file pointers for potential re-reading
            await image_file.seek(0)
            await audio_file.seek(0)

            # Upload files to FAL.ai storage
            logger.info("Uploading image file to FAL.ai storage...")
            image_url = fal_client.upload(
                image_content,
                content_type="image/jpeg"
            )

            logger.info("Uploading audio file to FAL.ai storage...")
            audio_url = fal_client.upload(
                audio_content,
                content_type=audio_file.content_type
            )

            logger.info(f"Using uploaded image URL: {image_url}")
            logger.info(f"Using uploaded audio URL: {audio_url}")
            
            # Submit the request to FAL.ai
            handler = fal_client.submit(
                "fal-ai/bytedance/omnihuman",
                arguments={
                    "image_url": image_url,
                    "audio_url": audio_url
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
            safe_name = "".join(c for c in image_file.filename[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"ai_avatar_{timestamp}_{safe_name}.mp4"

            # Try uploading to GCS
            try:
                destination_blob_name = f"video/{user_id}/{filename}"
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

            # Fallback: save locally
            local_video_url = await self._download_and_save_video(video_url, image_file.filename)
            
            logger.info(f"Successfully generated AI Avatar video")
            return local_video_url
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _download_and_save_video(self, video_url: str, image_filename: str) -> str:
        """
        Download video from URL and save it locally
        
        Args:
            video_url (str): URL of the generated video
            image_filename (str): Original image filename (for filename)
            
        Returns:
            str: Local video URL
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c for c in image_filename[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            filename = f"ai_avatar_{timestamp}_{safe_name}.mp4"
            
            # Full path for the video
            file_path = os.path.join(self.videos_folder, filename)
            
            # Download the video
            response = requests.get(video_url)
            response.raise_for_status()
            
            # Save the video
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Return URL
            local_video_url = f"{config.BASE_URL}/videos/{filename}"
            
            logger.info(f"Video saved to: {file_path}")
            logger.info(f"Video URL: {local_video_url}")
            return local_video_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving video: {str(e)}")
            raise

# Create a singleton instance
ai_avatar_service = AIAvatarService()
