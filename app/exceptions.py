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
