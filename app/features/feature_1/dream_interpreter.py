import logging
import os
from datetime import datetime
import uuid
from app.core.config import config
from openai import OpenAI
from google import genai

logger = logging.getLogger(__name__)

class DreamInterpreterService:
    """Simple service for interpreting dreams and generating images"""
    
    def __init__(self):
        # Initialize API clients
        self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.openai_client = OpenAI(api_key=config.OPEN_AI_API_KEY)
        
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
            image_path = await self._generate_dream_image(prompt, style, shape)
            
            return {
                "success_message": "Dream successfully interpreted and visualized!",
                "image_url": image_path,
                "dream_interpretation": dream_interpretation
            }
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
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

            # Save image with simple filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dream_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(self.images_folder, filename)
            
            result.generated_images[0].image.save(file_path)
            
            # Return full URL with proper BASE_URL
            image_url = f"{config.BASE_URL}/images/{filename}"
            
            logger.info(f"Image saved: {file_path}")
            logger.info(f"Image URL: {image_url}")
            return image_url
            
        except Exception as e:
            logger.error(f"Image generation error: {str(e)}")
            raise

# Create service instance
dream_interpreter_service = DreamInterpreterService()
