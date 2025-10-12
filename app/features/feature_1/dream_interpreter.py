import logging
import os
from datetime import datetime, timedelta
import uuid
from app.core.config import config
from openai import OpenAI
from google import genai
from google.cloud import storage

logger = logging.getLogger(__name__)

class DreamInterpreterService:
    """Simple service for interpreting dreams and generating images"""
    
    def __init__(self):
        # Initialize API clients
        self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.openai_client = OpenAI(api_key=config.OPEN_AI_API_KEY)
        
        # Initialize Google Cloud Storage client
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(config.GCS_BUCKET_NAME)
        
        # Create images folder
        self.images_folder = "generated_images"
        os.makedirs(self.images_folder, exist_ok=True)

    async def interpret_dream(self, prompt: str, style:str, shape: str) -> dict:
        """
        Simple dream interpretation with image generation
        """
        try:
            logger.info(f"Processing dream: {prompt[:50]}...")
            
            # Get dream interpretation
            dream_interpretation = await self._get_dream_interpretation(prompt)
            
            # Generate dream image
            image_result = await self._generate_dream_image(prompt, style, shape)
            
            # Prefer cloud url when available, otherwise fallback to local url
            if isinstance(image_result, dict):
                chosen_url = image_result.get("cloud_url") or image_result.get("local_url")
                return {
                    "success_message": "Dream successfully interpreted and visualized!",
                    "image_url": chosen_url,
                    "cloud_image_url": image_result.get("cloud_url"),
                    "dream_interpretation": dream_interpretation
                }
            else:
                # Legacy fallback
                return {
                    "success_message": "Dream successfully interpreted and visualized!",
                    "image_url": image_result,
                    "cloud_image_url": None,
                    "dream_interpretation": dream_interpretation
                }
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return {
                "success_message": f"Error processing dream: {str(e)}",
                "image_url": "No image generated",
                "cloud_image_url": None,
                "dream_interpretation": "Unable to interpret dream at this time."
            }
    
    async def _get_dream_interpretation(self, dream_description: str) -> str:
        """Get dream interpretation using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a dream analyst. Provide a brief, insightful dream interpretation."},
                    {"role": "user", "content": f"Interpret this dream: {dream_description}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            return f"Dream about {dream_description[:30]}... often represents subconscious thoughts and emotions."

    async def _generate_dream_image(self, prompt: str, style: str, shape: str) -> str:
        """Generate dream image using Gemini"""
        try:
            # Create dream-like prompt
            visual_prompt = f"Dreamy, surreal visualization of: {prompt}. Ethereal, mystical atmosphere. in {style} style."
            
            # Generate image
            if (shape == "square"):
                aspect_ratio = "1:1"
            elif (shape == "portrait"):
                aspect_ratio = "9:16"
            else:
                aspect_ratio = "16:9"
            result = self.gemini_client.models.generate_images(
                model="models/imagen-4.0-generate-001",
                prompt=visual_prompt,
                config={
                    "number_of_images": 1,
                    "output_mime_type": "image/jpeg",
                    "aspect_ratio": aspect_ratio,
                    "image_size": "1K"
                }
            )

            if not result.generated_images:
                raise Exception("No image generated")

            # Save image with filename format similar to your example
            # Example format from your URL: tts_1760172924372_5cce4d10-c26.wav
            timestamp = int(datetime.now().timestamp() * 1000)  # milliseconds timestamp
            unique_id = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:3]}"
            filename = f"dream_{timestamp}_{unique_id}.jpg"
            file_path = os.path.join(self.images_folder, filename)
            
            # Save locally first
            result.generated_images[0].image.save(file_path)
            
            # Upload to Google Cloud Storage
            try:
                # Define the path in the bucket (inside the "image" folder)
                destination_blob_name = f"image/{filename}"
                
                # Create a blob and upload the file
                blob = self.bucket.blob(destination_blob_name)
                blob.upload_from_filename(file_path)
                
                # Try to generate a signed URL (v4) so the client can access the object even
                # if the bucket/object is not publicly readable. Fall back to the public URL.
                try:
                    signed_url = blob.generate_signed_url(version="v4", expiration=timedelta(days=7))
                    cloud_url = signed_url
                except Exception:
                    # Fallback to the standard storage URL
                    cloud_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"

                logger.info(f"Image saved locally: {file_path}")
                logger.info(f"Image uploaded to GCS: {cloud_url}")

                # Return both URLs
                return {
                    "local_url": f"{config.BASE_URL}/images/{filename}",
                    "cloud_url": cloud_url
                }
            except Exception as e:
                logger.error(f"Failed to upload to Google Cloud Storage: {str(e)}")
                # Fallback to local URL if GCS upload fails. Return consistent dict.
                local_url = f"{config.BASE_URL}/images/{filename}"
                logger.info(f"Using local image URL: {local_url}")
                return {
                    "local_url": local_url,
                    "cloud_url": None
                }
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise Exception(f"Failed to generate dream image: {str(e)}")

# Create service instance
dream_interpreter_service = DreamInterpreterService()
