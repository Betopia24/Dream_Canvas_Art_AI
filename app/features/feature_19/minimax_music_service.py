import logging
import os
import requests
from datetime import datetime
import fal_client
from app.core.config import config
import openai
from google.cloud import storage
import mimetypes
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class MinimaxMusicService:
    """Service for generating music using MiniMax Music from FAL.ai"""
    
    def __init__(self):
        self.api_key = config.FAL_API_KEY
        if not self.api_key:
            raise ValueError("FAL_API_KEY is required in .env file")
        
        self.openai_api_key = config.OPEN_AI_API_KEY
        if not self.openai_api_key:
            raise ValueError("OPEN_AI_API_KEY is required in .env file")
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Configure FAL client
        os.environ["FAL_KEY"] = self.api_key
        fal_client.api_key = self.api_key
        
        self.audio_folder = "generated_audio"
        # Create the folder if it doesn't exist
        os.makedirs(self.audio_folder, exist_ok=True)
        
    async def generate_audio(self, verse_prompt: str, user_id: str, lyrics_prompt: str = None) -> str:
        """
        Generate audio using MiniMax Music and save it locally
        
        Args:
            verse_prompt (str): The actual lyrics content/text
            user_id (str): User ID for organizing files
            lyrics_prompt (str, optional): The music style description
            
        Returns:
            str: Local audio URL
        """
        try:
            logger.info(f"Generating music with MiniMax for lyrics: {verse_prompt[:50]}...")
            
            # Always enhance the verse_prompt (which contains the actual lyrics)
            verse_system_prompt = """You are an expert at writing verses. 
            Take the user's prompt and write creative and engaging verses that fit the prompt provided. MUST BE UNDER 300 CHARACTERS."""
            
            verse_user_message = f"""Write verses based on this prompt: "{verse_prompt}"
            
            Return only the enhanced verses, no explanations."""

            # Call OpenAI API for verse enhancement
            verse_response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": verse_system_prompt},
                    {"role": "user", "content": verse_user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Get the enhanced verses
            enhanced_verses = verse_response.choices[0].message.content.strip()
            
            # Truncate to 300 characters if needed
            if len(enhanced_verses) > 300:
                enhanced_verses = enhanced_verses[:297] + "..."
            
            # Only enhance music style if lyrics_prompt is provided and not empty
            enhanced_music_style = None
            if lyrics_prompt and lyrics_prompt.strip():
                logger.info(f"Enhancing music style: {lyrics_prompt[:50]}...")
                
                style_system_prompt = """You are an expert at writing music style. Take the user's prompt and write a precise music style descriptions that fit the prompt provided."""
                
                style_user_message = f"""Write a music style description based on this prompt: "{lyrics_prompt}"
                
                Return only the enhanced prompt, no explanations."""

                # Call OpenAI API for music style enhancement
                style_response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": style_system_prompt},
                        {"role": "user", "content": style_user_message}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                # Get the enhanced music style
                enhanced_music_style = style_response.choices[0].message.content.strip()
                
                # Truncate to 300 characters if needed
                if len(enhanced_music_style) > 300:
                    enhanced_music_style = enhanced_music_style[:297] + "..."
            
            # Prepare arguments for FAL.ai
            fal_arguments = {}
            
            # Always add verses (from verse_prompt) as prompt for FAL.ai
            fal_arguments["prompt"] = enhanced_verses

            # Add music style as lyrics_prompt if provided, otherwise use a default
            if enhanced_music_style and enhanced_music_style.strip():
                # Ensure music style is under 300 characters
                if len(enhanced_music_style) > 300:
                    enhanced_music_style = enhanced_music_style[:297] + "..."
                
                fal_arguments["lyrics_prompt"] = enhanced_music_style
            else:
                # FAL.ai requires lyrics_prompt, so provide a default music style
                fal_arguments["lyrics_prompt"] = "A melodic and harmonious composition"
            
            # Submit the request to FAL.ai
            handler = fal_client.submit(
                "fal-ai/minimax-music/v1.5",
                arguments=fal_arguments
            )
            
            # Get the result
            result = handler.get()
            
            if not result or "audio" not in result or not result["audio"]:
                raise Exception("No audio generated by FAL.ai")
            
            # Get the audio URL
            audio_url = result["audio"]["url"]
            
            # Download and save the audio locally
            local_audio_url = await self._download_and_save_audio(audio_url, verse_prompt, user_id)
            
            logger.info(f"Successfully generated audio")
            return local_audio_url
            
        except Exception as e:
            logger.error(f"Error generating audio: {str(e)}")
            raise
    
    async def _download_and_save_audio(self, audio_url: str, verse_prompt: str, user_id: str) -> str:
        """
        Download audio from URL and save it locally in user-specific directory
        
        Args:
            audio_url (str): URL of the generated audio
            verse_prompt (str): Original verse prompt (for filename)
            user_id (str): User ID for organizing files
            
        Returns:
            str: Local audio URL
        """
        try:
            # Create user-specific directory
            user_audio_folder = os.path.join(self.audio_folder, user_id)
            os.makedirs(user_audio_folder, exist_ok=True)
            
            # Create a safe filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_verse = "".join(c for c in verse_prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_verse = safe_verse.replace(' ', '_')
            
            # Simple filename without lyrics (to avoid long filenames)
            filename = f"minimax_music_{timestamp}_{safe_verse}.mp3"
            
            # Download the audio bytes
            response = requests.get(audio_url)
            response.raise_for_status()
            data = response.content

            try:               
                storage_client = storage.Client()
                bucket = storage_client.bucket(config.GCS_BUCKET_NAME)
                destination_blob_name = f"audio/{user_id}/{filename}"
                blob = bucket.blob(destination_blob_name)
                content_type = mimetypes.guess_type(filename)[0] or 'audio/mpeg'
                blob.upload_from_string(data, content_type=content_type)
                audio_url = f"https://storage.googleapis.com/{config.GCS_BUCKET_NAME}/{destination_blob_name}"
                logger.info(f"Audio uploaded to GCS: {audio_url}")
                return audio_url
            except Exception as e:
                logger.error(f"Error uploading audio to GCS: {e}")

            # Fallback: save locally in user-specific directory
            file_path = os.path.join(user_audio_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(data)

            # Return local URL with user_id path
            local_audio_url = f"{config.BASE_URL}/audio/{user_id}/{filename}"
            logger.info(f"Audio saved to: {file_path}")
            logger.info(f"Audio URL: {local_audio_url}")
            return local_audio_url
            
        except Exception as e:
            logger.error(f"Error downloading and saving audio: {str(e)}")
            raise

# Create a singleton instance
minimax_music_service = MinimaxMusicService()


