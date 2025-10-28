from fastapi import APIRouter, HTTPException
# from google.cloud import storage
# from google.cloud.exceptions import NotFound, Forbidden, GoogleCloudError
import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["delete-user-data"], prefix="/delete-user-data")

# Get bucket name from environment variable
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "xobestudio-bucket")

def get_gcs_client():
    """Get Google Cloud Storage client"""
    try:
        # Import here to avoid import errors if not available
        from google.cloud import storage
        return storage.Client()
    except ImportError:
        logger.error("Google Cloud Storage package not installed")
        raise HTTPException(status_code=500, detail="Google Cloud Storage service not available")
    except Exception as e:
        logger.error(f"Failed to initialize GCS client: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize Google Cloud Storage client")

def parse_gcs_url(gcs_url: str) -> str:
    """Parse GCS URL to extract the file path"""
    try:
        if gcs_url.startswith('gs://'):
            # Format: gs://bucket-name/path/to/file
            url_without_protocol = gcs_url[5:]  # Remove 'gs://'
            parts = url_without_protocol.split('/', 1)
            if len(parts) < 2:
                raise ValueError("Invalid GCS URL format")
            return parts[1]  # Return just the file path
            
        elif 'storage.googleapis.com' in gcs_url or 'storage.cloud.google.com' in gcs_url:
            # Format: https://storage.googleapis.com/bucket-name/path/to/file
            parsed_url = urlparse(gcs_url)
            path_parts = parsed_url.path.lstrip('/').split('/', 1)
            if len(path_parts) < 2:
                raise ValueError("Invalid GCS URL format")
            return path_parts[1]  # Return just the file path
            
        else:
            raise ValueError("Unsupported GCS URL format")
            
    except Exception as e:
        logger.error(f"Error parsing GCS URL {gcs_url}: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid GCS URL format: {e}")

@router.delete("/delete-file")
async def delete_gcs_file(file_url: str):
    """
    Delete a specific file from Google Cloud Storage using the provided URL
    
    Args:
        file_url: The full URL to the file in GCS
        
    Returns:
        Success message
    """
    try:
        logger.info(f"Attempting to delete file: {file_url}")
        
        # Get GCS client
        client = get_gcs_client()
        
        # Parse the URL to get file path
        file_path = parse_gcs_url(file_url)
        
        # Get the bucket
        bucket = client.bucket(BUCKET_NAME)
        
        # Get the blob (file)
        blob = bucket.blob(file_path)
        
        # Check if file exists and delete it
        if blob.exists():
            blob.delete()
            logger.info(f"Successfully deleted file: {file_url}")
            return {"message": "File deleted successfully"}
        else:
            logger.warning(f"File does not exist: {file_url}")
            raise HTTPException(status_code=404, detail="File not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file {file_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.delete("/delete-folder")
async def delete_gcs_folder(folder_name: str):
    """
    Delete a folder and all its contents from audio, video, and image directories
    
    Args:
        folder_name: Name of the folder to delete from all three directories
        
    Returns:
        Success message with details of deleted folders
    """
    try:
        logger.info(f"Attempting to delete folder: {folder_name}")
        
        # Get GCS client
        client = get_gcs_client()
        bucket = client.bucket(BUCKET_NAME)
        
        # Define the three folder paths
        folder_paths = [
            f"audio/{folder_name}/",
            f"video/{folder_name}/", 
            f"image/{folder_name}/"
        ]
        
        deleted_folders = []
        total_files_deleted = 0
        
        for folder_path in folder_paths:
            try:
                # List all blobs with the folder prefix
                blobs = bucket.list_blobs(prefix=folder_path)
                blob_list = list(blobs)
                
                if blob_list:
                    # Delete all files in the folder
                    files_in_folder = 0
                    for blob in blob_list:
                        blob.delete()
                        files_in_folder += 1
                        total_files_deleted += 1
                    
                    deleted_folders.append({
                        "folder": folder_path,
                        "files_deleted": files_in_folder
                    })
                    logger.info(f"Deleted folder {folder_path} with {files_in_folder} files")
                else:
                    logger.info(f"Folder {folder_path} was empty or didn't exist")
                    
            except Exception as e:
                logger.error(f"Error deleting folder {folder_path}: {e}")
                # Continue with other folders even if one fails
        
        if deleted_folders:
            logger.info(f"Successfully deleted {len(deleted_folders)} folders with total {total_files_deleted} files")
            return {
                "message": f"Successfully deleted folder '{folder_name}' from {len(deleted_folders)} directories",
                "deleted_folders": deleted_folders,
                "total_files_deleted": total_files_deleted
            }
        else:
            logger.warning(f"No folders found with name: {folder_name}")
            return {
                "message": f"No folders found with name '{folder_name}' in any directory",
                "deleted_folders": [],
                "total_files_deleted": 0
            }
            
    except Exception as e:
        logger.error(f"Error deleting folder {folder_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete folder: {str(e)}")