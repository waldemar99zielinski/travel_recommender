from __future__ import annotations

from fastapi import FastAPI
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from api.core.exceptions import ApiError
from api.schemas.common import ErrorResponseDto


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def handle_api_error(_: Request, exc: ApiError) -> JSONResponse:
        payload = ErrorResponseDto(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        payload = ErrorResponseDto(
            code="validation_error",
            message="Request validation failed.",
            details={"errors": exc.errors()},
        )
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        payload = ErrorResponseDto(
            code="internal_server_error",
            message="Unexpected server error.",
            details={"error_type": exc.__class__.__name__},
        )
        return JSONResponse(status_code=500, content=payload.model_dump())
