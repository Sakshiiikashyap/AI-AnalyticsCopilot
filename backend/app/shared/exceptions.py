"""
Domain-level exceptions, mapped to HTTP responses in main.py exception handlers.

Keeping these decoupled from FastAPI/HTTPException means service-layer code
doesn't need to know about HTTP at all — it just raises meaningful domain errors.
"""
import uuid


class AppError(Exception):
    """Base class for all expected application errors."""
    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403


class ConflictError(AppError):
    status_code = 409


class ValidationFailedError(AppError):
    status_code = 422


def parse_uuid(value: str, entity_name: str = "resource") -> uuid.UUID:
    """
    Parses a string into a UUID, raising a clean 404 instead of letting a
    malformed ID crash through as a raw ValueError/DB error. Also ensures
    consistent bind-parameter types across DB dialects when filtering by
    UUID primary/foreign keys.
    """
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        raise NotFoundError(f"{entity_name.capitalize()} not found.")