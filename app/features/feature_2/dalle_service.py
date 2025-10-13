import logging
import os
import requests
from datetime import datetime
from openai import OpenAI
from google.cloud import storage
from app.core.config import config

logger = logging.getLogger(__name__)

class DalleService:
    """Service for generating images using DALL-E 3"""
    
    def __init__(self):
        self.client = OpenAI(api_key=config.OPEN_AI_API_KEY)
        self.images_folder = "generated_images"
        # Create the folder if it doesn't exist
        os.makedirs(self.images_folder, exist_ok=True)
        # Initialize GCS client and bucket
        try:
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(config.GCS_BUCKET_NAME)
        except Exception:
            self.storage_client = None
            self.bucket = None
        
    async def generate_image(self, prompt: str, style: str, shape: str) -> str:
        """
        Generate an image using DALL-E 3 and save it locally
        
        Args:
            prompt (str): The image description prompt
            style (str): The style for the image (Photo, Illustration, Comic, etc.)
            shape (str): The shape/size of the image (square, portrait, landscape)
            
        Returns:
            str: Local file path of the saved image
        """
        try:
            # Create styled prompt by incorporating the style
            styled_prompt = f"{prompt}, in {style.lower()} style"
            
            # Map shape to DALL-E size format
            size_mapping = {
                "square": "1024x1024",
                "portrait": "1024x1792", 
                "landscape": "1792x1024"
            }
            size = size_mapping.get(shape, "1024x1024")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=styled_prompt,
                n=1,
                size=size,
                quality="standard",
            )
            
            # Get the image URL from the response
            image_url = response.data[0].url
            
            # Download and save the image
            local_image_path = await self._download_and_save_image(image_url, prompt, style, shape)
            
            logger.info(f"Successfully generated and saved {style} style image in {shape} format for prompt: {prompt}")
            return local_image_path
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    async def _download_and_save_image(self, image_url: str, prompt: str, style: str, shape: str) -> str:
        """
        Download image from URL and save it locally
        
        Args:
            image_url (str): URL of the generated image
            prompt (str): Original prompt (for filename)
            style (str): Image style
            shape (str): Image shape
            
        Returns:
            str: Local file path of the saved image
        """
        try:
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"dalle_{timestamp}_{style}_{shape}_{safe_prompt}.png"
            
            # Full path for the image
            file_path = os.path.join(self.images_folder, filename)
            
            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Save the image
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Upload to GCS if available and return plain storage URL
            if self.bucket:
                destination_blob_name = f"image/{filename}"
                try:
                    blob = self.bucket.blob(destination_blob_name)
                    blob.upload_from_filename(file_path)
                    image_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                    logger.info(f"Image uploaded to GCS: {image_url}")
                    return image_url
                except Exception as e:
                    logger.error(f"Error uploading to GCS: {str(e)}")
                    # Fallback to local URL
            image_url = f"{config.BASE_URL}/images/{filename}"

            logger.info(f"Image saved to: {file_path}")
            logger.info(f"Image URL: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving image: {str(e)}")
            raise
