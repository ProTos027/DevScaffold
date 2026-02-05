from fastapi import status


class ChessEngineException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class UnauthorizedException(ChessEngineException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(ChessEngineException):
    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(detail, status.HTTP_403_FORBIDDEN)


class NotFoundException(ChessEngineException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class ConflictException(ChessEngineException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail, status.HTTP_409_CONFLICT)


class BadRequestException(ChessEngineException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
