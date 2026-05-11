"""Custom exception classes."""

from fastapi import HTTPException, status


class OpsPilotException(Exception):
    """Base exception for OpsPilot."""
    pass


class NotFoundError(OpsPilotException):
    """Resource not found."""
    pass


class ValidationError(OpsPilotException):
    """Validation failed."""
    pass


class AuthenticationError(OpsPilotException):
    """Authentication failed."""
    pass


class AuthorizationError(OpsPilotException):
    """Authorization failed."""
    pass


class ExternalServiceError(OpsPilotException):
    """External service call failed."""
    pass


def not_found_error(detail: str = "Resource not found") -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def validation_error(detail: str = "Validation failed") -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def unauthorized_error(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


def forbidden_error(detail: str = "Forbidden") -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
