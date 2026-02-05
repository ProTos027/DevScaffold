from fastapi import HTTPException, status

class CredentialException(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})

class UserNotFoundException(HTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UserAlreadyExistsException(HTTPException):
    def __init__(self, detail: str = "Username already registered"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class TodoNotFoundException(HTTPException):
    def __init__(self, detail: str = "Todo item not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Not authenticated or authorized"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail,
                         headers={"WWW-Authenticate": "Bearer"})