from typing import Any, Dict, List, Optional
from fastapi import status


class AppException(Exception):
    """
    Base class for application-specific exceptions.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_name: str = "InternalServerError"

    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)


class BusinessValidationError(AppException):
    """
    Exception for business logic errors.

    Attributes:
        message - explanation of the error
        field - the field that caused the error
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_name: str = "BusinessValidationError"

    def __init__(self, message: str, field: str = ""):
        details = [{"field": field, "message": message}] if field else []
        super().__init__(message, details)


class NotFoundError(AppException):
    """
    Exception for not found errors.
    """

    status_code: int = status.HTTP_404_NOT_FOUND
    error_name: str = "NotFoundError"

    def __init__(self, message: str = "The requested resource was not found."):
        super().__init__(message)


class ForbiddenError(AppException):
    """
    Exception for forbidden access errors.
    """

    status_code: int = status.HTTP_403_FORBIDDEN
    error_name: str = "ForbiddenError"

    def __init__(self, message: str = "Access to the requested resource is forbidden."):
        super().__init__(message)


class UnauthorizedError(AppException):
    """
    Exception for unauthorized access errors.
    """

    status_code: int = status.HTTP_401_UNAUTHORIZED
    error_name: str = "UnauthorizedError"

    def __init__(
        self, message: str = "Authentication is required to access this resource."
    ):
        super().__init__(message)
