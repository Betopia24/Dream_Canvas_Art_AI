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
    logger.error(f"Error during {operation}: {str(e)}")
    
    # Handle fal.ai specific errors
    if "fal" in service_name.lower() or "fal.ai" in error_msg:
        return handle_fal_ai_error(e, operation)
    
    # Handle OpenAI specific errors
    if "openai" in error_msg or "gpt" in error_msg:
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
    Handle fal.ai specific errors with user-friendly messages
    """
    error_msg = str(e).lower()
    
    # API key issues
    if "api key" in error_msg or "unauthorized" in error_msg or "401" in error_msg:
        return create_error_response(
            401,
            "Authentication Error",
            "fal.ai authentication failed. Please check the service configuration.",
            details={"service": "fal.ai", "operation": operation, "error_type": "authentication"}
        )
    
    # Rate limiting
    if "rate limit" in error_msg or "429" in error_msg or "quota" in error_msg:
        return create_error_response(
            429,
            "Rate Limit Error",
            "fal.ai rate limit exceeded. Please wait a moment before trying again.",
            details={"service": "fal.ai", "operation": operation, "error_type": "rate_limit"}
        )
    
    # Content policy violations
    if "safety" in error_msg or "content policy" in error_msg or "inappropriate" in error_msg:
        return create_error_response(
            400,
            "Content Policy Violation",
            "Your request was rejected due to content policy restrictions. Please modify your prompt and try again.",
            details={"service": "fal.ai", "operation": operation, "error_type": "content_policy"}
        )
    
    # Model/service unavailable
    if "model" in error_msg and ("unavailable" in error_msg or "not found" in error_msg):
        return create_error_response(
            503,
            "Service Unavailable",
            "The AI model is temporarily unavailable. Please try again in a few minutes.",
            details={"service": "fal.ai", "operation": operation, "error_type": "model_unavailable"}
        )
    
    # Timeout errors
    if "timeout" in error_msg or "time out" in error_msg:
        return create_error_response(
            504,
            "Request Timeout",
            "The request took too long to process. Please try again with a simpler prompt.",
            details={"service": "fal.ai", "operation": operation, "error_type": "timeout"}
        )
    
    # Invalid parameters
    if "invalid" in error_msg or "parameter" in error_msg or "argument" in error_msg:
        return create_error_response(
            400,
            "Invalid Request",
            "Invalid parameters sent to fal.ai. Please check your request and try again.",
            details={"service": "fal.ai", "operation": operation, "error_type": "invalid_parameters"}
        )
    
    # No images generated
    if "no images" in error_msg or "empty result" in error_msg:
        return create_error_response(
            500,
            "Generation Failed",
            "Failed to generate image. Please try again with a different prompt.",
            details={"service": "fal.ai", "operation": operation, "error_type": "generation_failed"}
        )
    
    # Generic fal.ai error
    return create_error_response(
        500,
        "AI Service Error",
        f"An error occurred with the AI service during {operation}. Please try again later.",
        details={"service": "fal.ai", "operation": operation, "error_type": "generic"}
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