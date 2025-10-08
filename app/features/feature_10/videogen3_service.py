import logging
import time
import os
import requests
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import config

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
        # Create the folder if it doesn't exist
        os.makedirs(self.videos_folder, exist_ok=True)
        
    async def generate_video(self, prompt: str, shape: str) -> str:
        """
        Generate a video using Veo 3.0 Fast and save it locally
        
        Args:
            prompt (str): The video description prompt
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
            local_video_path = await self._download_and_save_video(video, prompt)
            
            logger.info(f"Successfully generated and saved video for prompt: {prompt}")
            return local_video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _download_and_save_video(self, video, prompt: str) -> str:
        """
        Download video using Google client and save it locally
        
        Args:
            video: The video object from Google GenAI
            prompt (str): Original prompt (for filename)
            
        Returns:
            str: Local file path of the saved video
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"veo3_{timestamp}_{safe_prompt}.mp4"
            
            # Full path for the video
            file_path = os.path.join(self.videos_folder, filename)
            
            # Download the video using the Google client
            self.client.files.download(file=video)
            video.save(file_path)
            
            # Return URL instead of file path
            video_url = f"{config.BASE_URL}/videos/{filename}"
            
            logger.info(f"Video saved to: {file_path}")
            logger.info(f"Video URL: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving video: {str(e)}")
            raise
