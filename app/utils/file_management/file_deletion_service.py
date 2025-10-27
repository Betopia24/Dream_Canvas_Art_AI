from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden, GoogleCloudError
import os
import re
import logging
from urllib.parse import urlparse
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class GCSFileDeleter:
    """Service class for deleting files from Google Cloud Storage"""
    
    def __init__(self):
        """Initialize the GCS client"""
        try:
            # Initialize the client - it will use the default credentials
            # You can set GOOGLE_APPLICATION_CREDENTIALS environment variable
            # or use service account key file
            self.client = storage.Client()
            logger.info("GCS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise

    def parse_gcs_url(self, gcs_url: str) -> Tuple[str, str]:
        """
        Parse GCS URL to extract bucket name and file path
        
        Args:
            gcs_url: Google Cloud Storage URL
            
        Returns:
            Tuple of (bucket_name, file_path)
            
        Raises:
            ValueError: If URL format is invalid
        """
        try:
            # Handle different GCS URL formats
            if gcs_url.startswith('gs://'):
                # Format: gs://bucket-name/path/to/file
                url_without_protocol = gcs_url[5:]  # Remove 'gs://'
                parts = url_without_protocol.split('/', 1)
                if len(parts) < 2:
                    raise ValueError("Invalid GCS URL format")
                bucket_name = parts[0]
                file_path = parts[1]
                
            elif 'storage.googleapis.com' in gcs_url or 'storage.cloud.google.com' in gcs_url:
                # Format: https://storage.googleapis.com/bucket-name/path/to/file
                # or https://storage.cloud.google.com/bucket-name/path/to/file
                parsed_url = urlparse(gcs_url)
                
                # Ensure it's HTTPS
                if parsed_url.scheme != 'https':
                    raise ValueError("GCS URLs must use HTTPS protocol")
                    
                path_parts = parsed_url.path.lstrip('/').split('/', 1)
                if len(path_parts) < 2:
                    raise ValueError("Invalid GCS URL format")
                bucket_name = path_parts[0]
                file_path = path_parts[1]
                
            else:
                raise ValueError("Unsupported GCS URL format")
                
            if not bucket_name or not file_path:
                raise ValueError("Could not extract bucket name or file path from URL")
                
            logger.info(f"Parsed GCS URL - Bucket: {bucket_name}, File: {file_path}")
            return bucket_name, file_path
            
        except Exception as e:
            logger.error(f"Error parsing GCS URL {gcs_url}: {e}")
            raise ValueError(f"Invalid GCS URL format: {e}")

    def delete_file(self, gcs_url: str) -> dict:
        """
        Delete a file from Google Cloud Storage
        
        Args:
            gcs_url: The full URL to the file in GCS
            
        Returns:
            Dictionary with deletion status and details
            
        Raises:
            Exception: If deletion fails
        """
        try:
            # Parse the URL to get bucket and file path
            bucket_name, file_path = self.parse_gcs_url(gcs_url)
            
            # Get the bucket
            bucket = self.client.bucket(bucket_name)
            
            # Get the blob (file)
            blob = bucket.blob(file_path)
            
            # Check if file exists
            if not blob.exists():
                logger.warning(f"File does not exist: {gcs_url}")
                return {
                    "success": False,
                    "message": f"File not found in Google Cloud Storage",
                    "deleted_file_url": gcs_url,
                    "bucket_name": bucket_name,
                    "file_path": file_path,
                    "error_type": "not_found"
                }
            
            # Delete the file
            blob.delete()
            
            logger.info(f"Successfully deleted file: {gcs_url}")
            return {
                "success": True,
                "message": "File deleted successfully from Google Cloud Storage",
                "deleted_file_url": gcs_url,
                "bucket_name": bucket_name,
                "file_path": file_path
            }
            
        except NotFound:
            logger.warning(f"File not found: {gcs_url}")
            return {
                "success": False,
                "message": "File not found in Google Cloud Storage",
                "deleted_file_url": gcs_url,
                "bucket_name": bucket_name if 'bucket_name' in locals() else None,
                "file_path": file_path if 'file_path' in locals() else None,
                "error_type": "not_found"
            }
            
        except Forbidden as e:
            logger.error(f"Permission denied for file deletion: {gcs_url} - {e}")
            return {
                "success": False,
                "message": "Permission denied. Check your Google Cloud Storage credentials and permissions",
                "deleted_file_url": gcs_url,
                "bucket_name": bucket_name if 'bucket_name' in locals() else None,
                "file_path": file_path if 'file_path' in locals() else None,
                "error_type": "permission_denied"
            }
            
        except GoogleCloudError as e:
            logger.error(f"Google Cloud error during file deletion: {gcs_url} - {e}")
            return {
                "success": False,
                "message": f"Google Cloud Storage error: {str(e)}",
                "deleted_file_url": gcs_url,
                "bucket_name": bucket_name if 'bucket_name' in locals() else None,
                "file_path": file_path if 'file_path' in locals() else None,
                "error_type": "gcs_error"
            }
            
        except Exception as e:
            logger.error(f"Unexpected error during file deletion: {gcs_url} - {e}")
            return {
                "success": False,
                "message": f"Unexpected error occurred: {str(e)}",
                "deleted_file_url": gcs_url,
                "bucket_name": bucket_name if 'bucket_name' in locals() else None,
                "file_path": file_path if 'file_path' in locals() else None,
                "error_type": "unexpected_error"
            }

    def health_check(self) -> dict:
        """
        Check if GCS client is properly configured and accessible
        
        Returns:
            Dictionary with health status
        """
        try:
            # Try to list buckets to test connection
            buckets = list(self.client.list_buckets(max_results=1))
            return {
                "status": "healthy",
                "message": "Google Cloud Storage client is working properly",
                "client_initialized": True
            }
        except Exception as e:
            logger.error(f"GCS health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Google Cloud Storage client error: {str(e)}",
                "client_initialized": False
            }