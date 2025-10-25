import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Simple configuration class that reads all settings from .env file"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_API_SECRET = os.getenv("GEMINI_API_SECRET")
    OPEN_AI_API_KEY = os.getenv("OPEN_AI_API_KEY")
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    FAL_API_KEY = os.getenv("FAL_API_KEY")
    
    # Stable Diffusion Settings
    STABLE_DIFFUSION_MODEL_ID = os.getenv("STABLE_DIFFUSION_MODEL_ID", "runwayml/stable-diffusion-v1-5")
    STABLE_DIFFUSION_DEVICE = os.getenv("STABLE_DIFFUSION_DEVICE", "cuda")
    
    # Image Generation Settings
    IMAGE_WIDTH = int(os.getenv("IMAGE_WIDTH", "1024"))
    IMAGE_HEIGHT = int(os.getenv("IMAGE_HEIGHT", "1024"))
    NUM_INFERENCE_STEPS = int(os.getenv("NUM_INFERENCE_STEPS", "50"))
    GUIDANCE_SCALE = float(os.getenv("GUIDANCE_SCALE", "7.0"))
    NEGATIVE_PROMPT = os.getenv("NEGATIVE_PROMPT", "blurry, low quality, distorted, deformed")
    
    # Advanced Quality Settings
    SCHEDULER_TYPE = os.getenv("SCHEDULER_TYPE", "DPMSolverMultistepScheduler")
    CFG_RESCALE = float(os.getenv("CFG_RESCALE", "0.7"))
    CLIP_SKIP = int(os.getenv("CLIP_SKIP", "1"))
    SEED = int(os.getenv("SEED", "-1"))
    
    # Output Settings
    IMAGES_DIR = os.getenv("IMAGES_DIR", "generated_images")
    BASE_URL = os.getenv("BASE_URL", "http://10.0.30.211:5642")
    
    # File Upload Settings
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))  # Maximum file size in MB
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

    GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


# Global config instance
config = Config()
