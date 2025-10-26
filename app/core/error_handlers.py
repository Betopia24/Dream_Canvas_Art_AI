"""
Common error handling utilities for the application
"""
from fastapi import HTTPException
from typing import List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ErrorMessages:
    """Standard error messages for consistent responses"""
    
    # File-related errors
    INVALID_FILE_TYPE = "Invalid file type. Supported formats: {formats}"
    FILE_TOO_LARGE = "File size exceeds maximum limit of {limit}"
    FILE_REQUIRED = "At least one file is required"
    MAX_FILES_EXCEEDED = "Maximum {max_files} files allowed"
    EMPTY_FILE = "File appears to be empty or corrupted"
    
    # Parameter validation errors
    REQUIRED_PARAMETER = "Required parameter '{param}' is missing"
    INVALID_PARAMETER_VALUE = "Invalid value for '{param}'. Valid options: {options}"
    PARAMETER_OUT_OF_RANGE = "Parameter '{param}' must be between {min_val} and {max_val}"
    
    # Service errors
    SERVICE_UNAVAILABLE = "The requested service is temporarily unavailable. Please try again later."
    API_RATE_LIMIT = "Rate limit exceeded. Please wait before making another request."
    PROCESSING_FAILED = "Failed to process your request. Please check your input and try again."
    
    # Authentication/Authorization
    UNAUTHORIZED = "Authentication required. Please provide valid credentials."
    FORBIDDEN = "You don't have permission to access this resource."
    
    # General errors
    INTERNAL_ERROR = "An internal error occurred. Please try again later."
    INVALID_REQUEST = "The request is invalid or malformed."

def validate_file_types(files: List[Any], allowed_types: List[str], field_name: str = "file") -> None:
    """
    Validate file types against allowed formats
    
    Args:
        files: List of UploadFile objects
        allowed_types: List of allowed MIME types
        field_name: Name of the field for error messaging
    
    Raises:
        HTTPException: If validation fails
    """
    for i, file in enumerate(files):
        if not hasattr(file, 'content_type') or file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Invalid File Type",
                    "message": ErrorMessages.INVALID_FILE_TYPE.format(
                        formats=", ".join(allowed_types)
                    ),
                    "field": f"{field_name}[{i}]" if len(files) > 1 else field_name,
                    "received_type": getattr(file, 'content_type', 'unknown')
                }
            )

def validate_file_count(files: List[Any], max_files: int, field_name: str = "files") -> None:
    """
    Validate file count against maximum limit
    
    Args:
        files: List of files
        max_files: Maximum allowed files
        field_name: Name of the field for error messaging
    
    Raises:
        HTTPException: If validation fails
    """
    if len(files) > max_files:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Too Many Files",
                "message": ErrorMessages.MAX_FILES_EXCEEDED.format(max_files=max_files),
                "field": field_name,
                "provided_count": len(files),
                "max_allowed": max_files
            }
        )

def validate_parameter_choice(value: str, valid_options: List[str], param_name: str) -> None:
    """
    Validate parameter value against allowed choices
    
    Args:
        value: Parameter value to validate
        valid_options: List of valid options
        param_name: Parameter name for error messaging
    
    Raises:
        HTTPException: If validation fails
    """
    if value not in valid_options:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid Parameter Value",
                "message": ErrorMessages.INVALID_PARAMETER_VALUE.format(
                    param=param_name,
                    options=", ".join(valid_options)
                ),
                "field": param_name,
                "provided_value": value,
                "valid_options": valid_options
            }
        )

def validate_required_fields(data: dict, required_fields: List[str]) -> None:
    """
    Validate that all required fields are present and not empty
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Raises:
        HTTPException: If validation fails
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields or empty_fields:
        error_details = []
        
        if missing_fields:
            error_details.append({
                "type": "missing_fields",
                "fields": missing_fields,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            })
        
        if empty_fields:
            error_details.append({
                "type": "empty_fields", 
                "fields": empty_fields,
                "message": f"Empty required fields: {', '.join(empty_fields)}"
            })
        
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Required Fields Validation Error",
                "message": "Some required fields are missing or empty",
                "details": error_details
            }
        )

def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Optional[Any] = None,
    field: Optional[str] = None
) -> HTTPException:
    """
    Create a standardized error response
    
    Args:
        status_code: HTTP status code
        error_type: Type of error (e.g., "Validation Error", "Service Error")
        message: Human-readable error message
        details: Additional error details
        field: Field name if error is field-specific
    
    Returns:
        HTTPException with standardized error format
    """
    error_detail = {
        "error": error_type,
        "message": message,
        "status_code": status_code
    }
    
    if details is not None:
        error_detail["details"] = details
        
    if field is not None:
        error_detail["field"] = field
    
    return HTTPException(status_code=status_code, detail=error_detail)

def handle_service_error(e: Exception, service_name: str, operation: str) -> HTTPException:
    """
    Handle service-level errors with consistent logging and response format
    
    Args:
        e: The exception that occurred
        service_name: Name of the service where error occurred
        operation: The operation being performed
    
    Returns:
        HTTPException with appropriate error response
    """
    error_msg = str(e).lower()
    original_error = str(e)
    logger.error(f"Error during {operation} with {service_name}: {original_error}")
    
    # Handle fal.ai specific errors - enhanced detection
    if any(indicator in service_name.lower() for indicator in ["fal", "flux", "kontext"]) or \
       any(indicator in error_msg for indicator in ["fal.ai", "fal_client", "fal-ai"]):
        return handle_fal_ai_error(e, operation)
    
    # Handle OpenAI specific errors
    if "openai" in error_msg or "gpt" in error_msg or "dalle" in error_msg:
        return handle_openai_error(e, operation)
    
    # Handle Google/Gemini specific errors
    if "gemini" in error_msg or "google" in error_msg or "imagen" in error_msg:
        return handle_google_ai_error(e, operation)
    
    # Handle storage errors
    if "storage" in error_msg or "gcs" in error_msg or "bucket" in error_msg:
        return handle_storage_error(e, operation)
    
    # Handle network/connection errors
    if any(keyword in error_msg for keyword in ["connection", "timeout", "network", "unreachable"]):
        return create_error_response(
            503,
            "Network Error",
            f"Network connection failed during {operation}. Please check your internet connection and try again.",
            details={"service": service_name, "operation": operation, "error_type": "network"}
        )
    
    # Determine appropriate status code and user message based on error type
    if "rate limit" in error_msg or "quota" in error_msg:
        return create_error_response(
            429,
            "Rate Limit Error",
            f"Rate limit exceeded during {operation}. Please wait a moment before trying again.",
            details={"service": service_name, "operation": operation}
        )
    elif "unauthorized" in error_msg or "api key" in error_msg or "authentication" in error_msg:
        return create_error_response(
            401,
            "Authentication Error",
            f"Authentication failed with {service_name}. Please check service configuration.",
            details={"service": service_name, "operation": operation}
        )
    elif "forbidden" in error_msg or "permission" in error_msg:
        return create_error_response(
            403,
            "Authorization Error", 
            f"Insufficient permissions for {operation} with {service_name}.",
            details={"service": service_name, "operation": operation}
        )
    elif "not found" in error_msg or "404" in error_msg:
        return create_error_response(
            404,
            "Resource Not Found",
            f"The requested resource for {operation} was not found.",
            details={"service": service_name, "operation": operation}
        )
    else:
        # Generic service error
        return create_error_response(
            500,
            "Service Error",
            f"An error occurred during {operation}. Please try again later.",
            details={"service": service_name, "operation": operation}
        )

def handle_fal_ai_error(e: Exception, operation: str) -> HTTPException:
    """
    Handle fal.ai specific errors with user-friendly messages based on common error patterns
    """
    error_msg = str(e).lower()
    original_error = str(e)
    
    # Check for specific fal.ai error patterns and status codes
    # Order is important - check more specific patterns first
    
    # Rate limiting errors (429, quota exceeded) - check before auth to catch "429" properly
    if any(pattern in error_msg for pattern in [
        "rate limit", "429", "quota exceeded", "too many requests", 
        "rate exceeded", "throttled", "quota"
    ]):
        return create_error_response(
            429,
            "Rate Limit Error",
            "API rate limit exceeded. You've made too many requests in a short time period.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "rate_limit",
                "resolution": "Wait a few minutes before making another request. Consider upgrading your service plan for higher limits."
            }
        )
    
    # Authentication errors (401, API key issues)
    if any(pattern in error_msg for pattern in [
        "api key", "unauthorized", "401", "authentication failed", 
        "invalid api key", "missing api key", "fal_key"
    ]):
        return create_error_response(
            401,
            "Authentication Error",
            "API authentication failed. Please check that your API key is correctly configured in the environment.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "authentication",
                "resolution": "Verify that your API key environment variable is set with a valid API key"
            }
        )
    
    # Face detection errors (422)
    if any(pattern in error_msg for pattern in [
        "face_detection_error", "could not detect face", "no face detected", 
        "face detection failed", "face not found"
    ]):
        return create_error_response(
            422,
            "Face Detection Error",
            "Could not detect a face in the provided image. Face detection is required for this operation.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "face_detection_error",
                "resolution": "Ensure the image contains a clear, visible face and try again with a different image."
            }
        )

    # Content policy violations (safety checker)
    if any(pattern in error_msg for pattern in [
        "safety", "content policy", "inappropriate", "nsfw", "violation",
        "safety checker", "moderation", "blocked", "filtered", "content_policy_violation"
    ]):
        return create_error_response(
            422,
            "Content Policy Violation",
            "Your request was blocked by the service's safety filters. The prompt may contain inappropriate content.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "content_policy_violation",
                "resolution": "Modify your prompt to remove potentially inappropriate, violent, or explicit content and try again."
            }
        )
    
    # Image size validation errors (422)
    if any(pattern in error_msg for pattern in [
        "image_too_small", "image too small", "minimum size", "min_height", "min_width"
    ]):
        return create_error_response(
            422,
            "Image Too Small",
            "The provided image dimensions are smaller than the required minimum size.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "image_too_small",
                "resolution": "Use an image with larger dimensions that meets the minimum size requirements."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "image_too_large", "image too large", "maximum size", "max_height", "max_width", "image dimensions exceed"
    ]):
        return create_error_response(
            422,
            "Image Too Large",
            "The provided image dimensions exceed the maximum allowed limits.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "image_too_large",
                "resolution": "Resize your image to smaller dimensions that meet the maximum size requirements."
            }
        )

    # File format validation errors (422)
    if any(pattern in error_msg for pattern in [
        "unsupported_image_format", "unsupported image format", "invalid image format",
        "image format not supported"
    ]):
        return create_error_response(
            422,
            "Unsupported Image Format",
            "The image file format is not supported. Use a supported format like JPEG, PNG, or WebP.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "unsupported_image_format",
                "resolution": "Convert your image to a supported format (JPEG, PNG, WebP) and try again."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "unsupported_audio_format", "unsupported audio format", "invalid audio format",
        "audio format not supported"
    ]):
        return create_error_response(
            422,
            "Unsupported Audio Format",
            "The audio file format is not supported. Use a supported format like MP3, WAV, or OGG.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "unsupported_audio_format",
                "resolution": "Convert your audio file to a supported format (MP3, WAV, OGG) and try again."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "unsupported_video_format", "unsupported video format", "invalid video format",
        "video format not supported"
    ]):
        return create_error_response(
            422,
            "Unsupported Video Format",
            "The video file format is not supported. Use a supported format like MP4, MOV, or WebM.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "unsupported_video_format",
                "resolution": "Convert your video file to a supported format (MP4, MOV, WebM) and try again."
            }
        )

    # Model/endpoint not found (404)
    if any(pattern in error_msg for pattern in [
        "404", "not found", "model not found", "endpoint not found",
        "invalid model", "model does not exist"
    ]):
        return create_error_response(
            404,
            "Model Not Found",
            "The specified AI model or endpoint was not found. The model may have been updated or deprecated.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "model_not_found",
                "resolution": "Check the API documentation for the correct model endpoint name and update your code."
            }
        )
    
    # File size and archive errors (422)
    if any(pattern in error_msg for pattern in [
        "file_too_large", "file too large", "file size", "exceeds maximum", "max_size"
    ]):
        return create_error_response(
            422,
            "File Too Large",
            "The uploaded file exceeds the maximum allowed size limit.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "file_too_large",
                "resolution": "Reduce the file size or use a smaller file that meets the size requirements."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "invalid_archive", "invalid archive", "corrupted archive", "cannot read archive",
        "archive format", "unsupported archive"
    ]):
        return create_error_response(
            422,
            "Invalid Archive",
            "The provided archive file cannot be read or processed. It may be corrupted or in an unsupported format.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "invalid_archive",
                "resolution": "Ensure the archive is a valid ZIP or TAR.GZ file and not corrupted."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "archive_file_count_below_minimum", "too few files", "minimum files", "min_count"
    ]):
        return create_error_response(
            422,
            "Archive Has Too Few Files",
            "The provided archive contains fewer files than the minimum required count.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "archive_file_count_below_minimum",
                "resolution": "Add more files to your archive to meet the minimum file count requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "archive_file_count_exceeds_maximum", "too many files", "maximum files", "max_count"
    ]):
        return create_error_response(
            422,
            "Archive Has Too Many Files",
            "The provided archive contains more files than the maximum allowed count.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "archive_file_count_exceeds_maximum",
                "resolution": "Remove some files from your archive to meet the maximum file count limit."
            }
        )

    # Media duration errors (422)
    if any(pattern in error_msg for pattern in [
        "audio_duration_too_long", "audio duration too long", "audio too long", "max_duration"
    ]):
        return create_error_response(
            422,
            "Audio Duration Too Long",
            "The provided audio file exceeds the maximum allowed duration.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "audio_duration_too_long",
                "resolution": "Trim your audio file to meet the maximum duration requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "audio_duration_too_short", "audio duration too short", "audio too short", "min_duration"
    ]):
        return create_error_response(
            422,
            "Audio Duration Too Short",
            "The provided audio file is shorter than the minimum required duration.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "audio_duration_too_short",
                "resolution": "Use a longer audio file that meets the minimum duration requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "video_duration_too_long", "video duration too long", "video too long"
    ]):
        return create_error_response(
            422,
            "Video Duration Too Long",
            "The provided video file exceeds the maximum allowed duration.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "video_duration_too_long",
                "resolution": "Trim your video file to meet the maximum duration requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "video_duration_too_short", "video duration too short", "video too short"
    ]):
        return create_error_response(
            422,
            "Video Duration Too Short",
            "The provided video file is shorter than the minimum required duration.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "video_duration_too_short",
                "resolution": "Use a longer video file that meets the minimum duration requirement."
            }
        )

    # Numeric validation errors (422)
    if any(pattern in error_msg for pattern in [
        "greater_than", "should be greater than", "must be greater than", "gt"
    ]):
        return create_error_response(
            422,
            "Value Too Small",
            "The provided numeric value is not greater than the required minimum.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "greater_than",
                "resolution": "Use a larger value that meets the minimum requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "greater_than_equal", "should be greater than or equal", "must be greater than or equal", "ge"
    ]):
        return create_error_response(
            422,
            "Value Too Small",
            "The provided numeric value is less than the required minimum.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "greater_than_equal",
                "resolution": "Use a value greater than or equal to the minimum requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "less_than", "should be less than", "must be less than", "lt"
    ]):
        return create_error_response(
            422,
            "Value Too Large",
            "The provided numeric value is not less than the required maximum.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "less_than",
                "resolution": "Use a smaller value that meets the maximum requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "less_than_equal", "should be less than or equal", "must be less than or equal", "le"
    ]):
        return create_error_response(
            422,
            "Value Too Large",
            "The provided numeric value is greater than the required maximum.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "less_than_equal",
                "resolution": "Use a value less than or equal to the maximum requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "multiple_of", "should be a multiple of", "must be a multiple of", "multiple"
    ]):
        return create_error_response(
            422,
            "Invalid Multiple",
            "The provided numeric value is not a multiple of the required factor.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "multiple_of",
                "resolution": "Use a value that is a multiple of the required factor."
            }
        )

    # Sequence validation errors (422)
    if any(pattern in error_msg for pattern in [
        "sequence_too_short", "sequence too short", "should have at least", "min_length"
    ]):
        return create_error_response(
            422,
            "Sequence Too Short",
            "The provided sequence has fewer items than the required minimum length.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "sequence_too_short",
                "resolution": "Add more items to meet the minimum length requirement."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "sequence_too_long", "sequence too long", "should have at most", "max_length"
    ]):
        return create_error_response(
            422,
            "Sequence Too Long",
            "The provided sequence has more items than the maximum allowed length.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "sequence_too_long",
                "resolution": "Remove some items to meet the maximum length limit."
            }
        )
    
    # Choice validation errors (422)
    if any(pattern in error_msg for pattern in [
        "one_of", "should be", "invalid choice", "not in allowed values", "expected"
    ]):
        return create_error_response(
            422,
            "Invalid Choice",
            "The provided value is not among the set of allowed values.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "one_of",
                "resolution": "Use one of the allowed values specified in the API documentation."
            }
        )

    # Service-specific errors
    if any(pattern in error_msg for pattern in [
        "generation_timeout", "generation timeout", "request timeout", "operation timed out"
    ]):
        return create_error_response(
            504,
            "Generation Timeout",
            "The generation request took longer than the allowed time limit to complete.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "generation_timeout",
                "resolution": "Try again with simpler parameters or retry later when the service is less busy."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "downstream_service_error", "downstream service error", "external service error"
    ]):
        return create_error_response(
            400,
            "Downstream Service Error",
            "There was a problem communicating with an external service required to fulfill the request.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "downstream_service_error",
                "resolution": "This is usually a temporary issue. Try again in a few minutes."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "downstream_service_unavailable", "downstream service unavailable", "external service unavailable"
    ]):
        return create_error_response(
            500,
            "Downstream Service Unavailable",
            "A required third-party service is currently unavailable, preventing the request from being fulfilled.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "downstream_service_unavailable",
                "resolution": "Wait a few minutes and try again. The external service should be back online shortly."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "feature_not_supported", "feature not supported", "not supported", "unsupported feature"
    ]):
        return create_error_response(
            422,
            "Feature Not Supported",
            "The combination of input parameters requests a feature that is not supported by this endpoint.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "feature_not_supported",
                "resolution": "Check the API documentation for supported features and adjust your parameters."
            }
        )
    
    # Image load and file download errors (422)
    if any(pattern in error_msg for pattern in [
        "image_load_error", "image load error", "failed to load image", "corrupted image"
    ]):
        return create_error_response(
            422,
            "Image Load Error",
            "Failed to load or process the provided image. The image may be corrupted or in an unsupported format.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "image_load_error",
                "resolution": "Verify the image file is not corrupted and is in a supported format."
            }
        )
    
    if any(pattern in error_msg for pattern in [
        "file_download_error", "file download error", "failed to download", "download failed"
    ]):
        return create_error_response(
            422,
            "File Download Error",
            "Failed to download the file from the provided URL. Ensure the URL is publicly accessible.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "file_download_error",
                "resolution": "Check that the URL is correct, publicly accessible, and not behind authentication."
            }
        )

    # Service unavailable (503, 502, 500)
    if any(pattern in error_msg for pattern in [
        "503", "502", "500", "service unavailable", "server error",
        "model unavailable", "temporarily unavailable", "maintenance"
    ]):
        return create_error_response(
            503,
            "Service Unavailable",
            "AI service is temporarily unavailable. This may be due to high demand or maintenance.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "service_unavailable",
                "resolution": "Wait a few minutes and try again. Check the service status page for any ongoing issues."
            }
        )
    
    # Timeout errors (504, timeouts)
    if any(pattern in error_msg for pattern in [
        "timeout", "504", "gateway timeout", "request timeout", 
        "time out", "timed out", "deadline exceeded"
    ]):
        return create_error_response(
            504,
            "Request Timeout",
            "The request to the AI service timed out. Complex prompts or high-resolution images may take longer to process.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "timeout",
                "resolution": "Try simplifying your prompt, reducing image size, or trying again later when the service is less busy."
            }
        )
    
    # Input validation errors (400, invalid parameters)
    if any(pattern in error_msg for pattern in [
        "400", "bad request", "invalid", "parameter", "argument",
        "validation error", "invalid input", "malformed", "parse error"
    ]):
        # Extract more specific parameter information if available
        param_hint = ""
        if "image_size" in error_msg:
            param_hint = " Check that image_size is valid (e.g., 'square_hd', 'portrait_4_3', 'landscape_4_3')."
        elif "prompt" in error_msg:
            param_hint = " Ensure your prompt is not empty and contains valid text."
        elif "num_inference_steps" in error_msg:
            param_hint = " Check that num_inference_steps is within the valid range (typically 1-50)."
        elif "guidance_scale" in error_msg:
            param_hint = " Ensure guidance_scale is a positive number (typically 1.0-20.0)."
            
        return create_error_response(
            400,
            "Invalid Request",
            f"Invalid parameters sent to the AI service.{param_hint}",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "invalid_parameters",
                "resolution": "Check the API documentation for valid parameter values and formats.",
                "original_error": original_error
            }
        )
    
    # File upload errors
    if any(pattern in error_msg for pattern in [
        "upload", "file", "image too large", "file size", "format not supported",
        "invalid file", "corrupted", "unsupported format"
    ]):
        return create_error_response(
            400,
            "File Upload Error",
            "There was an issue with the uploaded file. Check file format, size, and integrity.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "file_upload_error",
                "resolution": "Ensure files are in supported formats (JPEG, PNG, WebP), under size limits, and not corrupted."
            }
        )
    
    # Connection/network errors
    if any(pattern in error_msg for pattern in [
        "connection", "network", "dns", "unreachable", "connection refused",
        "connection error", "network error", "ssl error"
    ]):
        return create_error_response(
            503,
            "Network Error",
            "Unable to connect to AI services. Check your internet connection.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "network_error",
                "resolution": "Check your internet connection and firewall settings. The issue may be temporary."
            }
        )
    
    # No results/empty response
    if any(pattern in error_msg for pattern in [
        "no images", "empty result", "no output", "failed to generate",
        "generation failed", "no content generated"
    ]):
        return create_error_response(
            500,
            "Generation Failed",
            "AI service failed to generate any output. This may be due to prompt complexity or temporary service issues.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "generation_failed",
                "resolution": "Try simplifying your prompt, adjusting parameters, or trying again in a few minutes."
            }
        )
    
    # Payment/billing errors
    if any(pattern in error_msg for pattern in [
        "payment", "billing", "insufficient", "credits", "balance",
        "subscription", "plan", "payment required"
    ]):
        return create_error_response(
            402,
            "Payment Required",
            "Your AI service account has insufficient credits or an inactive subscription.",
            details={
                "service": "AI Service", 
                "operation": operation, 
                "error_type": "payment_required",
                "resolution": "Check your account balance and add credits or upgrade your subscription plan."
            }
        )
    
    # Generic AI service error with more context
    return create_error_response(
        500,
        "AI Service Error",
        f"An unexpected error occurred with AI service during {operation}. This may be a temporary service issue.",
        details={
            "service": "AI Service", 
            "operation": operation, 
            "error_type": "generic",
            "resolution": "Try again in a few minutes. If the problem persists, contact support.",
            "original_error": original_error[:200]  # Truncate very long error messages
        }
    )

def handle_openai_error(e: Exception, operation: str) -> HTTPException:
    """
    Handle OpenAI specific errors
    """
    error_msg = str(e).lower()
    
    if "api key" in error_msg or "unauthorized" in error_msg:
        return create_error_response(
            401,
            "Authentication Error",
            "OpenAI authentication failed. Please check the service configuration.",
            details={"service": "OpenAI", "operation": operation}
        )
    
    if "rate limit" in error_msg or "quota" in error_msg:
        return create_error_response(
            429,
            "Rate Limit Error",
            "OpenAI rate limit exceeded. Please wait a moment before trying again.",
            details={"service": "OpenAI", "operation": operation}
        )
    
    if "content policy" in error_msg or "safety" in error_msg:
        return create_error_response(
            400,
            "Content Policy Violation",
            "Your request was rejected due to content policy restrictions. Please modify your prompt and try again.",
            details={"service": "OpenAI", "operation": operation}
        )
    
    return create_error_response(
        500,
        "AI Service Error",
        f"An error occurred with OpenAI during {operation}. Please try again later.",
        details={"service": "OpenAI", "operation": operation}
    )

def handle_google_ai_error(e: Exception, operation: str) -> HTTPException:
    """
    Handle Google AI/Gemini specific errors
    """
    error_msg = str(e).lower()
    
    if "api key" in error_msg or "unauthorized" in error_msg:
        return create_error_response(
            401,
            "Authentication Error",
            "Google AI authentication failed. Please check the service configuration.",
            details={"service": "Google AI", "operation": operation}
        )
    
    if "quota" in error_msg or "rate limit" in error_msg:
        return create_error_response(
            429,
            "Rate Limit Error",
            "Google AI rate limit exceeded. Please wait a moment before trying again.",
            details={"service": "Google AI", "operation": operation}
        )
    
    if "safety" in error_msg or "content policy" in error_msg:
        return create_error_response(
            400,
            "Content Policy Violation",
            "Your request was rejected due to content policy restrictions. Please modify your prompt and try again.",
            details={"service": "Google AI", "operation": operation}
        )
    
    return create_error_response(
        500,
        "AI Service Error",
        f"An error occurred with Google AI during {operation}. Please try again later.",
        details={"service": "Google AI", "operation": operation}
    )

def handle_storage_error(e: Exception, operation: str) -> HTTPException:
    """
    Handle storage-related errors (GCS, local storage, etc.)
    """
    error_msg = str(e).lower()
    
    if "permission" in error_msg or "access denied" in error_msg:
        return create_error_response(
            403,
            "Storage Permission Error",
            "Unable to save the generated content due to storage permissions.",
            details={"service": "Storage", "operation": operation}
        )
    
    if "quota" in error_msg or "storage" in error_msg and "full" in error_msg:
        return create_error_response(
            507,
            "Storage Full",
            "Storage quota exceeded. Please contact support.",
            details={"service": "Storage", "operation": operation}
        )
    
    return create_error_response(
        500,
        "Storage Error",
        "Unable to save the generated content. The content was generated successfully but couldn't be stored.",
        details={"service": "Storage", "operation": operation}
    )