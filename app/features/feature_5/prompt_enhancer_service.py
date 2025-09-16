import openai
import os
import logging
import sys

# Add the app directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.core.config import config

logger = logging.getLogger(__name__)


class PromptEnhancerService:
    def __init__(self):
        """Initialize the prompt enhancer service"""
        self.api_key = config.OPEN_AI_API_KEY
        if not self.api_key:
            raise ValueError("OPEN_AI_API_KEY is required in .env file")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

    def enhance_prompt(self, original_prompt: str) -> str:
        """
        Enhance a prompt using OpenAI for better image generation
        
        Args:
            original_prompt: The original prompt to enhance
            
        Returns:
            Enhanced prompt string
        """
        try:
            logger.info(f"Enhancing prompt: {original_prompt[:50]}...")
            
            # Simple system prompt for enhancement
            system_prompt = """You are an expert at enhancing prompts for AI image generation. 
            Take the user's prompt and improve it by adding artistic details, quality terms, and technical specifications 
            that will help generate better images. Keep the original concept but make it more detailed and specific."""
            
            user_message = f"""Enhance this prompt for AI image generation: "{original_prompt}"
            
            Return only the enhanced prompt, no explanations."""

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Get the enhanced prompt
            enhanced_prompt = response.choices[0].message.content.strip()
            
            logger.info(f"Prompt enhanced successfully")
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            raise Exception(f"Failed to enhance prompt: {str(e)}")


# Create a singleton instance
prompt_enhancer_service = PromptEnhancerService()