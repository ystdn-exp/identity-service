from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.modules.shared.exceptions import register_exception_handlers
from app.core.routes.routes_v1 import router
from app.core.logging import init_logging
from app.core.sentry import init_sentry
from app.core.openapi import register_error_schema

description = """
## Identity Service

### Global error standard
All endpoints return standard error schemas on failure:
- 400 Bad Request - Business logic validation error
- 401 Unauthorized - Token is missing or invalid
- 403 Forbidden - User does not have permission to access the resource
- 404 Not Found - Resource not found
- 422 Unprocessable Entity - Request validation error
"""


def create_app() -> FastAPI:
    app = FastAPI(
        title="Identity Service",
        summary="Users and authentication service",
        version="0.1.0",
        description=description,
    )

    cors_settings = settings.cors_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods,
        allow_headers=cors_settings.allow_headers,
    )

    register_exception_handlers(app)

    app.include_router(router)

    register_error_schema(app)

    init_logging()
    init_sentry()

    return app


app = create_app()
