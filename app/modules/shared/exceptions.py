from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class BusinessValidationError(Exception):
    """
    Exception for business logic errors.

    Attributes:
        message - explanation of the error
        field - the field that caused the error
    """

    def __init__(self, message: str, field: str = ""):
        self.message = message
        self.field = field
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    Exception for not found errors.
    """

    def __init__(self, message: str = "The requested resource was not found."):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """
    Exception for forbidden access errors.
    """

    def __init__(self, message: str = "Access to the requested resource is forbidden."):
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """
    Exception for unauthorized access errors.
    """

    def __init__(
        self, message: str = "Authentication is required to access this resource."
    ):
        self.message = message
        super().__init__(self.message)


def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    """
    Exception handler for NotFoundError.
    Returns a JSON response with the error message.
    """

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "status_code": status.HTTP_404_NOT_FOUND,
            "error": "NotFoundError",
            "message": exc.message,
        },
    )


def forbidden_exception_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    """
    Exception handler for ForbiddenError.
    Returns a JSON response with the error message.
    """

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "status_code": status.HTTP_403_FORBIDDEN,
            "error": "ForbiddenError",
            "message": exc.message,
        },
    )


def busines_validation_exception_handler(
    request: Request, exc: BusinessValidationError
) -> JSONResponse:
    """
    Exception handler for BusinessValidationError.
    Returns a JSON response with the error message and field.
    """

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status_code": status.HTTP_400_BAD_REQUEST,
            "error": "BusinessValidationError",
            "message": "The data provided is invalid.",
            "details": [
                {
                    "field": exc.field,
                    "message": exc.message,
                }
            ],
        },
    )


def internal_server_error_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """
    Exception handler for unhandled exceptions.
    Returns a JSON response with a generic error message.
    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Exception handler for RequestValidationError.
    Returns a JSON response with the validation error details.
    """

    errors = []
    for error in exc.errors():
        field_name = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(
            {
                "field": field_name,
                "message": error["msg"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "error": "RequestValidationError",
            "message": "The request data is invalid.",
            "details": errors,
        },
    )


def unauthorized_exception_handler(
    request: Request, exc: UnauthorizedError
) -> JSONResponse:
    """
    Exception handler for UnauthorizedError.
    Returns a JSON response with the error message.
    """

    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "error": "UnauthorizedError",
            "message": exc.message,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers with the FastAPI app.
    """

    app.add_exception_handler(NotFoundError, not_found_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ForbiddenError, forbidden_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(
        BusinessValidationError, busines_validation_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, internal_server_error_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(UnauthorizedError, unauthorized_exception_handler)  # type: ignore[arg-type]
