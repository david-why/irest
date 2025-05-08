from typing import Any


class ApplicationException(Exception):
    """Base class for all application exceptions."""

    code = 500

    def __init__(self, detail: Any = None):
        super().__init__(detail)
        self.detail = detail


class NotFoundException(ApplicationException):
    """Exception raised when a resource is not found."""

    code = 404


class InternalException(ApplicationException):
    """Exception raised for internal errors."""

    code = 500


class ObjCException(InternalException):
    """Exception raised for Objective-C errors."""

    def __init__(self, error: Any, message: str | None = None):
        super().__init__(dict(error=error.description(), message=message))
