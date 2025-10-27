from pydantic import BaseModel, HttpUrl, validator
from typing import Optional

class DeleteFileRequest(BaseModel):
    """Request model for deleting a file from Google Cloud Storage"""
    file_url: HttpUrl
    
    @validator('file_url')
    def validate_gcs_url(cls, v):
        """Validate that the URL is a Google Cloud Storage URL"""
        url_str = str(v)
        if not (url_str.startswith('https://storage.googleapis.com/') or 
                url_str.startswith('gs://') or
                'storage.cloud.google.com' in url_str):
            raise ValueError('URL must be a valid Google Cloud Storage URL')
        return v

    class Config:
        schema_extra = {
            "example": {
                "file_url": "https://storage.googleapis.com/your-bucket-name/path/to/file.jpg"
            }
        }

class DeleteFileResponse(BaseModel):
    """Response model for file deletion"""
    success: bool
    message: str
    deleted_file_url: str
    bucket_name: Optional[str] = None
    file_path: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "File deleted successfully",
                "deleted_file_url": "https://storage.googleapis.com/your-bucket-name/path/to/file.jpg",
                "bucket_name": "your-bucket-name",
                "file_path": "path/to/file.jpg"
            }
        }