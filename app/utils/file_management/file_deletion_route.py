from fastapi import APIRouter, HTTPException, Depends
from .file_deletion_schema import DeleteFileRequest, DeleteFileResponse
from .file_deletion_service import GCSFileDeleter
from ...core.error_handlers import handle_service_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["file-management"], prefix="/file-management")

# Initialize the GCS file deleter service
def get_gcs_deleter():
    """Dependency to get GCS file deleter instance"""
    try:
        return GCSFileDeleter()
    except Exception as e:
        logger.error(f"Failed to initialize GCS deleter: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service Initialization Error",
                "message": "Failed to initialize Google Cloud Storage service. Please check your credentials.",
                "status_code": 500
            }
        )

@router.delete("/delete-gcs-file", response_model=DeleteFileResponse)
async def delete_gcs_file(
    request: DeleteFileRequest,
    gcs_deleter: GCSFileDeleter = Depends(get_gcs_deleter)
):
    """
    Delete a file from Google Cloud Storage using the provided URL
    
    Args:
        request: Contains the GCS file URL to delete
        gcs_deleter: GCS service dependency
        
    Returns:
        DeleteFileResponse with deletion status and details
        
    Raises:
        HTTPException: If deletion fails or URL is invalid
    """
    try:
        logger.info(f"Attempting to delete file: {request.file_url}")
        
        # Delete the file using the service
        result = gcs_deleter.delete_file(str(request.file_url))
        
        if result["success"]:
            logger.info(f"File deleted successfully: {request.file_url}")
            return DeleteFileResponse(**result)
        else:
            # Handle different types of errors
            error_type = result.get("error_type", "unknown")
            
            if error_type == "not_found":
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "File Not Found",
                        "message": result["message"],
                        "file_url": str(request.file_url),
                        "status_code": 404
                    }
                )
            elif error_type == "permission_denied":
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Permission Denied",
                        "message": result["message"],
                        "file_url": str(request.file_url),
                        "status_code": 403
                    }
                )
            elif error_type == "gcs_error":
                raise HTTPException(
                    status_code=502,
                    detail={
                        "error": "Google Cloud Storage Error",
                        "message": result["message"],
                        "file_url": str(request.file_url),
                        "status_code": 502
                    }
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "File Deletion Error",
                        "message": result["message"],
                        "file_url": str(request.file_url),
                        "status_code": 500
                    }
                )
                
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during file deletion: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": f"An unexpected error occurred while deleting the file: {str(e)}",
                "file_url": str(request.file_url),
                "status_code": 500
            }
        )

@router.get("/health")
async def health_check(gcs_deleter: GCSFileDeleter = Depends(get_gcs_deleter)):
    """
    Check the health of the Google Cloud Storage service
    
    Returns:
        Health status of the GCS service
    """
    try:
        health_status = gcs_deleter.health_check()
        
        if health_status["status"] == "healthy":
            return {
                "status": "healthy",
                "message": "File management service is operational",
                "gcs_status": health_status,
                "endpoints": [
                    "/file-management/delete-gcs-file",
                    "/file-management/health"
                ]
            }
        else:
            raise HTTPException(
                status_code=503,
                detail={
                    "error": "Service Unavailable",
                    "message": "Google Cloud Storage service is not healthy",
                    "gcs_status": health_status,
                    "status_code": 503
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Health Check Error",
                "message": f"Failed to perform health check: {str(e)}",
                "status_code": 500
            }
        )

@router.get("/info")
async def get_service_info():
    """
    Get information about the file management service
    """
    return {
        "service": "File Management Service",
        "version": "1.0.0",
        "description": "Service for managing files in Google Cloud Storage",
        "supported_operations": [
            "Delete files from GCS"
        ],
        "supported_url_formats": [
            "gs://bucket-name/path/to/file",
            "https://storage.googleapis.com/bucket-name/path/to/file",
            "https://storage.cloud.google.com/bucket-name/path/to/file"
        ],
        "endpoints": {
            "delete_file": "/file-management/delete-gcs-file",
            "health_check": "/file-management/health",
            "service_info": "/file-management/info"
        }
    }