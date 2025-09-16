# import logging
# import os
# import requests
# from datetime import datetime
# import base64
# from typing import List
# from fastapi import UploadFile
# from openai import OpenAI
# from core.config import config

# logger = logging.getLogger(__name__)

# class Image1Service:
#     """Service for generating images using GPT-Image-1 with multiple image inputs"""
    
#     def __init__(self):
#         self.client = OpenAI(api_key=config.OPEN_AI_API_KEY)
#         self.images_folder = "generated_images"
#         # Create the folder if it doesn't exist
#         os.makedirs(self.images_folder, exist_ok=True)
        
#     async def generate_image(self, prompt: str, image_files: List[UploadFile], style: str = "Photo", shape: str = "square") -> str:
#         """
#         Generate an image using GPT-Image-1 with multiple image inputs and save it locally
        
#         Args:
#             prompt (str): The image description prompt
#             image_files (List[UploadFile]): List of image files as input (max 5)
#             style (str): The style for the image (Photo, Illustration, Comic, etc.)
#             shape (str): The shape/size of the image (square, portrait, landscape)
            
#         Returns:
#             str: Local image URL of the generated image
#         """
#         try:
#             logger.info(f"Generating image with GPT-Image-1 using {len(image_files)} input images in {style} style with {shape} format for prompt: {prompt[:50]}...")
            
#             # Validate number of images
#             if len(image_files) > 5:
#                 raise ValueError("Maximum 5 images allowed")
            
#             # Create styled prompt by incorporating the style
#             styled_prompt = f"{prompt}, in {style.lower()} style"
            
#             # Map shape to size format
#             size_mapping = {
#                 "square": "1024x1024",
#                 "portrait": "1024x1792", 
#                 "landscape": "1792x1024"
#             }
#             size = size_mapping.get(shape, "1024x1024")
            
#             # Process uploaded images for OpenAI API
#             image_data_list = []
#             for i, image_file in enumerate(image_files):
#                 # Read the uploaded image
#                 image_content = await image_file.read()
                
#                 # Convert image to base64 for OpenAI API
#                 image_base64 = base64.b64encode(image_content).decode('utf-8')
#                 image_data_list.append({
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:{image_file.content_type};base64,{image_base64}"
#                     }
#                 })
            
#             # Prepare messages for GPT-4 Vision (as GPT-Image-1 uses similar structure)
#             messages = [
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "text",
#                             "text": f"Generate a new image based on the following prompt and reference images: {styled_prompt}"
#                         }
#                     ] + image_data_list
#                 }
#             ]
            
#             # Use GPT-Image-1 for image generation with multiple image inputs
#             response = self.client.images.generate(
#                 model="gpt-image-1",
#                 prompt=styled_prompt,
#                 n=1,
#                 size=size,
#             )
            
#             # Get the image URL
#             image_url = response.data[0].url
            
#             # Download and save the image locally
#             local_image_url = await self._download_and_save_image(image_url, prompt, style, shape, len(image_files))
            
#             logger.info(f"Successfully generated and saved {style} style image in {shape} format for prompt: {prompt}")
#             return local_image_url
            
#         except Exception as e:
#             logger.error(f"Error generating image: {str(e)}")
#             raise
    
#     async def _download_and_save_image(self, image_url: str, prompt: str, style: str, shape: str, num_images: int) -> str:
#         """
#         Download image from URL and save it locally
        
#         Args:
#             image_url (str): URL of the generated image
#             prompt (str): Original prompt (for filename)
#             style (str): Style used for generation
#             shape (str): Shape used for generation
#             num_images (int): Number of input images
            
#         Returns:
#             str: Local image URL
#         """
#         try:
#             # Create a safe filename
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
#             safe_prompt = safe_prompt.replace(' ', '_')
#             filename = f"gpt_image1_{timestamp}_{style}_{shape}_{num_images}imgs_{safe_prompt}.png"
            
#             # Full path for the image
#             file_path = os.path.join(self.images_folder, filename)
            
#             # Download the image
#             response = requests.get(image_url)
#             response.raise_for_status()
            
#             # Save the image
#             with open(file_path, 'wb') as f:
#                 f.write(response.content)
            
#             # Return URL
#             local_image_url = f"{config.BASE_URL}/images/{filename}"
            
#             logger.info(f"Image saved to: {file_path}")
#             logger.info(f"Image URL: {local_image_url}")
#             return local_image_url
            
#         except Exception as e:
#             logger.error(f"Error downloading and saving image: {str(e)}")
#             raise

# # Create a singleton instance
# image1_service = Image1Service()
