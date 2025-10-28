from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import os
import sys
from typing import Union

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.features.feature_1.dream_interpreter_route import router as dream_interpreter_router
from app.features.feature_2.dalle_route import router as dalle_router
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
from app.features.feature_16.pixverse_text_to_video_route import router as pixverse_text_image_router
from app.features.feature_17.pixverse_image_video_route import router as pixverse_image_video_router
from app.features.feature_18.ai_avatar_route import router as ai_avatar_router
from app.features.feature_19.minimax_music_route import router as minimax_music_router
from app.features.feature_20.seedream_image_edit_route import router as seedream_image_edit_router
from app.features.feature_21.prompt_enhancer_route import router as audio_prompt_enhancer_router
from app.features.feature_22.prompt_enhancer_route import router as video_prompt_enhancer_router
from app.utils.delete_user_info import router as delete_user_data_router


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

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with user-friendly messages
    """
    logger.error(f"Validation error on {request.url}: {exc}")
    
    # Extract specific error details
    errors = []
    for error in exc.errors():
        field_name = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = error["msg"]
        error_type = error["type"]
        
        # Create user-friendly error messages
        if error_type == "value_error" and "Expected UploadFile" in error_msg:
            user_friendly_msg = f"Invalid file format for field '{field_name}'. Please upload a valid file."
        elif error_type == "missing":
            user_friendly_msg = f"Required field '{field_name}' is missing."
        elif error_type == "type_error":
            user_friendly_msg = f"Invalid data type for field '{field_name}'. {error_msg}"
        else:
            user_friendly_msg = f"Invalid value for field '{field_name}': {error_msg}"
        
        errors.append({
            "field": field_name,
            "message": user_friendly_msg,
            "error_type": error_type
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "message": "The request contains invalid data. Please check the following fields:",
            "details": errors,
            "status_code": 422
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with consistent error format
    """
    logger.error(f"HTTP error on {request.url}: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code} Error",
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors
    """
    logger.error(f"Unexpected error on {request.url}: {type(exc).__name__}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later or contact support if the issue persists.",
            "status_code": 500,
            "path": str(request.url)
        }
    )


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "https://dream-canvas.art",
    #     "https://xobehtedistuo-web-88238903740.us-central1.run.app",
    #     "http://localhost:3001"
    # ],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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
app.include_router(audio_prompt_enhancer_router, prefix="/api/v1")
app.include_router(video_prompt_enhancer_router, prefix="/api/v1")
app.include_router(delete_user_data_router, prefix="/api/v1")

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
        port=8080,
        reload=True,
        log_level="info"
    )