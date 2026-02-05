from fastapi import Request, HTTPException, statusnfrom fastapi.responses import JSONResponsenfrom fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import jsonnnasync def http_exception_handler(request: Request, exc: HTTPException):n    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        },
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):n    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validation Error",
            "errors": errors,
            "error_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        },
    )