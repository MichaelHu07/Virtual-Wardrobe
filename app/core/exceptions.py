from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Custom handler for HTTP exceptions.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Custom handler for validation errors.
    """
    errors: Dict[str, Any] = {"detail": []}
    for error in exc.errors():
        error_msg = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        errors["detail"].append(error_msg) # type: ignore
        
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=errors,
    )

class ServiceException(Exception):
    """Base class for service-layer exceptions"""
    def __init__(self, message: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code

async def service_exception_handler(request: Request, exc: ServiceException) -> JSONResponse:
    """
    Handler for custom ServiceException.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

