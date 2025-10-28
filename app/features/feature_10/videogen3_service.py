import logging
import time
import os

import requests
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import config
import mimetypes
import tempfile
from google.cloud import storage

logger = logging.getLogger(__name__)

class VideoGen3Service:
    """Service for generating videos using Veo 3.0 Fast"""
    
    def __init__(self):
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=config.GEMINI_API_KEY,
        )
        self.model = "veo-3.0-fast-generate-001"
        self.videos_folder = "generated_videos"
        # Do NOT auto-create runtime folders inside the container. Expect the
        # environment (mounted volume, GCS, or host) to provide this directory.
        # os.makedirs(self.videos_folder, exist_ok=True)
        
    async def generate_video(self, prompt: str, user_id: str, shape: str) -> str:
        """
        Generate a video using Veo 3.0 Fast and save it locally
        
        Args:
            prompt (str): The video description prompt
            user_id (str): The user ID for folder organization
            shape (str): The video aspect ratio shape (square, portrait, landscape)
            
        Returns:
            str: Local file path of the saved video
        """
        try:
            # Map shape to aspect ratio
            aspect_ratio_mapping = {
                "square": "1:1",
                "portrait": "9:16", 
                "landscape": "16:9"
            }
            aspect_ratio = aspect_ratio_mapping.get(shape, "16:9")
            
            # Video configuration
            video_config = types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,
                duration_seconds=8,  # Keep it short for fast generation
                person_generation="ALLOW_ALL",
            )
            
            # Start video generation
            operation = self.client.models.generate_videos(
                model=self.model,
                prompt=prompt,
                config=video_config,
            )
            
            # Wait for completion
            while not operation.done:
                logger.info("Video generation in progress, checking again in 10 seconds...")
                time.sleep(10)
                operation = self.client.operations.get(operation)
            
            # Get result
            result = operation.result
            if not result:
                raise Exception("Error occurred while generating video")
            
            generated_videos = result.generated_videos
            if not generated_videos:
                raise Exception("No videos were generated")
            
            # Get the first video
            video = generated_videos[0].video
            
            # Download and save the video locally using the client
            local_video_path = await self._download_and_save_video(video, prompt, user_id)
            
            logger.info(f"Successfully generated and saved video for prompt: {prompt}")
            return local_video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _download_and_save_video(self, video, prompt: str, user_id: str) -> str:
        """
        Download video using Google client and upload to GCS, fallback to local save
        Args:
            video: The video object from Google GenAI
            prompt (str): Original prompt (for filename)
        Returns:
            str: URL of the saved video (GCS or local)
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"veo3_{timestamp}_{safe_prompt}.mp4"

            # Try to save to a temp file and upload to GCS
            try:
                # Download into a temporary file first
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tmp_path = tmp.name
                tmp.close()
                self.client.files.download(file=video)
                video.save(tmp_path)

                # Read bytes and upload to GCS
                with open(tmp_path, 'rb') as f:
                    data = f.read()

                destination_blob_name = f"video/{user_id}/{filename}"
                storage_client = storage.Client()
                bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                content_type = mimetypes.guess_type(filename)[0] or 'video/mp4'
                blob = bucket.blob(destination_blob_name)
                blob.upload_from_string(data, content_type=content_type)
                # Remove temp
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

                video_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                logger.info(f"Video uploaded to GCS: {video_url}")
                return video_url
            except Exception as e:
                logger.error(f"Error uploading generated video to GCS: {e}")
                # Fallback: save to the configured generated_videos folder
                file_path = os.path.join(self.videos_folder, filename)
                video.save(file_path)
                video_url = f"{config.BASE_URL}/videos/{filename}"
                logger.info(f"Video saved to: {file_path}")
                logger.info(f"Video URL: {video_url}")
                return video_url

        except Exception as e:
            logger.error(f"Error downloading and saving video: {str(e)}")
            raise
