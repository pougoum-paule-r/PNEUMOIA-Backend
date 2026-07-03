"""
Custom application exceptions.
"""


class PneumoIAException(Exception):
    """Base exception for all PneumoIA errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        """Initialize exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ValidationError(PneumoIAException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        """Initialize validation error."""
        super().__init__(message, code="VALIDATION_ERROR")


class AuthenticationError(PneumoIAException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        """Initialize authentication error."""
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(PneumoIAException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        """Initialize authorization error."""
        super().__init__(message, code="AUTHORIZATION_ERROR")


class NotFoundError(PneumoIAException):
    """Raised when resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        """Initialize not found error."""
        super().__init__(message, code="NOT_FOUND_ERROR")


class MLModelError(PneumoIAException):
    """Raised when ML model operations fail."""

    def __init__(self, message: str = "ML model error occurred"):
        """Initialize ML model error."""
        super().__init__(message, code="ML_MODEL_ERROR")


class DatabaseError(PneumoIAException):
    """Raised when database operations fail."""

    def __init__(self, message: str = "Database error occurred"):
        """Initialize database error."""
        super().__init__(message, code="DATABASE_ERROR")
