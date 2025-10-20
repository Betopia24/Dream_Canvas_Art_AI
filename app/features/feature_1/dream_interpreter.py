import os
import io
from datetime import datetime
import uuid
from app.core.config import config
from openai import OpenAI
from google import genai
from google.cloud import storage

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
            # processing starts
            
            # Get dream interpretation
            dream_interpretation = await self._get_dream_interpretation(prompt)
            
            # Generate dream image
            image_result = await self._generate_dream_image(prompt, style, shape)
            
            # return the plain GCS url string as image_url
            if isinstance(image_result, str):
                return {
                    "success_message": "Dream successfully interpreted and visualized!",
                    "image_url": image_result,
                    "dream_interpretation": dream_interpretation
                }
            else:
                # unexpected result type
                raise Exception("Image generation returned unexpected result")
            
        except Exception as e:
            return {
                "success_message": f"Error processing dream: {str(e)}",
                "image_url": "No image generated",
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
            # OpenAI error (swallowing for fallback)
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

            timestamp = int(datetime.now().timestamp() * 1000)
            unique_id = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:3]}"
            filename = f"dream_{timestamp}_{unique_id}.jpg"


            # Save image to memory and upload directly to GCS (no local file)
            generated_image = result.generated_images[0]
            filepath = os.path.join(self.images_folder, filename)
            try:
                buf = io.BytesIO()
                saved_to_disk = False
                try:
                    # Try saving to buffer (no format kwarg)
                    generated_image.image.save(buf)
                    buf.seek(0)
                    image_bytes = buf.read()
                except TypeError:
                    # Fallback: save to disk and read bytes
                    generated_image.image.save(filepath)
                    saved_to_disk = True
                    with open(filepath, 'rb') as f:
                        image_bytes = f.read()

                # Upload to GCS
                destination_blob_name = f"image/{filename}"
                blob = self.bucket.blob(destination_blob_name)
                content_type = 'image/jpeg'
                blob.upload_from_string(image_bytes, content_type=content_type)

                # Cleanup temp file if used
                if saved_to_disk:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
            except Exception as e:
                raise Exception(f"Failed to upload generated image to GCS: {e}")

            return f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
            
        except Exception as e:
            raise Exception(f"Failed to generate dream image: {str(e)}")


dream_interpreter_service = DreamInterpreterService()
