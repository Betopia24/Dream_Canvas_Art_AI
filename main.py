from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
import sys

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import feature routes directly
from app.features.feature_1.dream_interpreter_route import router as dream_interpreter_router
from app.features.feature_2.dalle_route import router as dalle_router
# from features.feature_3.image1_route import router as image1_router
from app.features.feature_4.videogen_route import router as videogen_router
from app.features.feature_5.prompt_enhancer_route import router as prompt_enhancer_router
from app.features.feature_6.flux_1_spro_route import router as flux1_spro_router
from app.features.feature_7.gemini_route import router as gemini_router
from app.features.feature_8.gemini_nanobanana_route import router as gemini_nanobanana_router
from app.features.feature_9.flux_kontext_dev_route import router as flux_kontext_dev_router
from app.features.feature_10.videogen3_route import router as videogen3_router
from app.features.feature_11.flux_kontext_dev_edit_route import router as flux_kontext_edit_router
from app.features.feature_12.qwen_route import router as qwen_router
from app.features.feature_13.kling_text_video_route import router as kling_text_video_router
from app.features.feature_14.kling_image_video_route import router as kling_image_video_router
from app.features.feature_15.wan2_2_image_video_route import router as wan22_image_video_router
from app.features.feature_16.pixverse_text_image_route import router as pixverse_text_image_router
from app.features.feature_17.pixverse_image_video_route import router as pixverse_image_video_router
from app.features.feature_18.ai_avatar_route import router as ai_avatar_router
from app.features.feature_19.minimax_music_route import router as minimax_music_router
from app.features.feature_20.seedream_image_edit_route import router as seedream_image_edit_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="XobehStudio AI Services",
    description="AI service platform with Stable Diffusion image generation, Gemini AI, and intelligent prompt enhancement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # List only the allowed origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["*"],  # Allow all headers
)



# Mount static files directory for serving generated images
images_dir = os.path.join(os.path.dirname(__file__), "generated_images")
os.makedirs(images_dir, exist_ok=True)
app.mount("/images", StaticFiles(directory=images_dir), name="images")

# Mount static files directory for serving generated videos
videos_dir = os.path.join(os.path.dirname(__file__), "generated_videos")
os.makedirs(videos_dir, exist_ok=True)
app.mount("/videos", StaticFiles(directory=videos_dir), name="videos")

# Mount static files directory for serving generated audio
audio_dir = os.path.join(os.path.dirname(__file__), "generated_audio")
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

# Mount temporary files directory for API file access
temp_dir = os.path.join(os.path.dirname(__file__), "temp_uploads")
os.makedirs(temp_dir, exist_ok=True)
app.mount("/temp", StaticFiles(directory=temp_dir), name="temp")

# Include routers
app.include_router(dream_interpreter_router, prefix="/api/v1")
app.include_router(prompt_enhancer_router, prefix="/api/v1")
app.include_router(dalle_router, prefix="/api/v1")
# app.include_router(image1_router, prefix="/api/v1")
app.include_router(videogen_router, prefix="/api/v1")
app.include_router(flux1_spro_router, prefix="/api/v1")
app.include_router(videogen3_router, prefix="/api/v1")
app.include_router(gemini_router, prefix="/api/v1")
app.include_router(gemini_nanobanana_router, prefix="/api/v1")
app.include_router(flux_kontext_dev_router, prefix="/api/v1")
app.include_router(flux_kontext_edit_router, prefix="/api/v1")
app.include_router(qwen_router, prefix="/api/v1")
app.include_router(kling_text_video_router, prefix="/api/v1")
app.include_router(kling_image_video_router, prefix="/api/v1")
app.include_router(wan22_image_video_router, prefix="/api/v1")
app.include_router(pixverse_text_image_router, prefix="/api/v1")
app.include_router(pixverse_image_video_router, prefix="/api/v1")
app.include_router(ai_avatar_router, prefix="/api/v1")
app.include_router(minimax_music_router, prefix="/api/v1")
app.include_router(seedream_image_edit_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "XobehStudio AI Services",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """General health check endpoint"""
    return {
        "status": "healthy",
        "message": "XobehStudio AI Services is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8069,
        reload=True,
        log_level="info"
    )