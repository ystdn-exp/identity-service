from fastapi import Request, status, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.modules.shared.exceptions import AppException


def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Exception handler for application-specific exceptions.
    Returns a JSON response with the error message and status code.
    """

    response_body = {
        "status_code": getattr(
            exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR
        ),
        "error": getattr(exc, "error_name", "InternalServerError"),
        "message": str(exc),
    }

    if hasattr(exc, "details"):
        response_body["details"] = getattr(exc, "details", [])

    return JSONResponse(
        status_code=getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR),
        content=response_body,
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
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "error": "RequestValidationError",
            "message": "The request data is invalid.",
            "details": errors,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers with the FastAPI app.
    """

    app.add_exception_handler(
        AppException, app_exception_handler  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, internal_server_error_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
