from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

class APIException(HTTPException):
    def __init__(self, status_code: int, detail: str = "An unexpected error occurred."):
        super().__init__(status_code=status_code, detail=detail)

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Example of a custom error
class UserNotFoundException(APIException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found.")

class UnauthorizedException(APIException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=401, detail=detail)

class ForbiddenException(APIException):
    def __init__(self):
        super().__init__(status_code=403, detail="Not enough permissions.")
