import logging
import os
import time
from datetime import datetime
from google import genai
from google.genai import types
from app.core.config import config

logger = logging.getLogger(__name__)

class VideoGenService:
    """Service for generating videos using Gemini Veo 2"""
    
    def __init__(self):
        self.client = genai.Client(
            http_options={"api_version": "v1beta"},
            api_key=config.GEMINI_API_KEY,
        )
        self.model = "veo-2.0-generate-001"
        self.videos_folder = "generated_videos"
        # Create the folder if it doesn't exist
        os.makedirs(self.videos_folder, exist_ok=True)
        
    async def generate_video(self, prompt: str, shape: str) -> str:
        """
        Generate a video using Gemini Veo 2 and save it locally
        
        Args:
            prompt (str): The video description prompt
            shape (str): The video aspect ratio shape (square, portrait, landscape)
            
        Returns:
            str: Local file path of the generated video
        """
        try:

            aspect_ratio_mapping = {
                "square": "1:1",     # Closest to 1:1 that's supported
                "portrait": "9:16",   # Closest to 9:16 that's supported  
                "landscape": "16:9"    # Standard landscape
            }
            aspect_ratio = aspect_ratio_mapping.get(shape, "16:9")
            
            # Video configuration with dynamic aspect ratio
            video_config = types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                number_of_videos=1,   # supported values: 1 - 4
                duration_seconds=8,   # supported values: 5 - 8
                person_generation="ALLOW_ALL",
            )
            
            # Start video generation operation
            operation = self.client.models.generate_videos(
                model=self.model,
                prompt=prompt,
                config=video_config,
            )
            
            # Wait for the video to be generated
            while not operation.done:
                logger.info("Video is being generated... checking again in 10 seconds...")
                time.sleep(10)
                operation = self.client.operations.get(operation)

            result = operation.result
            if not result:
                raise Exception("Error occurred while generating video.")

            generated_videos = result.generated_videos
            if not generated_videos:
                raise Exception("No videos were generated.")

            logger.info(f"Generated {len(generated_videos)} video(s).")
            
            # Download and save the first video
            video_path = await self._download_and_save_video(generated_videos[0], prompt)
            
            logger.info(f"Successfully generated and saved video for prompt: {prompt}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
    async def _download_and_save_video(self, generated_video, prompt: str) -> str:
        """
        Download video from Veo 2 response and save it locally
        
        Args:
            generated_video: The generated video object from Veo 2
            prompt (str): Original prompt (for filename)
            
        Returns:
            str: Local file path of the saved video
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"veo2_{timestamp}_{safe_prompt}.mp4"
            
            # Full path for the video
            file_path = os.path.join(self.videos_folder, filename)
            
            # Download the video file
            logger.info(f"Video URI: {generated_video.video.uri}")
            self.client.files.download(file=generated_video.video)
            
            # Save the video with custom filename
            generated_video.video.save(file_path)
            
            # Return URL instead of file path
            video_url = f"{config.BASE_URL}/videos/{filename}"
            
            logger.info(f"Video saved to: {file_path}")
            logger.info(f"Video URL: {video_url}")
            return video_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving video: {str(e)}")
            raise
