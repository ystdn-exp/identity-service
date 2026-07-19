from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

ERROR_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "status_code": {"type": "integer"},
        "error": {"type": "string"},
        "message": {"type": "string"},
        "details": {
            "type": "array",
            "items": {"type": "object"},
        },
    },
    "required": ["status_code", "error", "message"],
}


def register_error_schema(app: FastAPI):
    """Register the standard error schema in the OpenAPI spec for all endpoints."""

    def error_schema_openapi() -> dict:
        """OpenAPI schema generator that registers the standard error schema."""
        if app.openapi_schema:
            return app.openapi_schema

        schema = get_openapi(
            title=app.title,
            version=app.version,
            summary=app.summary,
            description=app.description,
            routes=app.routes,
        )

        # FastAPI auto-documents validation failures with its own
        # HTTPValidationError shape, regardless of the custom exception
        # handlers registered above. Point every reference to it at our
        # actual error envelope instead, so /docs matches what the API
        # really returns.
        schemas = schema.setdefault("components", {}).setdefault("schemas", {})
        schemas["ErrorResponse"] = ERROR_RESPONSE_SCHEMA
        schemas.pop("HTTPValidationError", None)
        schemas.pop("ValidationError", None)

        for path_item in schema["paths"].values():
            for operation in path_item.values():
                for response in operation.get("responses", {}).values():
                    content = response.get("content", {}).get("application/json", {})
                    if (
                        content.get("schema", {})
                        .get("$ref", "")
                        .endswith("HTTPValidationError")
                    ):
                        content["schema"] = {
                            "$ref": "#/components/schemas/ErrorResponse"
                        }

        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = error_schema_openapi

    return app.openapi_schema
