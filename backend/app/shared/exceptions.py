import uuid


class AppError(Exception):
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class UnauthorizedError(AppError):
    status_code = 401


class ConflictError(AppError):
    status_code = 409


class ValidationFailedError(AppError):
    status_code = 422


class UpstreamError(AppError):
    status_code = 502


def parse_uuid(value: str, entity_name: str = "resource"):
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError(entity_name.capitalize() + " not found.")
